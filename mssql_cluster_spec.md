# MSSQL Cluster Ordering Specification

## Purpose

Enable authorized DBA team members to order a two-node MSSQL cluster in SRS for SQL Enterprise workloads moving from physical hardware to VMware. An order creates one cluster TDX ticket and two standard MiServer TDX tickets, with server records and disks represented in SRS.

## Scope

- Add an order category named **MSSQL Cluster**, visible only to the DBA team.
- Collect cluster-level, server-level, and shared disk configuration.
- Create the cluster ticket and the two associated MiServer tickets.
- Create or update the two corresponding MiServer records, including their disks and shared data-sensitivity details.
- Support post-order disk additions, removals, size extensions, and disk-label edits through SRS.

## Access and Ownership

- Only members of the DBA team may view and submit MSSQL Cluster orders.
- Set the MiServer MCommunity admin group to `its mssqldba`.
- Use `its.mssqldba@umich.edu` as the support email and `734-822-7754` as the support phone.
- Assign the cluster TDX ticket to VCI.

## Cluster Naming

The requester supplies a four-character identifier comprising environment, instance type, and a two-digit sequence. SRS generates the cluster name and both hostnames.

| Component | Input | Meaning |
| --- | --- | --- |
| Environment | `t`, `n`, or `p` | Test, non-production, or production |
| Type | `d` or `a` | Database or SSAS |
| Sequence | `01`-`99` | Instance sequence |
| Datacenter | Assigned by SRS | `m` for MACC; `a` for ASB |

Naming templates:

- Cluster: `db-{env}{type}{seq}-c`
- Primary MACC host: `db-{env}{type}{seq}-cm1`
- Secondary ASB host: `db-{env}{type}{seq}-ca1`

Example for input `td01`:

- Cluster: `db-td01-c`
- Primary server: `db-td01-cm1`
- Secondary server: `db-td01-ca1`

The requester must not be able to edit the generated cluster name or hostnames. Validate the input components and reject sequences outside `01`-`99`.

## Order Fields

| Field | Behavior |
| --- | --- |
| Cluster name | Generated from the naming rules above. |
| Primary server | Generated MACC hostname; datacenter is MACC. |
| Secondary server | Generated ASB hostname; datacenter is ASB. |
| Application | Required free-text value; example: `eResearch`. |
| Production status | Derived from environment. Production uses 24/7 on-call; test and non-production use Business Hours Only (BHO) on-call. |
| Instance type | Derived from type: `d` becomes `Database`; `a` becomes `SSAS`. |
| VM cluster | Set to `mssqlcluster`. |
| CPU | DBA-provided value. |
| Memory | DBA-provided value, with no 64 GB approval limit. |
| Windows version | Required dropdown with `2022` and `2025`. |
| Daily OS backup time | DBA selects from the existing MiServer OS backup-time choices. The same selected time applies to both servers. |
| Additional details | Free text, replacing the label “Purpose.” |
| Shortcode | Collect using the existing MiServer shortcode behavior. |
| Data sensitivity | Use the existing MiServer/MiDatabase sensitivity choices and validation. Apply the selected values to both MiServer records. |

## Cluster Disks

Cluster disks are shared cluster configuration and must not include system disk 0. System disks remain part of the individual MiServer records, following the existing MiServer behavior.

Support any number of cluster disk rows; do not impose the current MiServer form's four-disk limit, if applicable.

| Disk field | Behavior |
| --- | --- |
| SCSI controller | Dropdown. For Database, allow controllers `1`, `2`, and `3`. For SSAS, allow controllers `1` and `3`. Update the choices when instance type changes. |
| Device ID | DBA-entered numeric device ID. IDs start at `0`; device ID `7` is reserved and must not be allowed. Validate that an ID is nonnegative and unique for its selected controller. |
| Disk label | Optional DBA-entered text. Blank values are allowed. Editable after the cluster is ordered. |
| Disk size | DBA-entered size in GB. Support increasing the size after ordering. |

After ordering, DBAs must be able to add cluster disks, remove cluster disks, extend existing cluster disks, and edit disk labels through SRS. Preserve the relationship between each disk and its cluster when changes are submitted.

## Cluster Data Model

Persist each ordered cluster as a dedicated MSSQL Cluster model. This model is the source of truth for cluster-level configuration and lifecycle, separate from either MiServer record.

- Store the generated cluster name and the environment, instance type, and sequence used to generate it. Cluster names must be unique.
- Store the application, VM cluster, CPU, memory, Windows version, shared daily OS backup time, shortcode, additional details, and other submitted cluster-level values.
- Associate exactly two MiServer `Server` records with each cluster: one primary MACC server and one secondary ASB server. Retain each server's role and datacenter association.
- Associate cluster disk records with the MSSQL Cluster model. Each cluster disk stores its controller, device ID, optional label, and size in GB.
- Enforce that a server cannot be assigned to more than one cluster, and that a cluster has no more than one primary and one secondary server.
- Expose the cluster relationship and **Part of cluster** status in the MiServer admin view.

