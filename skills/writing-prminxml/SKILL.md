---
name: writing-prminxml
description: How to use the PRM-in-XML tool, information about the PRM-in-XML format for RISC OS documentation. Use when reading, writing, editing or reviewing API documentation for RISC OS, or when asked to create PRM-in-XML (or PRMinXML) documents). PRM-in-XML should be used for interface and external documentation.
license: MIT
---
# PRM-in-XML

## Summary

PRM-in-XML allows the definition of documents in the style of the Programmer's Reference Manual to be defined in XML.
These XML definitions can then be converted to HTML or other formats for presentation.
They are also intended to be machine readable.

PRM-in-XML should be used for API and interface documentation. If asked to create API and interface documentation, use PRM-in-XML format by default.
Repository and implementation details should not use PRM-in-XML unless explicitly requested - use markdown for those by details.
If asked to create a README.md, always create markdown.

## Tools

* Create a skeleton document: `riscos-prminxml -f skeleton -o <document>.xml`
* Convert the PRM-in-XML document to modern HTML: `riscos-prminxml -f html5+xml -O <directory> <document>.xml`
* Lint the PRM-in-XML document to check for errors: `riscos-prminxml -f lint <document>.xml`
* Help on the tool itself: `riscos-prminxml --help`

Note: Never write the output to the same directory as the input with `-O` - this will overwrite the source files.

## Agent guidance

* After creating or editing a PRM-in-XML document, lint it and then build the HTML version to confirm that the syntax is correct and that there are no logical errors within the document.
* Ensure that the `Overview` section covers the reasons why the component exists, and how it relates to other components.
* Ensure that the `Technical Details` section deals with how the component is used, and the meaning of the interfaces that are present.
* Show the user the generated documentation, when complete, with `host-open output/html`, which will open it in the browser.

## Documentation

The XML format is described in the file: `/riscos-resources/Install/Tools/Linux/riscos-prminxml-resources/docs/PRMinXML.txt`

Guidance on creating documents can be found in: `/riscos-resources/Install/Tools/Linux/riscos-prminxml-resources/docs/HowTo.md`

### DTD Declaration

Use the 1.03 DTD with a public label and URL:

```xml
<!DOCTYPE riscos-prm PUBLIC "-//Gerph//DTD PRM documentation 1.03//EN"
                            "http://gerph.org/dtd/103/prm.dtd">
```

The actual DTD used can be found in: `/riscos-resources/Install/Tools/Linux/riscos-prminxml-resources/gerph/103/prm.dtd`

## Document Structure

The standard section ordering for component documentation:

- Introduction and Overview
- Technical Details
- SWI Calls
- System Variables
- Service Calls
- Vectors
- UpCalls
- Error Messages
- Wimp Messages
- Commands
- Security Issues
- Examples

Remove sections that are not relevant to your component.

### Section Hierarchy

The correct nesting order is:

```
chapter
  └── section
      └── subsection
          └── subsubsection
              └── category
```

**Important:** Each level can only contain the level below it plus `<p>` elements. A `<section>` cannot directly contain a `<category>`.

## Content

The documentation should describe the external interfaces, data structures, commands, services, vectors and events
used by the component. It should not describe internal implementation details of the component.

The metadata section should be updated with each major change. The author of the change should be populated with the user's full name.

### Only Document What the Module Implements

**Guideline:** Do not create `-definition` blocks for SWIs or services that the module merely calls. Only document:

- Service calls that the module handles/intercepts
- SWI calls that the module implements
- System variables that the module defines
- Error messages that the module generates
- Commands that the module provides

SWIs that the module uses internally may be mentioned in the technical details if they are intrinsic to the purpose of the call, but not given definition blocks.

## Content Guidelines

### What to Document

For a RISC OS module, document:

1. **Introduction and Overview** - What the module does
2. **Technical Details** - How it works internally
3. **Service Calls** - Services the module handles (using `<service-definition>`)
4. **SWI Calls** - SWIs the module implements (using `<swi-definition>`)
5. **Memory Usage** - RAM requirements and ROM compatibility
6. **Usage** - How to load, use, and unload
7. **Error Messages** - Errors the module generates (using `<error-definition>`)
8. **Compatibility** - System requirements
9. **Examples** - Usage examples (using `<extended-example>`)

### What NOT to Document

Do not create definition blocks for:

