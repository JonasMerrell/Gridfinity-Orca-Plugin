// Parametric Gridfinity bin
//
//   Preview: openscad gridfinity_bin.scad
//   Export:  openscad -o bin.stl gridfinity_bin.scad
//
// Bottom of the bin sits at z = 0, centred on the origin in X/Y.
// Heights are nominal: a gz-unit bin is 7*gz mm to the top of the body,
// and the stacking lip sticks up above that -- it is swallowed by the
// base of the bin stacked on top, so the stacking pitch stays 7 mm.

/* [Size] */
gx = 2;             // [1:1:8] grid units in X (42 mm each)
gy = 1;             // [1:1:8] grid units in Y
gz = 6;             // [1:1:20] height units (7 mm each)

/* [Compartments] */
divisions_x = 2;    // [1:1:10]
divisions_y = 1;    // [1:1:10]
row_divisions = []; // Custom divisions across X for each row (from -Y front to +Y back), e.g. [2, 1, 3]
col_divisions = []; // Custom divisions across Y for each column (from -X left to +X right), e.g. [2, 3]

/* [Features] */
stacking_lip = true;
scoop        = true;   // finger ramp at the front of each compartment
label_tab    = false;  // overhanging label ledge at the back
magnet_holes = false;  // 6x2 mm magnets
screw_holes  = false;  // M3

/* [Advanced] */
wall            = 1.2;
floor_thickness = 1.4;
scoop_radius    = 6;
label_depth     = 12;
label_width     = 0;   // 0 = full compartment width
inner_fillet    = 0.8;

/* [Hidden] */
$fa = 2;
$fs = 0.3;
eps = 0.01;

// ---------------------------------------------------------------------------
// Gridfinity specification constants (mm)
// ---------------------------------------------------------------------------
GRID   = 42;                          // grid pitch
UNIT_Z = 7;                           // height unit
GAP    = 0.5;                         // XY clearance to the grid (0.25/side)

FOOT_TOP = GRID - GAP;                // 41.50  top of the foot profile
R_TOP    = 3.75;                      //        corner radius there
CH_UPPER = 2.15;                      // upper 45 deg chamfer
H_MID    = 1.80;                      // vertical section
CH_LOWER = 0.80;                      // lower 45 deg chamfer
FOOT_MID = FOOT_TOP - 2 * CH_UPPER;   // 37.20
R_MID    = R_TOP - CH_UPPER;          //  1.60
FOOT_BOT = FOOT_MID - 2 * CH_LOWER;   // 35.60
R_BOT    = R_MID - CH_LOWER;          //  0.80
BASE_H   = CH_LOWER + H_MID + CH_UPPER; // 4.75

LIP_CLEAR = 0.25;                     // radial clearance around the nested foot
LIP_INSET = CH_UPPER - LIP_CLEAR;     // 1.90  lip thickness at its mating face
LIP_TAPER = 0.70;                     //       45 deg chamfer on the top ring
LIP_H     = CH_LOWER + H_MID + LIP_TAPER; // 3.30

MAGNET_D  = 6.5;
MAGNET_H  = 2.4;
SCREW_D   = 3.0;
SCREW_H   = 6.0;
HOLE_OFF  = 13;                       // holes sit 26 mm apart, per unit

OX     = gx * GRID - GAP;
OY     = gy * GRID - GAP;
H_BODY = gz * UNIT_Z;
// Screw holes are 6 mm deep, which would punch through a thin floor, so the
// floor is deepened to keep at least 0.8 mm of material above them.
FLOOR  = BASE_H + (screw_holes ? max(floor_thickness, SCREW_H - BASE_H + 0.8)
                               : floor_thickness);

// interior envelope and compartment grid
IW = OX - 2 * wall;
ID = OY - 2 * wall;
CW = (IW - (divisions_x - 1) * wall) / divisions_x;
CD = (ID - (divisions_y - 1) * wall) / divisions_y;
R_IN = min(R_TOP - wall, CW / 2 - eps, CD / 2 - eps);

