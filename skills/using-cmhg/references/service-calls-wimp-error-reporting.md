# Wimp error reporting services

## What they are used for

Wimp error reporting services allow modules to monitor or extend `Wimp_ReportError` handling. The examples in `SourcesSVC` use them for:

- logging the task, title, flags, and error message when an error report starts;
- detecting when the report has finished;
- forcing a display switch immediately when an error is shown.

The named service is `Service_ErrorStarting`. Older or private Wimp error-report phases may appear as numeric services; RecErrors uses `&400C0` and `&400C2`.

PRM reference: <https://www.riscos.com/support/developers/prm/desktop.html>, section "Service Calls" in the desktop chapter. The PRM describes these as RISC OS 3.5 and later services around `Wimp_ReportError`.

## CMHG form

VideoGuard uses the named service:

```cmhg
service-call-handler: Mod_Service Service_DisplayChanged,
                                  Service_DisplayStatus,
                                  Service_ErrorStarting
```

RecErrors uses numeric service values:

```cmhg
service-call-handler: Mod_Service &400C0 &400C2,
                                  Service_TaskManagerAcknowledgements
```

The RecErrors comments identify `&400C0` and `&400C2` as Wimp_ReportError-related phases. The PRM names them:

- `&400C0`: `Service_ErrorStarting`, issued immediately after `Wimp_ReportError` is called.
- `&400C1`: `Service_ErrorButtonPressed`, issued when a button in the report is pressed.
- `&400C2`: `Service_ErrorEnding`, issued immediately before the report closes.

## C usage

RecErrors treats `&400C0` as the start of Wimp error reporting. The PRM says the register contract is:

- `r1`: `&400C0`;
- `r2` to `r7`: the values of `r0` to `r5` that are intended for `Wimp_ReportError`;
- on exit, preserve `r1` to pass on the call;
- on exit, `r2` to `r7` are the values that will actually be passed to `Wimp_ReportError`.

This lets a service handler alter the report parameters before the Wimp displays the report. If a handler changes memory-backed fields, it must copy the memory and point the register at the copy rather than modifying the caller's original memory. If it adds buttons, it should append them to the button list rather than inserting them, so button numbering remains stable for other clients.

The observed RecErrors inputs map onto this PRM contract as:

- `r2`: pointer to `_kernel_oserror`;
- `r3`: Wimp error flags;
- `r4`: pointer to title string, or a non-positive special value.

It guards against recursion with an `inerror` flag, ignores click-only reports when the flags contain `ERROR_CLICKNOW`, gets the current task name, optionally writes `Error$` and `Error$Task` system variables, then logs the title, task, and error message.

RecErrors treats `&400C2` as the matching end phase and clears `inerror`. The PRM says `Service_ErrorEnding` has:

- `r1`: `&400C2`;
- `r2`: button number being returned to the application;
- on exit, claim with `r1 = 0` only if changing the button number returned in `r2`; otherwise pass it on.

`Service_ErrorButtonPressed` (`&400C1`) is not used by the observed RecErrors handler, but the PRM defines it for modules that add or interpret extra buttons:

- `r0`: zero on entry;
- `r1`: `&400C1`;
- `r2`: button number, where 1 is OK/Continue, 2 is Cancel, and 3 onwards are additional buttons;
- `r3`: pointer to the button list as displayed;
- on exit, return `r0 = 0` to return to the application, or `r0 = 1`, `r1 = 0`, and `r2` pointing at a new report block to redisplay an error report.

VideoGuard listens for the named `Service_ErrorStarting` and uses it as an urgent notification that a Wimp error is visible. Its handler immediately checks whether it must switch display state:

```c
case Service_ErrorStarting:
{
    dswitch_t ds = check_switch(0);
    ...
}
break;
```

## Related information

Wimp error reporting services run while the desktop is already dealing with an error. Keep handlers defensive and recursion-safe. `Service_ErrorStarting` must be passed on. `Service_ErrorButtonPressed` must be claimed if redisplaying the report. `Service_ErrorEnding` should be claimed only when changing the button number returned to the application.
