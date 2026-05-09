# Generic veneers for ticker events

## What they are used for

Generic veneers are used as entry points for `OS_CallEvery` and `OS_CallAfter` ticker events. The OS calls the veneer later in IRQ/ticker context, with the private word supplied when the event was registered. This is used for polling, retry timers, protocol expiry checks, and delayed scheduling.

Typical entries:

- Repeating poll entry: `FlushCallEvery_Entry/FlushCallEvery_Handler`.
- One-shot delayed entry: `Mod_CallAfter_entry/Mod_CallAfter`.
- Protocol timeout entry: `timeout_entry/timeout`.
- Short-form entry with default handler naming: `callevery` uses `callevery_handler`.

## CMHG form

Use `generic-veneers:` because the OS ticker APIs expect a plain code address and do not use the CMHG `event-handler:` or `vector-handlers:` conventions.

```cmhg
generic-veneers: FlushCallEvery_Entry/FlushCallEvery_Handler,
                 Mod_CallAfter_entry/Mod_CallAfter
```

If no handler is named, CMHG derives it by appending `_handler` to the entry name. Naming both entry and handler explicitly is clearer for callbacks registered with OS SWIs.

## C usage

Register the entry address, not the C handler:

```c
_swix(OS_CallEvery, _INR(0,2), period, FlushCallEvery_Entry, pw);
_swix(OS_CallAfter, _INR(0,2), delay, Mod_CallAfter_entry, pw);
```

Remove pending or repeating ticker events with the same entry and private word:

```c
_swix(OS_RemoveTickerEvent, _INR(0,1), FlushCallEvery_Entry, pw);
_swix(OS_RemoveTickerEvent, _INR(0,1), Mod_CallAfter_entry, pw);
```

The handler has the generic veneer prototype:

```c
_kernel_oserror *Mod_CallAfter(_kernel_swi_regs *r, void *pw);
```

The common pattern is to keep the ticker handler short and schedule an `OS_AddCallBack` for the real work. A repeating ticker can add a callback and return immediately; a one-shot `OS_CallAfter` handler can add a callback and clear its "scheduled" flag.

## Notes

- Store enough state to know whether a one-shot `OS_CallAfter` is already scheduled.
- Always remove the ticker event in finalisation, even if it may already have fired.
- Pass the module private word from initialisation or stored module state; do not invent a private word.
