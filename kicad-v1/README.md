# kicad-v1 - read-only reference copy of v1

Copy of the KiCad project in `kicad/` as of tag `v1.0.1`, so v1 can be opened side by side
while v2 is developed in `kicad/`. ERC and DRC are clean (0 violations, schematic parity OK).

- **Don't edit these files.** v1 changes belong on branch `release/v1` (and are merged into
  `main`); this copy is only refreshed from there.
- The footprint and 3D model libraries are project-relative (`${KIPRJMOD}`), so this directory
  opens on its own in KiCad. Both projects are called `aquaPCB`; the window title path tells
  them apart.
- Refresh after a v1 fix:
  `git rm -r -q kicad-v1 && git archive <v1 tag> kicad | tar -x --transform 's|^kicad|kicad-v1|'`,
  then restore this README.
