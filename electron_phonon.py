from manim import *
import numpy as np

N_IONS = 7
ION_RADIUS = 0.3
ION_SPACING = 1.2  # buff between circle edges
ELECTRON_RADIUS = 0.15
ELECTRON_SITE = 3  # center ion (0-indexed)
BOND_COLOR = BLACK
ION_COLOR = BLACK
ELECTRON_COLOR = BLUE
NUM_CYCLES = 2
RUN_TIME = 4  # seconds


def build_lattice():
    """Create a 1D lattice of 7 ions arranged horizontally."""
    ions = VGroup(
        *[
            Circle(
                radius=ION_RADIUS,
                color=ION_COLOR,
                fill_color=WHITE,
                fill_opacity=1,
                stroke_width=3,
            )
            for _ in range(N_IONS)
        ]
    )
    ions.arrange(RIGHT, buff=ION_SPACING)
    ions.shift(DOWN * 0.3)
    return ions


def build_bonds(ions):
    """Create bond lines between adjacent ions that update dynamically."""
    bonds = VGroup()
    for i in range(len(ions) - 1):
        bond = always_redraw(
            lambda i=i: Line(
                ions[i].get_right(),
                ions[i + 1].get_left(),
                color=BOND_COLOR,
                stroke_width=2.5,
            )
        )
        bonds.add(bond)
    return bonds


def build_electron(ions):
    """Create an electron dot that tracks the center ion."""
    electron = Dot(
        radius=ELECTRON_RADIUS, color=ELECTRON_COLOR, fill_opacity=1
    )
    electron.move_to(ions[ELECTRON_SITE].get_center())
    electron.add_updater(lambda m: m.move_to(ions[ELECTRON_SITE].get_center()))
    return electron


class HolsteinCoupling(Scene):
    def construct(self):
        # Title
        title = Text("Holstein Coupling", color=BLACK, font_size=40)
        title.to_edge(UP)

        # Lattice
        ions = build_lattice()
        original_positions = [ion.get_center().copy() for ion in ions]

        # Phase tracker
        phase = ValueTracker(0)

        # Only center ion oscillates vertically
        AMPLITUDE = 1.20
        ions[ELECTRON_SITE].add_updater(
            lambda m, orig=original_positions[ELECTRON_SITE]: m.move_to(
                orig + UP * AMPLITUDE * np.sin(phase.get_value())
            )
        )

        # Bonds and electron
        bonds = build_bonds(ions)
        electron = build_electron(ions)

        # Assemble scene
        self.add(title, bonds, ions, electron)

        # Animate 2 full cycles
        self.play(
            phase.animate.set_value(NUM_CYCLES * TAU),
            rate_func=linear,
            run_time=RUN_TIME,
        )


class PeierlsCoupling(Scene):
    def construct(self):
        # Title
        title = Text("Peierls Coupling", color=BLACK, font_size=40)
        title.to_edge(UP)

        # Lattice
        ions = build_lattice()
        original_positions = [ion.get_center().copy() for ion in ions]

        # Phase tracker
        phase = ValueTracker(0)

        # All ions oscillate horizontally with alternating signs
        AMPLITUDE = 0.2
        for i, ion in enumerate(ions):
            sign = (-1) ** i
            ion.add_updater(
                lambda m, orig=original_positions[i], s=sign: m.move_to(
                    orig + RIGHT * AMPLITUDE * s * np.sin(phase.get_value())
                )
            )

        # Bonds and electron
        bonds = build_bonds(ions)
        electron = build_electron(ions)

        # Assemble scene
        self.add(title, bonds, ions, electron)

        # Animate 2 full cycles
        self.play(
            phase.animate.set_value(NUM_CYCLES * TAU),
            rate_func=linear,
            run_time=RUN_TIME,
        )


