# Toolbox and Wimp lifecycle services

## What they are used for

Toolbox object modules use service calls to integrate with the Toolbox core and to maintain per-task state. Desktop utilities and Toolbox classes use Wimp services to start their helper task, learn the Wimp version, clean up on shutdown, and mediate deferred submenu work.

Common services:

- `Service_ToolboxStarting`: register the object module with Toolbox.
- `Service_ToolboxTaskBorn`: create per-Wimp-task state.
- `Service_ToolboxTaskDied`: remove per-task state.
- `Service_ToolboxSubMenu`: process deferred submenu/menu-warning state.
- `Service_StartWimp`: prepare for Wimp startup or read Wimp capabilities.
- `Service_StartedWimp`: start or attach to a desktop helper task.
- `Service_ShutDownComplete`: close windows, reset current task state, or stop background activity.

## CMHG form

A full Toolbox object example is the Window module:

```cmhg
service-call-handler: Window_services \
                                  Service_ModeChange,
                                  Service_ToolboxStarting,
                                  Service_ToolboxTaskBorn,
                                  Service_ToolboxTaskDied,
                                  Service_StartWimp,
                                  Service_ShutDownComplete,
                                  Service_RedrawManagerInstalled,
                                  Service_ResourceFSStarting,
                                  Service_ToolboxSubMenu
```

Smaller Toolbox modules use a common four-service form:

```cmhg
service-call-handler: SaveAs_services \
                                  Service_ToolboxStarting,
                                  Service_ToolboxTaskBorn,
                                  Service_ToolboxTaskDied,
                                  Service_ResourceFSStarting
```

Desktop helper modules such as DiscSpaceCheck and WindowScroll use:

```cmhg
service-call-handler: Mod_Service Service_StartWimp,
                                  Service_StartedWimp
```

## C usage

Toolbox modules register themselves during `Service_ToolboxStarting`:

```c
case Service_ToolboxStarting:
    regs.r[0] = 0;
    regs.r[1] = Menu_ObjectClass;
    regs.r[2] = Menu_ClassSWI;
    regs.r[3] = 0;
    _kernel_swi(Toolbox_RegisterObjectModule, &regs, &regs);
    break;
```

Per-task state is keyed by the Wimp task handle in `r0`:

```c
case Service_ToolboxTaskBorn:
    task_add(r->r[0]);
    break;

case Service_ToolboxTaskDied:
    task_remove(r->r[0]);
    break;
```

`Service_ToolboxSubMenu` uses `r0` as the task handle and `r3` as a sub-reason. Window and Menu use it to find the task and close or adjust submenu state after Toolbox has deferred a MenuWarning.

Desktop helper modules generally use `Service_StartWimp` to prepare and `Service_StartedWimp` to launch or bind to their task. Window uses `Service_StartWimp` to read and cache the Wimp version.

The Wimp PRM documents the resident module task protocol:

- `Service_StartWimp` (`&49`) is issued by Desktop to start resident module tasks. A module that is not already active sets its task handle state to `-1`, returns `r0` pointing at a `*` command that starts the task, and claims with `r1 = 0`. Desktop then calls `Wimp_StartTask` with that command and repeats the service until nobody claims it.
- `Service_StartedWimp` (`&4A`) is issued when the last resident module has been started. Modules should use it, and `Service_Reset`, to clear a stuck `-1` task-handle state left by a failed startup.
- When a module task exits or finalises, it should call `Wimp_CloseDown` with its task handle and clear the task handle to zero.

`Service_WimpCloseDown` is covered with the broader desktop lifecycle services in `service-calls-desktop.md`.

## Related information

Toolbox and Wimp lifecycle services are normally notifications and should not be claimed. They are about maintaining module state in response to task and desktop lifecycle changes.