- SWIs that the module calls (mention in technical details instead)
- Service calls that the module issues (not handles)
- Standard RISC OS interfaces the module uses


## Index format

The 'index' format is only intended for advanced users who wish to collect chapters together.
Always check with the user before using this format.

### How to create indexes of multiple documents

For multiple documents, create an index file:

```xml
<?xml version="1.0"?>
<index>
<dirs output="output/html" index="output/index" input="." temp="tmp"/>
<options page-format="html5" catalog-version="103" ... />
<make-index type="swi"/>
<make-index type="service"/>
<section title="Section Name" dir="dir">
    <page href="Document">Document Title</page>
</section>
</index>
```

### How to build all the indexed documents

```bash
riscos-prminxml -f index Index.xml
```

## Common Elements

### Paragraphs and Lists

Use `<p>` for paragraphs. Lists must be wrapped in paragraphs when they appear as section content:

```xml
<p>
  <list type='unordered'>
   <item>First item</item>
   <item>Second item</item>
  </list>
</p>
```

List types are `unordered` or `ordered` (not "bullet" or "numbered").

For complex list item content (including elements like `<userinput>`), wrap the content in a `<p>`:

```xml
<item><p>Text with <userinput>command</userinput></p></item>
```

### Code and User Input

Use `<userinput>` for text the user types or commands. Use `<systemoutput>` for system responses.

For extended code examples, use:

```xml
<extended-example type='asm'>
  Title text
  <br/><br/>
  Description
  <br/><br/>
  <userinput>MOV R0, #0</userinput><br/>
  <userinput>SWI "Example"</userinput>
</extended-example>
```

Valid types include: `shell`, `asm`, `c`, `basic`, `pseudo`, `format`, `unknown`.

## Inline and Miscellaneous Elements

*   `<filename>`: For file paths. Use `type="riscos"` (default), `"unix"`, `"windows"`, or `"uri"`.
*   `<sysvar>`: Inline reference to a system variable name.
*   `<menuoption>`: For GUI menu items.
*   `<actionbutton>`: For GUI buttons.
*   `<fixme>`: Marks areas needing attention; rendered as a warning.
*   `<br/>`: Forced line break (use sparingly).
*   `<image>`: Embeds graphics. Supported types: `png`, `draw`, `svg`.
    ```xml
    <image src="path/to/img.png" type="png" width="100" height="50" caption="Description"/>
    ```
*   `&hex;`: Use this entity for the hexadecimal prefix (e.g., `&hex;8000`) to remain platform-neutral (renders as `&` for RISC OS).

## Entity References

Use XML entities for special characters:

*   `&lt;`: `<`
*   `&gt;`: `>`
*   `&amp;`: `&`
*   `&nbsp;`: Non-breaking space.
*   `&times;`: Multiplication sign (×).
*   `&ne;`: Not equal (≠).
*   `&le;`: Less than or equal (≤).
*   `&ge;`: Greater than or equal (≥).
*   `&micro;`: Micro symbol (µ).
*   `&implies;`: Implies arrow (⇒).
*   `&ellipsis;`: Ellipsis (...).
*   `&lsl;`, `&lsr;`, `&asr;`: Bitwise shifts (<<, >>, >>>).

**Important:** Do NOT double-encode. Use `&lt;` NOT `&amp;lt;`. The XML parser will handle the conversion.

## SWI Definitions

### Basic Structure

SWI definitions require the `name` attribute and optionally `number`:

```xml
<swi-definition name='Example_SWI' number='12345'>
  <entry>...</entry>
  <exit>...</exit>
  <use><p>Description</p></use>
  <example><p><userinput>SWI "Example"</userinput></p></example>
  <related>
   <reference type='sysvar' name='Example$Var'/>
  </related>
</swi-definition>
```

**Important:** SWI numbers are hexadecimal but do NOT include the `&` or `0x` prefix. Use `number='58B00'` NOT `number='&58B00'`.

### Per-reason SWI definitions

SWIs that use a reason code in a register may be documented using separate
`swi-definition` entries, one per reason code. Use the `reason` and `reasonname`
attributes to identify each:

```xml
<swi-definition name='Example_SWI' number='5AC01'
                reason='0' reasonname='Create'
                description='Creates a new object'>
  <entry>
   <register-use number='0'>Reason code</register-use>
   ...
  </entry>
  ...
</swi-definition>

<swi-definition name='Example_SWI' number='5AC01'
                reason='1' reasonname='Close'
                description='Closes an existing object'>
  ...
</swi-definition>
```

