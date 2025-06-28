# Stage 1: Build Comby from source
FROM ubuntu:22.04 as comby-builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    m4 \
    pkg-config \
    zlib1g-dev \
    libgmp-dev \
    libpcre3-dev \
    libev-dev \
    libpcre2-dev \
    libssl-dev \
    libsqlite3-dev \
    libffi-dev \
    libncurses-dev \
    autoconf \
    automake \
    libtool \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install OPAM (OCaml Package Manager)
RUN apt-get update && apt-get install -y opam \
    && opam init --disable-sandboxing -y --bare \
    && opam switch create 4.14.0 \
    && eval $(opam env)

# Install OCaml dependencies
RUN opam update && opam install -y \
    dune \
    core \
    ppx_jane \
    ppx_deriving \
    ppx_deriving_yojson \
    yojson \
    && eval $(opam env)

# Clone and build Comby
WORKDIR /build
RUN git clone --depth 1 --branch 1.8.1 https://github.com/comby-tools/comby.git \
    && cd comby \
    && opam install -y --deps-only . \
    && eval $(opam env) \
    && make \
    && make release \
    && mv _release/comby /usr/local/bin/comby

# Stage 2: Build the Python application
FROM python:3.11-slim as python-builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package installer)
RUN pip install --no-cache-dir uv

# Create a dummy README.md if it doesn't exist
RUN touch README.md

# Copy only the dependency files first to leverage Docker cache
COPY pyproject.toml .

# Install dependencies with uv
RUN uv pip install --system --no-cache-dir -e .

# Copy the rest of the application (excluding files in .dockerignore)
COPY . .

# Stage 3: Create the final runtime image
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgmp10 \
    libffi8 \
    libpcre3 \
    libev4 \
    libpcre2-8-0 \
    libssl3 \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Comby binary from the builder
COPY --from=comby-builder /usr/local/bin/comby /usr/local/bin/

# Create a non-root user
RUN useradd -m appuser && \
    mkdir -p /workspace && \
    chown appuser:appuser /workspace && \
    chmod 755 /workspace

# Switch to non-root user
USER appuser

# Set the working directory
WORKDIR /workspace

# Copy the Python application from the builder
COPY --from=python-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-builder /app/mcp_server /app/mcp_server
COPY --from=python-builder /app/pyproject.toml /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000"]
