# Generic veneers for filter callbacks

## What they are used for

Filter APIs take callback entry addresses. Generic veneers can be used for Wimp/FilterManager callbacks and network packet filters.

Typical entries:

- Icon border filter entry: `border_entry/border_handler`.
- Post-rectangle redraw filter entry: `post_rect_entry/post_rect`.
- Post-icon redraw filter entry: `post_icon_entry/post_icon`.
- Internet packet filter entry: `Filter_Entry/Mod_Filter` or `Filter_Entry/Filter`.

## CMHG form

```cmhg
generic-veneers: border_entry/border_handler
generic-veneers: post_rect_entry/post_rect,
                 post_icon_entry/post_icon
generic-veneers: Filter_Entry/Mod_Filter
```

## C usage

Register the entry symbol with the owning filter API:

```c
_swix(Filter_RegisterIconBorderFilter, _INR(0,3),
      filtername, border_entry, pw, 0xff);

_swix(Filter_RegisterPostRectFilter, _INR(0,3),
      RectFilterName, post_rect_entry, my_pw, 0);
```

Deregister with the same name pointer, entry, and private word:

```c
_swix(Filter_DeRegisterIconBorderFilter, _INR(0,2),
      filtername, border_entry, pw);
```

Handlers inspect the register block according to the filter API. Icon border filters use `r->r[9]` as an operation code and set `r->r[9] = -1` to claim handled draw/size/fill/colour operations. Network filters inspect packet/interface pointers and write return codes into the register block as defined by the Internet filter interface.

## Notes

- Keep registered filter names stable. The icon border examples keep the name in static storage because FilterManager remembers the pointer.
- Re-register when the FilterManager or equivalent owner restarts; several modules listen for service calls and re-register.
- Return an error pointer only when the filter API expects V-set error returns.
