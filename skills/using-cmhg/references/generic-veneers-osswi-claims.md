# Generic veneers for OS_ClaimOSSWI handlers

## What they are used for

`OS_ClaimOSSWI` lets a module intercept or provide OS SWI implementations. Generic veneers can be used as the implementation entry points for claimed OS SWIs.

Typical entries:

- Argument parsing entries: `Entry_ReadArgs/OSSWI_ReadArgs`, `Entry_SubstituteArgs/OSSWI_SubstituteArgs`.
- Utility OS SWI entries: `Entry_CRC/OSSWI_CRC`, `Entry_HeapSort/OSSWI_HeapSort`, `Entry_PrettyPrint/OSSWI_PrettyPrint`.
- Line input entries: `Entry_ReadLine/OSSWI_ReadLine`, `Entry_ReadLine32/OSSWI_ReadLine32`.

## CMHG form

```cmhg
generic-veneers: Entry_ReadArgs/OSSWI_ReadArgs,
                 Entry_SubstituteArgs/OSSWI_SubstituteArgs
```

## C usage

A helper can claim or release a SWI by passing the generic veneer entry to `OS_ClaimOSSWI`:

```c
_swix(OS_ClaimOSSWI, _INR(0,3),
      claim ? ClaimOSSWI_Claim : ClaimOSSWI_Release,
      swi, func, pw);
```

The handler then implements that SWI's register contract using the register block:

```c
_kernel_oserror *OSSWI_SubstituteArgs(int number,
                                      _kernel_swi_regs *r,
                                      void *pw);
```

These handlers are often the same shape as normal CMHG SWI handlers, but they are installed as callback entry points for individual OS SWIs rather than as entries in the module's own SWI chunk.

## Notes

- Release claimed OS SWIs in finalisation.
- Match the OS SWI register contract exactly, including preserved registers and error returns.
- The generic veneer entry is the address registered with `OS_ClaimOSSWI`; do not register the C handler symbol directly.
