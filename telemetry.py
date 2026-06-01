"""
telemetry.py

Telemetry handling for MiniSatSimPractice.

This module owns the canonical layout of the satellite history array:
  - Column registry (name -> index, units)
  - Conversion from sat.history (list of dicts) -> numpy array
  - CSV save / load
  - Telemetry wrapper for named column access in notebooks
  - Pretty console summary

The numeric column layout is unchanged from the original get_history_array
output, so existing plotting functions that index history_array[:, N] keep
working without modification.
"""

from pathlib import Path
import numpy as np


# ----------------------------------------------------------------------
# Column registry
# ----------------------------------------------------------------------
# Single source of truth for what each column is and what unit it carries.
# Add new telemetry channels here and everything downstream (CSV header,
# Telemetry wrapper, summary) picks them up automatically.
#
# Format: list of (column_name, unit_string) in the order they appear
# in the history array.

TELEMETRY_COLUMNS = [
    ("time_s",                "s"),

    ("x_km",                  "km"),
    ("y_km",                  "km"),
    ("z_km",                  "km"),

    ("vx_km_s",               "km/s"),
    ("vy_km_s",               "km/s"),
    ("vz_km_s",               "km/s"),

    ("altitude_km",           "km"),
    ("speed_km_s",            "km/s"),

    ("in_eclipse",            "bool"),

    ("body_x_eci_x",          "-"),
    ("body_x_eci_y",          "-"),
    ("body_x_eci_z",          "-"),
    ("body_y_eci_x",          "-"),
    ("body_y_eci_y",          "-"),
    ("body_y_eci_z",          "-"),
    ("body_z_eci_x",          "-"),
    ("body_z_eci_y",          "-"),
    ("body_z_eci_z",          "-"),

    ("instantaneous_power_W", "W"),
]

COLUMN_NAMES = [name for name, _ in TELEMETRY_COLUMNS]
COLUMN_UNITS = {name: unit for name, unit in TELEMETRY_COLUMNS}
COLUMN_INDEX = {name: i for i, (name, _) in enumerate(TELEMETRY_COLUMNS)}


# ----------------------------------------------------------------------
# History -> array conversion
# ----------------------------------------------------------------------

def _flatten_state(state):
    """Convert one state dict from sat.history into a flat row of floats.

    Missing values (None) become np.nan so the array stays float dtype.
    """
    position = state["position_km"]
    velocity = state["velocity_km_s"]
    attitude = state["attitude"]

    if attitude is None:
        bx = by = bz = (np.nan, np.nan, np.nan)
    else:
        bx = tuple(attitude.body_x_eci)
        by = tuple(attitude.body_y_eci)
        bz = tuple(attitude.body_z_eci)

    in_eclipse = state.get("in_eclipse")
    power_w    = state.get("instantaneous_power_W")

    row = [
        state["time_since_epoch"],
        position[0], position[1], position[2],
        velocity[0], velocity[1], velocity[2],
        state["altitude_km"],
        state["speed_km_s"],
        np.nan if in_eclipse is None else float(in_eclipse),
        bx[0], bx[1], bx[2],
        by[0], by[1], by[2],
        bz[0], bz[1], bz[2],
        np.nan if power_w is None else float(power_w),
    ]
    return row


def history_to_array(history):
    """Convert a list of state dicts (sat.history) to a numpy array.

    Returned shape: (n_timesteps, len(TELEMETRY_COLUMNS))
    Column order matches TELEMETRY_COLUMNS.
    """
    if len(history) == 0:
        return np.zeros((0, len(TELEMETRY_COLUMNS)))
    rows = [_flatten_state(s) for s in history]
    return np.array(rows, dtype=float)


# ----------------------------------------------------------------------
# CSV save / load
# ----------------------------------------------------------------------

