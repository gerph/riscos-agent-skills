# Generic veneers for abort and error handlers

## What they are used for

Some error-related extension APIs take plain entry addresses. A memory-protection module can use generic veneers both for abort traps and for `ErrorV`, allowing it to turn protected memory accesses into clearer user-facing errors.

Typical entries:

- Abort trap entry: `Abort_Entry/Abort_Handler`.
- Error vector entry: `Error_Entry/Error_Handler`.
- Minimal reserved-memory helper entry: `Veneer_Entry/Veneer_Handler`.

## CMHG form

```cmhg
generic-veneers: Abort_Entry/Abort_Handler,
                 Error_Entry/Error_Handler
```

## C usage

A memory-protection module registers abort traps with a helper and the generic veneer entry:

```c
abort_trap_add(region[r].low, region[r].high, (void *)Abort_Entry, pw);
```

It also claims `ErrorV`:

```c
_swix(OS_Claim, _INR(0,2), ErrorV, Error_Entry, pw);
```

The abort handler reads fault information from registers:

- `r0`: flags.
- `r1`: block.
- `r2`: start address.
- `r3`: size.
- `r4`: PC.

For load/store faults in registered regions it returns a custom error pointer. The `ErrorV` handler examines `r0` as an error pointer and may replace `r->r[0]` with a better error after checking last-abort details with `OS_ReadSysInfo` and `OS_ChangeEnvironment`.

## Notes

- Remove abort traps and release `ErrorV` in finalisation.
- These handlers run during error/exception processing, so keep them conservative.
- Only replace an error when the fault details clearly match the exception being reported.
