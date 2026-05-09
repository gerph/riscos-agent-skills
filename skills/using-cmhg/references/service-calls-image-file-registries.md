# ImageFileConvert and ImageFileRender services

## What they are used for

Image conversion and rendering modules use service calls as registry lifecycle notifications. Converter modules register with ImageFileConvert when it starts, deregister or mark themselves inactive when it dies, and sometimes track renderer availability through ImageFileRender services.

Common services:

- `Service_ImageFileConvert_Started`: ImageFileConvert is present; converters should register.
- `Service_ImageFileConvert_ConverterChanged`: the converter registry changed; clients may clear caches.
- `Service_ImageFileConvert_Dying`: ImageFileConvert is going away; converters should mark themselves unregistered.
- `Service_ImageFileRender_Started`: ImageFileRender is present; renderers/clients should register or discover providers.
- `Service_ImageFileRender_RendererChanged`: renderer registry changed.
- `Service_ImageFileRender_Dying`: ImageFileRender is going away.

## CMHG form

A converter module, such as ConvertBMP, uses:

```cmhg
service-call-handler: Mod_Service Service_ImageFileConvert_Started,
                                  Service_ImageFileConvert_ConverterChanged,
                                  Service_ImageFileConvert_Dying,
                                  Service_TaskManagerAcknowledgements
```

ConvertSprite listens to both Convert and Render registries because it can bridge sprite conversion and rendering:

```cmhg
service-call-handler: Mod_Service Service_ImageFileConvert_Started,
                                  Service_ImageFileConvert_Dying,
                                  Service_ImageFileRender_Started,
                                  Service_ImageFileRender_RendererChanged,
                                  Service_ImageFileRender_Dying
```

ImageFileConvert itself listens for ImageFileRender:

```cmhg
service-call-handler: Mod_Service Service_ImageFileRender_Started,
                                  Service_ImageFileRender_RendererChanged,
                                  Service_ImageFileRender_Dying
```

## C usage

Converter modules generally split the service handler: `Mod_Service` receives the CMHG call, then forwards ImageFileConvert services to converter-library code:

```c
void ifc_service(int service, _kernel_swi_regs *r, void *pw)
{
    switch (service)
    {
        case Service_ImageFileConvert_Started:
            ifc_init(pw);
            break;

        case Service_ImageFileConvert_Dying:
            registered = 0;
            break;
    }
}
```

The actual registration is usually via ImageFileConvert SWIs and generic veneer entries. The service call tells the converter when it is safe or necessary to call those SWIs.

`Service_ImageFileConvert_ConverterChanged` is normally a notification for cache invalidation. Many converter modules list it but do not need action in their own C handler.

ImageFileRender follows the same lifecycle shape: `...Started` means register/discover, `...RendererChanged` means invalidate cached renderer choices, and `...Dying` means drop cached entry points or mark inactive.

## Related information

These registry lifecycle services should normally not be claimed. The registration itself is done by SWI calls or by passing generated generic veneer entry addresses to the registry module.
