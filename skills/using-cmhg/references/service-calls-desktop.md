# Desktop and Wimp services

## What they are used for

Desktop-facing modules use services to contribute banners, track Wimp task shutdown, handle system shutdown, and add TaskManager acknowledgement text.

Relevant PRM context:

- Wimp services: <http://www.riscos.com/support/developers/prm/wimp.html>
- RISC OS 3.5 desktop and Wimp error-report services: <https://www.riscos.com/support/developers/prm/desktop.html>

Common services:

- `Service_DesktopWelcome`: desktop welcome/banner notification.
- `Service_OSInitBanner`: OS initialisation banner hook.
- `Service_WimpCloseDown`: a Wimp task or the Wimp itself is closing down.
- `Service_ShutDown`, `Service_ShutDownDismounting`, `Service_ShutDownComplete`: system shutdown stages.
- `Service_TaskManagerAcknowledgements`: TaskManager asks modules for acknowledgement/copyright text.

## CMHG form

OwnerBanner listens for desktop and OS banner services:

```cmhg
service-call-handler: Mod_Service \
            Service_DesktopWelcome, \
            Service_OSInitBanner
```

Several modules combine Wimp close-down with acknowledgements:

```cmhg
service-call-handler: Mod_Service Service_WimpCloseDown,
                                  Service_TaskManagerAcknowledgements
```

SysLog listens for acknowledgement and shutdown stages:

```cmhg
service-call-handler: Mod_Service Service_TaskManagerAcknowledgements,
                                  Service_ShutDownDismounting,
                                  Service_ShutDown
```

## C usage

OwnerBanner claims `Service_OSInitBanner` after writing its banner:

```c
case Service_OSInitBanner:
    banner_osinit();
    r->r[1] = Service_Serviced;
    break;
```

`Service_DesktopWelcome` is listed by OwnerBanner as the desktop-side companion to the OS initialisation banner. Treat it as a desktop notification unless the service's documentation says to claim.

The PRM describes `Service_DesktopWelcome` (`&7C`) as being issued just before the RISC OS 3 startup screen is drawn. Set `r1 = 0` to claim it when replacing or suppressing the startup screen. It is not available under RISC OS 2.

`Service_WimpCloseDown` has service-specific register meanings. In the observed sources:

- ZLib/Zipper check `r0 == 0` for close-down and then terminate their dynamic-area domain.
- Toolbox uses `r2` as a Wimp task handle, finds the task descriptor, broadcasts `Service_ToolboxTaskDied`, then exits the task.
- Picker checks `r0 == 0` and uses the low bits of `r2` as the Wimp task handle for dialogue cleanup.

The PRM defines `Service_WimpCloseDown` (`&53`) as notification that the Wimp is about to close a task. `r0 = 0` when `Wimp_CloseDown` was called; `r0 > 0` when `Wimp_Initialise` was called in the task's domain and the Wimp is closing the original task before starting another. `r2` is the handle of the task being closed. If a task receives this because the Wimp is closing it on its behalf, it should perform the work it would have done around its own `Wimp_CloseDown`, preserve registers, and must not call `Wimp_CloseDown` again.

`Service_ShutDown` (`&7E`) is issued by TaskManager when shutdown is requested. It may be claimed with `r1 = 0` to stop shutdown, for example to warn about unsaved state. `Service_ShutDownComplete` (`&80`) is issued when shutdown has completed and should not be claimed. Shutdown services are used to flush logs, clear exported state, stop background work, or mark that shutdown is in progress.

## Related information

Desktop services overlap with Toolbox task services, but they operate at a broader Wimp or system level. Use `Service_ToolboxTaskBorn` and `Service_ToolboxTaskDied` for Toolbox task bookkeeping; use `Service_WimpCloseDown` and shutdown services for Wimp/system lifecycle.

For Wimp error-report services associated with the desktop, see `service-calls-wimp-error-reporting.md`.

For the `Service_TaskManagerAcknowledgements`, specific information is in the `writing-cmodules` skill.