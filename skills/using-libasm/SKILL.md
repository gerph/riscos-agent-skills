---
name: using-libasm
description: Library of routines for RISC OS C programming. Provides optimized multiplication/division, processor identification, IRQ control, floating-point preservation, and non-C (registrant) function calls. Use when C code needs assembly-level functionality or when porting code that requires these low-level operations. The library is linked by adding C:Asm.o.libAsm to the LIBS line in a makefile and included via headers like #include "Asm/muldiv.h".
license: MIT
---

# Using libasm

## Overview

**libasm** is a C-callable library containing optimized assembly routines that are useful
when writing RISC OS applications and modules in C. The library provides several categories
of functionality:

* **Multiplication and division** - 64-bit intermediate arithmetic to avoid overflow
* **Processor identification** - Runtime detection of ARM architecture and processor type
* **IRQ control** - Safe masking and unmasking of interrupts
* **Floating-point preservation** - Saving/restoring FPU state when using FP in SVC mode
* **Non-C function calls** - Calling arbitrary functions with register arguments
* **Task management** - Safely calling `Wimp_StartTask` from SVC mode

The library is distributed as an object library that you link into your project. It should
not be used directly from BASIC - these are C helper routines.

## Installation and Usage

### Linking in a Makefile

To use libAsm, add it to the `LIBS` variable in your `Makefile,fe1`:

```makefile
LIBS = ${CLIB} C:Asm.o.libAsm
```

Note: `Asm.o.libAsm` (32-bit) are available. The 64-bit variant is not available.

### Including Headers in C Code

Include the relevant headers in your C source files using the `Asm/` prefix:

```c
#include "Asm/muldiv.h"      /* Multiplication and division */
#include "Asm/processor.h"   /* Processor identification */
#include "Asm/irqs.h"        /* IRQ control */
#include "Asm/fpsvc.h"       /* Floating-point preservation */
#include "Asm/callx.h"       /* Cross-mode function calls */
#include "Asm/callbacks.h"   /* Triggering callbacks */
#include "Asm/starttasksvc.h"/* Wimp_StartTask from SVC mode */
```

## Available Routines

### Multiplication and Division (`Asm/muldiv.h`)

The `muldiv()` function performs `(a * b) / c` with a 64-bit intermediate product,
avoiding overflow that would occur with standard 32-bit multiplication.

```c
#include "Asm/muldiv.h"

int result = muldiv(100, 200, 50);  /* Returns (100 * 200) / 50 = 400 */
```

**Why use muldiv?** Standard C multiplication of two 32-bit values can overflow before
division. The `muldiv` function performs the calculation internally using 64-bit arithmetic
to preserve precision.

### Processor Identification (`Asm/processor.h`)

`processor_id()` returns the ARM processor ID register value, which encodes the processor
type, architecture, and revision.

```c
#include "Asm/processor.h"

unsigned long id = processor_id();
```

The header provides macros to interpret the processor ID:

| Macro | Description |
|-------|-------------|
| `processor_architecture(id)` | Returns an `procarch_t` enum value for the architecture |
| `processor_is_arm6x0(id)` | Non-zero if running on an ARM6x0 series processor |
| `processor_is_arm7(id)` | Non-zero if running on an ARM7 series processor |

Architecture enum values:

| Enum | Architecture |
|------|-------------|
| `arch_2` | ARM2/ARM3 |
| `arch_3` | ARM6/ARM60 |
| `arch_4` | ARM7500-style (Architecture 4) |
| `arch_4T` | ARM7TDMI (Architecture 4T) |
| `arch_5` | StrongARM (Architecture 5) |
| `arch_5T` | Architecture 5T |
| `arch_5TE` | Architecture 5TE |
| `arch_5TEJ` | Architecture 5TEJ |
| `arch_6` | Architecture 6 |

### IRQ Control (`Asm/irqs.h`)

These functions safely manipulate the interrupt mask bits in the processor mode register.

```c
#include "Asm/irqs.h"

unsigned long flags;

flags = ensure_irqs_off();   /* Disable IRQs, save previous state */
/* Critical section */
restore_irqs(flags);         /* Restore previous state */

flags = ensure_irqs_on();    /* Enable IRQs, save previous state */
/* Section where IRQs must be on */
restore_irqs(flags);         /* Restore previous state */
```

**Why use these?** Direct manipulation of the SPSR or CPSR is error-prone. These functions
provide a structured way to disable/enable interrupts while preserving the previous state,
which is essential for interrupt handlers and critical section code.

### Floating-Point Preservation (`Asm/fpsvc.h`)

When using floating-point operations in SVC mode (e.g., from a Wimp filter), the FPU
registers must be preserved because the APCS declares F0-F3 as corruptible.

