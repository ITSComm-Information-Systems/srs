# workflow.js Manual Smoke Test Checklist

Phase 1 safety net for the [workflow.js refactor](WORKFLOW_REFACTOR.md). No
automated JS tests exist for this file, so this checklist is the regression
suite to run before and after each refactor phase. `Action` records (and
their `id`, `use_cart`, `use_ajax`, `steps`) are managed in Django admin under
`order > Actions` — look up the current action names for the ids below there,
since they're data-driven and not hardcoded in code/templates.

## How to use this checklist

1. Run through every row **before** starting a refactor phase and note actual
   behavior (baseline).
2. Re-run the same rows **after** the phase and confirm no regressions.
3. Any discrepancy blocks the phase from being considered done.

## 1. Core wizard navigation (`wf/<action_id>`)

- [ ] Loading `/orders/wf/<id>` for a normal (non-cart, non-ajax) action:
  first pill tab is shown, all other pills are disabled/greyed out.
- [ ] Clicking "Next" on a valid step advances to the next visible tab and
  enables its pill.
- [ ] Clicking "Next" on an invalid step (missing required field) keeps you
  on the step and shows validation state (`was-validated`, invalid fields
  highlighted).
- [ ] Clicking "Previous" goes back a step; "Previous" is hidden on step 1.
- [ ] Clicking a disabled pill tab does nothing (navigation blocked).
- [ ] On the last step, the "Next" button label changes to "Submit Now"
  (`use_cart == False`) or "Add to Cart" (`use_cart == True`), and clicking
  it submits/redirects correctly.
- [ ] Progressive-disclosure fields (`data-sequence`/`data-condition`)
  reveal in order as prior questions are answered, and re-answering an
  earlier question hides/clears later ones.

## 2. `wfid`-specific branches

Confirm the actual current action ids in Django admin before testing — the
lists below are from the source at the time of writing.

- [ ] **Review-only pages** (`wfid` in `[50, 56, 61, 63, 66, 72, 73]`): first
  pill, all `<p>`/`<h2>` text, and the "Next" button are hidden on load.
- [ ] **Modify pages** (`wfid` in `[47, 49, 53, 55, 59, 60, 62, 65, 70, 71]`):
  "Next" button is hidden on load (page relies on AJAX tab submission /
  in-place actions instead).
- [ ] **Test workflow** (`wfid == 32`): all pill tabs are enabled/clickable
  immediately, bypassing normal step-locking.
- [ ] **Special server modify** (URL has `?server=<id>` query param): page
  jumps straight to the `volumeSelection` tab/step 4, `#instance_id` is
  pre-filled, `sendTabData()` fires automatically, and the
  `volumeSelection` tab link itself is hidden.

## 3. AJAX tab submission (`use_ajax == True`)

- [ ] Clicking "Next" disables the button and calls `sendTabData()` instead
  of client-side `nextPrev(1)`.
- [ ] Successful AJAX response swaps in the next tab's HTML
  (`[data-pane="..."]`), enables its pill, and shows it.
- [ ] AJAX response with `valid: false` keeps the user on the current tab
  and does not advance.
- [ ] AJAX response with a `redirect` value navigates the browser away.
- [ ] AJAX error response shows the `#results` alert box with the error
  message.

## 4. Cost calculator (server/disk provisioning tabs)

- [ ] Changing RAM (`#id_ram`) updates `#ram_cost` and total cost.
- [ ] Changing a disk's UOM between GB/TB updates that disk's size
  min/max/step correctly and recalculates its cost.
- [ ] Toggling "Replicated" vs "No replication" (`#replicated_0`) changes
  the disk rate used and recalculates total.
- [ ] Toggling "Backup" (`#backup_0`) adds/removes backup cost based on
  total disk size.
- [ ] Adding a disk (`addDisk`) inserts a new row, renumbers SCSI ids, and
  recalculates total cost; only the last delete (minus) button stays
  visible per your reading of the "keep second-to-last visible" logic.
- [ ] Deleting a disk (`deleteDisk`) removes the row, decrements
  `TOTAL_FORMS`, and recalculates total cost.
- [ ] For CPU/server type, changing CPU count auto-bumps RAM to `cpu * 2`
  if RAM was lower, and recalculates cost.

