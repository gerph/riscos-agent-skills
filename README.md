# Agent skills for RISC OS

When developing for RISC OS it is useful to give the AI agents sufficient
information to be able to drive the system. This repository contains an
extract from the [RISC OS Build Environment](https://hub.docker.com/r/gerph/riscos-build)
of the skills that are used there. It is intended that it be available to
others to use if they wish, or to contribute to if they create new skills
which are useful.

## Summary

Skills are definitions of how to perform certain actions which are commonly needed by AI
agents.
They don't comprise full information on a topic, but provide enough guidance to aid an AI
system to diagnose problems, follow procedures or perform certain tasks.

Within a project these skills are usually defined with the configuration directory for
the AI coding agent. For example:

* Qwen skills are held in: `.qwen/skills/`
* Claude skills are held in: `.claude/skills/`
* Gemini skills are held in: `.gemini/skills/`
* Codex skills are held in: `.agents/skills/`

Each skill is given a simple name for the directory, and contains a file `SKILL.md` which
describes the skill, with a short header. Other resources may also be stored in this directory
to help the skill with specific tasks.

More information on building these skill files can be found at [AgentSkills.io](https://agentskills.io/home).

## Skills

The following skills are provided:

* `using-bbcbasic`: Helps with the BASIC syntax, common usage and integration with RISC OS.
* `using-makefiles`: Helps with the build system's makefiles.
* `using-stronghelp`: Helps with the management of StrongHelp files.
* `using-cmhg`: Helps with the creation of CMHG files.
* `using-tooltester`: Helps with working with the golden test (expectation test) tool `riscos-tooltester`.
* `writing-cmodules`: Helps with the development, debugging and testing of modules in C.
* `writing-pymodules`: Helps with the development, debugging and testing of modules in Pyromaniac PyModules, particularly porting to and from C.
* `writing-prminxml`: Helps with creating documentation using PRM-in-XML.
* `riscos-re`: Helps with RISC OS reverse engineering.
* `riscos-commands`: Helps with using RISC OS commands.
* `riscos-output`: Helps with using RISC OS output (VDU, OS_Plot, Draw, Fonts, ColourTrans).

## Installation in Claude

This repository also provide a plugin marketplace for Claude. Add the marketplace to Claude and then enable the RISC OS skills plugin.

```
/plugin marketplace add gerph/riscos-agent-skills
/plugin install riscos-skills@riscos-agent-skills
/reload-plugins
```

### Plugin updates

Auto-update can be enabled by running `/plugin` and navigating to Marketplaces > riscos-skills-plugin and enabling auto-update. Each time Claude starts, any updates to the plugin will be automatically installed.

Or update manually using:

```
/plugin marketplace update riscos-skills-plugin
/reload-plugins
```

## Installation in Codex

This repository can also be used as a Codex plugin. The skill content is the
same; Codex discovers it through the `.codex-plugin/plugin.json` manifest at
the repository root.

To install it for your user account:

```bash
mkdir -p ~/plugins ~/.agents/plugins
ln -sfn /absolute/path/to/riscos-agent-skills ~/plugins/riscos-skills
```

Create or update `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "local",
  "interface": {
    "displayName": "Local Plugins"
  },
  "plugins": [
    {
      "name": "riscos-skills",
      "source": {
        "source": "local",
        "path": "./plugins/riscos-skills"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Coding"
    }
  ]
}
```

If you already have a marketplace file, append the `riscos-skills` entry instead
of replacing the whole file. Restart Codex after updating the marketplace.

## Installation in Gemini CLI

This repository is compatible with Gemini CLI's Agent Skills and Extensions system.

### As an Extension (Recommended)

Installing as an extension allows Gemini to automatically discover and use these skills whenever you are working on a RISC OS project.

```bash
gemini extensions install https://github.com/gerph/riscos-agent-skills
```

### As Agent Skills only

If you prefer to only install the individual skills without the full extension package:

```bash
gemini skills install https://github.com/gerph/riscos-agent-skills
```

Once installed, Gemini will automatically prompt to activate relevant skills (like `writing-cmodules` or `using-bbcbasic`) when it identifies a RISC OS task.