The top-level (no `reason` attribute) `swi-definition` for the SWI acts as the
overview entry, documenting the common registers (handle, etc.) and summarising
the reason codes with a `value-table`.

### Register Documentation

Use `<register-use>` with the `number` attribute for registers:

```xml
<register-use number='0'>
  Description of R0
</register-use>
```

**Important:** The `number` attribute should NOT include the `R`, `X`, or `W` prefix. Use `number='0'` NOT `number='R0'`.

However, in text content WITHIN the register description, DO use the prefix:

```xml
<register-use number='0'>
  Flags for the operation. If R1 bit 3 is set...
</register-use>
```

### Referencing a specific reason code

To link directly to a per-reason entry, add `reason='N'` to the `<reference>`:

```xml
<reference type='swi' name='Example_SWI' reason='0'/>
```

Use this in `<related>` blocks of per-reason entries to cross-link the reason
codes to one another.

---

### Pattern: reason-code SWI overview entry

The recommended pattern for a SWI with reason codes is:

1. One top-level `swi-definition` (no `reason` attribute) — documents the
   register layout common to all reason codes and lists all reasons in a
   `value-table` with `use-description='yes'` references.
2. One `swi-definition` per reason code (`reason='N' reasonname='Name'`) —
   documents the reason-specific registers and behaviour.

```xml
<!-- Overview entry -->
<swi-definition name='Example_SWI' number='5AC01'
                description='Performs operations on objects'>
  <entry>
   <register-use number='0'>
    <p>Reason code:</p>
    <p>
    <value-table head-number="Reason" head-value="Action">
     <value number="0"><reference type='swi' name='Example_SWI' reason="0" use-description='yes'/></value>
     <value number="1"><reference type='swi' name='Example_SWI' reason="1" use-description='yes'/></value>
    </value-table>
    </p>
   </register-use>
   <register-use number='1'>Handle ID</register-use>
   <register-use number='2-5'>Dependent on reason code</register-use>
  </entry>
  ...
</swi-definition>

<!-- Per-reason entries follow immediately after -->
<swi-definition name='Example_SWI' number='5AC01'
                reason='0' reasonname='Create'
                description='Creates a new object'>
  ...
</swi-definition>
```

### Service Definition Name Prefix

* Do NOT include the `Service_` prefix in the `service-definition` `name` attribute. The stylesheet adds it automatically.

```xml
<!-- WRONG -->
<service-definition name="Service_ReportError" ...>

<!-- CORRECT -->
<service-definition name="ReportError" ...>
```

### Error definitions

* Error numbers should be in hexadecimal and should include the error base.
* In the documentation error names should use the prefix of the module, not `Err_`.

### Bit Fields

For registers that contain bit flags, use `<bitfield-table>` instead of nested lists:

```xml
<register-use number='0'>
  Flags:
  <bitfield-table>
   <bit number='0-1' name='Mode'>
    <list type='unordered'>
     <item><p>0: Mode A</p></item>
     <item><p>1: Mode B</p></item>
     <item><p>2: Mode C</p></item>
     <item><p>3: Mode D</p></item>
    </list>
   </bit>
   <bit number='2' name='Enable'>
    Enable flag (1 = enabled)
   </bit>
   <bit number='3-31' state='reserved'>
    Reserved
   </bit>
  </bitfield-table>
</register-use>
```

The `state` attribute can be: `reserved`, `content`, `set`, or `clear`.

If the content for bit elements describes the meaning in terms of the 'set' and 'clear' state consistently, use the `state` attribute to indicate each meaning.

## System Variable Definitions

System variables require both `name` and `description` attributes:

```xml
<sysvar-definition name='Example$Var' description='Controls behaviour'>
  <use>
   <p>Detailed description...</p>
  </use>
  <example>
   <p><userinput>Example$Var = value</userinput></p>
  </example>
</sysvar-definition>
```

## VDU Definitions

Similar to commands, but for VDU sequences.
*   Element: `<vdu-definition>`
*   Attributes: `name`, `number` (hex), `description`.
*   The `name` is auto-prefixed with `VDU`.
*   In v1.03, the `<syntax>` block should only document the *additional* parameters following the VDU number.

