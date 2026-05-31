"""
iss_sat.py

A basic ISS orbit propagation scenario:

Run from project root:
    python -m scenarios.normal_sat
"""
from datetime import datetime
import math

from orbit import OrbitalElements, compute_orbital_period
from satellite import Satellite
from telemetry import Telemetry, save_history_to_csv
from plotting import (
    plot_altitude,
    plot_eclipse_tracker,
    plot_orbit_3d_plotly,
)

NAME = "ISS_sat"
EPOCH = datetime(2026, 1, 1)
N_ORBITS = 2

orbital_elements = OrbitalElements(
    semi_major_axis_km=6786.0,
    eccentricity=0.0003,
    inclination_rad=math.radians(51.6),
    raan_rad=math.radians(0.0),
    argument_of_perigee_rad=math.radians(0.0),
    true_anomaly_rad=math.radians(0.0),
)

sat = Satellite(
    name=NAME,
    orbital_elements=orbital_elements,
    epoch=EPOCH,
    central_body="Earth",
    use_eclipse=True,
    use_attitude=False,
    attitude_command=None,
    use_solar_panels=False,
    solar_panels=None,
)

period_s = compute_orbital_period(orbital_elements)
print(f"[{NAME}] period = {period_s / 3600:.3f} hr, "
      f"propagating {N_ORBITS} orbit(s)")

sat.propagate_history(
    final_time_since_epoch=period_s * N_ORBITS,
    time_step=30,
    time_unit="seconds",
)




# Plots and TLM 
history_array = sat.get_history_array()
tlm = Telemetry(history_array)
tlm.summary(scenario_name=NAME)

save_history_to_csv(f"data/{NAME}.csv", history_array)
print(f"[{NAME}] saved data/{NAME}.csv")

plot_altitude(history_array, time_unit="hours")
plot_eclipse_tracker(history_array, time_unit="hours")
plot_orbit_3d_plotly(history_array)