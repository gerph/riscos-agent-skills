# Generic veneers for ImageFileConvert converters

## What they are used for

Image conversion modules register generic veneer entry addresses with `ImageFileConvert_Register`. The ImageFileConvert module later calls those entries to perform conversions or miscellaneous operations.

Typical entries:

- Sprite/file converter entry: `sprite_convert_Entry/sprite_convert_Handler`.
- Converter miscellaneous-operation entry: `sprite_miscop_Entry/sprite_miscop_Handler`.
- Format-specific converter entry: `wmfdraw_convert_Entry/wmfdraw_convert_Handler`.
- Draw/SVG converter entry: `drawsvg_convert_Entry/drawsvg_convert_Handler`.

## CMHG form

```cmhg
generic-veneers: sprite_convert_Entry/sprite_convert_Handler,
                 sprite_miscop_Entry/sprite_miscop_Handler
```

## C usage

The converter module fills a converter definition with the generated entry addresses and registers it:

```c
converterdef_t image = {
  CONVERTER_API_VERSION,
  0,
  CONVERT_FILETYPE1,
  0,
  0,
  sprite_convert_Entry,
  sprite_miscop_Entry
};

image.private = pw;
image.name = format_name;
_swix(ImageFileConvert_Register, _INR(0,1), 0, &image);
```

Deregistration is by converter type and name, not by entry address:

```c
_swix(ImageFileConvert_Deregister, _INR(0,2),
      0, CONVERT_FILETYPE1, format_name);
```

The convert handler reads the ImageFileConvert call registers. A typical bitmap converter uses:

- `r0`: flags.
- `r1`: packed source/destination type.
- `r2`, `r3`: input buffer and length.
- `r4`, `r5`: output buffer and length.
- `r6`: background colour.

The handler writes results back into the register block, usually `r5` for output length.

## Notes

- Register all supported directions; many converters register both from-type-to-sprite and sprite-to-type.
- Keep the `private` field set to the CMHG private word so the veneer receives the correct `pw`.
- On partial registration failure, deregister anything already registered.
