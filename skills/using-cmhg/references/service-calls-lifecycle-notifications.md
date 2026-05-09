# Lifecycle notification services

## What they are used for

Many service handlers are pure lifecycle observers. They do not provide data to the caller; they update local state because another system component started, finished, reset, or is about to disappear.

Common lifecycle groups observed in `SourcesSVC`:

- OS/module boot: `Service_PostInit`, `Service_ModulePreInit`, `Service_PreReset`, `Service_Reset`.
- Desktop/Wimp: `Service_StartWimp`, `Service_StartedWimp`; see `service-calls-desktop.md` for `Service_WimpCloseDown`.
- System shutdown: `Service_ShutDown`, `Service_ShutDownDismounting`, `Service_ShutDownComplete`.
- Manager modules: `Service_FilterManagerInstalled`, `Service_FilterManagerDying`, `Service_RedrawManagerInstalled`, `Service_ToolboxStarting`.
- Registry modules: `Service_ImageFileConvert_Started`, `Service_ImageFileConvert_Dying`, `Service_ImageFileRender_Started`, `Service_ImageFileRender_Dying`.
- Device managers: `Service_SCSIStarted`, `Service_SCSIDying`, `Service_EasyUSB_Started`, `Service_EasyUSB_Dying`.
- Network managers: `Service_FreewayStarting`, `Service_FreewayTerminating`, `Service_DCIProtocolStatus`, `Service_DCIDriverStatus`, `Service_InternetStatus`.

## CMHG form

Lifecycle services are listed with the normal `service-call-handler` directive:

```cmhg
service-call-handler: Mod_Service Service_FilterManagerInstalled,
                                  Service_FilterManagerDying
```

or:

```cmhg
service-call-handler: Mod_Service Service_SCSIStarted,
                                  Service_SCSIDying
```

Some older modules use numeric services:

```cmhg
service-call-handler: sc_handler &95 &96
```

where the C code names them as `Service_FreewayTerminating` and `Service_FreewayStarting`.

## C usage

Lifecycle handlers usually switch on the service number and do small state changes:

```c
case Service_FilterManagerInstalled:
    register_filter();
    break;

case Service_FilterManagerDying:
    deregister_filter();
    break;
```

Device/provider modules use started/dying pairs to register and deregister:

```c
case Service_SCSIStarted:
    SCSIx_Register(pw);
    break;

case Service_SCSIDying:
    SCSIx_Deregister(pw, 0);
    break;
```

Shutdown services clear local state rather than claiming:

```c
case Service_ShutDownComplete:
    current_task = NULL;
    show_shutdown(0);
    break;
```

Reset services are normally used to reset cached task/driver state. CDFSFiler treats `Service_Reset` like `Service_StartedFiler` for its task handle reset. DOSFS logs `Service_Reset` and redeclares on `Service_FSRedeclare`.

## Related information

Lifecycle notifications are normally not claimed. If a service has both lifecycle and request semantics, only claim when the service documentation says that a module may take ownership of the event. The sources show this distinction clearly: `Service_SCSIStarted` is not claimed, but `Service_EasyUSB_NewDeviceByClass` is claimed when a driver accepts the device.
