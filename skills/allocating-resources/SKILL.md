---
name: allocating-resources
description: Guidance for registering RISC OS allocations with the RISC OS Open allocation service. Use when the user wants to register a module name, SWI chunk, error block, *command, filetype, system variable, or any other RISC OS allocation. Also use when the user asks "how do I register X", "I need to allocate X", or wants to send an allocation request to RISC OS Open.
license: MIT
---

# RISC OS Allocation Service

## Overview

RISC OS maintains a central registry for resources that must not clash between software
authors. The allocation service is run by RISC OS Open.

- **Allocation email address**: `allocate@riscosopen.org`
- **Preferred method**: Use the `!Allocate` desktop application to create a structured request
  file, then attach it to an email. Since `!Allocate` cannot be run in this environment,
  send an email directly describing the resources needed.
- **When to allocate**: Before publicly releasing any software that uses the resource.

**Response time**: RISC OS Open aim to respond within **5 working days**.

**Important**: The allocations service can be slow or unresponsive. If no reply has been
received after one week, resend — forward the original email with a brief note explaining
it is a resend.

**What allocation does NOT cover**: The service does not check for trademark, copyright,
patent, or other IPR issues. That remains the requester's responsibility.

## Step-by-Step Process

### 1. Identify what needs registering

If invoked with a project in context, examine the project to determine what allocations
are needed:

- Check the CMHG file (`cmhg/*`) for the module title, SWI chunk base, and error base
- Check the source files for any `*Commands`, service calls, system variables, or filetypes
- Check `VersionNum` or `Makefile,fe1` for the project name if not otherwise clear

If invoked without project context, ask the user:
- What software or resource needs registering?
- Which type(s) of allocation are required? (Use the table below.)
- Is a specific value already in use that should be formalised, or is a fresh allocation needed?
- Is there any documentation (e.g., a URL) describing the interface?

### 2. Ask how to deliver the email

Ask the user: **"Would you like the email written to a text file, or displayed on screen?"**

- **File**: write to `allocate-request.txt` in the current directory (or a name the user prefers)
- **Screen**: display the full email text in the conversation

### 3. Gather sender details

Ask for, or read from context:
- The user's full name
- The user's email address

These are needed for the `From:` header and the closing signature.

### 4. Compose the email

Structure the email as plain text:

```
To: allocate@riscosopen.org
From: <Full Name> <<email address>>
Subject: <brief description of the allocation request>

<Body>

-- 
<Full Name>
```

**Subject line**: Keep it short and factual. Describe what is being requested.
Examples:
- `Module registration: ExampleModule`
- `Filetype allocation for YAML`
- `SWI chunk request: ExampleRenderer`
- `System variable allocation: Sys$Example`

**Body**: Be clear and direct. State what is being requested and why. For each item, use the
terminology from the table of allocation types below. If a specific value is already in use,
state it. If any value will do, say so.

Example body for a module:

```
I would like to register the following allocations for a new module:

Module name: ExampleModule
SWI chunk (64 SWIs) and name prefix: ExampleModule
Error block (256 errors): required

*Commands provided:
    ExampleCmd
    ExampleStatus

Documentation: https://example.org/prm/examplemodule.html
```

Example body for a filetype:

```
I would like to allocate a filetype for YAML files. YAML is a human-readable
data serialisation format. JSON is allocated as &975 and XML as &980; a similar
&fxx range would be appropriate.

If a filetype has already been allocated, please let me know the number.
```

*NEVER* suggest numbers for SWI bases, error numbers or services. These will always be allocated from a pool.

### 5. Deliver and inform

After producing the email, tell the user:

- **Send to**: `allocate@riscosopen.org`
- **Expected response**: within 5 working days
- **If no response after one week**: resend the email by forwarding the original with a brief
  note at the top, such as: *"Resending this request as I have not received a reply."*

## Resending

When composing a resend, forward the original message and add a short note:

```
To: allocate@riscosopen.org
From: <Full Name> <<email address>>
Subject: <original subject> (resend)

Resending this request as I have not received a reply.

<any corrections or updates since the original, if applicable>

---------- Forwarded message ----------
<original email in full>
```

## Complete Table of Allocatable Resources

