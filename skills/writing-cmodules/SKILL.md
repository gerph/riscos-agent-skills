---
name: writing-cmodules
description: Development notes and procedures for working with RISC OS modules. Describes the layout of the project, how to build and tests, common patterns with SWIs and Vectors. Use when creating RISC OS modules, creating SWI implementations, claiming vectors, or writing service handlers.
license: MIT
---
# C modules

## Module Structure

### Creating a template project

* To create the base files, use `riscos-project create --name <project> --type cmodule --skeleton`
  This will create the files in the current directory.
* Then build the project to confirm that it works before making changes.

### Core Files

A RISC OS module requires three essential components:

1. **CMHG file** (`cmhg/*`) - Module definition describing:
   - Module title and help string (which should start with a capital letter, using Pascal Case).
   - SWI chunk base number
   - Entry points (initialisation, finalisation, SWI handler, veneers and others)
   - SWI decoding table (names of exported SWIs)
   - Error blocks
   - Command definitions

2. **Module interface** (`c/module`) - C code implementing:
   - `Mod_Init()` - Called when module is loaded
   - `Mod_Final()` - Called when module is unloaded
   - `Mod_SWI()` - Dispatches SWI calls to appropriate functions
   - `Mod_Service()` - Dispatches Services to appropriate functions

If the service handler or SWI handler is not required, it can be omitted, and the CMHG entry commented out.

3. **Makefile** (`Makefile,fe1`) - Build configuration using AMU (RISC OS make)

For more information about the CMHG file format, a blank template can be generated for reference with `riscos-cmunge -blank blank`. Do not commit the template file read in this way - always change the module header. See the `using-cmhg` skill for more information.

When editing the CMHG file or Makefiles, retain the commented lines to help guide future authors.

### File Naming Conventions

- C source files: `c/<name>` (no extension in filename, but `#include` uses `.h`)
- C header files: `h/<name>` (no extension in filename)
- Makefiles: `Makefile,fe1` (comma suffix is RISC OS file type)
- BBC BASIC files: `<name>,fd1`
- Built modules: `rm32/<name>,ffa` (32-bit RAM module)

In the filesystem:

**Wrong**:
* `c/name.c`
* `h/name.h`

**Correct**:
* `c/name`
* `h/name`


## Module Finalisation

### Mod_Final Function

The `Mod_Final()` function is called when the module is killed (unloaded). Ensure all resources are cleaned up:

```c
_kernel_oserror *Mod_Final(int fatal, int podule_base, void *pw)
{
    dprintf("Module JUnitXML dying\n");

    // Finalise the state manager - closes files, frees memory
    junit_state_final();

    return NULL;
}
```

Only report errors if shutdown is being prevented, and never leave the module in an inconsistent state - if an
error is returned, the finalisation code will be called again and must never crash.

### State Finaliser Pattern

The state finaliser should clean up in reverse order of creation:

```c
int junit_state_final(void)
{
    junit_handle_t *h, *next_h;

    // Iterate through all handles
    for (h = junit_global.handles; h != NULL; h = next_h) {
        next_h = h->next;
        free_handle(h);
    }

    // Clear global state
    junit_global.handles = NULL;
    junit_global.next_handle_id = 0;

    return 0;
}

static void free_handle(junit_handle_t *h)
{
    if (h == NULL) {
        return;
    }

    // Free filename string
    junit_strfree(&h->filename);

    // Close file if open
    if (h->fp != NULL) {
        fclose(h->fp);
        h->fp = NULL;
    }

    // Free all test suites
    junit_testsuite_t *ts, *next_ts;
    for (ts = h->suites; ts != NULL; ts = next_ts) {
        next_ts = ts->next;
        free_testsuite(ts);
    }

    // Free handle structure
    free(h);
}
```

### Key Points

1. **Close files** - Use `fclose()` for any open `FILE *` pointers
2. **Free memory** - Free all `malloc()`'d memory
3. **Clear state** - Reset global variables to initial state
4. **Handle errors gracefully** - Finalisation should not fail unless there is a resource lock preventing it.