def save_history_to_csv(filename, history_array):
    """Write a telemetry array to CSV with a header derived from the registry.

    Accepts either a raw numpy array (from sat.get_history_array() or
    history_to_array()) or a Telemetry wrapper object.
    """
    if isinstance(history_array, Telemetry):
        history_array = history_array.array

    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    header = ",".join(COLUMN_NAMES)

    np.savetxt(
        filename,
        history_array,
        delimiter=",",
        header=header,
        comments="",
    )


def load_history_from_csv(filename):
    """Read a telemetry CSV back into a numpy array.

    Returns a plain numpy array with the same column layout as
    history_to_array(). Wrap with Telemetry(...) for named access.
    """
    return np.loadtxt(filename, delimiter=",", skiprows=1)


# ----------------------------------------------------------------------
# Telemetry wrapper
# ----------------------------------------------------------------------

class Telemetry:
    """Convenience wrapper around a history array for notebook use.

    Plotting functions still want the raw numpy array; access it via
    `tlm.array`. Notebook code that wants named access uses tlm["col_name"]
    or tlm.col_name.

    Examples
    --------
    >>> tlm = Telemetry(sat.history)
    >>> tlm["altitude_km"]          # 1D array of altitudes
    >>> tlm.altitude_km             # same thing
    >>> tlm["time_s"] / 3600        # hours since epoch
    >>> plot_power(tlm.array)       # raw array for existing plot funcs
    >>> tlm.summary()               # print scenario summary
    """

    def __init__(self, source):
        """Build from either a list of state dicts or an existing array.

        The source is coerced to a float dtype array. Python None values
        (which can appear when satellite subsystems like eclipse/attitude/
        power are disabled) are converted to np.nan so downstream numeric
        ops behave.
        """
        if isinstance(source, np.ndarray):
            arr = source
        elif isinstance(source, list):
            arr = history_to_array(source)
        else:
            raise TypeError(
                "Telemetry source must be a numpy array or list of state dicts; "
                f"got {type(source).__name__}"
            )

        # If the array came in as object dtype (because the caller put None
        # in some cells), replace None with NaN and coerce to float.
        if arr.dtype == object:
            arr = np.where(arr == None, np.nan, arr).astype(float)  # noqa: E711
        elif arr.dtype != np.float64:
            arr = arr.astype(float)

        self.array = arr

        if self.array.ndim != 2 or self.array.shape[1] != len(TELEMETRY_COLUMNS):
            raise ValueError(
                f"Telemetry array must have shape (n, {len(TELEMETRY_COLUMNS)}); "
                f"got shape {self.array.shape}"
            )

    # --- Access patterns ---

    def __getitem__(self, key):
        if key not in COLUMN_INDEX:
            raise KeyError(
                f"Unknown column {key!r}. Available: {list(COLUMN_INDEX)}"
            )
        return self.array[:, COLUMN_INDEX[key]]

    def __getattr__(self, name):
        # Only called if normal attribute lookup fails, so this won't shadow
        # self.array. Lets you do tlm.altitude_km instead of tlm["altitude_km"].
        if name in COLUMN_INDEX:
            return self.array[:, COLUMN_INDEX[name]]
        raise AttributeError(f"Telemetry has no column or attribute {name!r}")

    def __len__(self):
        return self.array.shape[0]

    # --- Convenience views ---

    @property
    def n_steps(self):
        return self.array.shape[0]

    @property
    def duration_s(self):
        if self.n_steps < 2:
            return 0.0
        return float(self["time_s"][-1] - self["time_s"][0])

    @property
    def dt_s(self):
        """Mean timestep in seconds (assumes uniform spacing)."""
        if self.n_steps < 2:
            return float("nan")
        return self.duration_s / (self.n_steps - 1)

    def time(self, unit="seconds"):
        """Return the time array in the requested unit."""
        t = self["time_s"]
        if unit == "seconds":
            return t
        if unit == "minutes":
            return t / 60.0
        if unit == "hours":
            return t / 3600.0
        if unit == "days":
            return t / 86400.0
        raise ValueError("unit must be 'seconds', 'minutes', 'hours', or 'days'")

    def position_km(self):
        return self.array[:, COLUMN_INDEX["x_km"]:COLUMN_INDEX["z_km"] + 1]

    def velocity_km_s(self):
        return self.array[:, COLUMN_INDEX["vx_km_s"]:COLUMN_INDEX["vz_km_s"] + 1]

    # --- Summary ---

    def summary(self, scenario_name=None):
        """Print a human-readable summary of the run to stdout."""
        print(_format_summary(self, scenario_name=scenario_name))


