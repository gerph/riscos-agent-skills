---
name: designing-modules
description: How to design modules for RISC OS. Use when creating new modules, designing interfaces to modules, porting a library to be used in a new module, or extending the existing interfaces of modules.
license: MIT
---
# Module design for RISC OS

Modules are the building blocks of RISC OS, providing relocatable, privileged system extensions. Modern module design emphasizes extensibility, hardware abstraction, and robust interface standards that allow different components to interoperate seamlessly.

## Agent procedure

Do not start implementation immediately.

1. Gather requirements for the module
   - module name
   - purpose and expected usage
   - interfaces required (may come from the existing module)
2. Define a basic summary of the module and the interfaces in text.
   - Present interfaces to the user.
   - Offer suggestions for other interfaces that may be useful, or functionality that is missing.
3. Confirm with the user that this is acceptable, or whether changes are required.
4. Create a PRM-in-XML document to describe the interface, with a description of the intent and interfaces.
5. Confirm with the user that this is acceptable, or whether changes are required.
6. Once explicitly confirmed, you may begin implementation *IF* the user requests that you do so.

When implementing the module work on groups of interfaces, rather than trying to
implement the entire system in one go. Introduces tests as soon as feasible.

### Workflow Guidance

* Start with a short text design before writing PRM-in-XML. Include the proposed
  SWIs, register use, parameter blocks, ownership rules, error model, and any
  extension points.
* Ask explicit questions for choices that affect the ABI, such as who owns
  buffers, whether the module allocates memory, whether data structures are
  opaque, and whether advanced use cases need separate SWIs.


## Core Design Principles

*   **Modularity & Interworking:** Modules should be designed as "mix-and-match" components. They must adapt to the presence (or absence) of other modules.
*   **Encapsulation:** Public SWI interfaces should never expose internal pointers or ephemeral state. Data passed by the user should be copied if it needs to persist beyond the call.
*   **Extensibility:** Design for the future by reserving bits in flags and using "Magic Words" to identify extended data blocks.
*   **Hardware Abstraction:** Prefer using Vectors for hardware-specific logic. This allows the OS or other modules to intercept or provide drivers for the hardware while maintaining a unified API.

## SWI Interface Patterns

SWI calls are the primary API for modules. Each module has up to 64 SWIs, usually prefixed with the module name. The SWI base will need registration - during design pick a random base within the range `&C0000` - `&FFFC0` and mark the SWI base number as `; UNALLOCATED` in the CMHG file.

### Buffer Length Negotiation
Modern APIs must handle variable-length data gracefully. The standard pattern for buffer management is:
1.  **Request Size:** The caller passes `0` (or a null pointer) for the buffer and/or buffer length.
2.  **Return Size:** The SWI returns the required size (usually in the same register).
3.  **Buffer Overflow:** If the provided buffer is too small, the SWI should return a "Buffer Overflow" error and set the length register to the **negative** of the required size.

*Example:* `ImageFileRender_Info` and `PathUtils_EnumeratePath` use this pattern.

### Opaque Enumeration Contexts
When enumerating items (shares, files, devices), use an opaque context value (commonly in **R4** or **R1**):
*   **Start:** Caller passes `0` to start the enumeration.
*   **Iteration:** The SWI returns the next context value to use for the subsequent call.
*   **End:** The SWI returns `-1` when enumeration is complete.

### Flag Usage & Reserved Bits
*   **R0 as Flags:** It is common for R0 to contain flags. If any of the SWI interfaces use R0 for flags, ALL the SWIs should use flags in R0. Do *not* put the flags in another register, unless the user explicitly requests it.
    * Avoid a generic flags subsection if individual SWIs have different flag meanings.
*   **Reserved Bits:** Documentation must specify that reserved bits "must be zero" to ensure forward compatibility.
*   **Interpretation Changes:** Flags can change how other registers are interpreted (e.g., `ShareFS_IdentifyShare`).
*   **Default Values:** Use `0` to represent "automatic" or "system-preferred" settings.


