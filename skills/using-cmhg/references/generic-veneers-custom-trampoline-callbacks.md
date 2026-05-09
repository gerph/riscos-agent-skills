# Generic veneers for custom trampoline callbacks

## What they are used for

Some code uses a generic veneer as the target of a hand-built or third-party callback trampoline rather than passing it directly to an OS registration SWI. This is useful when an external renderer or library expects a private callback ABI but the module still needs to land in C with the module private word restored.

Typical entry:

- Custom renderer callback entry: `AWCallback_Entry/AWCallback_Handler(carry-capable: )`.

## CMHG form

Use a generic veneer with `carry-capable:` when the external ABI needs carry status on return:

```cmhg
generic-veneers: AWCallback_Entry/AWCallback_Handler(carry-capable: )
```

The `carry-capable:` parameter allows the handler to return `VENEER_SETCARRY` where the callback protocol requires carry set. Normal `NULL` and error-pointer returns still work.

## C usage

A renderer or external library adapter can patch a small instruction sequence with the module private word and generated entry address:

```c
callback_insts[6] = (unsigned long)pw;
callback_insts[7] = (unsigned long)AWCallback_Entry;
_swix(OS_SynchroniseCodeAreas, _INR(0,2),
      1, (char *)&callback_insts[0],
      ((char *)&callback_insts[0]) + sizeof(callback_insts));
```

The external renderer calls that trampoline. The trampoline restores the workspace/private word and branches to `AWCallback_Entry`; CMHG then calls:

```c
_kernel_oserror *AWCallback_Handler(_kernel_swi_regs *r, void *pw);
```

The handler reads an operation reason from the register block. One common convention is that `r11` selects operations such as memory manipulation, plate colour mapping, and interface queries. The handler updates return registers, may return an error pointer, and can use the carry-capable return convention when required.

## Notes

- Synchronise code areas after modifying executable callback instructions.
- Keep the generated instruction block in memory that remains executable and valid for the callback lifetime.
- Use this pattern only when a normal `workspace, function` descriptor or OS registration SWI cannot express the callback ABI.