```c
#include "Asm/fpsvc.h"

void my_svc_function(void) {
    int result;
    fpsvc_buf fpbuf;
    fpsvc_preserve(&fpbuf);

    /* Do floating-point operations here */
    result = calculate_value(3.14159);

    fpsvc_restore(&fpbuf);
}
```

**Why use this?** Without preserving FPU state, your code may corrupt the floating-point
context of the task that called your SVC-mode code, leading to incorrect calculations or
crashes in the calling application.

### Non-C Function Calls (`Asm/callx.h`)

`_callx()` allows you to call an arbitrary function with register arguments, similar to
`_swix()` but for function calls rather than SWIs.

```c
#include "Asm/callx.h"
#include "swis.h"

/* Call a function with R0-R4 as arguments, R0 as output */
void *func_ptr = some_function;
void *func_pw = module_pw;
int result;

/* Mask format: bits 0-11 = input registers: `_IN(reg)` and `_INR(loreg,hireg)`
                bits 22-31 = output registers: `_OUT(reg)` and `_OUTR(loreg,hireg)` */
int result;
_callx(func_ptr, func_pw, _INR(0,4)|_OUT(0), arg0, arg1, arg2, arg3, arg4,
       &result);
```

**Why use `_callx`?** When you need to call a function (e.g., a registered handler
), `_callx` provides a clean interface for passing arguments and receiving
results, similar to how `_swix` works for SWIs.

### Callback Triggering (`Asm/callbacks.h`)

`trigger_callbacks()` drops to user mode to allow pending callbacks to be processed.

```c
#include "Asm/callbacks.h"

/* During a long-running operation */
for (int i = 0; i < 1000; i++) {
    do_work_step(i);
    if ((i % 100) == 0) {
        trigger_callbacks();  /* Allow Wimp tasks and callbacks */
    }
}
```

**Why use this?** Long-running code in SVC mode can prevent the Wimp from processing
callbacks (e.g., TaskWindow events, mouse movements). Dropping to user mode briefly
allows the system to update and respond to user input.

### Wimp_StartTask from SVC (`Asm/starttasksvc.h`)

`svc_wimp_start_task()` safely calls `Wimp_StartTask` from SVC mode by dropping to USR
mode first.

```c
#include "Asm/starttasksvc.h"

unsigned long taskhandle = svc_wimp_start_task("SWidget swidget", 0);
if (taskhandle != 0) {
    /* Task started successfully */
}
```

**Why use this?** `Wimp_StartTask` cannot be called directly from SVC mode because it
triggers a task switch. This function handles the mode switch correctly and returns the
task handle without corrupting the USR mode stack.

## Common Patterns

### Safe Critical Section with IRQ Control

```c
#include "Asm/irqs.h"

void update_shared_data(void) {
    unsigned long flags = ensure_irqs_off();

    /* Atomic update of shared data structure */
    shared_counter++;
    shared_flag = TRUE;

    restore_irqs(flags);
}
```

### Architecture-Specific Code

```c
#include "Asm/processor.h"

void init_hardware(void) {
    unsigned long id = processor_id();

    switch (processor_architecture(id)) {
        case arch_4:
        case arch_4T:
            init_arm7_hardware();
            break;
        case arch_5:
        case arch_5T:
        case arch_5TE:
            init_strongarm_hardware();
            break;
        default:
            init_generic_hardware();
            break;
    }
}
```

### Floating-Point in a SWI call

```c
#include "kernel.h"
#include "Asm/fpsvc.h"

_kernel_oserror *my_filter(_kernel_swi_regs *r, void *wb) {
    fpsvc_buf fpbuf;
    fpsvc_preserve(&fpbuf);

    /* Use floating-point calculations */
    float scale = 1.5f;
    float value = compute_value() * scale;

    fpsvc_restore(&fpbuf);
    return NULL;
}
```

### Long-Running Operation with Callbacks

```c
#include "Asm/callbacks.h"

void process_large_file(void) {
    for (int block = 0; block < total_blocks; block++) {
        process_block(block);

        /* Allow callbacks every 100 blocks */
        if ((block % 100) == 0) {
            trigger_callbacks();
        }
    }
}
```

## Build Notes

* The library is only available for 32-bit builds. There is no 64-bit variant.
    * The `_callx` implementation is already present in the 64-bit C library.
* The standard variant (`libAsm`) is for application use.
* The module variant (`libAsmzm`) is position-independent and safe for ROM inclusion.

## See Also

* **`writing-cmodules`** - For integrating this library into RISC OS modules.
* **`using-makefiles`** - For linking libraries in RISC OS makefiles.