## SWI Interface

* SWIs are numbered relative to a base chunk. Find the SWI numbers for the module you are writing in the `h/modhead` header.
* Always look at the `h/modhead` file to find the signature for the SWI handlers.
* The SWI handler receives registers through a structure:

##E SWI Decoding Table

The `swi-decoding-table` in `cmhg/modhead` maps SWI names to handler functions.

**Format**:

```cmhg
swi-decoding-table: <prefix> <name1>/<handler1> <name2>/<handler2> ...
```

**Example**:

```cmhg
swi-decoding-table: JUnitXML Create/SWI_Create TestSuite/SWI_TestSuite TestCase/SWI_TestCase Close/SWI_Close
```

This creates:
- `JUnitXML_Create` → `SWI_Create()`
- `JUnitXML_TestSuite` → `SWI_TestSuite()`
- `JUnitXML_TestCase` → `SWI_TestCase()`
- `JUnitXML_Close` → `SWI_Close()`

### Common Mistake - Name Duplication

**Wrong:**
```cmhg
swi-decoding-table: JUnitXML JUnitXML_Create/SWI_Create
```
This creates `JUnitXML_JUnitXML_Create` (prefix is prepended to the name).

**Correct:**
```cmhg
swi-decoding-table: JUnitXML Create/SWI_Create
```
This creates `JUnitXML_Create`.

All the SWI handlers take the same form:

```c
_kernel_oserror *SWI_Handler(int swi, _kernel_swi_regs *r, void *pw)
{
    ...
}
```

SWI handlers should decode their parameters from registers into typed variables before passing the values to other
implementation functions. They should not pass in the `_kernel_swi_regs` outside the module interface C file (eg they
should pass parameters to hardware, or implementation functions as typed values).

### X-SWI Convention

For error handling, RISC OS uses the convention:

- Standard SWI: Reports an error through the error handler
- X-prefix: Sets V flag on error, error block pointer in R0.
- Within modules, you should always call SWIs with the X-prefix and examine or return errors.
- In BASIC test code, use standard SWI calls unless the error is explicitly being checked.

```basic
REM BBC BASIC - use X-SWIs for error handling
SYS "XTimer_ReturnNumber", 0 TO r0%,r1%,r2%;flags%
IF flags% AND 1 THEN
  error_num% = r0%!0 : REM Error number at R0+0
  PRINT "Error returned: &";~error_num%
ELSE
  PRINT "Timers count: ";r0%
ENDIF
```

### SWI Names

* SWI names follow the pattern `<Module>_<Function>` with PascalCase, for example `Timer_ReturnNumber`
* The X-prefixed SWIs are automatically handled by the Kernel, and do not need to be registered.
* CMHG may be used to register the SWI names.
* SWI names are defined in the header `swis.h`.

## C Coding Standards

* Floating point should not be used in modules.
* Don't leave trailing spaces on files.
* 4 character indents.
* Magic numbers and strings (bare numbers and strings in the code) should be avoided.
    * Use `enum` if you need to enumerate a set of values like state values.
    * Use `#define` for values like bit-fields and constant strings.

### No Threading

RISC OS is single-threaded. Do not use threading or assume re-entrancy.

## Memory Management

### Private memory

Memory for the module is managed by standard `malloc`, `free`, `realloc` and `calloc` calls.
Under RISC OS 3.1, `realloc` was not functional and must not be used. Modules should not target RISC OS 3.1
unless explicitly directed to do so.

Otherwise, the module can use global and local variables as they would in any other program.

### Private Word

* The `pw` parameter in init/final/handler is a module-private workspace pointer.
* The private word should be passed to any calls to `OS_Claim`, `OS_Release`, `OS_AddCallback`
  and other interfaces that require a private word.
* The private work should never be dereferenced.

## Error Handling

RISC OS error blocks have a fixed structure:

