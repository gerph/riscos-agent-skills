# CMHG command-keyword-table Reference

Use `command-keyword-table:` to describe the `*Commands` exported by a module and the C entry point that receives those commands.

```cmhg
command-keyword-table: <default-handler>
   CommandName(<field>: <value>, <flag>:, ...)
```

The first item after the directive is the default C handler. Every command in the table uses that handler unless its entry has a `handler:` field. CMunge also accepts `-` as the default handler when the table only contains `handler:` entries or `no-handler:` help-only entries.

At least one command entry must follow the handler. Entries can be separated by commas or whitespace and may be continued over several lines.

## Handler Interface

The default handler and any per-command handler have this shape:

```c
_kernel_oserror *command(const char *arg_string, int argc, int number, void *pw);
```

`arg_string` is the raw command tail, after any `gstrans-map:` processing. `argc` is the number of parsed arguments. `number` is the zero-based index of the command in the table. `pw` is the module private word.

For `*Help`, `*Configure`, and `*Status`, CMHG/CMunge may call the handler with special `arg_string` values defined in the generated header:

| Invocation | `arg_string` value | Expected action |
| --- | --- | --- |
| `*Help` | `help_PRINT_BUFFER` | Write zero-terminated help text into the supplied buffer and return the initial `arg_string`, or return `NULL` to print nothing. |
| `*Configure` syntax query | `arg_CONFIGURE_SYNTAX` | Print syntax and return `NULL`. |
| `*Status` | `arg_STATUS` | Print current status and return `NULL`. |
| `*Configure <value>` | normal argument string | Apply the configuration and return `NULL`, an error pointer, or a generated `configure_*` status value. |

## Command Entry Format

A command entry is:

```cmhg
CommandName(field: value, flag:, ...)
```

All fields are optional. An empty field list, as in `ModuleCommand()`, creates a command with default argument limits and no generated help or syntax strings.

| Field | Meaning |
| --- | --- |
| `min-args: <n>` | Minimum accepted argument count. Default is 0. |
| `max-args: <n>` | Maximum accepted argument count. Default is 0. Use 255 for commands that accept an open-ended tail. |
| `gstrans-map: <bits>` | Bit mask selecting arguments to pass through GSTrans before the handler sees them. Bit 0 is the first argument, bit 1 the second, and so on. |
| `fs-command:` | Filing-system-specific command. It is only used when this module is the current filing system. |
| `international:` | Treat `help-text:` and `invalid-syntax:` as tokens in the `international-help-file:` messages file. |
| `add-syntax:` | Append `invalid-syntax:` to `help-text:` when help is printed. |
| `configure:` | Mark the name as a `*Configure`/`*Status` command. |
| `status:` | Equivalent to `configure:`. Some existing headers use both. |
| `help:` | Requests calls for help handling. Existing headers contain this for some OS command tables, but current CMunge documentation marks it unsupported. Avoid it in new tables unless matching existing generated behaviour is required. |
| `invalid-syntax: <string>` | Syntax text, or a messages token when `international:` is present. |
| `help-text: <string>` | Help text, or a messages token when `international:` is present. |
| `handler: <function>` | CMunge per-command handler. Overrides the default handler for this command. |
| `no-handler:` | CMunge help-only command. No command code is generated for execution. Useful with a `-` default handler. |

Flag fields end in `:` and have no value, for example `international:, add-syntax:`. The comma after the final field or final command is optional in the examples in this source tree, but use a trailing comma only when another command follows.

## Common Patterns

Simple table using one default handler:

```cmhg
command-keyword-table: Mod_Command
   ModuleCommand(min-args: 0, max-args: 0)
```

Several simple commands, keeping names and argument fields aligned:

```cmhg
command-keyword-table: Mod_Command
   ROMModules(       max-args:   0, min-args:  0, international:),
   RMEnsure(         max-args: 255, min-args:  2, international:),
   RMLoad(           max-args: 255, min-args:  1, international:),
   Modules(          max-args:   0, min-args:  0, international:)
```

