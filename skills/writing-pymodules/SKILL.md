---
name: writing-pymodules
description: Describes how to build and test PyModules (Python modules for RISC OS Pyromaniac). Use when understanding, updating or creating PyModules to implement a RISC OS module for Pyromaniac.
---
# Pyromaniac

RISC OS Pyromaniac is a Python implementation of RISC OS.
It has modules just like RISC OS, called PyModules.

You can load a PyModule and test it with:

```
host-run pyrodev --common --load-pymodule <pymodule-filename> --command '<riscos command>'
```

If you had a BASIC program you wanted to use to test your module you could use:

```
host-run pyrodev --common --load-pymodule <pymodule-filename> --command 'Run <basic-filename>'
```

You cannot pass BASIC statements to the `--command` arguments.

---

## General Pyromaniac Structure (`riscos/`)

While the `PyModule` system handles modular extensions, the core OS logic is implemented directly in Python:

- **`riscos/quotedstrings.py`**: Provides the `QuotedStrings` class, essential for parsing command lines. It correctly handles space-separated arguments and double-quoted strings.
- **`riscos/readargs.py`**: Contains the core logic for `OS_ReadArgs`. When implementing this in C, remember that keyword definitions can be complex (e.g., abbreviations via the first character).
- **`riscos/evaluateexpression.py`**: Handles RISC OS expressions.
- **`riscos/gstrans.py`**: Handles string translation.
- **`riscos/sysvars.py`**: Handles system variables.
- **`riscos/vectors.py`**: Handles vector registration and dispatch.
- **`riscos/ticker.py`**: Handles timer registration and dispatch.
- **`riscos/kernel.py`**: Handles core kernel functionality (from booting and memory setup through SWI execution, to callbacks and tracing functions).
- **`riscos/bufferdata.py`**: Provides interfaces for writing to user buffers, with tracking of overflow and maximum data sizes (used by interfaces like file enumeration).
- **`riscos/swis/`**: Contains the SWI dispatchers. These often call into the core logic modules (like `readargs.py`).


---

## Python version

Pyromaniac uses **Python 2.7**, which has specific requirements:

* Use inheritance from `object` on all classes which would otherwise not inherit.
* `print` statements may have `(` around their parameters (this is safe in Python 2.7 and makes transition to Python 3 safer).


## Error Handling

### Error Definitions

Define errors with `error_base` and `errors` list in your PyModule class:

```
class JUnitXML(PyModule):
    error_base = 0x840000
    errors = [
        ('CreateFailed', "Failed to create JUnitXML handle"),
        ('CreateSuiteFailed', "Failed to create test suite"),
        ('CloseSuiteFailed', "Failed to close test suite"),
        ('BadSuiteOp', "Unknown TestSuite operation"),
        ('CreateCaseFailed', "Failed to create test case"),
        ('CloseCaseFailed', "Failed to close test case"),
        ('BadCaseOp', "Unknown TestCase operation"),
        ('CloseFailed', "Failed to close JUnitXML handle"),
        ('NoHandle', "No JUnitXML handle to close"),
        ('InitFailed', "Failed to initialise JUnitXML state"),
    ]
```

Error numbers are assigned sequentially from `error_base`:
- `CreateFailed` - &840000
- `CreateSuiteFailed` - &840001
- `CloseSuiteFailed` - &840002
- etc.

### Raising Errors

Use `self.error()` to raise defined errors:

```
def swi_create(self, regs):
    handle = self._create_handle()
    if handle < 0:
        raise self.error('CreateFailed')

    regs[0] = handle
    return True

def swi_testsuite(self, regs):
    handle = self.handles.get(handle_id)
    if not handle:
        raise self.error('NoHandle')

    if op == JUnitXML_TestSuite_OpUpdate:
        raise self.error('BadSuiteOp')
```

### Error Message Override

You can override the error message if needed:

```
raise self.error('BadSuiteOp', 'Custom error message')
```

---

## Module commands

A very basic PyModule might would look like this:

