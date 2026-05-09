# Diagnostic services

## What they are used for

Diagnostic modules use service calls to extend APCS backtrace handling. The examples in `SourcesSVC` are:

- CFrontDemangler: decodes C++/CFront symbol names for backtraces.
- MiniDump: writes a diagnostic dump when a backtrace is requested, then notifies other clients that a dump was created.

The key service is `Service_APCSBacktrace`, with sub-reasons in `r0`.

## CMHG form

Both CFrontDemangler and MiniDump listen for the same service:

```cmhg
service-call-handler: Mod_Service Service_APCSBacktrace
```

## C usage

CFrontDemangler handles subreason `Service_APCSBacktrace_DecodeName`:

```c
case Service_APCSBacktrace:
    if (apcsbacktrace(r->r[0], r))
        r->r[1] = Service_Serviced;
    break;
```

For the decode-name subreason, the observed register contract is:

- `r0`: `Service_APCSBacktrace_DecodeName`;
- `r1`: `Service_APCSBacktrace`;
- `r2`: pointer to the string to decode;
- `r3`: pointer to the language name, or NULL;
- on claim, `r2`: pointer to the decoded string.

CFrontDemangler treats a NULL language or language `"C"` as eligible, demangles into a static buffer, writes `r2` to that buffer, and claims by setting `r1` serviced.

MiniDump handles subreason `Service_APCSBacktrace_BacktraceRequested`. The observed inputs include:

- `r2`: diagnostic file handle;
- `r3`: pointer to register dump, if available;
- `r4`: unwind block, if register dump is not available;
- `r5`: language name;
- `r6`: error number;
- `r7`: fault address;
- `r8`: application descriptor.

If minidump generation is enabled, MiniDump writes a dump from either the register block or unwind data. It then broadcasts `Service_APCSBacktrace` with subreason `Service_APCSBacktrace_DiagDumpCreated`, passing the dump filename and original application name. If no other module services that notification, it performs its configured local fallback action.

## Related information

APCS backtrace services are claimable extension points. Claim only when the requested subreason has been handled and the documented return registers have been filled. Guard against recursion; MiniDump uses a `threaded` flag to avoid re-entering its handler.
