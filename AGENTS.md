# AGENTS.md

Context for AI coding agents (Claude Code, Junie, Codex, ...) working on aquaPCB.

## Project

aquaPCB is the Raspberry Pi base board for [aquaPi](https://github.com/schwabix-1311/aquaPI),
open hardware under CERN-OHL-S v2. [README.md](README.md) is the source of truth for the spec,
pin map, design decisions and roadmap. [BOM.md](BOM.md) lists the parts and
[COMPARISON.md](COMPARISON.md) compares the board with Robo-Tank and Leviathan.

- `kicad/` - KiCad project (schematic sheets, `aquaPCB.kicad_pcb`, project footprint and 3D libraries).
- `kicad-v1/` - read-only copy of the v1 KiCad project (tag `v1.0.1`) for side-by-side viewing
  while v2 is developed in `kicad/`. Never edit it; see `kicad-v1/README.md`.
- `tools/` - the retired schematic generator. Don't run it: the schematic is hand-edited now.

## Hardware vs. software sessions

aquaPCB and aquaPi are worked on in **separate agent sessions**:

- The **hardware session** starts in `~/aquaPCB` and owns this repository.
- The **software session** starts in `~/aquaPI` and owns the aquaPi repository (code, ROADMAP).

Only edit files in this repository. When hardware work needs a change in aquaPi (ROADMAP entry,
driver, board profile, port names), ask the software session or the user - don't edit aquaPi
files and don't run git commands there. Reading aquaPi for context is fine.

## Working with the KiCad files

- The `.kicad_sch` / `.kicad_pcb` files are hand-edited by the user in KiCad. Before touching
  them, check `git status`, the lock files (`*.lck`; KiCad open means unsaved work may exist)
  and `kicad/.history`. Make minimal, surgical edits, or ask the user to make the change in
  KiCad.
- After schematic changes, compare the connectivity (netlist) with the last verified state, and
  run ERC/DRC with `kicad-cli` (`sch erc`, `pcb drc`). v1: both clean. v2 (`kicad/`): ERC clean,
  DRC without errors - the deliberate ADC socket courtyard overlap is waived by a custom rule in
  `kicad/aquaPCB.kicad_dru`; the remaining warnings are silkscreen only.
- Read the board origin from `Edge.Cuts`; don't assume coordinates.

## Branches and versions

- `main` - current work: v2 (Robo-Tank v3 compatible head unit), layout complete 2026-10-23.
- `release/v1` - v1 as a restart point if v2 is dropped. Tags: `v1` (finished layout),
  `v1.0.1` (doc fixes). Fixes that are valid for v1 are committed on `release/v1`, tagged
  there, and merged into `main` with a real merge. v2-only changes go to `main` only.
- Never rewrite or force-push history, and never move tags that are already pushed.

## Commits

- Commit or push only when the user explicitly asks.
- Commit messages are English, short, and name the area (`README: ...`, `kicad: ...`, `BOM: ...`),
  with the agent's co-author trailer.
- Don't commit KiCad backups, lock files, caches or local history (see `.gitignore`).
