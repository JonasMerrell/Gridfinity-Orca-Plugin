# Gridfinity Bin & Baseplate Generator for OrcaSlicer

A parametric 3D generator plugin for **OrcaSlicer** that configures, previews, and drops custom Gridfinity models directly onto your 3D printer's build plate.

---

## ✨ Features

### 📦 Parametric Bins
* **Standard-Compliant Geometry**: Built strictly to **Zack Freedman’s Gridfinity specification** (42 mm grid pitch, 7 mm unit heights, standard stacking feet and mating lip profile).
* **Advanced Compartment Layouts**:
  * **Uniform Grid**: Divide interior into equal $X \times Y$ compartments.
  * **By Row**: Set total rows and customize the number of columns in each individual row (from front to back).
  * **By Column**: Set total columns and customize the number of rows in each individual column (from left to right).
* **Features & Hardware**:
  * Finger scoops with curved bottom ramps for easy small-part retrieval.
  * 45° angled label tabs designed to print without supports.
  * Blind magnet pockets ($6 \times 2\text{ mm}$) and stepped M3 screw holes in the feet.
  * Configurable wall thickness, floor thickness, and corner fillets.

### 🧩 Interlocking Baseplates
* **Multiple Sizing Modes**:
  * **Grid Units**: Sizing directly in integer $X \times Y$ grid units.
  * **Dimensions (mm)**: Input exact target drawer/tray dimensions in millimeters with automatic integer unit fitting ($\text{units} = \max(1, \lfloor(\text{mm} + 0.5)/42\rfloor)$).
  * **Exact Edge Padding**: Add fractional perimeter borders at the outer edges to hit the exact target millimeter dimensions without disrupting the 42 mm socket grid.
* **Large Bed Splitting & Connectors**:
  * Multi-piece interlocking segmentation planning ported from **GridFlock** (by Jonas Konrad).
  * Dove-tail puzzle joints that interlock securely across segments.
  * Staggered seam layout to prevent weak 4-way corner intersections.
  * Auto-detection of active printer bed dimensions from OrcaSlicer.

### 🚀 Slicer Integration & Experience
* **Direct Build Plate Injection**: Exports binary STL files and automatically drops them into your active OrcaSlicer plate via single-instance IPC (D-Bus on Linux, `WM_COPYDATA` on Windows).
* **Interactive 3D WebGL Viewport**: Orbit, zoom, and pan directly within the OrcaSlicer UI with dark/light theme matching and zero external web dependencies.
* **OpenSCAD Parity**: Matching parametric OpenSCAD script (`gridfinity_bin.scad`) supporting all features including custom `row_divisions` and `col_divisions` array parameters.

---

## 📥 Installation

### Method 1: Subscribe via Orca Cloud
Search for **Gridfinity Bin & Baseplate Generator** in Orca Cloud's **Plugin Hub** and click **Subscribe** to receive automatic updates directly in OrcaSlicer.

### Method 2: Automatic Install via Build Script
Run the builder with `--install` to compile and copy the target-tagged plugin into OrcaSlicer's plugin directory:

```bash
python3 build_orca_plugin.py --install
```

### Method 3: Manual Installation
1. Clone or download this repository.
2. Build target plugins:
   ```bash
   python3 build_orca_plugin.py --all-targets
   ```
3. Copy the generated `.py` file matching your operating system and architecture into an `orca_plugins/` subfolder:
   * **Linux**: `~/.config/OrcaSlicer/plugins/gridfinity_bin/gridfinity_bin_plugin_linux_x86_64.py`
   * **Windows**: `%APPDATA%\OrcaSlicer\plugins\gridfinity_bin\gridfinity_bin_plugin_win_x86_64.py`
   * **macOS**: `~/Library/Application Support/OrcaSlicer/plugins/gridfinity_bin/gridfinity_bin_plugin_macosx_arm64.py`
4. Restart OrcaSlicer. You will see a new **Gridfinity** tab in the top navigation bar.

---

## 🛠️ Supported Targets

| Platform | Architecture | Plugin Filename |
| :--- | :--- | :--- |
| **Linux** | x86_64 | `gridfinity_bin_plugin_linux_x86_64.py` |
| **Linux** | ARM64 | `gridfinity_bin_plugin_linux_arm64.py` |
| **Windows** | x86_64 | `gridfinity_bin_plugin_win_x86_64.py` |
| **Windows** | ARM64 | `gridfinity_bin_plugin_win_arm64.py` |
| **macOS** | Apple Silicon (ARM64) | `gridfinity_bin_plugin_macosx_arm64.py` |
| **macOS** | Intel (x86_64) | `gridfinity_bin_plugin_macosx_x86_64.py` |

---

## 📖 Usage Guide

### 1. Generating Bins
1. Select **Model > Bin**.
2. Adjust **Bin Size**:
   * **Width / Depth**: Multiples of 42 mm grid pitch.
   * **Height**: Multiples of 7 mm Gridfinity unit height (default $6\text{ units} = 42\text{ mm}$).
3. Configure **Compartments**:
   * **Uniform**: Select divisions along X and Y.
   * **By Row**: Set total rows, then choose compartments per row.
   * **By Column**: Set total columns, then choose compartments per column.
4. Toggle **Features** (Stacking lip, Finger scoop, Label tab, Magnet/Screw holes).
5. Click **Export STL** to save or drop onto the build plate.

### 2. Generating Baseplates
1. Select **Model > Baseplate**.
2. Choose **Grid Units** or **Dimensions (mm)**:
   * When using **Dimensions (mm)**, enter your drawer or enclosure size (e.g. `250 × 210 mm`).
   * Click **`Add edge padding for exact size`** if you want symmetrical outer rim padding to fill the drawer completely.