```c
typedef struct _kernel_oserror_s {
    int errnum;        /* Error number */
    char errmess[252]; /* Error message */
} _kernel_oserror;
```

### Error Identifiers

Define error blocks in `cmhg/modhead` using the `error-identifiers` directive. Errors are automatically numbered sequentially from the `error-base`:

```cmhg
error-base: &840000

error-identifiers: \
    Err_CreateFailed("Failed to create JUnitXML handle"),
    Err_CreateSuiteFailed("Failed to create test suite"),
    Err_CloseSuiteFailed("Failed to close test suite"),
    Err_BadOp(&12e, "Unknown operation")
```

This generates error blocks with sequential numbers:
- `Err_CreateFailed` - error number &840000
- `Err_CreateSuiteFailed` - error number &840001
- `Err_CloseSuiteFailed` - error number &840002
- `Err_BadOp` - error number &12e

If the error is static, it MUST be defined within the CMHG file. Only if the error contains dynamic information should the error block be stored in the module global workspace. These symbols will be `#define`'d to hide their internal implementation - the actual symbol in the object file looks like `__err_Err_Name`.

Standard error numbers and strings are defined in the header `riscos/NewErrors.h`.


### Using Error Blocks in C Code

The generated header (`h/modhead`) provides error block pointers that can be returned directly from SWI handlers:

```c
#include "modhead.h"

_kernel_oserror *SWI_Create(int number, _kernel_swi_regs *r, void *pw)
{
    int handle = junit_create(filename, flags);

    if (handle < 0) {
        return Err_CreateFailed;  // Returns pointer to error block
    }

    r->r[0] = handle;
    return NULL;
}
```

### Benefits of CMHG Error Blocks

1. **Efficiency** - Error blocks are pre-allocated in the module image
2. **Consistency** - Error numbers are automatically assigned
3. **Maintainability** - Error messages are defined in one place
4. **Type safety** - Compiler checks error block references

### Implementation Pitfall
The standard practice is to use the macros defined in the generated header:
```c
#include "modhead.h"
...
return Err_NotRegistered; // Returns a pointer to an OS error block
```
**Problem found**: If you get undefined symbols during linking like `__err_Err_NotRegistered`, it usually means `o.modhead` is missing from the `OBJS` list in your `Makefile`.


## Time Handling

### RISC OS Quin Format

RISC OS time is stored as either a **quin** or a **5-byte time**.
This is a 5-byte (40-bit) little-endian value representing centiseconds since 1900-01-01 00:00:00 UTC.

* Conversion to strings can be performed using the SWI `Territory_ConvertDateAndTime`.
* The 5-byte value can be converted to date and time values with the SWI `Territory_ConvertTimeToOrdinals`


## Build System

### AMU Makefiles

The build uses AMU (RISC OS make) with `,fe1` filetype:

```makefile
OBJS = o.modhead \
       o.module \
       o.hardware

include CModule
```

If a new header is added, the makefile should be updated to add a dependency in the form `h.header`.
For example, if the file `c/hardware` was created and included the module header with `#include "modhead.h"`, a line should be added
beside the additional dependencies like:

```makefile
${OZDIR}.hardware: h.modhead
```

If a new header file like `h/os` is created, it would be included with `#include "os.h"` and the dependency in the makefile is `h.os`:

```makefile
${OZDIR}.hardware: h.os
```


### Build Targets

- `riscos-amu` or `riscos-amu ram` - Build RAM module
- `riscos-amu rom` - Build ROM module
- `riscos-amu BUILD26=1` - Build 26-bit compatible version
- `riscos-amu BUILD64=1` - Build 64-bit version
- `riscos-amu export` - Export headers/libraries
- `riscos-amu clean` - Remove build artifacts

### Output Directories

- `oz32/` - 32-bit object files for modules
- `rm32/` - 32-bit modules (RAM)
- `aof32/` - 32-bit AOF files (ROM)
- `oz64/` - 64-bit object files for modules
- `rm64/` - 64-bit modules (RAM)