# ----------------------------------------------------------------------
# Pretty summary
# ----------------------------------------------------------------------

def _safe_stats(arr):
    """Return min/max/mean ignoring NaNs, or None if all-NaN."""
    if np.all(np.isnan(arr)):
        return None
    return float(np.nanmin(arr)), float(np.nanmax(arr)), float(np.nanmean(arr))


def _format_summary(tlm, scenario_name=None):
    """Build a human-readable summary string for a Telemetry object."""
    lines = []
    bar = "=" * 60

    title = "Simulation Summary"
    if scenario_name:
        title = f"Simulation Summary -- {scenario_name}"

    lines.append(bar)
    lines.append(title)
    lines.append(bar)

    # --- Run parameters ---
    lines.append("Run")
    lines.append(f"  timesteps          : {tlm.n_steps}")
    lines.append(f"  duration           : {tlm.duration_s:.1f} s "
                 f"({tlm.duration_s/3600:.3f} hr)")
    lines.append(f"  mean timestep      : {tlm.dt_s:.2f} s")

    # --- Orbit ---
    alt_stats = _safe_stats(tlm["altitude_km"])
    spd_stats = _safe_stats(tlm["speed_km_s"])
    if alt_stats is not None:
        lo, hi, mean = alt_stats
        lines.append("Orbit")
        lines.append(f"  altitude min/max   : {lo:>10.2f} / {hi:>10.2f} km")
        lines.append(f"  altitude mean      : {mean:>10.2f} km")
        if spd_stats is not None:
            lo, hi, mean = spd_stats
            lines.append(f"  speed    min/max   : {lo:>10.4f} / {hi:>10.4f} km/s")
            lines.append(f"  speed    mean      : {mean:>10.4f} km/s")

    # --- Eclipse ---
    ecl = tlm["in_eclipse"]
    if not np.all(np.isnan(ecl)):
        ecl_bool = ecl > 0.5
        eclipse_steps = int(np.sum(ecl_bool))
        eclipse_frac  = eclipse_steps / max(1, tlm.n_steps)
        eclipse_time  = eclipse_frac * tlm.duration_s
        lines.append("Eclipse")
        lines.append(f"  eclipse fraction   : {eclipse_frac*100:>6.2f} %")
        lines.append(f"  eclipse duration   : {eclipse_time:.1f} s "
                     f"({eclipse_time/60:.2f} min)")

    # --- Power ---
    pwr = tlm["instantaneous_power_W"]
    if not np.all(np.isnan(pwr)):
        lo, hi, mean = _safe_stats(pwr)
        # Energy: trapezoidal integral W * s -> J, convert to Wh
        # Only valid if dt is uniform-ish, but that's what we have.
        try:
            energy_j = float(np.trapezoid(np.nan_to_num(pwr), tlm["time_s"]))
        except AttributeError:
            # numpy < 2.0 fallback
            energy_j = float(np.trapz(np.nan_to_num(pwr), tlm["time_s"]))
        energy_wh = energy_j / 3600.0

        lines.append("Power")
        lines.append(f"  inst power min/max : {lo:>10.2f} / {hi:>10.2f} W")
        lines.append(f"  inst power mean    : {mean:>10.2f} W")
        lines.append(f"  energy generated   : {energy_wh:>10.2f} Wh "
                     f"({energy_j:.1f} J)")

    lines.append(bar)
    return "\n".join(lines)