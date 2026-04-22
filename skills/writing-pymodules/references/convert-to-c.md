# Converting PyModules to/from C

When creating a PyModule that mirrors a C module, or a C module that mirrors a Pyromaniac module, this document should help.

## Match Error Numbers

Ensure `error_base` matches the C module's `error-base` in `cmhg/modhead`:

```cmhg
; C module cmhg/modhead
error-base: &840000
```

```python
# Python module
error_base = 0x840000
```

## 2. Match Error Messages

Error messages should be identical:

```cmhg
error-identifiers: \
    Err_CreateFailed("Failed to create JUnitXML handle") \
```

```python
errors = [
    ('CreateFailed', "Failed to create JUnitXML handle"),
]
```

## 3. Match SWI Interface

SWI names, parameters, and return values should be identical:

```python
swi_prefix = "JUnitXML"
swi_names = ['Create', 'TestSuite', 'TestCase', 'Close']
```

## Notes for C modules

###  Norcroft C & C89 Standards

The Norcroft compiler is strictly C89. This is the most common cause of "Serious error" build failures.

*   **Variable Declarations**: All variables **must** be declared at the top of their scope block, before any executable statements. If you need a temporary variable mid-function, create a new `{ ... }` block.
*   **Typedef Naming**: Avoid naming a variable the same as a typedef (e.g., `CDDriver *CDDriver`). Use a naming convention like `typedef struct { ... } cd_driver_t;` and `cd_driver_t *driver;` to prevent "typedef name used in expression context" errors.
*   **Pointer Arithmetic**: When reading control blocks or structures from memory addresses passed in registers, use `(int *)` or `(uint32_t *)` pointers for word-aligned access.

### Register Handling & Assembly Veneers

PyModules often handle complex register sets (R0-R12) which standard C functions and `_kernel_swi` cannot fully control.

### The "R11/R12" Problem

Drivers (like CDFSDriver, SCSI, etc.) often use:

*   **R11**: Reason code or Interface ID.
*   **R12**: Private word or Workspace pointer.

**Lesson**: You cannot call these entry points directly from C because the compiler uses R12 for its own purposes (IP) and doesn't provide a way to set R11.
**Solution**: Use a small assembly veneer (`s/veneer`) to:
1. Preserve registers (`STMFD sp!, {r4-r12, lr}`).
2. Load R0-R9 from a `_kernel_swi_regs` block.
3. Manually set R11 and R12 from C arguments.
4. Call the address (`MOV lr, pc` then `MOV pc, rX`).
5. Handle the V-flag for errors.

### CMHG Generic Veneers
When your module provides an entry point to the OS or other drivers (e.g., conversion functions in a Driver Info Block), you **must** use a CMHG `generic-veneer`. This ensures that when the external code calls your C function, the C relocation registers (like the static base) are correctly set up.

###  Analyzing the Python Source (Pyromaniac)

To understand how a PyModule functions, look for these patterns in the Python code:

*   **SWI Dispatch**: Look for a dictionary mapping numbers to methods (e.g., `1: self.swi_cd_readdata`).
*   **Interface IDs**: Native drivers often use a different set of IDs than SWI offsets. In Pyromaniac, these are often held in a `CDConstants` or similar class. **Crucial**: Verify if the SWI number `+1` maps to Interface ID `0` or `1`.
*   **Control Blocks**: Look for `populate_control` methods. They reveal the expected memory layout (e.g., a 20-byte block of 5 words).

## Testing in Pyromaniac

Pyromaniac's build environment handles file suffixes specially.

*   **Comma Suffixes**: Files on the host should use `,xxx` (e.g., `test,fd1`, `driver,ffc`).
*   **File Loading**: In BASIC scripts used for testing, refer to files by their RISC OS name (without the comma). Example: `SYS "OS_File", 17, "driver" TO ,,,,size%`.
*   **Build Runner**: When using `riscos-build-run`, you must explicitly list every binary and script needed in the virtual environment. If the module needs a test driver binary, include it in the arguments: `riscos-build-run module,ffa driver,ffc test,fd1 ...`.

### BBC BASIC Standards

Agents must activate the `using-bbcbasic` skill. Key reminders:
*   **Renumbering**: BASIC renumbers by 10. Your error handler should use `STR$(ERL/10)`.
*   **Standard Header**: Always include the `REM >filename` and `ON ERROR` boilerplate.
*   **Strings**: C modules return 0-terminated strings. Use `SYS "OS_IntOn",ptr% TO s$` in a helper function to read them into BASIC strings.
*   **R7/Control Blocks**: When calling SWIs that take a pointer in R7, ensure you pass enough dummy arguments to the `SYS` call to reach the 8th register (R0-R7).
    *   Correct: `SYS "XSWI", r0, r1, r2, r3, r4, r5, r6, r7 TO ...`