Command with generated help and syntax:

```cmhg
command-keyword-table: Mod_Command
   CommandCache(min-args: 0, max-args: 2,
                help-text: "*CommandCache is used to control the caching of absolute files.\r",
                add-syntax:,
                invalid-syntax: "Syntax: *CommandCache [-permanent | -temporary | -remove <filename>] [-dump] [-flush] [-auto on | off]")
```

Per-command handlers, useful when the command set is large or already split into separate C functions:

```cmhg
command-keyword-table: Mod_Command
   Cat(handler: Cmd_Cat),
   Info(handler: Cmd_Info),
   Copy(handler: Cmd_Copy,
        add-syntax:,
        help-text: "Copy one or more objects.",
        invalid-syntax: "Syntax: *Copy <source spec> <destination spec> [<options>]")
```

Help-only command table:

```cmhg
command-keyword-table: -
   DiagnosticDump(help-text: "The DiagnosticDump module records output from C programs which exited abnormally.",
                  no-handler:)
```

Filing-system and configure commands:

```cmhg
command-keyword-table: command_handler
   Bye(min-args: 0, max-args: 0, fs-command:,
       help-text: "*Bye closes all files and unsets all directories.",
       invalid-syntax: "Syntax: *Bye"),
   CDROMBuffers(min-args: 1, max-args: 1, status:, configure:,
                help-text: "*Configure CDROMBuffers sets the buffer size.",
                invalid-syntax: "Syntax: *Configure CDROMBuffers <power of two>[K]")
```

Internationalised commands:

```cmhg
international-help-file: "Resources:$.ThirdParty.Module.Messages"

command-keyword-table: main_command
   LoadModeFile(min-args: 1, max-args: 1, international:,
                invalid-syntax: "LoadModeFileSyntax",
                help-text: "LoadModeFileHelp")
```

## Layout Advice

Keep the directive and default handler on the first line. Put command entries on following indented lines unless there is exactly one short command.

For a small table, use one command per line:

```cmhg
command-keyword-table: main_commands
   CDDevices(min-args: 0, max-args: 0),
   CDUnlock( min-args: 0, max-args: 1)
```

For a large table with many similar entries, align the opening parenthesis and the `min-args`/`max-args` columns. This makes omissions obvious during review:

```cmhg
command-keyword-table: Mod_Command
   Time(               max-args:   0, min-args:  0, international:),
   Error(              max-args: 255, min-args:  1, international:),
   FX(                 max-args:   5, min-args:  1, international:)
```

For commands with help text or several flags, put each field on its own continuation line. Align continuation fields under the first field, not under column 1:

```cmhg
command-keyword-table: Mod_Command
   FilePlay(min-args: 0, max-args: 5,
            invalid-syntax: "Syntax: *FilePlay [-buffersize <n bytes>] [-file <file name>] [-stop]\r",
            help-text: "*FilePlay allows playback of various sound files\r"
                       "Syntax: *FilePlay [-buffersize <n bytes>] [-file <file name>] [-stop]\r")
```

Prefer a stable field order within a file. A practical order is:

```text
handler, min-args, max-args, gstrans-map, fs-command/configure/status,
international, help-text, add-syntax, invalid-syntax, no-handler
```

If the local file already uses a consistent order, follow that local order instead.

Avoid very long single-line command entries. Long help strings are easier to maintain when split with C-style string concatenation in preprocessed CMHG files, or with explicit `\r`, `\n`, and `\t` escapes where the existing file style uses them.

Avoid leading commas inside the command parentheses in new code. Some old headers contain forms such as `Command(, min-args: 0, ...)`, but this is untidy and makes the field list look accidental.

When using `international:`, keep `help-text:` and `invalid-syntax:` short token names, not user-visible English. The actual text belongs in the Messages file named by `international-help-file:`.

Use `no-handler:` only for real help-only commands. For commands that should execute, either provide a default handler or set `handler:` explicitly.
