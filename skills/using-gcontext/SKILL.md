---
name: using-gcontext
description: Guidance for using the GContext graphics library on RISC OS for drawing primitives and rendering text. Use when the agent needs to implement screen output, handle font metrics, or manage graphics contexts.
license: MIT
---

# Using GContext

The GContext library provides an abstracted interface for 2D graphics operations.

## Core Concepts

### Graphics Context
All operations require a `gcontext_t` pointer. It is typically initialized with `gcontext_initvdu(2)`.

### Coordinate System
- Coordinates are standard RISC OS OS-units.
- Y-axis typically increases upwards.
- For text painting, the coordinates specified are for the **baseline** of the string.

### Colours
- Use `colour_t` for all colour parameters.
- Use `COLOUR_RGB(r, g, b)` to create a colour value.
- Use `COLOUR_NONE` to skip drawing (e.g., for transparent backgrounds).

## Workflows

### Drawing Primitives
1.  Initialize the context.
2.  Use `rectangle_fill` or `rectangle_outline` for boxes.
3.  For lines, use the sequence: `line_start(gc, colour)`, then one or more `line_line(gc, x0, y0, x1, y1)`, and finally `line_end(gc)`.

### Rendering Text
1.  Find a font using `text_findfont(gc, name, xsize, ysize)`.
2.  Calculate dimensions if needed using `text_getstringsize`. **Crucial**: Use the `xoffset` field of `stringbounds_t` for advancing the cursor horizontally, as it accounts for character spacing correctly. The total width of the string is `bounds.xoffset + bounds.rbearing`.
3.  Paint text using `text_paint(gc, font, xb, yb, bg, fg, str, len)`. Use `GCONTEXT_ZEROTERM` for the length if the string is null-terminated.
4.  Release the font when finished using `text_losefont(gc, font)`.

## Installation and Setup

### Linking
Link against the GContext library in your `Makefile,fe1`:
```makefile
LIBS = ${CLIB} C:GContext.o.libGContext
```

### Environment
Ensure `C$Path` includes the directory containing the GContext library. In `.robuild.yaml`, you can add:
```yaml
- Set C$Path @.Lib.,<C$Path>
```
(Assuming the library is extracted to a `Lib` directory in your project root).

### Continuous Integration (GitHub Actions)
To use GContext in CI, download and extract the library:
```yaml
- name: Obtain the GContext library
  run: |
    curl -s -L -o libgcontext.zip https://github.com/gerph/riscos-gcontext/releases/download/v0.05/GContext-0.05.zip
    python3 -m rozipfile --verbose --extract libgcontext.zip
    rm libgcontext.zip
```

## API Reference

See [api.md](references/api.md) for detailed structure definitions and function pointer signatures.
