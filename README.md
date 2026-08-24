# Gridfinity Bin & Baseplate Generator for OrcaSlicer

A parametric 3D generator plugin for **OrcaSlicer** that configures, previews, and drops custom Gridfinity models directly onto your build plate.

## Features
* **Parametric Bins:** Full control over grid units, compartments, stacking lips, scoops, label tabs, and magnet/screw holes built strictly to **Zack Freedman’s Gridfinity specification** (42 mm pitch, 7 mm height units).
* **Interlocking Baseplates:** Generates bed-fitted, multi-piece baseplates using segmentation planning and puzzle-joint connector profiles ported from **GridFlock** (by Jonas Konrad).
* **Seamless OrcaSlicer Integration:** Runs as a main-window tab or floating tool, auto-detects your active printer's bed size, and routes generated binary STLs directly to the build plate via single-instance IPC (D-Bus on Linux / `WM_COPYDATA` on Windows).
* **Interactive 3D WebGL Viewport:** Zero-dependency, real-time preview with orbit/pan/zoom controls and theme matching.
* **OpenSCAD Compatibility:** Generates matching CLI commands for headless rendering via the included `gridfinity_bin.scad` script.

## Building & Installing

Requirements: Python 3.12+

```bash
# Rebuild the plugin for the current OS/architecture
python3 build_orca_plugin.py

# Build for all supported OS and architecture targets
python3 build_orca_plugin.py --all-targets

# Build and automatically install into your OrcaSlicer plugins directory
python3 build_orca_plugin.py --install
```

## References & Acknowledgments
* [Gridfinity](https://gridfinity.xyz/) standard by Zack Freedman ([Voidstar Lab](https://www.youtube.com/c/ZackFreedman)).
* [GridFlock](https://github.com/jkonrad/gridflock) segmentation planning and puzzle connector profiles by Jonas Konrad.
* [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) plugin system and host APIs.
* [OpenSCAD](https://openscad.org/) parametric CAD framework.
