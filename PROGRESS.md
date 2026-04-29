# Trails — Build Progress

> Auto-updated by Claude Code after each completed task.

**Plan:** `docs/superpowers/plans/2026-04-29-stacker.md` (18 tasks, 3 phases)
**Worktree:** `.worktrees/build` · Branch: `feature/build`

---

## Phase 1 — Python Engine

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1 | Project scaffold + data models | ✅ Done | `engine/models.py` — FrameRecord, StackJob, StackOptions, StackResult |
| 2 | IPC helpers (stdin/stdout JSON) | ✅ Done | `engine/ipc.py` — send_event(), read_command() |
| 3 | File loader | ✅ Done | `engine/loader.py` — scan_folder(), sort_frames(), EXIF reading |
| 4 | Stacking methods (lighten/maximum/average/comet) | ✅ Done | `engine/methods/` — 4 blend functions |
| 5 | Gap fill method | ✅ Done | `engine/methods/gapfill.py` — two-pass gap interpolation (per-pixel index arrays) |
| 6 | CPU backend + pipeline orchestrator | ✅ Done | `85fc64d` — CPUBackend, streaming pipeline, gapfill path, hot-pixel reduction |
| 7 | Exporter + filename generation | ✅ Done | `d378983` — export_result(), generate_filename(), JPEG/PNG/TIFF support |
| 8 | Server (stdin/stdout dispatcher) | ✅ Done | `16191b5` — scan_folder, start_stack, export handlers; 37 tests passing |

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

- Tasks 1–5 reviewed: spec compliant + code quality approved
- Quality notes to address in Task 17: lazy imports in loader.py, SUPPORTED_EXTENSIONS duplication in conftest.py, unconstrained `by` param in sort_frames, gap fill edge-case tests (trailing gap, single frame, threshold boundary)
- Tasks 6–8 implemented by Codex (OpenAI) in ~4 min; commits made manually after sandbox git restriction
- Full test suite: **37 passed** as of Task 8 completion
- Permissions: `.claude/settings.local.json` has `defaultMode: bypassPermissions` — restart Claude Code to activate
