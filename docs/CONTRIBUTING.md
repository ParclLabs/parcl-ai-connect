# Contributing to Parcl AI Connect

We welcome contributions! Whether it's a new use case, an improvement to an existing skill, or a bug fix.

## Adding a New Use Case

1. Create a directory under `use-cases/<your-use-case>/`
2. Add a `README.md` explaining the use case, what it produces, and the basic vs advanced paths
3. Add a `basic/PROMPT.md` with a self-contained copy-paste prompt
4. Optionally, create an advanced skill under `.claude/skills/<skill-name>/`

## Creating a Skill

1. Create a directory: `.claude/skills/<skill-name>/`
2. Add a `SKILL.md` with required frontmatter:

```yaml
---
name: skill-name          # kebab-case, max 64 characters
description: What it does  # Under 250 characters, front-load the key use case
user-invocable: true
argument-hint: "[args]"
allowed-tools: Read, Grep, ...  # Restrict to what the skill needs
---
```

3. Add reference docs and examples in subdirectories as needed
4. Update the root README.md skill table

## Naming Conventions

- Directories: `kebab-case`
- Markdown files: `kebab-case.md` (except `SKILL.md`, `PROMPT.md`, `README.md`, `CLAUDE.md`)
- Data files: `snake_case` acceptable (CSVs, images)
- Skill names: `kebab-case`, verb-noun for actions (e.g., `competitor-analysis`)

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b add/my-use-case`
3. Run `npx markdownlint-cli2 '**/*.md'` to lint
4. Open a PR against `main` with:
   - Description of the use case
   - Example invocation
   - Any MCP tools used

## Code of Conduct

Be respectful, constructive, and focused on making real estate data more accessible.