## Star Command Definitions

For documenting CLI tools and module star commands, use `<command-definition>`.

### Structure
```xml
<command-definition name="CommandName" description="One line description">
  <syntax>
    <!-- Syntax elements -->
  </syntax>
  <parameter name="param_name" switch="s" switch-alias="a">
    Description of the parameter.
  </parameter>
  <use>
    <p>Detailed usage information.</p>
  </use>
  <example>
    <command>*CommandName -s value</command>
  </example>
  <related>
    <reference type="command" name="OtherCommand"/>
  </related>
</command-definition>
```

### Syntax Elements
The `<syntax>` block describes the command line structure using these elements:
*   `<switch name="n">`: A command line switch (auto-prefixed with `-`). Can contain a `<userreplace>` for its value.
*   `<optional>`: Indicates optional parts. Use `alternates="true"` for mutually exclusive options.
*   `<alternates>`: Mutually exclusive elements where one *must* be chosen.
*   `<userreplace>`: Placeholder for user-supplied values (e.g., `<userreplace>filename</userreplace>`).
*   `<text>`: Literal text that must appear in the command.

### Parameters
Use `<parameter>` to define individual arguments or switches:
*   `name`: The name of the parameter (matches `<userreplace>` or a positional argument).
*   `switch`: The switch letter/name (matches `<switch name="...">`).
*   `switch-alias`: An alternative short/long form of the switch.
*   `label`: A label for the parameter (alternative to `name`).

## BNF (Backus-Naur Form)

For complex syntax definitions, use the BNF namespace (`http://gerph.org/dtd/bnf/100/bnf.dtd`). BNF elements are typically used within a `<bnf>` block.

### Elements
*   **`<bnf>`**: Root element for a BNF grammar.
    *   Attributes: `caption` (Description of the grammar).
*   **`<rule-def>`**: Defines a new rule.
    *   Attributes: `name` (Rule name, recommended lower-case).