```
from riscos.modules.pymodules import PyModule
from riscos.errors import RISCOSSyntheticError


class NewModule(PyModule):
    version = '0.01'
    date = '26 Mar 2026'

    commands = [
            ('TestCommand', 'A Test command', 0x010000),
        ]

    def cmd_testcommand(self, args):
        """
        Syntax: TestCommand [<arg>]
        """
        self.ro.kernel.writeln("TestCommand: %r" % (args,))
```

Which would provide one command.

You could test it with a command like this:

```
host-run pyrodev --common --load-pymodule newmodule.py --command 'TestCommand hello world'
```

---

## Module SWIs

A module with SWIs would look like this:

```
from riscos.modules.pymodules import PyModule
from riscos.errors import RISCOSSyntheticError


class ModuleWithSWIs(PyModule):
    version = '0.01'
    date = '26 Mar 2026'
    swi_base = 0xC0540
    swi_prefix = "SWITest"
    swi_names = [
            "FirstSWI",
        ]

    def __init__(self, ro, module):
        super(ModuleWithSWIs, self).__init__(ro, module)
        self.swi_dispatch = {
                0: self.swi_firstswi,
            }

    def swi(self, offset, regs):
        func = self.swi_dispatch.get(offset, None)
        if func:
            return func(regs)

        return False

    def swi_firstswi(self, regs):
        self.ro.kernel.writeln("SWI called with R0 = %i" % (regs[0],))
        regs[0] = regs[0] + 1
        return True
```

Which provides one SWI and will print a message and increment R0.

The SWI functions:

* SWI parameters are passed in the `regs` array, and can be accessed using array syntax, eg `regs[0]`.
* Signed values can be accessed using `regs.signed[0]`
* Use dispatch dictionaries to determine the SWI methods to call, for speed.

The return from SWI calls has the following values:

- Return `True` - SWI handled successfully
- Return `False` - SWI not handled (will try next module)
- Raise `self.error()` - Return error to caller
- Raise `RISCOSSyntheticError()` - Return error to caller, for errors which are not defined in the header (rare).


You could test it by creating a BASIC program that looked like this:

```
SYS "SWITest_FirstSWI", 99 TO result%
IF result% = 100 THEN
  PRINT "SUCCESS!"
ELSE
  ERROR 0, "Failed - returned " + STR$result
ENDIF
```

Then test the two together with a command like this:

```
host-run pyrodev --common --load-pymodule newmodule.py --command 'Run TestModule'
```

## Memory Access

Pyromaniac provides convenient methods for reading from RISC OS memory via `self.ro.memory[address]`:

### Reading Strings

```
# Read null-terminated string from memory
filename_ptr = regs[1]
filename = self.ro.memory[filename_ptr].string
```

### Reading Quins (RISC OS Time)

```
# Read 5-byte quin (RISC OS time value)
time_ptr = regs[5]
quin = self.ro.memory[time_ptr].quin
```

### Reading Words

```
# Read multiple 32-bit words from memory
ptr = regs[2]
words = self.ro.memory[ptr].read_words(count)
```

### Single words

```
# Read a single 32-bit word from memory (unsigned)
ptr = regs[2]
word = self.ro.memory[ptr].word

# Read a single 32-bit word from memory (signed)
word = self.ro.memory[ptr].signedword

# Write a single 32-bit word to memory
self.ro.memory[ptr].word = word
```

### Double words (64-bit)

```
# Read a single 64-bit word from memory (unsigned)
ptr = regs[2]
dword = self.ro.memory[ptr].dword

# Read a single 64-bit word from memory (signed)
dword = self.ro.memory[ptr].signeddword

# Write a single 32-bit word to memory
self.ro.memory[ptr].dword = dword
```

### Bytes

```
# Read bytes from memory
ptr = regs[3]
data = self.ro.memory[ptr].read_bytes(length)

# Writing bytes to memory
self.ro.memory[ptr].write_bytes(data)
```

### Single byte

