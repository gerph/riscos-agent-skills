# Filing-system and format services

## What they are used for

Filing-system modules use service calls to declare themselves, handle filer lifecycle events, protect application space, react to disc dismounts, and participate in MultiFS disc-format discovery.

Relevant PRM context:

- Filer services: <http://www.riscos.com/support/developers/prm/filers.html>
- FileCore `Service_IdentifyDisc`: <http://www.riscos.com/support/developers/prm/filecore.html#56320>
- ADFS format services: <http://www.riscos.com/support/developers/prm/adfs.html#34389>
- Wimp `Service_WimpSaveDesktop`: <http://www.riscos.com/support/developers/prm/wimp.html#98784>

Common services:

- `Service_FSRedeclare`: declare or redeclare a filing system.
- `Service_StartUpFS`: select the filing system at startup.
- `Service_StartFiler`, `Service_StartedFiler`, `Service_FilerDying`: integrate a desktop filer helper.
- `Service_DiscDismounted`: close windows or notify clients when a disc is dismounted.
- `Service_Memory`: prevent remapping of a module's application space or claim memory-related requests that target the module.
- `Service_IdentifyDisc`, `Service_EnumerateFormats`, `Service_IdentifyFormat`, `Service_DisplayFormatHelp`: MultiFS format negotiation.
- `Service_WimpSaveDesktop`: write commands needed to restore module configuration.

## CMHG form

CDFS declares only `Service_FSRedeclare`, using the numeric value `0x40`:

```cmhg
service-call-handler: cdfs_service_handler 0x40
```

CDFSFiler receives a compact numeric list:

```cmhg
service-call-handler: cdfiler_service_handler 0x4b 0x27 0x4c 0x4f 0x11 0x7d
```

DOSFS lists the MultiFS and filing-system services by name:

```cmhg
service-call-handler: fs_service Service_Memory,
                                 Service_StartUpFS,
                                 Service_Reset,
                                 Service_FSRedeclare,
                                 Service_LookupFileType,
                                 Service_WimpSaveDesktop,
                                 Service_CloseFile,
                                 Service_IdentifyDisc,
                                 Service_EnumerateFormats,
                                 Service_IdentifyFormat,
                                 Service_DisplayFormatHelp
```

## C usage

`Service_FSRedeclare` is a notification to call the module's declaration routine:

```c
case Service_FSRedeclare:
    declare_filing_system(pw);
    break;
```

Filer modules track the desktop filer task and close their own state when needed. The PRM defines `Service_StartFiler` (`&4B`) as analogous to `Service_StartWimp`, but issued by the Filer so filing-system-specific desktop filers are only started when the Filer exists:

```c
case Service_StartFiler:
    global_filer_task_handle = r->r[0];
    r->r[0] = (int)CDFiler_StartTaskCommand;
    r->r[1] = 0;
    break;

case Service_FilerDying:
    global_task_handle = 0;
    task_quit();
    break;
```

On entry, `r0` is the Filer task handle and `r1` is `&4B`. To start a filer task, return `r0` pointing at the `*` command and claim with `r1 = 0`. Set the module's task handle to `-1` while startup is pending, so a failed startup does not cause an infinite retry loop.

`Service_StartedFiler` (`&4C`) and `Service_Reset` (`&27`) should clear a stuck `-1` task handle back to zero. `Service_FilerDying` (`&4F`) tells filing-system-specific filers that the Filer module is closing down; if active, they should clear their task handle and call `Wimp_CloseDown`.

`Service_Memory` is claimable when it targets this module's application space:

```c
case Service_Memory:
    if ((void *)r->r[2] == Image__RO_Base)
        r->r[1] = 0;
    break;
```

DOSFS implements the MultiFS format interface:

- `Service_IdentifyDisc` (`&69`): inputs include `r2` format-name buffer, `r3` buffer length, `r5` disc record, `r6` sector cache handle, `r8` FileCore private word. On success set `r1 = 0`, update the disc record at `r5`, set `r2` to the filetype for the image, update `r6`, and preserve `r8`. If not recognised, preserve `r1` and `r5`, but still return the new `r6` if sector cache operations changed it. Fill the `r2` buffer with a short format description without exceeding the length in `r3`.
- `Service_EnumerateFormats` (`&6A`): `r2` is the head of a linked list of RMA blocks describing menu/help entries. Append RMA-allocated `format_info` blocks, preserve `r1`, and do not claim on success. The issuer must free the list after use.
- `Service_IdentifyFormat` (`&6B`): input `r0` is a null-terminated format identifier string. On match, set `r1 = 0`, `r2`/`r3` to the format SWI and parameter, and `r4`/`r5` to the layout SWI and parameter. Preserve all registers if the format is not recognised.
- `Service_DisplayFormatHelp` (`&6C`): writes human-readable help using OS output SWIs, one format per line as `format - description`. On success preserve `r0` and `r1` and pass on. On error set `r0` to the error block and `r1 = 0`.

`Service_DiscDismounted` (`&7D`) uses `r2` as a pointer to a null-terminated `filing_system::disc` string, such as `ADFS::MyFloppy` or `ADFS::0` for an unnamed disc. Preserve all registers and do not claim.

`Service_WimpSaveDesktop` (`&5C`) uses `r0` as a flag word and `r2` as the file handle to write restart `*` commands to. On success preserve registers and pass on. On error, set `r0` to an error block and claim with `r1 = 0`.

## Related information

Most filing-system services are notifications; MultiFS identification services are synchronous extension calls and should be claimed only when the module has provided a valid answer.
