// A simple cube.
// Render with: openscad -o cube.stl cube.scad

size = 20;      // edge length in mm
centered = true; // center on the origin instead of the first octant

cube(size, center = centered);
