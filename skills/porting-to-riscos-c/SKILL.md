---
name: porting-to-riscos-c
description: Port C projects to RISC OS using `riscos-cport`, RISC OS makefiles, and Norcroft/RISC OS build validation. Use when a repository needs a RISC OS library or command-line port, especially when you need to create a `RISCOS/` tree, generate `Makefile,fe1` files, or repair source for the RISC OS toolchain.
license: MIT
---

# Porting To RISC OS C

Use this skill when the task is to turn a C repository into a RISC OS buildable port.
Prefer the repository's existing structure and let `riscos-cport` do the first pass.

## Workflow

1. Inspect the repository layout and detect the real entry points.
2. Run `riscos-cport` on the repository root. This will create Makefiles for each of the files and libraries it finds within the source directory. It will create symlinks within the `RISCOS/c` and `RISCOS/h` which point to the original files. This should be sufficient to build the commands or libraries with `riscos-amu export` or `riscos-amu -f Makefile...,fe1`.
3. Use overrides when discovery is wrong or incomplete. If the code is failing to build, there may be updates that are needed for the `riscos-cport` command line to ignore certain files or explicitly set defines and includes.
4. Build the generated `RISCOS/` tree with `riscos-amu export`.
5. Build any generated command makefiles with `riscos-amu -f Makefile...,fe1`.
6. Patch source only when the Norcroft compiler or the RISC OS build model requires it.


## Use The Tool

Prefer these switches when discovery needs help:

- `--name` for the RISC OS component/library name.
- `--source`, `--header`, `--internal-header`, `--export-header` for explicit file control.
- `--exclude-source` to remove sources autodiscovery picked up incorrectly.
- `--command-source` for example tools and tests that contain `main()`.
- `--define` and `--command-define` for compile-time configuration.
- `--include` and `--command-lib` for extra include paths and libraries.

If a repository is mainly a command-line tool, treat the command source as the important artifact:

- keep the command Makefile(s)
- exclude unrelated sources from the command build
- add any required command-only defines or libraries explicitly

## RISC OS Porting Rules

Read [references/porting-process.md](references/porting-process.md) when you need the build rules, file layout, or validation sequence.

## Source Fixes

- Keep edits narrow and RISC OS specific.
- Prefer compatibility defines and small header shims over broad rewrites.
    - For RISC OS-specific changes, the define `__riscos` will be set for the platform.
    - For RISC OS 64-specific changes, the define `__riscos64` will be set for the platform.
    - For feature-specific changes use a define to delineate the state (eg `ENABLE_CRYPTO`).
- Preserve upstream comments and layout unless a change is required to compile.
- Rebuild after every meaningful source fix.

## Validation

- Libraries: `riscos-amu export`
- Commands: `riscos-amu -f MakefileExample,fe1`
- If a command fails because of an external dependency, note that separately rather than forcing the port to absorb it.
