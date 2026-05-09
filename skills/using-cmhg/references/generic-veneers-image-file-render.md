# Generic veneers for ImageFileRender handlers

## What they are used for

Image renderers use generic veneers as function pointers inside ImageFileRender handler definitions. The core ImageFileRender module stores those pointers and calls them later for render, bounding-box, font declaration, information, and optional start/stop operations.

Typical entries:

- Built-in renderer entries: `ir_drawfile_render_Entry`, `ir_drawfile_bbox_Entry`, `ir_drawfile_declare_Entry`, `ir_drawfile_info_Entry`.
- Additional format entries: `ir_jpeg_render_Entry`, `ir_jpeg_bbox_Entry`, `ir_jpeg_info_Entry`.
- Renderer lifecycle entries: `ir_artworks_start_Entry`, `ir_artworks_stop_Entry`.
- Renderer operation entries: `ir_artworks_render_Entry`, `ir_artworks_bbox_Entry`, `ir_artworks_info_Entry`, `ir_artworks_declare_Entry`.

## CMHG form

```cmhg
generic-veneers: ir_drawfile_render_Entry/ir_drawfile_render_Handler,
                 ir_drawfile_bbox_Entry/ir_drawfile_bbox_Handler,
                 ir_drawfile_declare_Entry/ir_drawfile_declare_Handler,
                 ir_drawfile_info_Entry/ir_drawfile_info_Handler
```

## C usage

The renderer creates a handler definition containing the generic veneer entries, then registers the definition with the renderer's internal registry or exported SWI:

```c
handlerdef_t handler = {
  HANDLER_API_VERSION,
  flags,
  type,
  name,
  pw,
  ir_drawfile_render_Entry,
  ir_drawfile_bbox_Entry,
  ir_drawfile_declare_Entry,
  ir_drawfile_info_Entry
};
handler_add(&handler);
```

The ImageFileRender core later calls stored entries through `_callx`, passing the handler private word and argument pointers. A standard handler wrapper extracts:

- `r0`: flags.
- `r1`: pointer to `handler_image_t`.
- `r2`: pointer to operation-specific details, such as `handler_render_t` or `handler_bbox_t`.

Then the wrapper calls the renderer-specific C routine.

## Notes

- Handler definitions must keep their callback entry fields valid until deregistration.
- The generic veneer handler returns a `_kernel_oserror *`; returning an error reports failure to the caller of ImageFileRender.
- The built-in renderer schedules a startup callback so registration and service announcement happen after module initialisation.
