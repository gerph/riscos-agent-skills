# Generic veneers for system variable handlers

## What they are used for

Some modules install code variables with `OS_SetVarVal` type 16. The variable value is a small code block containing read and write entry addresses. Generic veneers provide those read/write entry addresses and translate the variable manager's register interface into C.

Typical entries:

- Per-variable read/write entries: `var_hostname_write`, `var_hostname_read`, `var_domain_write`, `var_domain_read`.
- Service-specific variable entries: `time_var_write_entry/time_var_write`, `ntp_var_read_entry/ntp_var_read`.
- Generic variable entries: `var_write_entry/var_write`, `var_read_entry/var_read`.
- Namespace-specific entries: `filer_var_write_entry/filer_var_write`, `var_uuid_read_entry/var_uuid_read`.

## CMHG form

Read and write entries are ordinary generic veneers:

```cmhg
generic-veneers: var_resolvers_write, var_resolvers_read,
                 var_hostname_write, var_hostname_read
```

When no handler is named, handlers are derived from the entry names, for example `var_resolvers_write_handler`.

## C usage

A typical implementation builds a code variable block containing branch/load instructions and the generic veneer entry addresses, then installs it with `OS_SetVarVal`:

```c
code[0] = 0xe59ff000;
code[1] = 0xe59ff000;
code[2] = (int)writer;
code[3] = (int)reader;
_swix(OS_SetVarVal, _INR(0,5), var, code, sizeof(code), 0, 16, pw);
```

Read handlers set the output pointer and length in the register block:

```c
regs->r[0] = (int)string;
regs->r[2] = strlen(string);
```

Write handlers usually read:

- `r->r[1]`: pointer to the new value.
- `r->r[2]`: length, or a negative value for deletion.

They update module state, may validate the value, and may schedule follow-up work or service calls.

## Notes

- Delete or replace the code variable during module finalisation. Several modules delete the code variable and recreate it as a literal string if a value should survive.
- If the installed code is generated in memory on older systems, synchronise code areas after writing it.
- The private word passed to `OS_SetVarVal` is what the generic veneer receives as `pw`.
