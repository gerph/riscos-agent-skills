---
name: writing-assembly
description: ARM assembly with the RISC OS toolchain, using the ObjAsm assembler. Use when RISC OS assembly code needs to be understood or written, or `s/*` assembly files are processed.
license: MIT
---

# Assembly Development for RISC OS with ObjAsm

This document outlines the procedures, standards, and pitfalls for writing and building ARM assembly code on RISC OS using the `objasm` assembler and `riscos-link`.

## 1. Source File Structure

`objasm` source files are held in an `s/` directory.

### Syntax Rules
*   **Labels**: Must start at the very beginning of the line (Column 1).
*   **Instructions**: Must be indented (at least one space or tab).
*   **Comments**: Start with a semicolon (`;`).
*   **Directives**: Essential for correct object generation.

### Essential Directives
```arm
        AREA    |Name|, CODE, READONLY  ; Define the area name and type
        EXPORT  my_function             ; Make symbol visible to linker
        GET     hdr.swis                ; Include header files
        END                             ; Mandatory end of file
```

## 2. The Build Process

The standard RISC OS build toolchain uses a two-stage process: Assemble to Object (AOF), then Link to Executable.

### Assembling (objasm)
*   **Default**: Produces an AOF object file.
*   **Command**: `riscos-objasm -o o.mycode s.mycode`
*   **Architecture**: For 32-bit code, use `-32bit` (though often handled by Makefiles).

### Linking (riscos-link)
*   **Default**: Produces an AIF (Absolute Interface Format) executable.
*   **Utility/Binary Output**: To create a raw binary (e.g., for loading into RMA or as a utility module), you **must** use the `-bin` flag.
*   **Command**: `riscos-link -bin -o mybinary,ffc o.mycode`
*   **Note**: Without `-bin`, the linker adds a header that may cause "Branch through zero" exceptions if you try to jump directly to the start of the file.

## 3. Register Conventions (APCS)

When interfacing with C or the OS, follow the ARM Procedure Call Standard (APCS):

*   **R0-R3**: Argument passing and result return (R0). These are "caller-saved" (volatile).
*   **R4-R11**: Variable registers. These **must** be preserved by the called function.
*   **R12**: IP (Intra-Procedure-call scratch register). Often used as a workspace pointer.
*   **R13 (SP)**: Stack pointer. Must be 8-byte aligned at public interfaces.
*   **R14 (LR)**: Link register (return address).
*   **R15 (PC)**: Program counter.

## 4. RISC OS Error Convention

RISC OS uses the **V flag** (Overflow) to indicate errors:
*   **VC** (V Clear): Success. R0 may contain a result.
*   **VS** (V Set): Failure. R0 contains a pointer to an error block (`int error_number, char error_message[]`).

In your assembly return logic:
```arm
        MOVVC   r0, #0          ; Return NULL on success
        ; V flag is preserved from the last instruction (e.g., a driver call)
        LDMFD   sp!, {r4-r12, pc}
```

## 5. 32-bit Pitfalls

### The Return Instruction
*   **Avoid**: `MOVS pc, lr` in 32-bit user/SVC mode. This is a 26-bit era instruction that restores the PSR from the PC's top bits, which is incorrect in 32-bit mode.
*   **Correct**: Use `MOV pc, lr` for simple returns or `LDMFD sp!, {regs, pc}` to return and pop registers simultaneously.

### The Magic Word Requirement
For certain module-related drivers (like CDFSDriver registration), the code block in memory often requires a "Magic Word" immediately preceding the entry point.
*   **CDFSDriver**: Expects `&EE50EE50` at `entry - 4`.

### Register Blocks (`_kernel_swi_regs`)
*   The standard C structure `_kernel_swi_regs` only contains **10 words** (R0-R9).
*   If you need to pass R11 or R12 to a routine, you cannot put them in that block. You must pass them as separate arguments to an assembly veneer.

## 6. Debugging

*   **Disassembly**: Use `riscos-dumpi <file>` to see the actual instructions generated. This is vital for checking if the linker added unwanted headers or if the `MOVVC`/`STRVS` conditions are correct.
*   **Hex Dump**: Use `riscos-dump <file>` to verify byte alignments and magic words.
*   **Branch through zero**: This exception usually means you jumped to a NULL pointer, often caused by an incorrect entry point address or a corrupted stack during a return.
