# Final Apple Silicon evidence

Successful native run: https://github.com/thomastt-cryoo/embroidery-aapp-/actions/runs/39346926486

`native-ui/results.json` and its eight checks describe this final run. `mac-zip-install.json` records the exact installed customer ZIP hash. The saved project, PES export and native screenshots are retained here.

The workflow downloaded the sealed build artifact, so this directory also retains build/compression comparison metadata from that source artifact. Comparison candidates are historical; `mac-selected-package.json`, the installation manifest and the root delivery manifest identify the final 19,870,862-byte ZIP.

Inherited `failure.png`/`failure.json` files from the earlier build's failed UI driver were excluded from this curated successful-run directory. The original downloaded archives and action records remain retained separately; failed runs have not been relabelled as passing.