class Polaron(Scene):
    def construct(self):
        # Title
        title = Text("Polaron", color=BLACK, font_size=40)
        title.to_edge(UP)

        # 2D lattice parameters
        ROWS = 5
        COLS = 9
        SPACING = 1.1
        ION_R = 0.15
        LATTICE_CENTER_Y = -0.3  # shift down to make room for title

        # Build 2D lattice
        ions = VGroup()
        equilibrium = []
        for row in range(ROWS):
            for col in range(COLS):
                x = (col - (COLS - 1) / 2) * SPACING
                y = (row - (ROWS - 1) / 2) * SPACING + LATTICE_CENTER_Y
                ion = Circle(
                    radius=ION_R,
                    color=BLACK,
                    fill_color=WHITE,
                    fill_opacity=1,
                    stroke_width=2,
                )
                ion.move_to([x, y, 0])
                ions.add(ion)
                equilibrium.append(np.array([x, y, 0]))

        # Phase tracker — electron oscillates left-right through center
        phase = ValueTracker(0)
        ELECTRON_RANGE = 3.5  # horizontal travel amplitude

        def get_electron_pos():
            return np.array(
                [ELECTRON_RANGE * np.sin(phase.get_value()), LATTICE_CENTER_Y, 0]
            )

        # Distortion: each ion pulled toward electron with Gaussian falloff
        DIST_AMPLITUDE = 0.2
        SIGMA = 1.5

        for idx, ion in enumerate(ions):
            eq = equilibrium[idx].copy()

            def make_updater(eq_pos):
                def updater(m):
                    e_pos = get_electron_pos()
                    diff = eq_pos - e_pos
                    dist = np.linalg.norm(diff[:2])
                    if dist < 0.01:
                        m.move_to(eq_pos)
                    else:
                        displacement = DIST_AMPLITUDE * np.exp(
                            -(dist**2) / (2 * SIGMA**2)
                        )
                        direction = -diff / dist  # toward electron
                        m.move_to(eq_pos + direction * displacement)

                return updater

            ion.add_updater(make_updater(eq))

        # Bonds between adjacent ions (horizontal + vertical), redrawn each frame
        def make_bonds():
            bonds = VGroup()
            for row in range(ROWS):
                for col in range(COLS):
                    idx = row * COLS + col
                    if col < COLS - 1:  # horizontal bond
                        bonds.add(
                            Line(
                                ions[idx].get_center(),
                                ions[idx + 1].get_center(),
                                color=BLACK,
                                stroke_width=1.5,
                            )
                        )
                    if row < ROWS - 1:  # vertical bond
                        bonds.add(
                            Line(
                                ions[idx].get_center(),
                                ions[idx + COLS].get_center(),
                                color=BLACK,
                                stroke_width=1.5,
                            )
                        )
            return bonds

        bonds = always_redraw(make_bonds)

        # Electron dot
        electron = Dot(radius=0.12, color=BLUE, fill_opacity=1)
        electron.add_updater(lambda m: m.move_to(get_electron_pos()))

        # Assemble: bonds behind ions, electron on top
        self.add(title, bonds, ions, electron)

        # Animate 2 full oscillation cycles (seamless loop)
        self.play(
            phase.animate.set_value(2 * TAU),
            rate_func=linear,
            run_time=6,
        )


