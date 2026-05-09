# Generic veneers for dynamic-area handlers

## What they are used for

`OS_DynamicArea` can take a handler entry when creating an area. Modules use generic veneers where the dynamic-area manager needs to call module code for grow/shrink or special mapping decisions.

Typical entries:

- General dynamic-area handler: `da_handler_entry/da_handler`.
- Module-specific dynamic-area handler: `DA_Entry/DA_Handler`.
- Cache area handler: `cache_da_Entry/cache_da_Handler`.

## CMHG form

```cmhg
generic-veneers: da_handler_entry/da_handler
```

## C usage

Pass the entry address and private word to `OS_DynamicArea` when creating the area:

```c
_swix(OS_DynamicArea, _INR(0,8) | _OUT(1),
      0, -1, 0, -1, DA_FLAGS, max_size,
      da_handler_entry, PrivateWord, DA_NAME, &DANumber);
```

The C handler receives the dynamic-area manager's registers in `_kernel_swi_regs *r` and the private word as `pw`. It must implement the ABI required by the dynamic-area reason codes used for the area.

## Notes

- Remove the dynamic area before module finalisation completes.
- Keep any global state used by the handler valid for the entire lifetime of the area.
- Dynamic-area callbacks may occur while memory management is in progress; avoid unnecessary allocation or re-entrant behaviour unless the interface explicitly permits it.
