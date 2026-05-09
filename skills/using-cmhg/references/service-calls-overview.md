# CMHG service call handlers

## What they are used for

RISC OS modules receive service calls when the system or another module announces a change or asks for optional providers. In `SourcesSVC`, service handlers are used for:

- lifecycle notification: module starting/dying, Wimp starting, shutdown, reset, ResourceFS starting;
- registering or deregistering with another module when it appears;
- enumerating providers, modes, formats, network drivers, statistics, or other extension lists;
- claiming a request and returning data by writing back to the register block;
- patching or adapting another module/application before it starts;
- keeping caches in sync after display, font, palette, network, or filing-system changes.

## CMHG form

The CMHG directive names the C handler followed by the service numbers the module wants to receive:

```cmhg
#include "riscos/Services.h"

service-call-handler: Mod_Service Service_StartWimp,
                                  Service_StartedWimp
```

Long entries commonly use either comma continuation or a backslash:

```cmhg
service-call-handler: Window_services \
                                  Service_ModeChange,
                                  Service_ToolboxStarting,
                                  Service_ToolboxTaskBorn
```

Numeric values are valid when no symbolic name is available or the source predates a header definition:

```cmhg
service-call-handler: sc_handler &95 &96
service-call-handler: cdfs_service_handler 0x40
```

Use symbolic names from `riscos/Services.h` where possible. If a local service is not in the headers, define a local `Service_...` constant close to the CMHG/C code, as the Toolbox gadget modules do for `Service_WindowModuleStarting` and `Service_RedrawingWindow`.

## C handler ABI

CMHG generates the module service veneer and calls the named C function as:

```c
void Mod_Service(int service_number, _kernel_swi_regs *r, void *pw)
{
    switch (service_number)
    {
        case Service_StartWimp:
            break;
    }
}
```

- `service_number` is the incoming service number, normally equal to `r->r[1]`.
- `r` points at the live register set. Read inputs from `r->r[n]` and write outputs back to it.
- `pw` is the module private word.
- The meaning of `r0` onwards is service-specific.

## Claiming

Many services are pure notification and must not be claimed. For extension requests, set `r->r[1]` to `Service_Serviced`, or to zero in older code, to claim:

```c
if (handled)
    r->r[1] = Service_Serviced;
```

Observed examples:

- `SystemBell2` claims `Service_ExternalBell` only after successfully making the replacement sound call.
- `ScrSaver` claims `Service_ScreenBlanking` only when it has blanked the screen itself.
- DOSFS claims `Service_IdentifyDisc`, `Service_IdentifyFormat`, and some error cases by setting `r1` to zero after filling return registers.
- EasyUSB SCSI claims `Service_EasyUSB_NewDeviceByClass` when it accepts the new device.
- Some patching handlers intentionally do not claim because other patchers may also need to inspect or modify the same image.

## Filtering matters

The service list in CMHG is part of the module interface. If the CMHG list and C switch do not match, the C case will not run. One source example has `ScrSaver` listing `Service_StartWimp` in CMHG while the C handler tests `Service_StartedWimp`; an implementation should keep these exact.

## Safety rules

Service calls often run at awkward times. Avoid blocking work and be cautious about I/O unless the service documentation permits it. DOSFS comments explicitly say not to perform I/O from most service functions, then performs the required sector reads only for the disc-identification protocol. Prefer setting flags, registering callbacks, or updating small pieces of state when possible.