class Bipolaron(Scene):
    def construct(self):
        # Shorter frame (no title)
        config.frame_height = 5.5
        config.pixel_height = 500

        # 2D lattice parameters (matching Polaron scene)
        ROWS = 5
        COLS = 9
        SPACING = 1.1
        ION_R = 0.15
        LATTICE_CENTER_Y = 0.0

        # Build 2D lattice
        ions = VGroup()
        equilibrium = []
        for row in range(ROWS):
            for col in range(COLS):
                x = (col - (COLS - 1) / 2) * SPACING
                y = (row - (ROWS - 1) / 2) * SPACING + LATTICE_CENTER_Y
                ion = Circle(
                    radius=ION_R,
                    color=BLACK,
                    fill_color=WHITE,
                    fill_opacity=1,
                    stroke_width=2,
                )
                ion.move_to([x, y, 0])
                ions.add(ion)
                equilibrium.append(np.array([x, y, 0]))

        # Progress tracker drives the entire animation (0 → 1)
        progress = ValueTracker(0)

        # --- Electron positions: start separated, converge into bipolaron ---
        START_HALF_SEP = 3.0  # initial distance from center
        END_HALF_SEP = 0.55  # final ~1 lattice spacing apart

        def get_electron_positions():
            t = progress.get_value()
            # Electrons stay put while distortion builds, then converge
            t_move = max((t - 0.15) / 0.85, 0.0)
            t_smooth = 3 * t_move**2 - 2 * t_move**3  # smoothstep
            half_sep = START_HALF_SEP + (END_HALF_SEP - START_HALF_SEP) * t_smooth
            return (
                np.array([-half_sep, LATTICE_CENTER_Y, 0]),
                np.array([half_sep, LATTICE_CENTER_Y, 0]),
            )

        # --- Lattice distortion: ions pulled toward each electron ---
        DIST_AMPLITUDE = 0.18
        SIGMA = 1.5

        def distortion_scale(t):
            """Ramp distortion from 0 to full over t in [0, 0.3]."""
            return min(t / 0.3, 1.0)

        for idx, ion in enumerate(ions):
            eq = equilibrium[idx].copy()

            def make_updater(eq_pos):
                def updater(m):
                    t = progress.get_value()
                    d_scale = distortion_scale(t)
                    e1, e2 = get_electron_positions()
                    total_disp = np.array([0.0, 0.0, 0.0])
                    for e_pos in [e1, e2]:
                        diff = eq_pos - e_pos
                        dist = np.linalg.norm(diff[:2])
                        if dist > 0.01:
                            displacement = d_scale * DIST_AMPLITUDE * np.exp(
                                -(dist**2) / (2 * SIGMA**2)
                            )
                            direction = -diff / dist  # toward electron
                            total_disp += direction * displacement
                    m.move_to(eq_pos + total_disp)

                return updater

            ion.add_updater(make_updater(eq))

        # --- Dynamic bonds ---
        def make_bonds():
            bonds = VGroup()
            for row in range(ROWS):
                for col in range(COLS):
                    idx = row * COLS + col
                    if col < COLS - 1:
                        bonds.add(
                            Line(
                                ions[idx].get_center(),
                                ions[idx + 1].get_center(),
                                color=BLACK,
                                stroke_width=1.5,
                            )
                        )
                    if row < ROWS - 1:
                        bonds.add(
                            Line(
                                ions[idx].get_center(),
                                ions[idx + COLS].get_center(),
                                color=BLACK,
                                stroke_width=1.5,
                            )
                        )
            return bonds

        bonds = always_redraw(make_bonds)

        # --- Two electron dots ---
        electron1 = Dot(radius=0.12, color=BLUE, fill_opacity=1)
        electron2 = Dot(radius=0.12, color=BLUE, fill_opacity=1)
        electron1.add_updater(lambda m: m.move_to(get_electron_positions()[0]))
        electron2.add_updater(lambda m: m.move_to(get_electron_positions()[1]))

        # Assemble: bonds behind ions, electrons on top
        self.add(bonds, ions, electron1, electron2)

        # Animate formation
        self.play(
            progress.animate.set_value(1),
            rate_func=linear,
            run_time=8,
        )
        self.wait(0.5)