function cx(i) = -IW / 2 + i * (CW + wall) + CW / 2;
function cy(j) = -ID / 2 + j * (CD + wall) + CD / 2;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// Rounded rectangle, centred.
module rrect(sx, sy, r) {
    if (r > 0) offset(r = r) square([sx - 2 * r, sy - 2 * r], center = true);
    else square([sx, sy], center = true);
}

// Convex solid between two rounded rectangles at two heights.
module prism(sx1, sy1, r1, z1, sx2, sy2, r2, z2) {
    hull() {
        translate([0, 0, z1])       linear_extrude(eps) rrect(sx1, sy1, r1);
        translate([0, 0, z2 - eps]) linear_extrude(eps) rrect(sx2, sy2, r2);
    }
}

// ---------------------------------------------------------------------------
// Solid body
// ---------------------------------------------------------------------------

// One grid unit's stacking foot, centred on the origin.
module foot() {
    prism(FOOT_BOT, FOOT_BOT, R_BOT, 0,
          FOOT_MID, FOOT_MID, R_MID, CH_LOWER);
    prism(FOOT_MID, FOOT_MID, R_MID, CH_LOWER,
          FOOT_MID, FOOT_MID, R_MID, CH_LOWER + H_MID);
    prism(FOOT_MID, FOOT_MID, R_MID, CH_LOWER + H_MID,
          FOOT_TOP, FOOT_TOP, R_TOP, BASE_H);
}

module bin_solid() {
    for (i = [0 : gx - 1], j = [0 : gy - 1])
        translate([(i - (gx - 1) / 2) * GRID,
                   (j - (gy - 1) / 2) * GRID, 0]) foot();

    prism(OX, OY, R_TOP, BASE_H, OX, OY, R_TOP, H_BODY);

    if (stacking_lip)
        prism(OX, OY, R_TOP, H_BODY, OX, OY, R_TOP, H_BODY + LIP_H);
}

// ---------------------------------------------------------------------------
// Negative space
// ---------------------------------------------------------------------------

// Cavity through the lip: mirrors the foot profile above with clearance, so a
// bin dropped on top nests instead of resting on the rim.
module lip_cavity() {
    d  = max(0, LIP_INSET - wall);          // inward overhang needing support
    nw = OX - 2 * LIP_INSET;                // narrow (mating) size
    nd = OY - 2 * LIP_INSET;
    nr = max(0, R_TOP - LIP_INSET);
    tw = nw + 2 * LIP_TAPER;                // opening at the top ring
    td = nd + 2 * LIP_TAPER;
    tr = max(0, nr + LIP_TAPER);

    z0 = H_BODY - eps;
    z1 = H_BODY + CH_LOWER - d;             // start of the 45 deg support
    z2 = H_BODY + CH_LOWER;
    z3 = z2 + H_MID;
    z4 = H_BODY + LIP_H;

    prism(IW, ID, R_TOP - wall, z0, IW, ID, R_TOP - wall, z1 + eps);
    prism(IW, ID, R_TOP - wall, z1, nw, nd, nr, z2);
    prism(nw, nd, nr, z2, nw, nd, nr, z3);
    prism(nw, nd, nr, z3, tw, td, tr, z4);
}

module single_compartment(cx, cy, cw, cd) {
    r_in = min(R_TOP - wall, cw / 2 - eps, cd / 2 - eps);
    f = min(inner_fillet, cw / 2 - eps, cd / 2 - eps);
    translate([cx, cy, 0]) {
        prism(cw - 2 * f, cd - 2 * f, max(0, r_in - f), FLOOR,
              cw, cd, r_in, FLOOR + f);
        prism(cw, cd, r_in, FLOOR + f, cw, cd, r_in, H_BODY + eps);
    }
}