### Reason-Coded Multiplexing
For modules with many related functions, group them under a single SWI using a "Reason Code" (usually in **R0**).
*Example:* `ZeroConf` and `RTCV` use reason codes for Control/Status or Read/Write operations.

### Magic Identifiers
To safely pass format-specific or renderer-specific extension data, use 32-bit "Magic Word" identifiers to prevent misinterpretation of private data blocks.

Avoid exposing library-internal data formats as public ABI. Use names such as
"opaque workspace block" and document that callers must not inspect or depend
on the contents.

### Interface Complexity

* Keep simple and advanced interfaces separate when the common case can be much
  easier than the full control surface. A simple SWI can wrap multiple advanced
  steps using defaults.
* If the caller may build data incrementally, consider whether an append/update
  operation should be part of the interface rather than forcing callers to gather
  all input before a single call.
* Split subtly different output formats into distinct enumeration values. For
  example, a sprite file containing a sprite and a single sprite without the
  sprite area header should be separate formats.


### Buffer and ownership conventions

* Prefer caller-supplied output buffers for predictable ownership. Document each
  output as a buffer pointer and buffer length pair.
* Document the exact size-query and overflow convention used by the interface.
  Do not assume every module should use the same sign convention for the
  required size; follow the user's requirement or the local component convention.
* If a SWI returns a variable sized opaque block, put the block's size in the
  block itself when this simplifies later calls.
* State whether input pointers are retained. Public interfaces should normally
  copy data that must persist after the SWI returns.
* On append/update operations, document whether failure leaves the existing
  block unchanged.

### Returning information
* If raw bitmap or image data is returned, provide a way to discover its
  dimensions, stride/alignment if relevant, and byte count. Returning width and
  height in registers is often simpler than requiring callers to parse output.

## Asynchronous & Desktop Interaction

### 1. Non-blocking Operations
For long-running tasks (networking, slow I/O), modules should not stall the system.
*   **Status Codes:** The module returns a "Pending" status, and the caller polls for completion.
*   **Wimp Pollwords:** For Wimp applications, a module can set bits in a memory location (the "Pollword") provided by the application. This allows the Wimp to wake the task only when data is ready (`Reason_PollWordNonZero`).
*   **Inter-module Notification:** Use **UpCalls** to notify other modules of background events. Note that user-mode applications cannot generally trap UpCalls.

*Example:* `EasySocket` uses Pollwords to notify applications of network activity without constant polling.

### 2. Desktop (Wimp) Integration
*   **Polled Status:** Applications typically poll the module via a "Status" SWI to update their UI.
*   **Front-ends:** Modules may have an application front-end that handles configuration and issues notifications based on module state changes.
*   **Task-local Storage:** Avoid storing state tied to a task unless necessary. If needed, ensure it is cleaned up if the task dies.

## Filters, Hooks, and Traps

### 1. Vector Trapping
To intercept or modify system behavior (like filesystem calls), modules "claim" or "examine" vectors.
*   **Pre/Post Trapping:** Modules can pass calls down the vector chain or intercept them entirely.
*   **Limitations:** While powerful, trapping (e.g., `DDEUtils` trapping FS vectors) can be deficient if the API expects atomic operations or specific state that the trapper cannot perfectly replicate.

### 2. Specialized Filter Managers
Some subsystems provide explicit "Filter" interfaces (e.g., `FilterManager`, `Toolbox`, `ColourPicker`).
*   **Event Modification:** Filters are used to intercept Wimp events and modify them (e.g., the Toolbox converting raw Wimp events into higher-level Toolbox events).
*   **Interface Hijacking:** The `ColourPicker` design is a classic (though now rare) example of using filters to manage a complex desktop interface.

## Resource Management & Localization

### 1. MessageTrans & Internationalization
*   **Message Files:** Modules should use `MessageTrans` to look up localized strings. Open the message file during initialization and cache it.
*   **Localizing Errors:** Errors should be looked up from the message file at the point of failure to provide the correct language to the user.

