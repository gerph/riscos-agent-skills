# Resource and message registration services

## What they are used for

Modules that keep resources in ResourceFS must re-register those files when ResourceFS starts or restarts. Many Toolbox object modules and render/converter modules listen for `Service_ResourceFSStarting`; font-related modules also use `Service_FontsChanged` to rebuild font-dependent state.

Relevant PRM context:

- ResourceFS services: <https://www.riscos.com/support/developers/prm/resourcefs.html#84271>
- Font Manager `Service_FontsChanged`: <http://www.riscos.com/support/developers/prm/fontmanager.html#34419>

Typical uses:

- register message files and templates with ResourceFS;
- refresh cached font handles or names after `Service_FontsChanged`;
- register object-module resources before Toolbox/Wimp clients need them.

## CMHG form

Resource registration services are listed with the module's normal service handler:

```cmhg
service-call-handler: Menu_services \
                                  Service_ToolboxStarting,
                                  Service_ToolboxTaskBorn,
                                  Service_ToolboxTaskDied,
                                  Service_ResourceFSStarting,
                                  Service_ToolboxSubMenu
```

FontMap uses both ResourceFS and font change notification:

```cmhg
service-call-handler: Mod_Service Service_ResourceFSStarting,
                                  Service_FontsChanged
```

ReplaySupport is a minimal ResourceFS-only case:

```cmhg
service-call-handler: Replay_services Service_ResourceFSStarting
```

## C usage

The ResourceFS starting protocol passes a registration function in `r2` and a ResourceFS workspace/context value in `r3`. The Toolbox modules cast `r2` to a callback type and call it with the address of their ResourceFS data:

```c
case Service_ResourceFSStarting:
{
    regfunc func = (regfunc)r->r[2];
    func(messages_file(), 0, 0, r->r[3]);
}
break;
```

The PRM states that `Service_ResourceFSStarting` (`&60`) is issued when ResourceFS is reloaded or reinitialised. On entry, `r1 = &60`, `r2` is the code address to call, and `r3` is the ResourceFS workspace pointer. Preserve all registers and do not claim. `ResourceFS_RegisterFiles` cannot be used at this point because ResourceFS is not linked into the module chain yet; instead call the code address in `r2`, passing the resource file data pointer and preserving the `r3` workspace value. This path does not itself issue `Service_ResourceFSStarted`; ResourceFS waits until all modules have seen `Service_ResourceFSStarting`, then broadcasts `Service_ResourceFSStarted`.

Do this only when the module is built with embedded resources; several sources guard the case with `#ifdef RAM`.

`Service_FontsChanged` (`&6E`) is a cache invalidation event issued by Font Manager after `Font$Path` changes or a directory is scanned. Preserve all registers. Module-based applications should call `Font_ListFonts` again to refresh available-font lists. `FontDbox` includes it in CMHG and its C handler reacts by making registered tasks re-evaluate font-dependent state. `FontMap` listens for it alongside `Service_ResourceFSStarting`.

## Related information

Resource registration services are notification services. Do not claim them. The module receiving the call contributes its resources by calling the supplied function and leaves `r1` unchanged.
