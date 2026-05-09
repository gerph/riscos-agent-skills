# Generic veneers reference index

These files describe common generic veneer usage patterns:

- `generic-veneers-ticker-events.md`: `OS_CallEvery`, `OS_CallAfter`, and `OS_RemoveTickerEvent`.
- `generic-veneers-transient-callbacks.md`: `OS_AddCallBack`/`OS_RemoveCallBack` deferred work.
- `generic-veneers-system-variable-handlers.md`: `OS_SetVarVal` type 16 read/write code variables.
- `generic-veneers-filter-callbacks.md`: FilterManager and Internet filter callbacks.
- `generic-veneers-image-file-convert.md`: ImageFileConvert converter and miscellaneous-operation entries.
- `generic-veneers-image-file-render.md`: ImageFileRender render, bbox, info, declare, start, and stop entries.
- `generic-veneers-colour-map-callbacks.md`: colour-map `workspace, function` descriptors.
- `generic-veneers-database-provider-callbacks.md`: DBResultManager provider callbacks.
- `generic-veneers-dynamic-area-handlers.md`: `OS_DynamicArea` handlers.
- `generic-veneers-os-vector-hooks.md`: generic-veneer entries claimed with `OS_Claim`.
- `generic-veneers-osswi-claims.md`: `OS_ClaimOSSWI` handlers.
- `generic-veneers-network-driver-callbacks.md`: PPP, WebFTP, AUN, and network driver callback entries.
- `generic-veneers-scsi-driver-callbacks.md`: SCSI provider operation callbacks.
- `generic-veneers-abort-and-error-handlers.md`: abort traps and `ErrorV` handling.
- `generic-veneers-custom-trampoline-callbacks.md`: hand-built callback trampolines and `carry-capable:`.

All of these use the same CMHG mechanism:

```cmhg
generic-veneers: EntryName/HandlerName
```

CMHG generates `EntryName`, which is the address passed to the OS or another module. The C function `HandlerName` is called by the veneer with:

```c
_kernel_oserror *HandlerName(_kernel_swi_regs *r, void *pw);
```

The handler reads and writes the register block according to the owning API's ABI, not according to CMHG itself.