class Diffusion(Scene):
    def construct(self):
        # Shorter frame (no title)
        config.frame_height = 5.0
        config.pixel_height = 450

        # --- Static 1D lattice ---
        N = 7
        SPACING = 1.5
        LATTICE_Y = 0.35
        ION_R = 0.2

        ions = VGroup()
        ion_x = []
        for i in range(N):
            x = (i - (N - 1) / 2) * SPACING
            ion_x.append(x)
            ion = Circle(
                radius=ION_R,
                color=BLACK,
                fill_color=WHITE,
                fill_opacity=1,
                stroke_width=2.5,
            )
            ion.move_to([x, LATTICE_Y, 0])
            ions.add(ion)

        bonds = VGroup()
        for i in range(N - 1):
            bonds.add(
                Line(
                    ions[i].get_right(),
                    ions[i + 1].get_left(),
                    color=BLACK,
                    stroke_width=2,
                )
            )

        # --- Time tracker (0 → 1) ---
        progress = ValueTracker(0)

        # --- Gaussian wavepacket above lattice ---
        GAUSS_BASE_Y = LATTICE_Y + 0.4
        SIGMA_0 = 0.1
        SIGMA_MAX = 3.0
        GAUSS_HEIGHT = 2.4
        X_MIN = ion_x[0] - SPACING
        X_MAX = ion_x[-1] + SPACING

        def make_gaussian():
            tv = progress.get_value()
            sigma = SIGMA_0 + (SIGMA_MAX - SIGMA_0) * tv
            amp = GAUSS_HEIGHT * SIGMA_0 / sigma
            curve = FunctionGraph(
                lambda x: amp * np.exp(-(x**2) / (2 * sigma**2)),
                x_range=[X_MIN, X_MAX, 0.05],
                color=BLUE,
                stroke_width=2.5,
            )
            curve.set_fill(BLUE, opacity=0.3)
            curve.shift(UP * GAUSS_BASE_Y)
            return curve

        gaussian = always_redraw(make_gaussian)

        # --- Parabolic phonon potentials below lattice ---
        PARA_TOP_Y = LATTICE_Y - 0.5
        PARA_DEPTH = 2.0
        PARA_HALF_W = 0.45
        N_LEVELS = 5
        LEVEL_SPACING = PARA_DEPTH / (N_LEVELS + 0.5)

        # Dynamic parabolas: black outline + red gradient fill inside
        N_STRIPS = 10

        def make_parabolas():
            grp = VGroup()
            tv = progress.get_value()
            tv_fast = tv ** 0.6  # front-load visual change
            sigma = SIGMA_0 + (SIGMA_MAX - SIGMA_0) * tv

            for i in range(N):
                xs = ion_x[i]
                y_bot = PARA_TOP_Y - PARA_DEPTH
                a_coeff = PARA_DEPTH / (PARA_HALF_W**2)

                # Red intensity depends on time and electron density
                e_density = np.exp(-(xs**2) / (2 * sigma**2))
                red_amount = min(tv_fast * e_density * 1.5, 1.0)

                # Filled horizontal strips: redder toward the top
                for s in range(N_STRIPS):
                    y_lo = y_bot + s * PARA_DEPTH / N_STRIPS
                    y_hi = y_bot + (s + 1) * PARA_DEPTH / N_STRIPS
                    # Half-widths from parabola: y = y_bot + a*(x-xs)^2
                    x_half_lo = PARA_HALF_W * np.sqrt(
                        max((y_lo - y_bot) / PARA_DEPTH, 0)
                    )
                    x_half_hi = PARA_HALF_W * np.sqrt(
                        max((y_hi - y_bot) / PARA_DEPTH, 0)
                    )
                    frac = (s + 0.5) / N_STRIPS  # 0 at bottom, 1 at top
                    opacity = frac * red_amount * 0.55
                    if opacity > 0.01:
                        strip = Polygon(
                            [xs - x_half_lo, y_lo, 0],
                            [xs - x_half_hi, y_hi, 0],
                            [xs + x_half_hi, y_hi, 0],
                            [xs + x_half_lo, y_lo, 0],
                            fill_color=RED,
                            fill_opacity=opacity,
                            stroke_width=0,
                        )
                        grp.add(strip)

                # Black parabola outline on top
                para = FunctionGraph(
                    lambda x, _xs=xs, _yb=y_bot, _a=a_coeff: _yb
                    + _a * (x - _xs) ** 2,
                    x_range=[xs - PARA_HALF_W, xs + PARA_HALF_W, 0.01],
                    color=BLACK,
                    stroke_width=1.5,
                )
                grp.add(para)
            return grp

        parabolas = always_redraw(make_parabolas)

        # Dynamic phonon level lines (color = occupation)
        def occ_color(occ):
            """Interpolate light grey -> red based on occupation."""
            occ = max(0.0, min(1.0, occ))
            r = int(0xBB + (0xCC - 0xBB) * occ)
            g = int(0xBB * (1 - occ))
            b = int(0xBB * (1 - occ))
            return f"#{r:02x}{g:02x}{b:02x}"

        def make_levels():
            grp = VGroup()
            tv = progress.get_value()
            tv_fast = tv ** 0.6  # front-load visual change
            sigma = SIGMA_0 + (SIGMA_MAX - SIGMA_0) * tv

            for site_idx in range(N):
                xs = ion_x[site_idx]
                y_bot = PARA_TOP_Y - PARA_DEPTH
                # Electron density at this site (unnormalized Gaussian)
                e_density = np.exp(-(xs**2) / (2 * sigma**2))

                for lev in range(N_LEVELS):
                    y_lev = y_bot + (lev + 0.75) * LEVEL_SPACING
                    # Half-width of level line bounded by parabola
                    frac = max((y_lev - y_bot) / PARA_DEPTH, 0)
                    half_w = PARA_HALF_W * np.sqrt(frac) * 0.85
                    half_w = max(half_w, 0.03)

                    # Occupation: thermal base + electron-induced excitation
                    thermal = np.exp(-0.8 * lev)
                    excited = (
                        tv_fast * e_density * lev / max(N_LEVELS - 1, 1) * 2.5
                    )
                    occ = min(thermal + excited, 1.0)

                    line = Line(
                        [xs - half_w, y_lev, 0],
                        [xs + half_w, y_lev, 0],
                        color=occ_color(occ),
                        stroke_width=1.5 + occ * 2.0,
                    )
                    grp.add(line)
            return grp

        level_indicators = always_redraw(make_levels)

        # Assemble
        self.add(bonds, ions, parabolas, level_indicators, gaussian)

        # Animate diffusion
        self.play(
            progress.animate.set_value(1),
            rate_func=linear,
            run_time=4,
        )
        self.wait(0.5)
