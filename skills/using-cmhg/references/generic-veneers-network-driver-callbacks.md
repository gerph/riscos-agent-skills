# Generic veneers for network driver callbacks

## What they are used for

Network modules use generic veneers as callback entry points for packet reception, delayed protocol work, service announcements, and Internet filter integration. These are not all the same OS API, but they share the same pattern: a networking subsystem stores an entry address plus workspace and calls it later with a register ABI.

Typical entries:

- Service announcement entry: `announce_entry/announce`.
- Packet receive entry: `receive_entry/receive` or `rxf_entry/rxf_handler`.
- Deferred processing entry: `callback_entry/callback` or `callback_entry/callback_handler`.
- Timeout entry: `timeout_entry/timeout` or `timer_entry/timer_handler`.
- Internet event entry: `inetevent_entry/inetevent_handler`.
- Startup entry: `startup_entry/startup_handler`.

## CMHG form

```cmhg
generic-veneers: announce_entry/announce,
                 receive_entry/receive,
                 callback_entry/callback,
                 timeout_entry/timeout
```

## C usage

A network protocol module schedules timeout and callback entries with the OS ticker/callback APIs:

```c
_swix(OS_CallAfter, _INR(0,2), next, timeout_entry, private_word);
_swix(OS_AddCallBack, _INR(0,1), callback_entry, private_word);
```

It also uses `announce_entry` as a deferred startup service announcement:

```c
_swix(OS_AddCallBack, _INR(0,2), announce_entry, private_word);
```

The receive entries are handed to networking or driver registration structures/SWIs in the same style as ImageFileConvert and SCSI callbacks: the owning subsystem later calls the entry with its documented register layout.

## Notes

- Network receive paths often run in constrained contexts. Schedule `OS_AddCallBack` for heavy work.
- Keep separate entries for timeout and callback handling; the timeout handler usually just schedules the callback and returns.
- Finalisation should remove pending ticker and callback entries before tearing down protocol state.