Cluster disks are distinct from each MiServer's system disk and are managed as cluster-owned disk records. They must remain associated with the cluster when added, edited, extended, or removed after ordering.

## MiServer Record Defaults

Create two MiServer records using the existing server-ordering conventions and populate each record from the cluster order. Set the following values on both records unless otherwise noted:

- Turn billing off.
- Enable disk replication.
- No reboot needed.
- Not public-facing.
- Technical-team consultation: No.
- MCommunity admin group: `its mssqldba`.
- Database type/instance type: derived from the requester's `d` or `a` selection.
- Production status, on-call, CPU, memory, Windows version, support contacts, shortcode, and data sensitivity: copied from the submitted order.
- Daily OS backup time: the same selected time on both servers.
- Primary host datacenter: MACC; secondary host datacenter: ASB.

Use the existing MiServer and ServerDisk data conventions wherever they represent the requested values. Do not create a cluster-level system disk; retain each host's normal MiServer system disk.

## Patch Windows

Set the patch day and time independently for each host based on the order environment:

| Environment | Primary MACC host | Secondary ASB host |
| --- | --- | --- |
| Production (`p`) | Sunday at 2:00 AM; use 3:00 AM if 2:00 AM is not an available choice. | Sunday at 5:00 AM. |
| Test or non-production (`t` or `n`) | Thursday at 2:00 AM; use 3:00 AM if 2:00 AM is not an available choice. | Thursday at 5:00 AM. |

Use the existing MiServer patch-day and patch-time choice sets. The selected daily OS backup time must be at least two elapsed hours from each server's scheduled patch event. Check the closest occurrence of the daily backup relative to each patch event, including when the schedules cross midnight. Reject any selection that violates this minimum with a clear validation message.

## Ticketing and Order Lifecycle

Submitting an order creates:

1. One cluster TDX ticket assigned to VCI.
2. One standard MiServer TDX ticket for the primary MACC server.
3. One standard MiServer TDX ticket for the secondary ASB server.

The cluster ticket is a coordination ticket. It does not require a TDX workflow. VCI manually closes it after both MiServer tickets are complete. Do not change the existing workflow behavior of the MiServer tickets.

The three tickets must be associated with the same SRS order and retain enough information to identify the cluster, both generated hostnames, the selected application and instance type, and the cluster disk configuration. A failure creating any required ticket or record must be reported and must not leave the order in an ambiguous partially-submitted state.

The ticket outcomes and ownership above remain in scope. Detailed TDX form, payload, and attribute mapping are outside the scope of this specification.

## Existing SRS Patterns to Reuse

- Use the existing order flow for request steps, review, submission, and routing rather than creating a separate ordering mechanism.
- Create each host as a normal MiServer `Server` record and represent host disks with the existing `ServerDisk` relationship where applicable.
- Follow the existing MiServer forms for backup-time, patch-time, support contact, shortcode, and data-sensitivity choice behavior and validation.
- Use the existing MiServer TDX payload/integration for the two host tickets so their fields and workflow remain consistent with standard MiServer requests.
- Persist the cluster and its cluster disks in the dedicated cluster model, and create the cluster-level ticket; do not treat the cluster as a third MiServer.
- In the SRS admin view, expose a **Part of cluster** flag on MiServer records and identify their associated cluster.

## Acceptance Criteria

- Only DBA team members can access and submit the MSSQL Cluster category.
- Valid input generates the expected cluster name and the MACC/ASB hostnames; invalid environment, type, or sequence input is rejected.
- Database and SSAS orders show only their allowed SCSI controller choices.
- The form supports more than four cluster disks, permits blank disk labels, excludes system disk 0, accepts nonnegative device IDs starting at `0`, rejects device ID `7`, and prevents duplicate IDs on the same controller.
- Each ordered cluster is persisted as a dedicated cluster record linked to exactly one primary MACC MiServer record, one secondary ASB MiServer record, and its cluster disk records.
- Both MiServer records receive the correct defaults and shared order values, including data sensitivity and backup time.
- Patch windows follow the environment/host matrix, including the primary-host 3:00 AM fallback when 2:00 AM is unavailable.
- The selected daily OS backup is at least two elapsed hours from both servers' patch events; validation accounts for schedules crossing midnight and rejects closer times before submission.
- Successful submission creates exactly one VCI-owned cluster ticket and two MiServer tickets, with the existing MiServer ticket workflow preserved.
- The cluster ticket has no TDX workflow and can be manually closed by VCI after both MiServer tickets are complete.
- After ordering, a DBA can add and remove cluster disks, increase a disk's size, and edit its label through SRS.
- MiServer records show the Part of cluster flag and cluster association in SRS admin.

## Reference

- Existing development test entry point: https://srs-dev.dsc.umich.edu/services/cluster/add/
- Requested target timeline: prefer completion by the end of September 2026.