## Testing

### Loading Modules

```basic
* `*RMLoad rm32.MODULE`: Load module
* `*RMKill MODULE`: Unload module
```

### BASIC Testing

Use SYS calls from BBC BASIC:

```basic
REM Standard SWI (error raises BASIC error)
SYS "Timer_ReturnNumber", 0 TO ,,,num_timers%

REM X-SWI (check flags for errors)
SYS "XTimer_Claim", 0, 0, 1000, 0 TO r0%,r1%,rate%;flags%
IF flags% AND 1 THEN
  error_num% = r0%!0
ENDIF
```

### Build Testing

```bash
riscos-build-run rm32 test_MODULE,fd1 \
  --command "*RMLoad rm32.MODULE" \
  --command "run test_MODULE,fd1"
```

Note: The `--command` argument takes RISC OS commands, NOT BASIC commands.

## Debugging

### Debug Output

Use conditional compilation for debug output:

```c
#define DEBUG

#ifdef DEBUG
#define dprintf if (1) printf
#else
#define dprintf if (0) printf
#endif

dprintf("Debug: value=%d\n", value);
```

Note: `printf` output goes to the debug stream, visible in build logs.

When debug is no longer required, comment out the `#define DEBUG` line. Uncomment if it is needed again.

### Build Verification

Always verify builds:

```bash
riscos-amu
riscos-build-run rm32 --command "*RMLoad rm32.<module>"
```

Only clean the build if there are problems with the invocation that are not expected (`riscos-amu clean`).

64-bit builds can be tested with a load, but cannot use BBC BASIC:

```bash
riscos-amu BUILD64=1
riscos-build-run --arch aarch64 rm64 --command "*RMLoad rm64.<module>"
```

## CI/CD

CI files can be created automatically and will generate `.robuild.yaml` which contains RISC OS commands to run.
Use `riscos-project create-ci` to create these files for the current project.


## Common features

### Claiming vectors

Vector claims are usually done in the module initialisation code. They must be released on module finalisation.

In these examples the vector example is `ReadLineV`.

In the Module initialisation function add a call to the vector claims, like this:

```c
_kernel_oserror *err;
err = vector_claims(pw);
if (err)
    goto failed;
```

In the Module finalisation function release the vector claims, like this:

```c
vector_releases(pw);
```

All vector management should be performed in the C file `c/vector`.

Vector numbers are defined in the include file `riscos/Vectors.h`.

Implement the claims in the `vector_claims` function, and the releases in `vector_releases` with code like this:

```c
#include "riscos/Vectors.h"

_kernel_oserror *vector_claims(void *pw)
{
    _kernel_oserror *err;

    err = os_claim(ReadLineV, ReadLineV_Entry, pw);
    return err;
}
_kernel_oserror *vector_releases(void *pw)
{
    _kernel_oserror *err;
    err = os_release(ReadLineV, ReadLineV_Entry, pw);
    return err;
}
```

The `os_claim` and `os_release` functions should be defined in the `c/os` file, like this:

```c
#include "swis.h"

_kernel_oserror *os_claim(int vector, void (*func)(void), void *pw)
{
    _kernel_oserror *err;
    err = _swix(OS_Claim, _INR(0,2),
                          vector, func, pw);
    return err;
}

_kernel_oserror *os_release(int vector, void (*func)(void), void *pw)
{
    _kernel_oserror *err;
    err = _swix(OS_Release, _INR(0,2),
                           vector, func, pw);
    return err;
}
```

Update the CMHG header file to add a `vector-handler` entry:

```
vector-handlers: ReadLineV_Entry/ReadLineV_Handler(error-capable:)
```

The handler for the vector should be implemented in a separate file, and has a prototype that looks like this:

```
int ReadLineV_Handler(_kernel_swi_regs *regs, void *pw)
{
    /* Decode registers into typed values, validate and call implementation function */
    return VECTOR_PASSON;
}
```

