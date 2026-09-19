# The Automation Architect's Playbook

The book source is in `book_final.md`; `index.html` is its hand-styled web
edition. The repository intentionally keeps that custom HTML rather than
replacing it with a generic Markdown renderer.

## Reproducible checks

The checker uses only the Python standard library and performs no network
requests. It verifies:

- balanced Markdown fenced code blocks and existing local Markdown links;
- unique HTML IDs, valid internal anchors, and existing local HTML assets;
- that every numbered chapter present in the Markdown source is represented in
  the web edition;
- an HTML5 doctype.

Run it with:

```bash
python scripts/book.py check
```

## Build the static site

```bash
python scripts/book.py build --output dist
```

The build first runs all checks, then copies `index.html` and `assets/` into a
new or empty output directory and writes `build-manifest.json` with
deterministic SHA-256 hashes for the output and both book sources. To protect
source files, in-repository output is limited to `./dist`, and non-empty output
directories are refused. Building the same revision twice produces identical
output.
