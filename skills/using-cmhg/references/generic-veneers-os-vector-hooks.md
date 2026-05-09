# Generic veneers for OS vector hooks

## What they are used for

Although CMHG has `vector-handlers:`, `generic-veneers:` is often better for `OS_Claim` vector-style hooks where the callback ABI is not the simple pass-on/claim protocol of CMHG vector handlers. These hooks need full control over the register block and usually return `NULL` or an error pointer.

Typical entries:

- `WRCHV_Entry/WRCHV_Call` for `WRCHV`.
- `FSControl_Entry/FSControl_Handler` for `FSControlV`.
- `ReadCV_Entry/ReadCV_Handler` and `ByteV_Entry/ByteV_Handler` for input-related vectors.
- `Error_Entry/Error_Handler` for `ErrorV`.
- `upcall_Entry/upcall_Handler` for `UpCallV`.

## CMHG form

```cmhg
generic-veneers: WRCHV_Entry/WRCHV_Call
generic-veneers: FSControl_Entry/FSControl_Handler
generic-veneers: ReadCV_Entry/ReadCV_Handler,
                 ByteV_Entry/ByteV_Handler
```

## C usage

Claim and release the vector with the generated entry symbol:

```c
_swix(OS_Claim, _INR(0,2), WRCHV, WRCHV_Entry, pw);
_swix(OS_Release, _INR(0,2), WRCHV, WRCHV_Entry, pw);
```

Handlers inspect and update the raw register block according to the claimed vector. For example, an input-monitoring module can watch `ByteV` and `RdchV` to trigger a display mode switch when keyboard input would otherwise block, while a memory-protection module can claim `ErrorV` and replace abort errors by writing a new error pointer into `r->r[0]`.

## Notes

- Use `generic-veneers:` when the vector's ABI is not CMHG's `VECTOR_CLAIM`/`VECTOR_PASSON` model.
- Claim and release using the exact same entry and private word.
- Be careful with vectors that can be called in restricted contexts; keep handlers short and avoid unsafe APIs.
