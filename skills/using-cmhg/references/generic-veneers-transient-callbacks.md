# Generic veneers for transient callbacks

## What they are used for

Generic veneers are commonly used with `OS_AddCallBack` for deferred work. A callback runs when RISC OS returns to a safer callback context, so modules use it to avoid doing substantial work in initialisation, service calls, ticker handlers, event handlers, or interrupt-like contexts.

Typical entries:

- Deferred flush or housekeeping entry: `FlushCallBack_Entry/FlushCallBack_Handler`.
- Generic module callback: `callback_entry/callback`.
- Startup announcement entry: `Mod_Started_Entry/Mod_Started` or `StartupCallback_Entry/StartupCallback_Handler`.
- Service announcement entry: `CallBack_Entry/CallBack`.

## CMHG form

```cmhg
generic-veneers: callback_entry/callback,
                 StartupCallback_Entry/StartupCallback_Handler
```

The generated header declares the entry symbol. The entry symbol is passed to `OS_AddCallBack`; the C handler is only called by the veneer.

## C usage

Register and remove callbacks with the entry and private word:

```c
_swix(OS_AddCallBack, _INR(0,1), callback_entry, pw);
_swix(OS_RemoveCallBack, _INR(0,1), callback_entry, pw);
```

Some code uses callbacks as startup announcements. The initialisation routine schedules a callback; the callback handler then issues the module's "started" service call once the module is fully entered and callback context is available.

The handler shape is:

```c
_kernel_oserror *callback(_kernel_swi_regs *r, void *pw);
```

Handlers usually return `NULL`. If the handler changes return registers, write to `r->r[n]`, but most callback handlers ignore `r`.

## Notes

- Remove pending callbacks in finalisation. `OS_RemoveCallBack` is harmless when the callback is not pending.
- Use a boolean guard if repeated triggers could schedule the same callback many times.
- A ticker handler may schedule a callback and return immediately; this is the preferred pattern for work that is not safe in ticker context.
