# workflow.js Refactor Plan

## Context

`order/static/order/js/workflow.js` (~1450 lines) is a monolithic jQuery script
loaded as a single classic `<script>` tag from
[order/templates/order/workflow.html](../../../templates/order/workflow.html).
There is no bundler/build step and no ES module system — everything runs in
one global scope. A separate, likely-related file exists at
`/static/js/rte/workflow.js` (referenced from
`apps/rte/templates/rte/workflow.html`) that has not yet been compared against
this one for duplicated logic.

## Problems Identified

- **Implicit globals everywhere.** Many variables (`ram`, `disk_rate`,
  `database`, `managed_windows`, `currStep`, `tabs`, `wfid`, etc.) are assigned
  without `var`/`let`, so they leak into `window` and are shared across
  unrelated features. This makes the file fragile to reorder or split.
- **No test coverage.** There is no JS test harness in the repo. The only
  verification path is manual smoke testing per workflow type.
- **Many distinct workflow branches** driven by `wfid`/`reviewPages`/
  `modifyPages` arrays, each with different tab visibility rules — these need
  to be enumerated and manually verified after any change.
- **Dead/undefined reference:** `updateDisplayConditions` is called at the
  bottom of the file (`DOMContentLoaded` and `change` listeners) but is never
  defined in this file. Needs investigation — either it's defined in another
  script loaded on the same page, or it's dead code that silently no-ops
  (calling an undefined function would actually throw, so this should be
  confirmed before relying on current behavior).
- **Feature logic is interleaved** in a single `$(document).ready(...)` block
  instead of being organized by concern.

## Why a Split Is Feasible

Most handlers already use event delegation:
`$(document).on(event, selector, fn)`. This means a handler is inert on any
page where its target selector doesn't exist in the DOM. Because of this,
the file can be split into multiple independently-loadable files without
needing conditional includes per template — every split file can be safely
loaded on every page that currently loads `workflow.js`.

## Feature Clusters Found in the File

| Cluster | Representative functions/handlers |
|---|---|
| Wizard / tab navigation & validation | `nextPrev`, `validateForm`, tab `shown.bs.tab`/`show.bs.tab` handlers, `#nextBtn`/`#prevBtn` clicks |
| Review & submission | `saveReviewData`, `fillReviewForm`, `sendTabData` (AJAX tab submit) |
| Cost calculator | `update_total_cost`, disk UOM change handlers, `.cost-driver` change |
| Disk formset management | `addDisk`, `deleteDisk`, `#id_form-*` handlers |
| MiServer provisioning | `set_managed_windows`, `set_dedicated_server`, `get_db_type`, `set_server_name`, DB-type/backup/reboot-window handlers |
| Phone / softphone / Zoom | `#id_phoneCategory`, `#id_zoomRoom`, radio-driven `data-phoneset`/`data-tab` visibility toggles |
| Chartfield / chartcom (OCC) | `chartcomChange`, `filterChartcom`, `useSameShortCode` |
| Host/volume/subscription modify actions | `addHost`, `addRow`, `modifyVolume`, `modifySubscription` |

## Phased Plan

### Phase 1 — Safety net (no code changes)
Write a manual smoke-test checklist covering each `wfid` branch
(`reviewPages`, `modifyPages`, the "Test Workflow" `wfid == 32` path, and the
`server_id` query-param "Special Server Modify" path), plus the MiServer,
phone/Zoom, and disk-cost flows. This is the regression suite until real
automated tests exist.

### Phase 2 — Stop the global leaks
Wrap the existing file contents in an IIFE and add missing `var`/`let`
declarations to variables that are currently implicit globals, **without
moving any code**. This is a small, mechanically-diffable change that makes
later splitting safe, and can be verified with the Phase 1 checklist.

### Phase 3 — Split into feature files
Break the file into separate files along the clusters above, e.g.:

- `workflow-core.js` — wizard/tab navigation, `validateForm`, `nextPrev`,
  `saveReviewData`, `fillReviewForm`, `sendTabData`
- `workflow-cost.js` — `update_total_cost`, disk add/delete/cost handlers
- `workflow-miserver.js` — managed/dedicated server, DB type, server naming,
  backup/reboot window logic
- `workflow-phone.js` — phone category, Zoom, radio-driven visibility
- `workflow-chartcom.js` — chartfield/OCC logic

Each file keeps its own delegated `$(document).on(...)` handlers. Any
genuinely cross-cutting state (`currStep`, `tabs`, `wfid`, `lastStep`) moves
into one small shared object (e.g., `Workflow.state`) so files depend on an
explicit contract instead of implicit globals.

### Phase 4 — Template wiring
Update [workflow.html](../../../templates/order/workflow.html) to include the
split files in dependency order. Investigate whether
`apps/rte/templates/rte/workflow.html` / its `workflow.js` duplicates any of
this logic and should be reconciled at the same time.

### Phase 5 — Optional modernization
Once split, consider ES modules (`type="module"`) or a bundler for
import/export and dead-code elimination. Not required for the split itself
and should only be pursued if there's appetite for build-tooling changes.

## Open Questions

- Does `/static/js/rte/workflow.js` duplicate logic from this file, and
  should the two be reconciled/shared?
