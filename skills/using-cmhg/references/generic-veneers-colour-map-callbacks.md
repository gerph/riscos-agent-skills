# Generic veneers for colour mapping callbacks

## What they are used for

Colour mapping APIs use small descriptors containing a workspace pointer and a function pointer. Generic veneers provide the function pointer so a C module can be called as a colour mapper.

Typical entry:

- Faded colour mapper entry: `fadedcolour_entry/fadedcolour`.

## CMHG form

```cmhg
generic-veneers: fadedcolour_entry/fadedcolour
```

## C usage

A gadget or renderer creates a colour map descriptor:

```c
colourmap_t colmap;
colmap.workspace = private_word;
colmap.function = fadedcolour_entry;
```

It passes that descriptor to ColourMap/ImageFileRender code, or calls it through `_callx`:

```c
_callx((void *)colmap.function, colmap.workspace,
       _IN(0) | _OUT(0), background, &background);
```

The handler receives the colour in `r0`, changes it in place, and returns `NULL`:

```c
_kernel_oserror *fadedcolour(_kernel_swi_regs *regs, void *pw)
{
  unsigned int bg = 0xffffffff;
  colours_fade((unsigned int *)&regs->r[0], &bg);
  return NULL;
}
```

## Notes

- The descriptor's workspace should be the module private word or another value the handler understands.
- The handler must follow the colour mapping interface's register convention; in this case `r0` is both input and output.
- This pattern is general: any RISC OS API that takes a `workspace, function` pair can use a generic veneer entry as the function.
