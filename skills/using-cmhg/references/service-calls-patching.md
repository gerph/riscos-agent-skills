# Patching services

## What they are used for

Patching services let a module inspect and modify code before it runs. The AppPatcher module uses them to apply signature-based fixes to applications and modules, usually for StrongARM or 26/32-bit compatibility issues.

The important services are:

- `Service_UKCompression`: used while UKCompression is handling an application or module image.
- `Service_ModulePreInit`: issued before a module initialises, allowing the module image to be inspected or patched.

## CMHG form

AppPatcher lists both patching services explicitly:

```cmhg
service-call-handler: patch_services Service_UKCompression,
                                     Service_ModulePreInit
```

The handler is a normal CMHG service handler:

```c
void patch_services(int service_number, _kernel_swi_regs *r, void *pw)
```

## C usage

For `Service_UKCompression`, AppPatcher only acts on subreason `r0 == 1`, which it treats as application patching. It reads the application image from the service registers, checks whether the image looks like an AIF header, derives the searchable size, and inspects the AIF flags to decide whether the code is 26-bit and whether it is StrongARM-safe.

The handler then calls its signature finder with flags describing:

- application patching rather than module patching;
- whether StrongARM-specific patches should be allowed;
- whether 26-bit or 32-bit patch variants are appropriate.

If a signature matches, AppPatcher applies the patch. It deliberately does not claim the service, because another patcher may also need to inspect or patch the same image.

For `Service_ModulePreInit`, AppPatcher reads:

- `r0`: module base address;
- `r2`: module length information used by this source as `r2 - 4`;
- module name: found through the module header name offset.

It applies generic module signature patches, then module-specific patches. It also leaves the service unclaimed so other patchers can contribute.

## Related information

Patching services run at sensitive times. Keep the handler small, avoid unnecessary I/O, and do not claim unless the service protocol specifically requires exclusive handling. In the observed AppPatcher code, claiming was considered and intentionally disabled because preventing downstream handlers would be harmful.