```
# Read byte from memory
ptr = regs[3]
data = self.ro.memory[ptr].byte

# Writing byte to memory
self.ro.memory[ptr].byte = data
```

---

## Time Conversion

### Using quin_to_datetime

The `riscos.rotime` module provides `quin_to_datetime()` for converting RISC OS time to Python datetime:

```
from riscos.rotime import quin_to_datetime

# Read quin from memory
quin = self.ro.memory[time_ptr].quin

# Convert to datetime
dt = quin_to_datetime(quin)

# Format as ISO 8601
timestamp = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
```

---

## File I/O

### Using ro.kernel.api.open

**Never use Python's built-in `open()`** - it accesses the host filesystem, not the RISC OS filesystem.

```
# WRONG - uses host filesystem
self.file = open(self.filename, 'w')

# CORRECT - uses RISC OS filesystem
self.file = self.ro.kernel.api.open(self.filename, 'w')
```

### File Operations

```
# Open file for writing
self.file = self.ro.kernel.api.open(self.filename, 'w')

# Write data
self.file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
self.file.write('<testsuites>\n')

# Flush to ensure data is written
self.file.flush()

# Close file
self.file.close()
```

### File Modes

Supported modes:
- `'w'` - Write (create/truncate)
- `'r'` - Read
- `'a'` - Append
- `'w+'` - Read/write (create/truncate)
- `'r+'` - Read/write (existing file)


---

## Calls to SWIs

SWIs can be called through the interfaces in `riscos/api/__init__.py` which is usually referenced as `self.ro.kernel.api`.
There are SWI interfaces present for most common SWIs.
Output to the screen using `OS_Write*` SWIs can be achieved most efficiently by using:

* `self.ro.kernel.write(str)` to write a string to the output.
* `self.ro.kernel.writeln(str)` to write a string to the output followed by a newline.

### Passing arguments to SWIs API

When calling SWIs via `self.ro.kernel.api.swi(swi_number, args)`, the `args` parameter **must be an iterable** (tuple or list), even if passing only a single register value. Passing a single integer directly will result in a `TypeError: 'long' object is not iterable`.

- **Correct**: `self.ro.kernel.api.swi(swis.Hourglass_On, (r1,))`
- **Incorrect**: `self.ro.kernel.api.swi(swis.Hourglass_On, r1)`


---

## Custom Entry Points (Vectors & Callbacks)

Beyond SWIs and Commands, PyModules can define custom entry points for use with vectors (e.g., `OS_Claim`) or callbacks.

- **Definition**: Add the names to `entrypoint_names` in your class definition.
- **Dispatch**: Implement a method with the same name. It will receive the `regs` object.
- **Address Retrieval**: Access the generated RISC OS address via `self.module.entrypoints['name'].address`.

```python
class MyModule(PyModule):
    entrypoint_names = ['my_vector_handler']

    def initialise(self, arguments, pwp):
        # Claim a vector using the generated entry point address
        self.ro.kernel.api.os_claim(vectors.MyV,
                                    self.module.entrypoints['my_vector_handler'].address,
                                    self.pwp.address)

    def my_vector_handler(self, regs):
        # Handle the vector call
        return True # Return True to claim, False to pass on
```

If vectors are claimed this way, they must be released in the finalisation method.

---

## Debugging with `debug_register_ivar`

To support the `--debug <name>` command-line flag, use the `debug_register_ivar` registration mechanism.

- **Initialization**: Define a boolean `self.debug_<name>` in `__init__`.
- **Registration**: Call `self.ro.debug_register_ivar('<name>', self)`.
- **Usage**: Use standard Python `print` statements (not `kernel.writeln`) wrapped in checks of the debug flag.

```python
def __init__(self, ro, module):
    super(MyModule, self).__init__(ro, module)
    self.debug_mymod = False
    self.ro.debug_register_ivar('mymod', self)

def some_method(self):
    if self.debug_mymod:
        print("Debugging info...")
```

---

## Private Word Access

