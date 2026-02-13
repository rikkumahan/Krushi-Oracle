# Directives

This directory contains Standard Operating Procedures (SOPs) written in Markdown. Each directive defines **what to do** for a specific task.

## Purpose

Directives are the instruction set for the orchestration layer (the AI). They specify:
- Goals and expected outcomes
- Required inputs
- Which execution scripts to use
- Expected outputs and where they go
- Edge cases and learnings from past runs

## Creating New Directives

Use `_template.md` as a starting point:
1. Copy the template: `cp _template.md new_directive.md`
2. Fill in all sections
3. Reference scripts from `execution/` that this directive uses

## Living Documents

Directives evolve. When you discover:
- API constraints or rate limits
- Better approaches
- Common errors and fixes
- Timing expectations

**Update the directive.** This is the self-annealing process—the system gets smarter over time.

## Naming Convention

Use descriptive, action-oriented names:
- `scrape_website.md`
- `generate_report.md`
- `sync_to_sheets.md`