// Concave finger ramp at the -Y wall of a compartment.
module single_scoop(cx, cy, cw, cd) {
    is_left_outer  = abs((cx - cw / 2) - (-IW / 2)) < 0.01;
    is_right_outer = abs((cx + cw / 2) - (IW / 2)) < 0.01;
    is_front_outer = abs((cy - cd / 2) - (-ID / 2)) < 0.01;

    rL = (is_left_outer && is_front_outer) ? max(0, R_TOP - wall) : min(inner_fillet, cw / 2 - eps);
    rR = (is_right_outer && is_front_outer) ? max(0, R_TOP - wall) : min(inner_fillet, cw / 2 - eps);

    f = min(inner_fillet, cw / 2 - eps, cd / 2 - eps);
    rs = min(scoop_radius, cd - 2 * f, H_BODY - FLOOR);
    sw = cw - rL - rR;
    scx = cx - cw / 2 + rL + sw / 2;
    if (rs > 0 && sw > 0)
        translate([scx - sw / 2, cy - cd / 2, FLOOR])
        difference() {
            cube([sw, rs, rs]);
            translate([-eps, rs, rs]) rotate([0, 90, 0])
                cylinder(r = rs, h = sw + 2 * eps);
        }
}

// Label ledge at the +Y wall, 45 deg underside so it prints unsupported.
module single_label(cx, cy, cw, cd) {
    is_left_outer  = abs((cx - cw / 2) - (-IW / 2)) < 0.01;
    is_right_outer = abs((cx + cw / 2) - (IW / 2)) < 0.01;
    is_back_outer  = abs((cy + cd / 2) - (ID / 2)) < 0.01;

    rL = (is_left_outer && is_back_outer) ? max(0, R_TOP - wall) : min(inner_fillet, cw / 2 - eps);
    rR = (is_right_outer && is_back_outer) ? max(0, R_TOP - wall) : min(inner_fillet, cw / 2 - eps);

    ld = min(label_depth, cd - 1, H_BODY - FLOOR);
    max_lw = cw - rL - rR;
    lw = (label_width > 0 && label_width < max_lw) ? label_width : max_lw;
    lcx = cx - cw / 2 + rL + max_lw / 2;
    yb = cy + cd / 2;
    if (ld > 0 && lw > 0)
        translate([lcx, 0, 0])
        hull() {
            translate([-lw / 2, yb - ld, H_BODY - eps])
                cube([lw, ld, eps + LIP_H]);
            translate([-lw / 2, yb - eps, H_BODY - ld])
                cube([lw, eps, eps]);
        }
}

module interior() {
    use_rows = len(row_divisions) > 0;
    use_cols = len(col_divisions) > 0 && !use_rows;

