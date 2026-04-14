---
name: using-tooltesters
description: Information about using the riscos-tooltester command, the `tests.txt` file format and replacements that can be used. Use this when the riscos-tooltester command (or its direct perl script `test.pl`) is used to manage testing.
license: MIT
---
# Test Runner Guide for Agents

This document describes the Pyromaniac test system so that agents can understand
how to run tests, interpret results, and diagnose failures.

## Overview

The test system uses a Perl script `testcode/test.pl` to execute test suites.
Each suite is described by a file `testcode/tests-<name>.txt`. Tests run a
command-line tool, capture its output, and compare it against expected output in
files under `testcode/expect/`.

---

## Running Tests

### Direct make invocation

Usually commands are managed through a Makefile, using a command like:

```bash
make tests TEST=<suite-name>
```

The `TEST=` argument maps to `testcode/tests-<name>.txt`. Omit `TEST=` to run
all suites.

### Direct invocation

The tool can be directly invoked on test script like this:

```bash
riscos-tooltester mytool testdir
```

Commonly the tests are held in a directory `testcode` or `testdata`.

---

## Test Specification File Format

Test suite files are named `tests-<suite-name>.txt`. They are line-oriented;
`#` begins a comment. Statements have the form `<Keyword>: <argument>`.

### Structure

Tests are grouped; a `Group:` block sets defaults that each `Test:` within it
inherits. A `Test:` overrides those defaults. A `-` prefix on a statement
(with no argument) clears a group-level setting.

```
Group: Descriptive Group Name

Command: $TOOL --some-flags --command "$ARG1"
Expect: expect/mymodule/default-expect

Test: Basic case
Args: hello

Test: Error case
Args: badarg
RC: 1
Expect: expect/mymodule/error-case
```

### All Statements

| Statement | Meaning |
|-----------|---------|
| `Include: <file>` | Include another file inline |
| `Suite: <name>` | Suite name for JUnitXML output |
| `Group: <name>` | Begin a group (sets defaults for following Tests) |
| `Test: <name>` | Begin a test definition |
| `Command: <cmd>` | Shell command to execute |
| `Capture: <mode>` | What to capture: `stdout`, `stderr`, or `both` (default `both`) |
| `File: <path>` | Source filename, available as `$FILE` |
| `Args: <value>` | Arbitrary arguments; available as `$ARGS`, `$ARG1`, `$ARG2`, … |
| `Expect: <path>` | File to compare captured output against |
| `Replace: <path>` | Replacement script to normalise output before comparison |
| `Creates: <files>` | Space-separated files expected to be created (deleted before/after) |
| `CreatesDir: <dirs>` | Directories expected to be created (removed after) |
| `Length: <n>` | Expected byte length of the created file |
| `Removes: <file>` | File expected to be deleted by the command |
| `Absent: <file>` | File expected not to exist after the command |
| `RC: <n>` | Expected return code (default 0) |
| `Input: <file>` | File supplied as stdin |
| `InputLine: <text>` | Text supplied as stdin, followed by a newline |
| `Env: <VAR>=<value>` | Environment variable set for this test only |
| `Disable: <message>` | Disable the test or group with a reason |

### Substitution Variables

These expand inside statement arguments:

| Variable | Value |
|----------|-------|
| `$TOOL` | The tool under test (path passed on the command line) |
| `$FILE` | Value of the `File:` statement |
| `$BASE` | Base filename (without directory) from `$FILE` |
| `$OFILE` | Generated object file path |
| `$SFILE` | Generated assembler file path |
| `$CFILE` | Generated C file path |
| `$ARGS` | Full value of the `Args:` statement |
| `$ARG1`, `$ARG2`, … | Individual whitespace-split tokens from `Args:` |

---

## Test Output and Interpreting Results

### Live output format

Each test prints a single line like:

```
Group Name / Test Name ... OK
Group Name / Test Name ... FAIL: Expected output did not match
Group Name / Test Name ... CRASH: Expected RC 0, got 139
```

- `OK` — test passed
- `FAIL` — test ran but output or RC was wrong
- `CRASH` — the command was killed by a signal

At the end of each suite, totals are printed:

```
Pass: 58  Fail: 0  Crash: 0  Skip: 0
```

### Diff output on failure

When output does not match, a diff is shown immediately below the `FAIL` line.
The diff uses a line-number prefix and a marker character:

| Marker | Meaning |
|--------|---------|
| `:` | Line matches (shown for context) |
| `+` | Line is in the **actual output only** (extra/wrong) |
| `-` | Line is in the **expected file only** (missing from actual) |

Example:
```
 1 : Group header line
 2 + data: [{'number': 0, 'enabled': False, ...}]
   - data: [{'triggered': False, 'enabled': False, ...}]
```
This means line 2 in actual output has `number` first but the expected file has
`triggered` first.

### The `-actual` file

Whenever output does **not** match the expected file, `test.pl` writes the
(post-replacement) actual output to `<expect-file>-actual`. For example:

```
testcode/expect/pymodules/timermanager/sysrq-list-claimed-actual
```

This is the most useful file for diagnosing failures — it shows exactly what the
tool produced after replacements were applied. Compare it to the expected file
using a normal diff:

```bash
diff testcode/expect/mymodule/mytest testcode/expect/mymodule/mytest-actual
```

