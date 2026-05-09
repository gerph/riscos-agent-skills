# GContext API Reference

The GContext library provides an abstracted interface for 2D graphics operations on RISC OS.

## Core Structures

### Basic Types
```c
typedef uint32_t colour_t;
#define COLOUR_NONE (0xFFFFFFFFlu)
#define COLOUR_RGB(r,g,b) ((((int)(r))<<8) | (((int)(g))<<16) | (((int)(b))<<24))

#define GCONTEXT_ZEROTERM (-1)
#define GCONTEXT_NOSPLIT (-1)
```

### coords_t
```c
typedef struct coords_s {
    int32_t x;
    int32_t y;
} coords_t;
```

### bounds_t
```c
typedef struct bounds_s {
    int32_t width;
    int32_t height;
} bounds_t;
```

### bbox_t
```c
typedef struct bbox_s {
    int32_t x0, y0;
    int32_t x1, y1;
} bbox_t;
```

### stringbounds_t
Returned by `text_getstringsize`. Note that `xoffset` is the cumulative width for subsequent characters.
```c
typedef struct stringbounds_s {
    int32_t ascent, descent;
    int32_t lbearing, rbearing;
    int32_t xoffset;
    int32_t charoffset;
} stringbounds_t;
```

## gcontext_t
The main graphics context structure contains function pointers for all operations.

### Drawing Operations
- `rectangle_fill(gc, colour, x0, y0, x1, y1)`
- `rectangle_outline(gc, colour, x0, y0, x1, y1)`
- `line_start(gc, colour)`
- `line_line(gc, x0, y0, x1, y1)`
- `line_end(gc)`

### Text Operations
- `text_findfont(gc, name, xsize, ysize)`: Returns `font_t`.
- `text_losefont(gc, handle)`: Releases a font.
- `text_getstringsize(gc, font, bounds, xlimit, str, size, split_char)`: Calculates dimensions.
- `text_getemsize(gc, font)`: Returns default character size.
- `text_paint(gc, font, xb, yb, bg, fg, str, size)`: Renders text. `xb, yb` are the baseline coordinates.

## Initialization
Typically initialized via `gcontext_initvdu(type)`.
