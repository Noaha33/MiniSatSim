from datetime import datetime
import math

from orbit import OrbitalElements, compute_orbital_period
from satellite import Satellite
from telemetry import save_history_to_csv
from plotting import plot_altitude, plot_orbit_3d_plotly, plot_orbit_3d



orbit = OrbitalElements(
    semi_major_axis_km=17000.0,
    eccentricity=0.5,
    inclination_rad=math.radians(51.6),
    raan_rad=math.radians(5.6),
    argument_of_perigee_rad=math.radians(6.7),
    true_anomaly_rad=math.radians(6.7)
)

epoch = datetime(2026, 1, 1, 0, 0, 0)
epoch2 = datetime(2026, 1, 2, 1, 0, 0)
time_seconds = (epoch2 - epoch).total_seconds()
period = compute_orbital_period(orbit) 

sat = Satellite(
    name="MiniSat-1",
    orbital_elements=orbit,
    epoch=epoch,
    central_body="Earth"
)

"""
sat.propagate_to(0.0)
print(sat.get_state())

sat.propagate_to(time_seconds)
print(sat.get_state())
"""
time_step = 5
time_unit = "seconds"
sat.propagate_history(period*.5, time_step, time_unit)
history_array = sat.get_history_array()

save_history_to_csv("data/minisat_history_half_orbit.csv", history_array)
plot_altitude(history_array, time_unit="hours")
plot_orbit_3d_plotly(history_array)