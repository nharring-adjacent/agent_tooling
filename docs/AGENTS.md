# /docs/AGENTS.md
# For Agents: How to Work with the Project Documentation

Greetings, agent. This document provides the mandatory protocol for modifying or extending this project's human-readable documentation.

## Primary Directive: Documentation Maintenance

Your role here is to manage the Markdown files and configuration that generate the project's documentation website.

## Technical Specification

* **Framework:** This documentation is built using **MkDocs**.
* **Source Files:** All content is written in Markdown (`.md`) and located within this `/docs` directory.
* **Configuration:** The site's structure, navigation, and theme are all defined in the `mkdocs.yml` file located in the repository's root directory.

## Protocol for Modifying Documentation

You must follow these steps precisely when asked to update the documentation.

#### To Edit an Existing Page:

1.  Locate the relevant `.md` file within this `/docs` directory.
2.  Apply the required edits to the file.
3.  Proceed to the "Verification" step.

#### To Add a New Page:

1.  Create a new, appropriately named `.md` file within this `/docs` directory.
2.  Add your content to the new file.
3.  **Crucially, you must register the new page in the `mkdocs.yml` file.** Open the root `mkdocs.yml` and add a reference to your new file in the `nav:` section, following the existing structure. An unregistered page will not be visible on the website.
4.  Proceed to the "Verification" step.

#### Verification:

After any change, you must verify that the documentation site can still be built successfully. Run the following command from the repository root:
`mkdocs build`

If this command completes without errors, your task is successful. If it fails, you must analyze the error and correct the issue before completing your task.