Watch out for recursion. For example, using `OS_Write*` or `printf` within `WrchV` will create a recursive loop.

### Generic veneers

For non-claimable entry points, like driver registrations, the CMHG `generic-veneer` should be used.
Many modules (CDFSDriver, SCSI, etc.) require passing entry point addresses to the OS or other drivers via a Driver Information Block.
Other interfaces, like timed events (`OS_CallAfter`, `OS_CallEvery`) have a similar entry point.

**Implementation**: Use the addresses of CMHG-generated generic veneers, not the raw C functions.
```c
/* In Mod_Register */
CDFS_DIB *dib = (CDFS_DIB *)r->r[0];
dib->msf_to_lba_fn = (int)Entry_MSFToLBA_Veneer; // Address of the veneer
```
or
```c
_swix(OS_CallAfter, _INR(0,2), 10, Entry_Tick_Veneer, pw); // Veneer address.
```

This ensures the C environment (relocation, static base) is correctly initialized when the function is called from external assembly or the OS.


## CMHG style guidelines

* Don't remove the comment sections that describe the file. They are useful for humans to know how to add new sections.
* Any definition which may be split across lines if the definition is incomplete. For example, a list of SWIs like:

```
swi-decoding-table: JUnitXML Create/SWI_Create TestSuite/SWI_TestSuite TestCase/SWI_TestCase Close/SWI_Close
```

Can be comma separated, thus:

```
swi-decoding-table: JUnitXML Create/SWI_Create, TestSuite/SWI_TestSuite, TestCase/SWI_TestCase Close/SWI_Close
```

And the comma separated parts can be split if the comma is the last entry on the line:

```
swi-decoding-table: JUnitXML Create/SWI_Create,
                             TestSuite/SWI_TestSuite,
                             TestCase/SWI_TestCase,
                             Close/SWI_Close
```

Which makes for nice aligned text.

* If services are required for the module, use the symbolic names where possible from the include file `riscos/Services.h`.
  This can be included using C preprocessor includes, like this:

```
#include "riscos/Services.h"

service-call-handler: Mod_Service Service_ModeChange
```

## Module Testing Strategies

### Verifying SWIs in BASIC
A simple BASIC script is the most effective way to test a new module. Use the skill `using-bbcbasic` if you need to work with BASIC.

**Example: Testing a complex SWI (CD_DriveStatus)**
```bbcbasic
REM Passing a pointer in R7
DIM control_block% 20
control_block%!0 = device%
control_block%!4 = card%
...
SYS "CD_DriveStatus", 0, 0, 0, 0, 0, 0, 0, control_block% TO status%
PRINT "Status is: "; status%
```
**Key Tip**: Always pass explicit 0s for intermediate registers (R0-R6) to ensure your target register (R7) is correctly populated.

### Verifying Version Blocks
If your SWI returns a pointer to a block of data:
```bbcbasic
SYS "CD_Version" TO v%
PRINT "Version word: "; v%!0
PRINT "Version string: "; FNstring0(v%+4)

DEFFNstring0(p%):LOCAL s$:SYS "OS_IntOn",p% TO s$:=s$
```

## Build and Linker Pitfalls

*   **Missing COMPONENT**: If `COMPONENT` is not defined in the `Makefile`, the build may fail or produce oddly named binaries.
*   **RAM vs ROM**: Ensure you are building the `ram` target for testing.
*   **File Suffixes**: Always ensure your `Makefile` handles dependencies on generated headers:
    `${OZDIR}.module: h.modhead`


## Resources

- [RISC OS PRM - Software Interrupts](https://www.riscos.info/modules/)
- [CMHG Documentation](https://www.riscos.info/modules/cmhg.htm)
- [PRM 1-26 - SWI Chunk Allocation](https://www.riscos.info/modules/)

- Manager modules may need to announce that they are starting up and shutting down. Usually services are issued for these events. The module announcements pattern can be found here [references/module-announcements.md](references/module-announcements.md).