## 5. MiServer provisioning tab

- [ ] Selecting "Managed" vs "Unmanaged" shows/hides the OS dropdown vs
  the non-managed textbox, and marks the correct one required.
- [ ] Selecting a Windows OS under "Managed" reveals the prefix
  Yes/No question and, if "Yes", the registered-prefix field.
- [ ] Selecting a Linux OS forces disk 0 to 50 GB and makes it read-only.
- [ ] Server name preview (`#id_name`) updates correctly for: PCI-flagged
  server (prefix `p-`), database server (`db-`/`-ora`/`-<db>` suffix),
  managed Windows non-PCI server (prefix from registered prefix or
  `MIS-`).
- [ ] Choosing a DB type (MySQL/MSSQL/Oracle) sets a sane default disk
  size and enforces the type's minimum when size is edited below it.
- [ ] "Sensitive data" or "SQL Agent Jobs" (MSSQL) or size > 50 forces
  `dedicated` shared-server checkbox to checked/read-only.
- [ ] Reboot day = "No Reboot Needed" hides the reboot time field;
  otherwise it's shown/enabled.
- [ ] Choosing a backup time disables reboot/patch time options that
  fall within 2 hours of it (including wraparound across midnight).

## 6. Phone / softphone / Zoom tab

- [ ] Selecting phone category "LN-STAFF"/"LN-FACULTY" shows the Uniqname
  field; other categories hide and clear it.
- [ ] Selecting "LN-CONFRM"/"OTHER" shows the Zoom Room question;
  selecting "OTHER" also shows the "other softphone category" field.
- [ ] Zoom Room = "Yes" shows the Zoom Room Name field.
- [ ] Radio value `basic`/`advanced`/`voip` toggles the correct
  `data-phoneset` panel and shows/hides Restrictions, SelectFeatures, and
  zoomOptions tabs as expected.
- [ ] PCI radio (`yes_pci`/`no_pci`) restricts/unrestricts phone category
  options and forces/unforces `LN-HYLAFAX`.
- [ ] "Existing phone" yes/no toggles PhoneLocation vs LocationNew tabs
  and SelectFeatures/Restrictions visibility correctly.
- [ ] Active phone yes/no toggles PhoneLocation vs LocationNew similarly.
- [ ] Analog vs VoIP IP fax radio toggles IPFaxInfo/2Chartfields vs
  LocationNew/Restrictions/4Chartfields tabs.
- [ ] "Buy equipment" yes/no shows/hides the Equipment tab.

## 7. Chartfield / OCC (one-time charges)

- [ ] Selecting a chartcom option updates the linked chart value field for
  that row.
- [ ] Checking "use same code" (`useSameCode<tabid>`) copies the OCC
  chartcom/value to all other chartcom rows and disables them; unchecking
  re-enables them.
- [ ] Filtering chartcom by department (`filterChartcom`) shows only
  matching `data-dept` options.

## 8. Review step

- [ ] On the final step of a cart-based action, the review tab lists every
  prior step's answered fields with correct labels (including the special
  cases: Speed Call, Voicemail, Optional, Subscriber ID, product name +
  zcode).
- [ ] `#reviewSummary` hidden field is populated with the tilde/caret
  delimited summary text used on submit.

## 9. Volume / subscription modify actions

- [ ] `modifyVolume(0, id)` pre-fills `#instance_id`, hides
  `volumeSelection` tab, and calls `sendTabData()`.
- [ ] `modifyVolume(1, id)` (delete flag) additionally hides
  nfsAccess/detailsNFS/detailsCIFS/storageBilling tabs, enables the last
  pill, and posts `volaction=Delete`.
- [ ] `modifySubscription` behaves the same way for
  backupDetails/storageBilling tabs.
- [ ] `addHost` / `addRow` clone the "new" template row, show it, hide the
  original "new" placeholder, and focus the new node-name field.

## 10. Known open issue to verify

- [ ] Confirm whether `updateDisplayConditions` (wired to
  `DOMContentLoaded` and `change` at the bottom of the file) is defined by
  another script loaded on these pages, or throws/no-ops today. Record the
  actual current behavior before refactoring so it isn't accidentally
  "fixed" or broken.
