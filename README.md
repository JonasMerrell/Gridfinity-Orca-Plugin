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

### Method 1: Automatic Install via Build Script
Run the builder with `--install` to compile and copy the target-tagged plugin into OrcaSlicer's plugin directory:

```bash
python3 build_orca_plugin.py --install
```

### Method 2: Manual Installation
1. Clone or download this repository.
2. Build target plugins:
   ```bash
   python3 build_orca_plugin.py --all-targets
   ```
3. Copy the generated `.py` file matching your operating system and architecture into an `orca_plugins/` subfolder:
   * **Linux**: `~/.config/OrcaSlicer/plugins/gridfinity_bin/gridfinity_bin_plugin_linux_x86_64.py`
   * **Windows**: `%APPDATA%\OrcaSlicer\plugins\gridfinity_bin\gridfinity_bin_plugin_win_x86_64.py`
   * **macOS**: `~/Library/Application Support/OrcaSlicer/plugins/gridfinity_bin/gridfinity_bin_plugin_mac_arm64.py`
4. Restart OrcaSlicer. You will see a new **Gridfinity** tab in the top navigation bar.

### Method 3: Subscribe via Orca Cloud
Search for **Gridfinity Bin & Baseplate Generator** in Orca Cloud's **Plugin Hub** and click **Subscribe** to receive automatic updates directly in OrcaSlicer.

---

## ☁️ Continuous Deployment via GitHub (Orca Cloud)

This repository includes a GitHub Actions workflow (`.github/workflows/publish-orcacloud.yml`) for zero-secret [OIDC trusted publishing to Orca Cloud](https://cloud.orcaslicer.com/wiki/#publish-from-github):

1. Connect this repository in [Orca Cloud](https://cloud.orcaslicer.com) under **Shared Plugins > (Your Plugin) > Edit plugin > GitHub publishing** by entering `JonasMerrell/Gridfinity-Orca-Plugin`.
2. Whenever a new GitHub Release is published (e.g. `v1.5.0`), GitHub Actions will automatically compile all 6 platform targets and upload them directly to the Orca Cloud Plugin Hub.

---

## 🛠️ Supported Targets

| Platform | Architecture | Plugin Filename |
| :--- | :--- | :--- |
| **Linux** | x86_64 | `gridfinity_bin_plugin_linux_x86_64.py` |
| **Linux** | ARM64 | `gridfinity_bin_plugin_linux_arm64.py` |
| **Windows** | x86_64 | `gridfinity_bin_plugin_win_x86_64.py` |
| **Windows** | ARM64 | `gridfinity_bin_plugin_win_arm64.py` |
| **macOS** | Apple Silicon (ARM64) | `gridfinity_bin_plugin_mac_arm64.py` |
| **macOS** | Intel (x86_64) | `gridfinity_bin_plugin_mac_x86_64.py` |

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