The module's private word pointer address is available via `self.pwp.address`. This is typically passed as the `handle` (R2) when claiming vectors or registering for services.

---

## Vector Handler Return Values

When an entry point is used as a vector handler (e.g., via `OS_Claim`):
- Returning `True` is equivalent to claiming the vector (the handler returns to the caller of the vector).
- Returning `False` is equivalent to passing the vector on (the handler returns to the next claimant in the chain).
- This behavior is handled by `entrypoint_dispatch` in `pymodules.py`, which adjusts the `pc` based on the return value.


---

## Integration Tests

PyModule tests live in `testcode/` and use a gold-master comparison approach. Run them with:

```
bash run-tests <suite-name>
```

The log is written to `/tmp/pyro-tests-<suite-name>.log`. Read that file for detailed pass/fail output — do not re-run to inspect results.

### Test suite file format

Each suite is a file `testcode/tests-<name>.txt`. The master list `testcode/tests.txt` includes them via `Include:` lines (add your new suite there, in alphabetical order within its section).

A minimal suite file looks like:

```
#
# SUT:    Extension Modules: MyModule
# Area:   SWIs
# Class:  Functional
# Type:   Integration test
#


Group: MyModule: Basic operations

Test: Init and reinit
Command: $TOOL --load-internal-modules --command "RMReinit MyModule"
Expect: expect/pymodules/mymodule/reinit

Test: Help text
Command: $TOOL --load-internal-modules --help-config mymodule.implementation
Expect: expect/pymodules/mymodule/help_implementation
```

`$TOOL` is substituted with the pyro.py invocation. Standard options used in most suites:

- `--load-internal-modules` — load all built-in modules
- `--load-internal-group core` — load only the core group (faster for basic tests)
- `--config key=value` — set a configuration value
- `--set-variable "Name=value"` — set a RISC OS system variable
- `--set-variable-encoded "Name:charset=value"` — set a variable with charset-encoded content
- `--command 'RISC OS command'` — execute a command (may be repeated)
- `--boot-debug <flag>` — enable a debug flag during boot

### Parameterised tests

Groups can share a command template, with each test supplying an `Args:` substitution (`$ARG1`, `$ARG2`, ...):

```
Group: MyModule: Operations

Command: $TOOL --load-internal-modules bin/mymodule_test $ARG1
Expect: expect/pymodules/mymodule/$ARG1

Test: Create handle
Args: create

Test: Close handle
Args: close
```

### Replacement scripts

If the output contains timestamps or other variable content, use a `Replace:` file to normalise it before comparison:

```
Test: Show timestamp
Command: $TOOL --load-internal-modules --command "MyMod_ShowTime"
Expect: expect/pymodules/mymodule/showtime
Replace: expect/pymodules/mymodule/replacements
```

A replacements file contains Perl-style substitutions, one per line:

```
s/\d{4}-\d{2}-\d{2}/DATE/g
s/\d{2}:\d{2}:\d{2}/TIME/g
```

### Creating expectation files

Run the command manually and capture its output to create the initial expectation file:

```
python3 pyro.py --load-internal-modules --command "MyCommand" > testcode/expect/pymodules/mymodule/mycommand
```

Then verify the content looks correct before committing it. Expectation files live in `testcode/expect/<suite-subpath>/`.

### Adding a test to an existing suite

1. Open the relevant `testcode/tests-<name>.txt`.
2. Add a `Test:` block inside the appropriate `Group:`, or create a new `Group:` if needed.
3. Create the corresponding expectation file in `testcode/expect/`.
4. Run `bash run-tests <name>` and confirm the new test passes.

### Registering a new suite

Add an `Include:` line to `testcode/tests.txt` in the appropriate section, in alphabetical order:

```
Include: tests-pymodules-mymodule.txt
```

---

## References

* If you need to convert a PyModule to or from C, refer to [references/convert-to-c.md](references/convert-to-c.md), and use the skills `writing-cmodules` and `using-cmhg`.
* If you need more information on the testing file format, use the still `using-tooltester`.