    difference() {
        union() {
            if (use_rows) {
                nr = len(row_divisions);
                cd = (ID - (nr - 1) * wall) / nr;
                for (j = [0 : nr - 1]) {
                    rcols = row_divisions[j];
                    cw = (IW - (rcols - 1) * wall) / rcols;
                    cy = -ID / 2 + j * (cd + wall) + cd / 2;
                    for (i = [0 : rcols - 1]) {
                        cx = -IW / 2 + i * (cw + wall) + cw / 2;
                        single_compartment(cx, cy, cw, cd);
                    }
                }
            } else if (use_cols) {
                nc = len(col_divisions);
                cw = (IW - (nc - 1) * wall) / nc;
                for (i = [0 : nc - 1]) {
                    crows = col_divisions[i];
                    cd = (ID - (crows - 1) * wall) / crows;
                    cx = -IW / 2 + i * (cw + wall) + cw / 2;
                    for (j = [0 : crows - 1]) {
                        cy = -ID / 2 + j * (cd + wall) + cd / 2;
                        single_compartment(cx, cy, cw, cd);
                    }
                }
            } else {
                for (i = [0 : divisions_x - 1], j = [0 : divisions_y - 1])
                    single_compartment(cx(i), cy(j), CW, CD);
            }
        }
        if (scoop) {
            if (use_rows) {
                nr = len(row_divisions);
                cd = (ID - (nr - 1) * wall) / nr;
                for (j = [0 : nr - 1]) {
                    rcols = row_divisions[j];
                    cw = (IW - (rcols - 1) * wall) / rcols;
                    cy = -ID / 2 + j * (cd + wall) + cd / 2;
                    for (i = [0 : rcols - 1]) {
                        cx = -IW / 2 + i * (cw + wall) + cw / 2;
                        single_scoop(cx, cy, cw, cd);
                    }
                }
            } else if (use_cols) {
                nc = len(col_divisions);
                cw = (IW - (nc - 1) * wall) / nc;
                for (i = [0 : nc - 1]) {
                    crows = col_divisions[i];
                    cd = (ID - (crows - 1) * wall) / crows;
                    cx = -IW / 2 + i * (cw + wall) + cw / 2;
                    for (j = [0 : crows - 1]) {
                        cy = -ID / 2 + j * (cd + wall) + cd / 2;
                        single_scoop(cx, cy, cw, cd);
                    }
                }
            } else {
                for (i = [0 : divisions_x - 1], j = [0 : divisions_y - 1])
                    single_scoop(cx(i), cy(j), CW, CD);
            }
        }
        if (label_tab) {
            if (use_rows) {
                nr = len(row_divisions);
                cd = (ID - (nr - 1) * wall) / nr;
                for (j = [0 : nr - 1]) {
                    rcols = row_divisions[j];
                    cw = (IW - (rcols - 1) * wall) / rcols;
                    cy = -ID / 2 + j * (cd + wall) + cd / 2;
                    for (i = [0 : rcols - 1]) {
                        cx = -IW / 2 + i * (cw + wall) + cw / 2;
                        single_label(cx, cy, cw, cd);
                    }
                }
            } else if (use_cols) {
                nc = len(col_divisions);
                cw = (IW - (nc - 1) * wall) / nc;
                for (i = [0 : nc - 1]) {
                    crows = col_divisions[i];
                    cd = (ID - (crows - 1) * wall) / crows;
                    cx = -IW / 2 + i * (cw + wall) + cw / 2;
                    for (j = [0 : crows - 1]) {
                        cy = -ID / 2 + j * (cd + wall) + cd / 2;
                        single_label(cx, cy, cw, cd);
                    }
                }
            } else {
                for (i = [0 : divisions_x - 1], j = [0 : divisions_y - 1])
                    single_label(cx(i), cy(j), CW, CD);
            }
        }
    }
}

module base_holes() {
    for (i = [0 : gx - 1], j = [0 : gy - 1],
         sx = [-1, 1], sy = [-1, 1])
        translate([(i - (gx - 1) / 2) * GRID + sx * HOLE_OFF,
                   (j - (gy - 1) / 2) * GRID + sy * HOLE_OFF, -eps]) {
            if (magnet_holes) cylinder(d = MAGNET_D, h = MAGNET_H + eps);
            if (screw_holes)  cylinder(d = SCREW_D,  h = SCREW_H + eps);
        }
}

// ---------------------------------------------------------------------------

module gridfinity_bin() {
    difference() {
        bin_solid();
        interior();
        if (stacking_lip) lip_cavity();
        base_holes();
    }
}

gridfinity_bin();

echo(str("bin ", gx, "x", gy, "x", gz, "  footprint ", OX, " x ", OY,
         " mm, body ", H_BODY, " mm, total ",
         stacking_lip ? H_BODY + LIP_H : H_BODY,
         " mm, compartments ", divisions_x, "x", divisions_y, " of ",
         CW, " x ", CD, " x ", H_BODY - FLOOR, " mm"));

if (H_BODY - FLOOR < 2)
    echo("WARNING: compartments are shallower than 2 mm -- raise gz");
