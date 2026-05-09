# Generic veneers for SCSI driver callbacks

## What they are used for

SCSI provider modules register generic veneer entries with the SCSI driver. The SCSI driver later calls those entries to perform device operations.

Typical entries:

- SCSI provider operation entry: `SCSIx_Entry/SCSIx_Handler`.
- Startup service announcement entry: `Mod_Started_Entry/Mod_Started`.

## CMHG form

```cmhg
generic-veneers: SCSIx_Entry/SCSIx_Handler
```

## C usage

A SCSI provider registers each device with the SCSI driver by passing the veneer entry, private word, and device-specific pointer:

```c
_swix(SCSI_Register, _INR(0,3) | _OUT(0),
      0, SCSIx_Entry, private_word, scsi, &scsi->scsi_deviceid);
```

They deregister with the same entry and private word:

```c
_swix(SCSI_Deregister, _INR(0,3),
      deviceid, SCSIx_Entry, private_word, scsi);
```

`SCSIx_Handler` reads the SCSI driver's register ABI. A common convention is that `r8` contains the device pointer and the operation reason is read from the extended register block. The handler then switches on operations such as features, reset bus, foreground operations, and transfer requests.

## Notes

- The SCSI handler relies on registers beyond the standard `_kernel_swi_regs` fields in some builds. Treat this as an interface-specific requirement, not a generic CMHG guarantee.
- Register again when `Service_SCSIStarted` is received, and deregister on `Service_SCSIDying`.
- Device-specific state must outlive registration and be removed only after deregistration.
