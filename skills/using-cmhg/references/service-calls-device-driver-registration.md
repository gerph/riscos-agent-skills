# Device and provider registration services

## What they are used for

Hardware and provider modules use service calls to register with manager modules that may start after them, and to deregister or clean up when those managers die. The same pattern appears for SCSI, USB, sound, buffers, database providers, and file-type-specific media providers.

Relevant PRM context: Buffer Manager `Service_BufferStarting` is documented at <http://www.riscos.com/support/developers/prm/bufferman.html#12732>.

Common services:

- `Service_SCSIStarted`, `Service_SCSIDying`: register/deregister a SCSI provider.
- `Service_EasyUSB_Started`, `Service_EasyUSB_Dying`: scan or forget USB transport state.
- `Service_EasyUSB_NewDeviceByClass`, `Service_EasyUSB_NewDeviceByVendor`, `Service_EasyUSB_DeviceDead`: accept/remove USB devices.
- `Service_BufferStarting`: register with BufferManager.
- `Service_Sound`, `Service_SoundControl`: update sound-related state.
- `Service_DBResult_Starting`, `Service_DBResult_Dying`: register/deregister database result providers.
- `Service_SoundFileIdentify`: sound file identification; SoundFile issues this service to find format handlers.

## CMHG form

SoftSCSI over EasyUSB demonstrates the manager/provider lifecycle:

```cmhg
service-call-handler: Mod_Service Service_SCSIStarted,
                                  Service_SCSIDying,
                                  Service_EasyUSB_Started,
                                  Service_EasyUSB_Dying,
                                  Service_EasyUSB_NewDeviceByClass,
                                  Service_EasyUSB_DeviceDead
```

The Sigmatel variant uses `Service_EasyUSB_NewDeviceByVendor` instead of class matching.

PrinterBuffer2 listens for the buffer manager:

```cmhg
service-call-handler: Mod_Service Service_BufferStarting
```

Database modules listen for DBResultManager:

```cmhg
service-call-handler: Mod_Service Service_DBResult_Starting,
                                  Service_DBResult_Dying
```

## C usage

Provider registration is usually a notification:

```c
case Service_SCSIStarted:
    SCSIx_Register(pw);
    break;

case Service_SCSIDying:
    SCSIx_Deregister(pw, 0);
    break;
```

Manager lifecycle services trigger scans and cleanup:

```c
case Service_EasyUSB_Started:
    transport_finddevices();
    break;

case Service_EasyUSB_Dying:
    transport_usbshutdown();
    break;
```

New device services are claimable. EasyUSB class matching uses:

- `r0`: EasyUSB device handle;
- `r2`: USB class;
- `r3`: subclass;
- `r4`: protocol.

The handler claims only if it accepts the device:

```c
case Service_EasyUSB_NewDeviceByClass:
{
    void *newdev = (void *)r->r[0];
    int class = r->r[2];
    int subclass = r->r[3];
    int protocol = r->r[4];
    if (transport_newdevice(newdev, class, subclass, protocol))
        r->r[1] = Service_Serviced;
}
break;
```

Device death services are cleanup notifications:

```c
case Service_EasyUSB_DeviceDead:
    transport_removedevice((device_t)r->r[0]);
    break;
```

`Service_BufferStarting` (`&6F`) is issued after Buffer Manager has initialised or reset. Modules that provide buffers can then register buffers and use `Buffer_...` SWIs. Preserve all registers; this is a notification and should not be claimed.

## Related information

Registration services are often paired with module initialisation/finalisation. A robust module should register in `Mod_Init` if the manager is already present, and also listen for the manager's `...Started` service in case it appears later.
