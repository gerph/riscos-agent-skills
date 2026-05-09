---
name: riscos-filesystem
description: Information about how to interact with the RISC OS filesystem. Use when RISC OS filesystem operations are not clear, or when writing code which interacts with the RISC OS filesystem.
license: MIT
---

# RISC OS Filesystems information

## Filename conventions

* Directory component separators are `.` - this is similar to the `/` separator on POSIX systems.
    * A trailing `.` is not allowed on a filename.
    * A leading `.` is not allowed on a filename.
* RISC OS does not use filename extensions.
    * Where compatibility or interworking is expected, the filename may include the equivalent of an extension in the form `/html` on the end of the filename.
* Filetypes differentiate the purposes that files have.
    * Files have a type (the `filetype`), which is a value from 0-0xFFF, usually expressed as a 3 hex-digit value, or a name.
    * Directories do not have filetypes.
* The root specifier for a filesystem is `$` which is treated as a component: `$.Foo` would be a file `Foo` within the root of a device.
* The current working directory (knowns a the `currently selected directory`, or `CSD`) may be referenced as `@`: `@.Foo` is the file `Foo` within the current directory.
* `%` is the library directory, `&` is the 'user root directory' and `\\` is the previously selected directory. These are not commonly used.
* Different filesystem drivers have separate prefixes within filenames, which may include a disc specifier.
    * `ADFS::Disc1.$` is the root of the disc labelled `Disc1` on the ADFS driver's devices.
    * `ADFS:$` is the root of the currently selected ADFS device's disc.
    * `Parallel:$` is the parallel device's root.
* Filenames, device names and disc names are case-insensitive, using the current RISC OS alphabet as the translation. UTF-8 is generally not used.
* Environment variables are expanded by the filesystem, not by the caller.
    * A filename `<Boot$Dir>.Run` is valid, and will be expanded by the filesystem by extracting the value of the `Boot$Dir` variable and substituting it for the `<...>` region.
    * Variables may appear anywhere in a filename: `<Boot$Dir>.Choices.<User$Name>.Start` would expand both the `Boot$Dir` and `User$Name` variables before using the filename.
* Pseudo filesystems can be created through the use of path variables. These are variables which specify multiple filename paths which will be searched by the filesystem to resolve a candidate.
    * Path variables have the form `Name$Path`, and will be expanded when a path is given like `Name:$.Foo` or `Name:Foo`.
    * The value of path variables is a comma-separated list of paths to search, each of which is terminated by a `.`.
    * If `Name$Path` was set to `ADFS::4.$.Name.,RAM::Disc.$.Another.` and a filename like `Name:$.Foo` was supplied, the filesystem will search for `ADFS::4.$.Name.Foo` and `RAM::Disc.$.Another.Foo`. The first found object will be further traversed.
    * Writing to filenames speicifed in this way will cause the `Name$Write` variable to be used in place of the path as a directory. For example, if `Name$Write` was set to `RAM::Disc.$.Another.` and a write operation was performed on `Name:$.Foo` the write will always happen on `RAM::Disc.$.Another.Foo`, even if a file named `Foo` exists on the ADFS path.
* The parent directory `^` can be used within paths to traverse up the directory tree.
    * `ADFS::Disc1.$.This.That.^` will resolve to `ADFS::Disc.$.This`.
    * The parent of the root is the root, that is `$.^` is the same as `$`, and `ADFS::Disc.$.^` is the same as `ADFS::Disc.$`.
* Components who are supplied filenames should not try to decompose them, or decode their values. The filenames should be passed on directly to filesystem interfaces. Errors returned by the interfaces will indicate whether the filename is valid and whether a target filename could be resolved.
* Within RISC OS filenames, `*` is a multicharacter wildcard, `#` is a single character wildcard.
* Files have properties known as 'load' and 'exec' addresses. These are legacy from 8-bit era, but have been repurposed to hold information about the file's timestamp and its filetype.
    * However, there are encodings which do not refer to a timestamp and instead directly expose the load and exec addresses as values. These are to be avoided but may be encountered.
* Access permissions on files allow for read access, write access and locking.
    * These are applied for the current user, and 'other' users, usually specified in the for `LWR/WR` (left side being the current user, and right side being other users).
    * Locked files may not be deleted.
    * Files without the read or write permission will not be able to be read or written respectively.
* File enumeration does not guarantee any ordering.
    * Whilst some filesystems will enumerate objects in a sorted order, others may be random, or may return items in creation order. The order returned should never be relied upon.
* File enumeration never includes the 'current' or 'parent' in its returned values.


## Host filename convention

When RISC OS files are stored on a host filesystem, they are given special treatment:

* Filenames are encoded using UTF-8 from the RISC OS Alphabet by the RISC OS filesystem. The host filesystem only deals in UTF-8.
* Root specifiers (`$`) are never used on the host filesystem.
* Filetypes are encoded within the filename as a suffix `,xxx` where `xxx` is a 3-hex digit sequence for the filtype number, left padded with `0`s.
    * A RISC OS filename of `$.Foo.Bar` which has a filetype of 0xFFD would be stored in the host filesystem as `Foo/Bar,ffd`.
* Timestamps for the file are taken from the host filesystem's 'modification' time and implicitly encoded into the load and exec address by RISC OS implementations.
* Where load and exec addresses do not encode the filetype, but are in legacy format, these are encoded in the host filesystem as `,llllllll,eeeeeeee`.

## Filetypes

* Common filetypes you may need to know (used in filenames in the form `,xxx`):
    * `fff` - Text file (plain text, no defined encoding, but usually ISO 8859-1)
    * `ffd` - Data file (arbitrary data)
    * `ff8` - Absolute (user mode executable, usually in C)
    * `ffc` - Utility (user mode executable for small operations, usually in assembly)
    * `ffa` - Module (relocatable priviledged system extension, usually written in C, but historically in assembly)
    * `fd1` - Textual BASIC (user mode executable in textual format)
    * `ffb` - Tokenised BASIC (user mode executable in binary format)
    * `ff9` - RISC OS Sprite (collection of bitmap images)
    * `fec` - RISC OS Template (collection of desktop window definitions)
    * `feb` - RISC OS Obey file (script containing RISC OS commands to execute)
    * `fe1` - RISC OS AMU file ('Acorn Make Utility' - a makefile format)
    * `aff` - RISC OS DrawFile (vector graphic)
    * `a91` - Zip archive (collection of compressed files, which may include RISC OS filetype information)
    * `b60` - PNG graphic
    * `c85` - JPEG graphic
    * `695` - GIF graphic