The following is taken from the official RISC OS Open allocation page
(https://www.riscosopen.org/content/allocate). The `!Allocate request type` column shows
the terminology used by the `!Allocate` application; use the same terms in the email where
relevant.

| Allocation | !Allocate request type | Restrictions on name | Case-sensitive? | Included with allocation |
|---|---|---|---|---|
| Message_DeviceClaim device number | Devices | — | Yes | — |
| DrawFile object type | Draws object block | — | Yes | — |
| DrawFile tagged object type | Draws tag block | — | Yes | — |
| Error block (256 errors) | Error block | — | Yes | — |
| Filetype | Filetype | ≤ 8 chars | No | File$Type_XXX, Alias$LoadTypeXXX, Alias$PrintTypeXXX, Alias$@RunType_XXX, Wimp sprites file_XXX, small_XXX |
| Filing system number and name | Filing system | — | No | Block of 256 error numbers |
| Wimp message block (64 messages) | Messages | — | Yes | — |
| Expansion card ID | Podule | — | Yes | — |
| Application or shared resource directory | Reservation (AppName) | unlimited; first 9 chars must be unique | No | AppName$*, Wimp sprites !AppName, sm!AppName, ic_AppName, Choices:AppName |
| File in Devices:$ | Reservation (DeviceFS) | — | No | — |
| System variable | Reservation (EnvVar) | must include at least one `$` | No | — |
| Font name | Reservation (FontName) | — | No | — |
| Module name | Reservation (ModName) | — | No | ModName$*, $.Resources.ModName, BootFirmware:ModName |
| Directory in ResourceFS | Reservation (ResourceFS) | — | No | — |
| Directory in Wimp$ScrapDir | Reservation (ScrapDir) | — | No | — |
| Star command | Reservation (StarComm) | — | No | — |
| Utility name | Reservation (Transient) | — | No | — |
| Sprite name in Wimp sprite pool | Reservation (WimpSprite) | ≤ 12 chars | No | — |
| Service call block (64 service calls) | Service block | — | Yes | — |
| SWI chunk (64 SWIs) and name prefix | SWI chunk | — | Yes | Wimp message numbers in same range |
| Toolbox gadget type number | SWI chunk | — | Yes | Toolbox events in same range |
| Toolbox object class number | SWI chunk | — | Yes | Toolbox events in same range |
| Buffer | (email only) | — | Yes | — |
| CMOS RAM byte | (email only) | — | Yes | — |
| Econet port number | (email only) | — | Yes | — |
| Ethernet driver suffix | (email only) | 1-char exhausted; keep short | No | — |
| Environment handler | (email only) | — | Yes | — |
| Event | (email only) | — | Yes | — |
| Filing system option (`*Opt`) | (email only) | — | No | — |
| Freeway type number | (email only) | — | Yes | — |
| Keyboard type (KeyV) | (email only) | — | No | — |
| Monitor type | (email only) | — | No | — |
| Pointer type (PointerV) | (email only) | — | No | — |
| Printer driver | (email only) | typically 2 chars | No | — |
| Printer dumper | (email only) | typically 2 chars | No | — |
| Printer type number | (email only) | — | No | — |
| Reason codes to vectors (including vectored SWIs) | (email only) | — | Yes | — |
| Service calls and SWIs in system range (0–&FF) | (email only) | — | Yes | — |
| Territory, country, alphabet, keyboard | (email only) | — | Yes | — |
| UpCall block (256 UpCalls) | (email only) | — | Yes | — |
| Vector | (email only) | — | Yes | — |
| Wireless driver suffix | (email only) | 1–2 chars preferred; keep short | No | — |

Resources without a `!Allocate request type` must be requested by email only, describing
the resource in plain terms.

## Notes on Common Patterns

### Typical module requiring SWIs

Most modules need:
- Module name (`Reservation (ModName)`)
- SWI chunk and name prefix (`SWI chunk`)
- Error block (`Error block`)
- Any `*Commands` (`Reservation (StarComm)` for each)

### Module without SWIs

A module that only provides commands and claims a service call may only need:
- Module name
- Error block (if it raises errors)
- Star command names

### Filetype

State the format name, what it contains, and any relationship to existing types. Ask whether
a filetype is already allocated before requesting a new one.

### System variable

State the full variable name (must contain `$`), the format of its value, when it is set,
and who sets it.
