# Temporary

This directory's contents are temporary. They will be moved at a later date.

## Building and checking

The publishing pipeline requires GNU Make and Java 17. The Saxon processor is
included as `build/saxon8.jar`; no additional Java libraries are needed.

Run `make` from the repository root to regenerate the specification HTML,
intermediate XML, essence XML, and the two legacy unit files. The Makefile tracks
the imported stylesheets, entity files, graphics metadata, and Saxon jar so that
changes to these inputs trigger the affected transforms.

Run `make check` with Python 3.12 or later to build a temporary copy and run the
regression checks without modifying the committed artifacts. These checks verify
the definition inventory, XML syntax, image references, local HTML resources,
incremental dependencies, and consistency with committed artifacts. HTML markup
and text are compared after ignoring serialization whitespace; the other four
artifacts are compared byte for byte. These are publishing checks, not a UCUM
parser or a claim of functional-test conformance.
