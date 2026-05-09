# RISC OS Porting Process

## Standard Layout

- Generate a `RISCOS/` directory inside the repository.
- Link sources into `RISCOS/c/` and headers into `RISCOS/h/`.
- Use `riscos-project create --type lib --name NAME` for the base library skeleton.
- Run `riscos-project update` and `riscos-project create-git` after the makefiles are generated.

## Command Tools And Examples

- Any source with `main()` should usually get its own `LibraryCommand` makefile.
- Keep the command source list small and explicit.
- If a command needs extra compile-time switches, set them in the generated command makefile.
- If a command needs another library, add it in `LIBS` as `C:<name>.o.lib<name>`.
- For include paths, use `INCLUDES += C:<name>.` style entries.

## Library Validation

- Build the port with `riscos-amu export`.
- Check the generated exports and object list if the build picks up the wrong files.
- When discovery gets the source tree wrong, fix it with the script's overrides before editing source.

## Source Compatibility

- Keep changes local to the smallest file set that unblocks the build.
- Prefer RISC OS-friendly includes and headers over host-specific paths.
- When the Norcroft compiler rejects a construct, adapt to C89-style declarations and remove unsupported syntax only where needed.
- If the repository has a generated config header, make sure the port has an equivalent header or a suitable bundled fallback.

## Practical Overrides

- `--name` when the upstream project name is generic or misleading.
- `--source` and `--header` when autodiscovery misses the real code.
- `--exclude-source` when examples, tests, or amalgamated sources leak into the library build.
- `--command-define` for test/example-specific flags.
- `--command-lib` for secondary dependencies.