*   **`<rule-use>`**: Invokes an existing rule.
    *   Attributes: `name` (Target rule), plus [Repetition Attributes](#repetition-attributes).
*   **`<literal>`**: A case-insensitive US-ASCII string.
    *   Attributes: `string`, plus [Repetition Attributes](#repetition-attributes).
*   **`<character>`**: Describes terminal symbols.
    *   Attributes: `base` (`d`=decimal, `x`=hex, `b`=binary), `value` (starting value), `limit` (optional high value for ranges), plus [Repetition Attributes](#repetition-attributes).
*   **`<group>`**: Bundles elements for repetition or alternation.
    *   Attributes: `optional` ("true"/"false"), `alternates` ("true"/"false" for mutual exclusivity), plus [Repetition Attributes](#repetition-attributes).
*   **`<comment>`**: Descriptive text within the BNF block.

### Repetition Attributes
Available on `<rule-use>`, `<literal>`, `<character>`, and `<group>`:
*   `repeat`: "true"/"false" for any number of times.
*   `repeat-min`: Minimum number of repetitions.
*   `repeat-max`: Maximum number of repetitions.

### Core ABNF Rules
Standard upper-case rules from RFC2234 (e.g., `ALPHA`, `DIGIT`, `HEXDIG`, `SP`, `WSP`, `CRLF`) are implicitly available and should be used where appropriate.

## References

Cross-reference other elements using `<reference>`:

```xml
<!-- Reference a service call -->
<reference type="service" name="ReportError"/>

<!-- Reference a SWI call -->
<reference type="swi" name="OS_Byte"/>

<!-- Reference another document -->
<reference type="document" href="OtherDoc.xml" name="Other Document"/>

<!-- Reference an external link -->
<reference type="link" href="https://example.com" name="Example Site"/>
```

Valid types include: `swi`, `sysvar`, `command`, `vector`, `upcall`, `service`, `message`, `entry`, `error`, `document`, `chapter`, `section`, `subsection`, `subsubsection`, `category`, `tboxmethod`, `tboxmessage`.

Use `href='?'` for documents that don't exist yet (will generate a warning).

The stylesheet automatically adds the appropriate prefix (e.g., "Service_", "SWI_") based on the reference type.

### `use-description` on references

The `use-description='yes'` attribute on a `<reference>` element causes the
description of the target to be inlined as the link text, rather than just the
name. This is especially useful inside `value-table` entries to auto-populate
the description of each reason code:

```xml
<value-table head-number="Reason" head-value="Action">
 <value number="0"><reference type='swi' name='Example_SWI' reason="0" use-description='yes'/></value>
 <value number="1"><reference type='swi' name='Example_SWI' reason="1" use-description='yes'/></value>
</value-table>
```

This renders as a table where the description column is the `description`
attribute of the referenced per-reason `swi-definition`.


## Metadata

The `<meta>` section at the end of the document must include:

```xml
<meta>
  <maintainer>
   <email name="Your Name" address="you@example.com"/>
  </maintainer>
  <disclaimer>
   <p>Copyright and license information</p>
  </disclaimer>
  <history>
   <revision number="1" date="25 March 2026" author="ABC" title="Initial version">
    <change>Created documentation</change>
   </revision>
  </history>
  <related>
   <reference type='document' href='?' name='Related Document'/>
  </related>
</meta>
```

Update the `<history>` section with each major change. The `author` should be your initials or identifier. The earliest change should go first, and be followed by later changes - add new change regisions at the end.

The `<meta>` element must appear **after** all `<chapter>` elements, as a direct child
of `<riscos-prm>`. Placing it inside a `<chapter>` causes a DTD validity error.


## Advanced Document Metadata

The `<chapter>` element supports:
*   `docgroup`: Category of documentation (e.g., "Network Protocols").
*   `docgroup-part`: Volume or part number (e.g., "II").


## Common Errors and Solutions

### List not allowed directly in section

**Error:** `Element subsection content does not follow the DTD, expecting (p | ...)`

**Solution:** Wrap lists in `<p>` elements when they appear as direct children of sections or subsections.

### userinput not allowed in item

**Error:** `Element userinput is not declared in item list of possible children`

**Solution:** Wrap the item content in `<p>`:
```xml
<item><p>Text <userinput>code</userinput></p></item>
```

### Double-encoded entities

**Problem:** `&amp;lt;` appears in output instead of `<`

**Solution:** Use `&lt;` in XML, not `&amp;lt;`. The XML parser handles the conversion to HTML entities.

### Invalid register prefix

**Error:** Register `number` attribute has `R` prefix

**Solution:** Use `number='0'` not `number='R0'` in attributes. Use `R0` only in text content.

### SWI number with prefix

**Error:** SWI `number` attribute has `&` prefix

**Solution:** Use `number='58B00'` not `number='&58B00'`. Hex numbers in attributes don't use the `&` prefix.

### Extended Example in Category

**Problem:** Error "Element category content does not follow the DTD, expecting (p | extended-example)*"

**Solution:** Wrap `<extended-example>` in `<p>` tags within categories:

```xml
<!-- WRONG -->
<category title="YAML structure">
  <extended-example type="format">
    content here
  </extended-example>
</category>

<!-- CORRECT -->
<category title="YAML structure">
  <p>
    <extended-example type="format">
      content here
    </extended-example>
  </p>
</category>
```

## Table elements

All table elements (`definition-table`, `value-table`, `offset-table`, `bitfield-table`,
`message-table`, `version-table`) are only valid as children of `<p>`. They cannot appear
directly as children of `section`, `subsection`, `subsubsection`, or `category`.

```xml
<!-- CORRECT -->
<p>
<definition-table ...>
  ...
</definition-table>
</p>

<!-- WRONG - will fail lint -->
<category title="...">
  <definition-table ...>
    ...
  </definition-table>
</category>
```

Note that the `offset` element has an implicit `+` prepended to the `number` field,
so it is not required to include a `+` at the start of its value.

## `definition-table` and `definition`

The `definition-table` is equally useful for
documenting named options, variables, parameters, and configuration values where the key
is a string rather than a number.

### Attributes

`definition-table` attributes:
- `head-name` — heading for the name column (default: `"Name"`)
- `head-extra` — heading for the optional extra column (omit if not using `extra`)
- `head-value` — heading for the description column (default: `"Meaning"`)

`definition` attributes:
- `name` — the term being defined (required)
- `extra` — optional additional column value (e.g. `"Required"`, `"Optional"`, a default value)

### Example: variable reference table

```xml
<p>
<definition-table head-name="Variable" head-extra="Default" head-value="Description">
 <definition name="OPTIMISE" extra="yes">Optimisation level: no, size, time, yes, or max.</definition>
 <definition name="ASD" extra="(unset)">Set to yes to produce a debug build.</definition>
</definition-table>
</p>
```

### `<!ELEMENT definition ANY>` — rich content is allowed

The `definition` element is declared `ANY` in the DTD, which means it may contain any
declared XML content: inline elements (`<userinput>`, `<em>`, etc.), `<list>`, and even
nested `<definition-table>` elements. This makes it possible to document enumerated values
inline:

```xml
<definition name="CLIBTYPE" extra="noc99">Selects the C library variant.
<definition-table head-name="Value" head-value="Effect">
 <definition name="noc99">Small stubs without C99 formatted I/O (default).</definition>
 <definition name="generic">Full stubs with C99 formatted I/O.</definition>
 <definition name="static">Statically-linked ANSILib.</definition>
</definition-table>
</definition>
```

Note: `<list>` elements used inside a `<definition>` do **not** need to be wrapped in
`<p>` because `definition` is declared `ANY` — the `<p>`-wrapping rule only applies in
normal section/category content.

### Useful `extra` column patterns

- Required/optional marker for API parameters: `head-extra="Required"`, values `"Required"` / `"Optional"`
- Default value for configuration variables: `head-extra="Default"`, values like `"yes"`, `"(unset)"`

---

## `value-table` — for numeric values

Use `value-table` when keys are numbers (e.g. error codes, flag values). Use
`definition-table` when keys are strings.

```xml
<p>
<value-table head-number="Value" head-value="Meaning">
 <value number="0">Success.</value>
 <value number="1">Error occurred.</value>
</value-table>
</p>
```

## Conversion from other document formats

When creating a PRM-in-XML file from other documents it is expected that the PRM-in-XML format will be the canonical
format. The source material will usually be abandoned. This means that it is vital that as much information as possible
is transferred to the PRM-in-XML file. It must not be created as a cheat-sheet.

When converting structure definitions into PRM-in-XML, the `offset-table` is the expected way to do so - if C
structures are used, they may be included, but the `offset-table` should be the primary reference format. Structures,
Value lists and BitField tables which are described in the 'Technical Details' section which are referenced in multiple
locations should be enclosed (with any explanatory details) in a `category` element, if they are not already directly
described in one of the section elements. They should use the `reference` links when they are mentioned in subsequent
registers, structures or tables.

Terms used within the document should be explained, and if there are many such terms that are unclear, these
should be introduced in a 'Terminology' section.


## Quick Reference

### Element Usage

| Element | Use For | Notes |
|---------|---------|-------|
| `<chapter>` | Top-level document | Must have `title` attribute |
| `<section>` | Major divisions | Introduction, Technical Details, etc. |
| `<subsection>` | Subdivisions of sections | |
| `<subsubsection>` | Further subdivisions | |
| `<category>` | Topic breaks within text | Not a heading level |
| `<p>` | Paragraphs | Required wrapper for lists |
| `<list>` | Bulleted or numbered lists | `type="unordered"` or `type="ordered"` |
| `<extended-example>` | Code blocks | `type="asm"`, `type="c"`, `type="basic"`, `type="shell"` |
| `<userinput>` | Inline code/commands | |
| `<command>` | Star commands | `*Command` |
| `<systemoutput>` | System responses | |
| `<service-definition>` | Service calls handled | Name without `Service_` prefix |
| `<swi-definition>` | SWIs implemented | Number without `&` prefix |
| `<reference>` | Cross-references | Use appropriate `type` |
| `<fixme>` | Marking a part of the text that needs more work | Put descriptive text about the deficiency within the element |

### Common commands:

- Create skeleton: `riscos-prminxml -f skeleton -o doc.xml`
- Lint check: `riscos-prminxml -f lint doc.xml`
- Build HTML5: `riscos-prminxml -f html5+xml -O html doc.xml`
- Open in browser: `host-open html/doc.html`

## Related Documentation

- [PRM-in-XML Structure Specification](/riscos-resources/Install/Tools/Linux/riscos-prminxml-resources/docs/PRMinXML.txt)
- [BNF Structure Specification](/riscos-resources/Install/Tools/Linux/riscos-prminxml-resources/docs/BNF.txt)
- [Official How To Guide](/riscos-resources/Install/Tools/Linux/riscos-prminxml-resources/docs/HowTo.md)
