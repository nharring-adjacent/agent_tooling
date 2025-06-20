# Doxygen Embedding Tool

This tool processes a repository using Doxygen, extracts class documentation, generates vector embeddings for each text chunk, and stores the results in a Parquet file using **polars**.

## Usage

Call `doxygen_embedding_tool` with the repository path, output Parquet file, embedding service URL, and optional API key.