When the test passes, the `-actual` file is deleted. Stale `-actual` files from
previous runs may linger; only trust them if you just ran the relevant test.

---

## Expect Files

Expect files live under `expect/<suite-name>/<test-name>`. They contain
the verbatim expected output. No special syntax — plain text.

Common conventions:
- Normalised placeholder tokens replace variable data (e.g. `SHA`, `BRANCH`,
  `XXXXXXXX`, `DATE`, `TESTDATA`)
- RISC OS addresses appear normalised by the replacement script rather than raw hex

---

## Replacement Scripts

A `Replace: <path>` statement applies a script to the actual output **before**
comparing it to the expected file. This is used to normalise variable data such
as:
- Git commit SHAs
- Memory addresses
- Branch names (`master` vs `main`)
- Dates and timestamps
- Absolute paths

Replacement scripts are similar in intent to `sed`. They live alongside the
expect files, by convention named `<test-name>_replacements`.

### Replacement script syntax

- Lines starting with `#` or containing only whitespace are ignored.
- Lines beginning with `%` are directives:
  - `%include <file>` — include another replacement file inline
- All other lines are **rules**. Each rule has an optional **condition** followed
  by an **action**, separated by whitespace.

#### Conditions

| Form | Meaning |
|------|---------|
| `<n>` | Apply only to line number n (1-based) |
| `<n>-<m>` | Apply to lines n through m |
| `-<m>` | Apply to lines 1 through m |
| `<n>-` | Apply to lines n onwards |
| `/<regex>/` | Apply only if the line matches the regex |
| (none) | Apply to every line |

Append `!` to negate a condition: `/regex/!` means "if line does NOT match".

Conditions can be combined: `3-10 /pattern/` means "lines 3–10 that also match
the pattern".

#### Actions

| Action | Meaning |
|--------|---------|
| `p` | Output the line immediately and move to the next line |
| `q` | Stop processing; end the output here (line is not included) |
| `d` | Skip this line entirely (do not include in output) |
| `s/<from>/<to>/` | Substitute regex match within the line |
| `s/<from>/<to>/g` | Substitute all occurrences |
| `s/<from>/<to>/i` | Case-insensitive substitution |
| `s/<from>/<to>/gi` | Both flags |

#### Examples

```
# Normalise all commit SHAs
s/\[(main|master)( \(root-commit\) | )[a-f0-9]+\]/[BRANCH$2SHA]/

# Replace absolute test data paths
s!/[^ ]+/testcode/testdata!TESTDATA!g

# Skip git hint lines
/hint: .*/ d

# Normalise memory addresses (wildcard addresses)
s/([^0-9a-f\-])[0-9a-f]{8}/$1XXXXXXXX/gi

# Include a shared replacement file
%include status_replacements
```

### Shared replacement files

The `testcode/expect/` directory might contain reusable replacement files:

| File | Purpose |
|------|---------|
| `address_replacements` | Normalise known RISC OS address ranges (kernel, RMA, heap, etc.) |
| `address_any_replacements` | Same plus catch-all 8-digit hex address replacement |
| `ansi_replacements` | Replace ANSI escape codes and `\r` with readable tokens |

Per-suite shared files are typically placed alongside their expect files and
included with `%include`.

---

## Common Patterns and Tips

### Diagnosing a failure

1. Run the suite: `make tests TEST=<name> 2>&1 | tee output.log`
2. Look at the `FAIL:` line message in the output or log.
3. Read `expect/<suite>/<test>-actual` — this is exactly what the tool
   produced after replacements.
4. Diff it against the expected file to see what changed.
5. If the difference is in **variable data** (addresses, timestamps, SHAs) and
   no replacement is normalising it, add a substitution rule to the replacement
   script.
6. If the difference is in **structural output** (different ordering, new or
   removed lines, different text), update the expected file to match the new
   correct output.

### When to update expected files vs fix code

- Update the **expected file** when output is correct but differs due to
  environmental variation (e.g. git version differences, dictionary order
  changes, argparse version differences).
- Fix the **code** when the output is wrong.
- Add/update a **replacement script** when the output varies between runs for
  legitimate reasons (SHAs, timestamps, addresses, absolute paths).

### Return code failures

If a test fails with `Expected RC 0, got N`, the tool crashed or errored.
Check the `-actual` file for any error message.

### Missing `-actual` file after failure

If a test fails with an RC mismatch but no expected output mismatch (no `Expect:`
statement, or RC failure prevents comparison), there will be no `-actual` file.
Re-run with extra verbosity or add temporary debug output to diagnose.

---

## Test Data

Test data files used by tests live in `testcode/testdata/`. Absolute paths to
this directory are normalised by replacement scripts (typically replaced with
the token `TESTDATA`).

---

## Suite Naming Conventions

Suite names follow a hierarchical pattern:
- `pymodules-<module>` — tests for Python extension modules
- `graphics-<area>` — graphics subsystem tests
- `filesystem-<area>` — filesystem tests
- `core`, `core-write` — core OS tests

Test suites are commonly split out and included from an all encompassing `tests.txt` which includes all the files. This allows individual suites to be run independantly.

The suite name is the part after `tests-` in the filename, e.g.
`testcode/tests-pymodules-iic.txt` → suite name `pymodules-iic`.
