# Trails — Build Progress

> Auto-updated by Claude Code after each completed task.

**Plan:** `docs/superpowers/plans/2026-04-29-stacker.md` (18 tasks, 3 phases)
**Worktree:** `.worktrees/build` · Branch: `feature/build`

---

## Phase 1 — Python Engine

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1 | Project scaffold + data models | ✅ Done | `6184ebd` — FrameRecord, StackJob, StackOptions, StackResult + round-trip tests |
| 2 | IPC helpers (stdin/stdout JSON) | ✅ Done | `182845a` — send_event(), read_command() |
| 3 | File loader | ✅ Done | `d567304` — scan_folder(), sort_frames(), EXIF reading |
| 4 | Stacking methods (lighten/maximum/average/comet) | ✅ Done | `073f7d8` — 4 blend functions |
| 5 | Gap fill method | ✅ Done | `763ca35` — two-pass gap interpolation (per-pixel index arrays) |
| 6 | CPU backend + pipeline orchestrator | ✅ Done | `85fc64d` — CPUBackend, streaming pipeline, dark frame, hot-pixel reduction |
| 7 | Exporter + filename generation | ✅ Done | `d378983` — export_result(), generate_filename(), JPEG/PNG/TIFF |
| 8 | Server (stdin/stdout dispatcher) | ✅ Done | `16191b5` — scan_folder, start_stack, export, cancel handlers |

## Phase 2 — Swift Shell

| # | Task | Status |
|---|------|--------|
| 9  | Xcode project setup | ⬜ Pending |
| 10 | IPC types + AppState model | ⬜ Pending |
| 11 | EngineClient (subprocess + IPC) | ⬜ Pending |
| 12 | ContentView + FolderPickerView | ⬜ Pending |
| 13 | FrameListView + range selector | ⬜ Pending |
| 14 | SettingsPanelView | ⬜ Pending |
| 15 | PreviewPaneView + StackProgressView | ⬜ Pending |

## Phase 3 — Integration

| # | Task | Status |
|---|------|--------|
| 16 | Dev launch path (env vars + script) | ⬜ Pending |
| 17 | Full Python test suite pass | ⬜ Pending |
| 18 | End-to-end smoke test | ⬜ Pending |

---

## Notes

- Tasks 1–8 implemented and code-reviewed; all fixes applied
- **Test suite: 61 tests passing** (up from 37 after review fixes)
- Code review findings addressed (`ee52741`, `0e8e67b`):
  - `gapfill.py`: logic rewritten — interpolation path now actually fires (was unreachable)
  - `server.py`: cancel now works during stacking (background thread + `_cancel_event`)
  - `server.py`: stale `_pending_result` cleared at start of each stack
  - `server.py`: `.npy` temp file deleted after loading; process joins thread on exit
  - `pipeline.py`: hot-pixel reduction implemented via Pillow `MedianFilter`
  - `pipeline.py`: `preview_every_n_frames=0` no longer crashes (clamped to 1)
  - `loader.py`: `p.is_file()` guard added to exclude directories with image-like names
  - `ipc.py`: `read_command()` skips blank lines instead of crashing
  - New tests: preview cadence, gapfill branch, dark frame, hot pixel, crop, TIFF,
    unknown format, cancel, full stack→export pipeline, stale result clearing
- Tasks 6–8 initially implemented by Codex in ~4 min (git writes blocked by sandbox; committed manually)
- Permissions: `.claude/settings.local.json` has `defaultMode: bypassPermissions`
