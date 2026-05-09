# Screen and display services

## What they are used for

Display-related modules use service calls to keep cached display state in sync, provide screen modes to the OS, adapt to palette/font changes, and claim screen blanking.

Relevant PRM context:

- Mode and screen mode services: <http://www.riscos.com/support/developers/prm/video.html>
- `Service_ModeChange`: <http://www.riscos.com/support/developers/prm/vdu.html#89772>
- Screen blanking services: <https://www.riscos.com/support/developers/prm/screenblanker.html>

Common services:

- `Service_ModeChange`: a mode or palette-relevant mode state changed.
- `Service_DisplayChanged`: display parameters changed; often includes pre/post state in `r0`.
- `Service_DisplayStatus`: a display provider or status has registered/deregistered.
- `Service_EnumerateScreenModes`: append mode descriptions to the caller's enumeration buffer.
- `Service_ModeExtension`: translate a mode selector into a VIDC mode list.
- `Service_ScreenBlanking`, `Service_ScreenRestored`: screen saver/blanking negotiation.
- `Service_WimpPalette`, `Service_TerritoryStarted`: invalidate cached colours or translated text.

## CMHG form

ScreenModes provides mode enumeration and extension:

```cmhg
service-call-handler: ScreenModes_servicecall Service_EnumerateScreenModes,
                                              Service_ModeExtension,
                                              Service_DisplayChanged
```

LegacyScreen handles display/mode-change notifications:

```cmhg
service-call-handler: Mod_Service Service_ModeChange Service_DisplayChanged
```

ScrSaver handles blanking and restoration:

```cmhg
service-call-handler: module_service Service_ScreenBlanking,
                                     Service_ScreenRestored,
                                     Service_ShutDownComplete,
                                     Service_StartWimp
```

## C usage

`Service_DisplayChanged` may be handled even when the module is not the current preferred provider. ScreenModes uses `r0 == 0` as pre-mode-selection notification, rereads display parameters, then issues its own mode-file-changed notification if needed.

`Service_ModeChange` (`&46`) is issued after a mode change. The PRM gives `r2` as the mode number and `r3` as the monitor type on newer systems; older RISC OS versions did not pass those values. Preserve all registers and do not claim.

`Service_ModeExtension` returns a VIDC list:

```c
regs->r[1] = 0;       /* Service_Serviced */
regs->r[3] = (int)vp; /* VIDC list */
regs->r[4] = 0;       /* no workspace list */
```

For RISC OS 3.5 and later, `Service_ModeExtension` (`&50`) receives:

- `r2`: mode specifier requested;
- `r3`: monitor type, or `-1` for don't care;
- `r4`: available memory bandwidth in bytes/second;
- `r5`: total video RAM in bytes.

Claim only if the module recognises the mode/monitor and can satisfy the bandwidth and memory limits. On claim set `r1 = 0`, preserve `r2`, return `r3` pointing at a type 3 VIDC list, and return `r4` pointing at a workspace list for mode-number requests or zero for mode-selector requests. For mode selectors, check the format specifier in bits 0-7 of the flags word; unrecognised formats must be passed on.

`Service_EnumerateScreenModes` uses:

- `r2`: skip/count position, decremented as modes are considered;
- `r4`: data-rate limit, transformed into the module's internal units;
- `r5`: data-size limit;
- `r6`: output buffer pointer, or zero for size/count probing;
- `r7`: remaining output buffer size.

For each matching mode, ScreenModes writes a `ModeInfoBlock`, advances `r6`, and subtracts the entry size from `r7`. If the buffer is too small, it claims by setting `r1` serviced and returns.

The PRM notes that applications should not issue `Service_EnumerateScreenModes` directly; they should use `OS_ScreenMode 2`, which fills in the current monitor type, memory bandwidth, and video RAM before issuing the service. Modules still implement the service handler.

Screen saver blanking is a claimable service:

```c
case Service_ScreenBlanking:
    if (safe_to_claim_blanking())
    {
        blank_screen();
        r->r[1] = 0;
    }
    break;

case Service_ScreenRestored:
    restore_time = read_time();
    poll_word = 1;
    break;
```

The PRM documents `Service_ScreenRestored` (`&7B`) as a notification issued after the screen has been restored. `r0` is normally zero, or flags from `ScreenBlanker_Control 2` for a flash cycle. Preserve all registers and do not claim. The same PRM documents `Service_ScreenBlanked` (`&7A`), which is distinct from the `Service_ScreenBlanking` claim point used by ScrSaver in these sources.

## Related information

Mode enumeration and mode extension are provider interfaces, not simple notifications. Claim only after writing a complete answer. Plain mode/display change services are cache invalidation notifications and are normally left unclaimed.
