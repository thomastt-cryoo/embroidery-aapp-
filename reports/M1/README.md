# M1 — Lilo interface redesign

**M1 is complete and ready for review.** The final report contains the Windows build, screenshots, passing checks and hardware limits.

Start with [the final report](04-final-report.md) for the finished interface, screenshots, test results and remaining platform limits.

The checkpoint reports explain the work in order:

1. [Baseline and interface plan](01-baseline-and-plan.md)
2. [Layout and themes](02-layout-and-themes.md)
3. [Workflow and editor integration](03-workflow-and-editor.md)
4. [Final verification and delivery](04-final-report.md)

The review build is placed in **M1 Preview** in the main project folder. Open **Lilo M1 Review.exe** there. It uses a separate local profile. Keep other Lilo copies closed while using the review build's machine connection, since the existing bridge uses one local port.

If an earlier **Lilo M1 Preview** window is open, it is left intact to protect the design being tried there. Save that design before closing it; its `.lilo` project can be opened in the final review build.

Screenshots, exported sample files and structured results are in `evidence/`. Raw build/test logs, including interrupted attempts, are retained locally in that folder. The final report identifies the successful runs.

M1 stops at review. No later milestone or public release is started.