3. Configure puzzle connectors and optional solid base thickness.
4. If the plate exceeds your printer bed, the plugin automatically splits it into puzzle-joint segments.
5. Click **Export STL**.

---

## Linux automatic import permissions

OrcaSlicer 2.5.1 audits `subprocess.Popen` against the exact string representation
of its argument list. A timestamped export filename therefore used to require a
new process approval on every export. Linux imports now copy the finished archive
to `gridfinity_output/.plate-import/gridfinity.stl` and hand off that stable path.
The original named STL remains available (subject to the existing last-50 archive
retention policy); the staging copy is outside archive pruning.

Only approve commands you recognize. A permission rejection/pending approval stops
that import immediately: no automatic retries, alternate interface, or Bambu Studio
fallback. If approval is deferred, approving it does **not** replay the failed
operation: click **Export STL** again. Initial setup can require separate approvals
for D-Bus discovery, PID lookup, and delivery. With the same plugin location and
Orca instance, new archive names no longer change those commands. Restarting Orca,
changing its installation, or changing the transport can still require approval.

Linux handoff stays in the host callback's audit context rather than a new Python
worker thread. This can briefly block the panel while waiting for IPC. No blanket
`full_access` or audit bypass is requested. The supported `orca.request_permissions`
API is discovery-only, not a runtime approval API; the destination's instance hash
is only known at runtime, so this fix retains host-managed per-command prompts.
See the upstream [audit documentation](https://github.com/OrcaSlicer/OrcaSlicer/wiki/plugin_audit_hook),
[2.5.1 permission implementation](https://github.com/OrcaSlicer/OrcaSlicer/blob/v2.5.1/src/slic3r/plugin/PluginAuditManager.cpp),
and [Python API binding](https://github.com/OrcaSlicer/OrcaSlicer/blob/v2.5.1/src/slic3r/plugin/PythonPluginBridge.cpp).

**IPC limitations:** Orca's D-Bus `AnotherInstance` normally sends no reply. A
`NoReply` or timeout is reported as **unconfirmed**, never as successful placement,
and is not retried because the request may already be queued. Confirm the model
visually on the plate before another automatic export; if it is absent, import the
named archive manually. A zero exit status acknowledges the handoff, not a verified
plate change. A lock prevents overlapping/reentrant handoffs in one plugin runtime
from replacing the staging copy, but cannot acknowledge an asynchronous read after
handoff returns, or coordinate separate Orca processes. Do not batch automatic
exports or share a plugin output folder between concurrent Orca instances; use the
individual archives for those cases. The staging copy persists after denial or
uncertain delivery, and is replaced only by the next explicit import attempt.

### Development tests (no installation or GUI access)

Edit `build_orca_plugin.py` for Python integration changes; generated plugins are
not the source. These stdlib-only tests build/load real generated code with a stub
`orca` module and fake subprocess boundary, covering both export protocols,
permission rejection/retry, exact-command reuse, staging isolation, and uncertain
IPC outcomes. They do not test a real Orca plate or its audit hook.

```bash
python3 build_orca_plugin.py --all-targets
python3 -m unittest discover -s tests -v
python3 -m compileall -q build_orca_plugin.py gridfinity_bin_plugin_*.py tests
# The test suite also checks all six tracked artifacts and repeat-build equality.
git diff --check
```

### Manual Linux validation (required before release)

1. Build locally, then deliberately install the matching generated plugin into a
   test OrcaSlicer 2.5.1 profile. Do not disable audit checks or grant full access.
2. Export a bin onto an empty test plate. Deny a requested process permission:
   verify the named STL is saved, placement is not reported successful, and no
   Bambu/alternate-command prompt follows from that attempt.
3. Retry, approve only the specific expected Orca/D-Bus commands, and explicitly
   retry after any deferred approval. Check the plate before repeating so a queued
   request is not imported twice. An unconfirmed result is expected for `NoReply`.
4. Change bin dimensions and export again under a new filename. Verify the new
   geometry on the plate, both distinct archives on disk, and no new permission
   caused solely by the archive filename. Repeat with a baseplate/chunked export.
5. Try the page and floating panel together: overlapping handoffs should report
   busy rather than overwrite an in-flight staging file. Wait for each visible
   import before the next one. Restart Orca and check any new instance-specific
   approvals separately.

---

## 📐 Gridfinity Dimensions Quick Reference

| Parameter | Dimension | Notes |
| :--- | :--- | :--- |
| **Grid Pitch** | $42.0\text{ mm}$ | Center-to-center cell spacing |
| **Unit Height ($Z$)** | $7.0\text{ mm}$ | Standard height unit ($1U = 7\text{ mm}$) |
| **Foot Height** | $4.75\text{ mm}$ | Base stacking profile height |
| **Foot Top Dimension** | $41.5\text{ mm}$ | $42.0\text{ mm} - 0.5\text{ mm}$ grid clearance gap |
| **Top Lip Height** | $3.30\text{ mm}$ | Male stacking rim |
| **Magnet Recess** | $\varnothing 6.5\text{ mm} \times 2.4\text{ mm}$ | Fits standard $6 \times 2\text{ mm}$ neodymium magnets |
| **Screw Holes** | $\varnothing 3.0\text{ mm}$ | Fits standard M3 socket head screws |

---

## 📜 References & Acknowledgments
* [Gridfinity Standard](https://gridfinity.xyz/) by Zack Freedman ([Voidstar Lab](https://www.youtube.com/c/ZackFreedman)).
* [GridFlock](https://github.com/jkonrad/gridflock) segmentation planning and puzzle connector profiles by Jonas Konrad.
* [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) plugin architecture and slicing engine.
* [OpenSCAD](https://openscad.org/) parametric CAD framework.
