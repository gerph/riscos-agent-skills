---
name: using-cmhg
description: Describes the CMHG file format and CMunge usage. Use when CMHG files are required for RISC OS modules.
license: MIT
---

# CMunge Skill Summary

## Purpose
CMunge is an enhanced, free alternative to the Acorn/Castle C Module Header Generator (CMHG). It generates ARM assembly "veneers" that allow RISC OS relocatable modules to be written in C or C++. It supports 26-bit, 32-bit, and 64-bit ARM architectures.

## Command Line Usage
`CMunge [options] <infile>`

Key options:
- `-o <file>`: Output object (AOF) file.
- `-s <file>`: Output assembly file.
- `-d <file>`: Output C header file.
- `-26bit`: Target legacy 26-bit ARM (default).
- `-32bit`: Target 32-bit compatible ARM.
- `-64bit`: Target 64-bit (AArch64) ARM for GCC.
- `-p` / `-px`: Pre-process input file (standard / extended).
- `-throwback`: Enable error reporting to editors.
- `-zoslib` / `-zoslibpath`: Use OSLib header styles.

## CMHG/CMunge Directives Summary
- `title-string`: Internal module name.
- `help-string`: Descriptive name and version.
- `initialisation-code`: C function called on load.
- `finalisation-code`: C function called on unload.
- `module-is-initialised-early`: (CMunge) Requests early initialization for ROM.
- `service-call-handler`: C function for service calls.
- `swi-chunk-base-number`: Base SWI number.
- `swi-handler-code`: Central SWI handler C function.
- `swi-decoding-table`: Lists SWI names and optional specific handlers.
- `command-keyword-table`: Defines `*Commands` and their handlers — see [references/command-tables.md](references/command-tables.md).
- `generic-veneers`: General purpose C wrappers.
- `vector-handlers`: Wrappers for claiming RISC OS vectors.
- `event-handler`: Wrappers for RISC OS events.
- `error-base` (CMunge): Base error number for the module.
- `error-identifiers` (CMunge): Automatically generates error definitions.
- `vector-traps` (CMunge): Advanced vector chaining handlers — see [references/vector-traps.md](references/vector-traps.md).
- `library-initialisation-code` / `library-enter-code`: Override C library entry symbols.


## Generic veneers reference index

These files describe common generic veneer usage patterns:

- [Timers: `OS_CallEvery`, `OS_CallAfter`, and `OS_RemoveTickerEvent`.](references/generic-veneers-ticker-events.md)
- [`OS_AddCallBack`/`OS_RemoveCallBack` deferred work.](references/generic-veneers-transient-callbacks.md)
- [`OS_SetVarVal` type 16 read/write code variables.](references/generic-veneers-system-variable-handlers.md)
- [FilterManager and Internet filter callbacks.](references/generic-veneers-filter-callbacks.md)
- [ImageFileConvert converter and miscellaneous-operation entries.](references/generic-veneers-image-file-convert.md)
- [ImageFileRender render, bbox, info, declare, start, and stop entries.](references/generic-veneers-image-file-render.md)
- [colour-map `workspace, function` descriptors.](references/generic-veneers-colour-map-callbacks.md)
- [DBResultManager provider callbacks.](references/generic-veneers-database-provider-callbacks.md)
- [`OS_DynamicArea` handlers.](references/generic-veneers-dynamic-area-handlers.md)
- [Vectors claimed with `OS_Claim`.](references/generic-veneers-os-vector-hooks.md)
- [`OS_ClaimOSSWI` handlers.](references/generic-veneers-osswi-claims.md)
- [PPP, WebFTP, AUN, and network driver callback entries.](references/generic-veneers-network-driver-callbacks.md)
- [SCSI provider operation callbacks.](references/generic-veneers-scsi-driver-callbacks.md)
- [abort traps and `ErrorV` handling.](references/generic-veneers-abort-and-error-handlers.md)
- [hand-built callback trampolines and `carry-capable:`.](references/generic-veneers-custom-trampoline-callbacks.md)

All of these use the same CMHG mechanism:

```cmhg
generic-veneers: EntryName/HandlerName
```

CMHG generates `EntryName`, which is the address passed to the OS or another module. The C function `HandlerName` is called by the veneer with:

```c
_kernel_oserror *HandlerName(_kernel_swi_regs *r, void *pw);
```

The handler reads and writes the register block according to the owning API's ABI, not according to CMHG itself.

## Service call reference index

General information on CMHG syntax, C handler ABI, claiming, and filtering is in the [Service Calls overview](references/service-calls-overview.md).

These files describe common CMHG `service-call-handler` usage patterns:

- [startup, shutdown, reset, and manager started/dying notifications](references/service-calls-lifecycle-notifications.md)
- [ResourceFS related registration services](references/service-calls-resource-registration.md)
- [Toolbox object/task lifecycle, Wimp start/shutdown, submenu mediation](references/service-calls-toolbox-and-wimp.md)
- [filing-system redeclaration, filer lifecycle, disc dismount, and MultiFS format negotiation](references/service-calls-filing-systems-and-formats.md)
- [mode changes, display changes/status, screen mode enumeration, and blanking](references/service-calls-screen-and-display.md)
- [SCSI, USB, buffers, sound, and other device/provider registrations](references/service-calls-device-driver-registration.md)
- [DCI driver/protocol, Internet state, PPP, Freeway, and statistics services](references/service-calls-networking-status.md)
- [ImageFileConvert and ImageFileRender registry lifecycle services](references/service-calls-image-file-registries.md)
- [services used as synchronous extension interfaces by claiming and returning register values](references/service-calls-claimable-interfaces.md)
- [`Service_UKCompression` and `Service_ModulePreInit` patching hooks](references/service-calls-patching.md)
- [desktop banners, Wimp shutdown, TaskManager acknowledgements, and shutdown services](references/service-calls-desktop.md)
- [`Service_APCSBacktrace` diagnostic extension and minidump hooks](references/service-calls-diagnostics.md)
- [`Service_ErrorStarting` and related Wimp error-report monitoring hooks](references/service-calls-wimp-error-reporting.md)

Service information may often also be found through the `riscos-prm --url Service_...` command.

## References

For more information on the CMHG file format, see [references/cmhg-syntax.md](references/cmhg-syntax.md).

For detailed information on `vector-traps` including a worked example, see [references/vector-traps.md](references/vector-traps.md).

For examples and detailed syntax of the *Command tables, see [references/command-tables.md](references/command-tables.md).
