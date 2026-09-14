from manim import *
import numpy as np
from scipy.ndimage import gaussian_filter

BOX_HALF = 3.0            # half-width of the water box
CENTER = np.array([0.0, 0.0, 0.0])
N_PARTICLES = 1200        # Monte-Carlo samples used to build the concentration field
STEPS = 150                # discrete random-walk steps
STEP_STD = 0.055           # std dev of each random-walk step
CLUSTER_SIGMA = 0.12       # radius of the initial drop
RUN_TIME = 7
SEED = 7
TAG_IDX = 0                 # index of the particle tagged in the second scene

GRID_RES = 130              # resolution of the concentration field
BLUR_SIGMA_BINS = 3.2        # kernel width (in grid bins) used to smooth the field into a continuum
INTENSITY_SCALE = 2.0        # multiplier on concentration -> darkness (doubles the max intensity at t=0)


def make_trajectories(seed, n=N_PARTICLES, steps=STEPS, box_half=BOX_HALF,
                       step_std=STEP_STD, cluster_sigma=CLUSTER_SIGMA):
    """Precompute a reflecting 2D random walk for n particles, all starting
    clustered near the origin (the initial drop of tracer)."""
    rng = np.random.default_rng(seed)
    traj = np.zeros((n, steps + 1, 3))
    traj[:, 0, :2] = rng.normal(0, cluster_sigma, size=(n, 2))
    for s in range(1, steps + 1):
        step = rng.normal(0, step_std, size=(n, 2))
        pos = traj[:, s - 1, :2] + step
        for dim in range(2):
            over = pos[:, dim] > box_half
            pos[over, dim] = 2 * box_half - pos[over, dim]
            under = pos[:, dim] < -box_half
            pos[under, dim] = -2 * box_half - pos[under, dim]
            pos[:, dim] = np.clip(pos[:, dim], -box_half, box_half)
        traj[:, s, :2] = pos
    return traj


def pos_at(traj, i, val):
    """Linearly interpolate particle i's position at continuous step value."""
    i0 = int(val)
    if i0 >= STEPS:
        return traj[i, STEPS] + CENTER
    frac = val - i0
    return traj[i, i0] * (1 - frac) + traj[i, i0 + 1] * frac + CENTER


def positions_at(traj, val):
    """Vectorized interpolated (x, y) for every particle at continuous step value."""
    i0 = int(np.floor(val))
    if i0 >= STEPS:
        return traj[:, STEPS, :2]
    frac = val - i0
    return traj[:, i0, :2] * (1 - frac) + traj[:, i0 + 1, :2] * frac


def density_field(positions, box_half=BOX_HALF, grid_res=GRID_RES, sigma_bins=BLUR_SIGMA_BINS):
    """Kernel-density estimate of particle concentration over the box, as a
    smooth (grid_res, grid_res) field."""
    hist, _, _ = np.histogram2d(
        positions[:, 0], positions[:, 1],
        bins=grid_res, range=[[-box_half, box_half], [-box_half, box_half]],
    )
    return gaussian_filter(hist, sigma=sigma_bins)


def field_to_rgb(field, ref_peak, intensity_scale=1.0):
    """Map concentration -> grayscale intensity (dark = concentrated tracer,
    white = pure water), oriented for ImageMobject."""
    norm = np.clip(intensity_scale * field / ref_peak, 0, 1)
    gray = ((1 - norm) * 255).astype(np.uint8)
    img = np.flipud(gray.T)
    return np.stack([img] * 3, axis=-1)


def build_box():
    box = Square(side_length=2 * BOX_HALF, color=BLACK, stroke_width=3)
    box.move_to(CENTER)
    return box


def build_density_image(traj, t, ref_peak):
    """always_redraw factory for the continuum concentration field."""

    def make():
        positions = positions_at(traj, t.get_value())
        field = density_field(positions)
        rgb = field_to_rgb(field, ref_peak, INTENSITY_SCALE)
        img = ImageMobject(rgb)
        img.height = 2 * BOX_HALF
        img.width = 2 * BOX_HALF
        img.move_to(CENTER)
        return img

    return always_redraw(make)


class TracerDiffusion(Scene):
    """A drop of black tracer fluid spreading through a box of water until
    it can no longer be distinguished from the background. The tracer is
    rendered as a continuum concentration field, not discrete particles."""

    def construct(self):
        box = build_box()
        traj = make_trajectories(SEED)
        ref_peak = density_field(positions_at(traj, 0)).max()

        t = ValueTracker(0)
        density_img = build_density_image(traj, t, ref_peak)

        self.add(density_img, box)

        self.play(
            t.animate.set_value(STEPS),
            rate_func=linear,
            run_time=RUN_TIME,
        )
        self.wait(0.5)


class TracerDiffusionTagged(Scene):
    """Same tracer diffusion continuum field, but one particle is tagged with
    a red dot so its individual random-walk path can be followed as the
    tracer spreads."""

    def construct(self):
        box = build_box()
        traj = make_trajectories(SEED)  # identical trajectories to the first scene
        ref_peak = density_field(positions_at(traj, 0)).max()

        t = ValueTracker(0)
        density_img = build_density_image(traj, t, ref_peak)

        tagged_dot = Dot(radius=0.06, color=DARK_BROWN, fill_opacity=1)
        tagged_dot.move_to(traj[TAG_IDX, 0] + CENTER)
        tagged_dot.add_updater(lambda m: m.move_to(pos_at(traj, TAG_IDX, t.get_value())))

        trail = TracedPath(
            tagged_dot.get_center,
            stroke_color=DARK_BROWN,
            stroke_width=2,
            stroke_opacity=0.8,
        )

        self.add(density_img, box, trail, tagged_dot)

        self.play(
            t.animate.set_value(STEPS),
            rate_func=linear,
            run_time=RUN_TIME,
        )
        self.wait(0.5)
