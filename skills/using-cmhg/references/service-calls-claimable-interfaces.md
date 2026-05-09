# Claimable service-call interfaces

## What they are used for

Some services are not just notifications. They are synchronous extension interfaces: the caller broadcasts a request, and the first suitable module claims by setting `r1` to `Service_Serviced` or zero and returning values in other registers.

Examples found in `SourcesSVC`:

- disc and format recognition: DOSFS `Service_IdentifyDisc`, `Service_IdentifyFormat`, `Service_DisplayFormatHelp`;
- screen mode selection: ScreenModes `Service_ModeExtension`, `Service_EnumerateScreenModes`;
- USB device acceptance: SoftSCSI `Service_EasyUSB_NewDeviceByClass` or `...ByVendor`;
- screen saver blanking: ScrSaver `Service_ScreenBlanking`;
- external bell replacement: SystemBell2 `Service_ExternalBell`;
- help query extensions: LibraryHelp `Service_HelpQuery`;
- APCS backtrace extensions: CFrontDemangler and MiniDump `Service_APCSBacktrace` (see `service-calls-diagnostics.md`);
- generic provider enumeration: network drivers and statistics services.

## CMHG form

The CMHG form is the same as for notifications. The difference is the C-level contract:

```cmhg
service-call-handler: Mod_Service Service_ExternalBell
```

or:

```cmhg
service-call-handler: Mod_Service Service_APCSBacktrace
```

## C usage

Claim only after satisfying the request:

```c
if (handled)
    r->r[1] = Service_Serviced;
```

SystemBell2 handles `Service_ExternalBell` by reading the legacy bell OS_Byte values, converting them to a `Sound_ControlPacked` request, and claiming only if the sound call succeeds:

```c
err = sound_controlpacked(packed1, packed2);
if (!err)
    r->r[1] = Service_Serviced;
```

LibraryHelp uses `Service_HelpQuery` to provide help for aliases, commands, or groups. It reads:

- `r0`: query string;
- `r2`: flags, with low bits selecting alias/command/group;
- `r7`: caller state/claim flag.

If it provides an answer, it sets `r7` to `1`. This service uses `r7` rather than the usual `r1` claim in the observed code.

APCS backtrace services are claimable diagnostic extension points. Their subreason register maps are described in `service-calls-diagnostics.md`.

ScreenModes and DOSFS are larger examples where the service fills blocks or records before claiming. See the screen/display and filing-system references for their register maps.

## Related information

For claimable interfaces, the handler is part of another module's ABI. Do not infer register meanings from CMHG; use the service's PRM or local header definitions. CMHG only arranges dispatch to the C function.