### 2. ResourceFS & $Path Variables
*   **Location:** Store resources (icons, templates) in **ResourceFS**.
*   **Access Pattern:** Access resources via `<ModuleName>:<FileName>`.
*   **Customization:** If the module needs to look elsewhere, it should check `Resources:$.Resources.<ModuleName>.<FileName>`.
*   **Path Variable:** Define a system variable `<ModuleName>$Path`. This allows developers to redirect resource lookups to a physical disc during development or customization.

## Data Structures & Arithmetic

### Standard Blocks
*   **Transformation Matrices:** Standard 6-word block (m00-m21).
*   **Scale Blocks:** Standard 4-word block (X/Y mul/div).

### Fixed-Point Arithmetic
*   **16.16:** Common for angles and matrix elements.
*   **24.8:** Common for translations and coordinates.

## Module and interface errors

Errors should be defined as part of the SWI interface design, to ensure that the callers
of the module are able to determine what the failure is by the error number. The error number base will be defined in the CMHG file and will need to be registered. Start out with a random base number between `&800000` - `&FFFFFF` with a granularity of 256, and mark this in the CMHG file with a `; UNALLOCATED` comment.

* Use existing standard error numbers where appropriate, such as the standard
  Buffer Overflow error, instead of allocating module-specific equivalents.

* Define module-specific errors for invalid parameters, bad opaque blocks, data
  that cannot be represented, and temporary allocation failure.

## Allocations

Allocations for module names, SWI bases, error bases, services, *Commands and many other constants may be required. At the end of the design phase, ask the user if they
wish to register their module resources. Use the `allocating-resources` skill to do this.

## Documentation Standards

* Always use **PRM-in-XML** to define SWIs, Services, and *Commands. This ensures consistency and allows for the automatic generation of headers and documentation.
* If the introductory section needs it (if the content covers more than a few paragraphs) split introductory material into:
  * `Introduction`: what the module provides and why it exists.
  * `Overview`: domain concepts a caller needs before reading the SWI details.
* `Technical Details` should document how to use the interface, parameter blocks, sequences, and data formats.
* Define domain terminology that may be ambiguous in RISC OS documentation. For
  example, in QR code documentation "module" means a square cell of the QR
  matrix, which is distinct from a RISC OS relocatable module.
* Add a "Typical sequences" subsection for common use cases. List the SWIs in
  the order callers should use them.
* Include external references in the overview or metadata when a public standard,
  canonical documentation, or project repository helps explain the interface.

## References & Examples

### Networking
*   **ShareFS:** [Interface for sharing files and interaction](https://gerph.github.io/riscos-prminxml-staging/prm-modern/html/select/networking/sharefs.html)
*   **ZeroConf:** [Recent interface for network configuration](https://gerph.github.io/riscos-prminxml-staging/prm-modern/html/select/networking/zeroconf.html)
*   **EasySocket:** [Example of Asynchronous/Pollword usage](https://raw.githubusercontent.com/gerph/riscos-make-a-module/refs/heads/master/EasySocket.xml)

### Graphics & UI
*   **ImageFileRender:** [Registration manager for image renderers](https://gerph.github.io/riscos-prminxml-staging/prm-modern/html/select/graphics/imagefilerender.html)
*   **DrawFile:** [Interface for rendering RISC OS DrawFiles](https://www.riscos.com/support/developers/prm/drawfile.html)
*   **ColourPicker:** [Filter-based desktop interface](http://www.riscos.com/support/developers/prm/colpick.html)

### System & Logic
*   **PathUtils:** [Interface for path manipulation and enumeration](https://gerph.github.io/riscos-prminxml-staging/prm-modern/html/select/programmer/pathutils.html)
*   **MessageTrans:** [Standard localization and message management](http://www.riscos.com/support/developers/prm/messagetrans.html)

### Hardware & Vectors
*   **RTCV:** [Vector interface for clock operations](https://gerph.github.io/riscos-prminxml-staging/prm-modern/html/select/time/rtcv.html)
*   **FanController:** [Interface for managing hardware fans](https://gitlab.gerph.org/notriscos/gerph/fancontroller/-/raw/master/FanController/prminxml/fancontroller.xml)
