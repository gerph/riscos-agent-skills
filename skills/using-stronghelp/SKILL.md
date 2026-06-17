---
name: using-stronghelp
description: Development and maintenance of StrongHelp manuals for RISC OS. Use when the agent needs to create, edit, or build StrongHelp manuals, or when processing help pages in the StrongHelp format.
license: MIT
---

# StrongHelp Development

This skill provides guidance for developing StrongHelp manuals, which are the standard hypertext help format for RISC OS.

## Quick Start

1.  **Extract a manual**: `riscos-shextract --extract-dir <dirname> <manual_file,3d6>`
2.  **List pages**: `riscos-shextract --list <manual_file,3d6>`
3.  **Build a manual**: `riscos-strongcopy -o <manual_file,3d6> <directory>`

## Developing Pages

Every StrongHelp page is a text file where the first line is the title. Use `#Parent` on every page to ensure navigation works correctly.

### Workflow

1.  **Identify the target page**: Find the existing page or determine the filename for a new one.
2.  **Apply Syntax**: Use the syntax guide in [references/syntax.md](references/syntax.md) for formatting and links.
3.  **Organize Structure**: Use the structure guide in [references/structure.md](references/structure.md) for directory organization and special files.
4.  **Verify Links**: Ensure all links point to valid page names or files.
5.  **Build**: Use `riscos-strongcopy` to package the directory into a `.3d6` manual file.

## Tools

-   **riscos-shextract**: Extracts contents from a StrongHelp `.3d6` container.
-   **riscos-strongcopy**: Packages a directory into a StrongHelp `.3d6` container.

## Best Practices

-   **Navigation**: Include `#Parent !Root` (or the appropriate parent) on every page.
-   **Columns**: Use `TAB` for alignment instead of spaces to ensure correct rendering.
-   **Formatting**: Use `#fCode` for examples and `#H1` for main headers.
-   **Organization**: For manuals with many pages, use prefix directories (e.g., `Wimp_`) or first-letter ranges (e.g., `[a-z]`).
-   **Filenames**: Remember that StrongHelp uses special filenames for redirection (e.g., `OLD>NEW`).
