from datetime import datetime
from pathlib import Path
import math
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from attitude import AttitudeCommand
from power import SolarPanel, PowerLoad, Battery
from orbit import OrbitalElements, compute_orbital_period
from satellite import Satellite
from telemetry import Telemetry, save_history_to_csv
from plotting import plot_battery_soc


NAME = "ISS_sat"
EPOCH = datetime(2026, 1, 1)
N_ORBITS = 9

orbital_elements = OrbitalElements(
    semi_major_axis_km=6786.0,
    eccentricity=0.0003,
    inclination_rad=math.radians(51.6),
    raan_rad=0.0,
    argument_of_perigee_rad=0.0,
    true_anomaly_rad=0.0,
)
attitude_command = AttitudeCommand(mode="Sun Track", body_axis="+X")
solar_panels = [
    SolarPanel(surface_area_m_2=75, cell_efficiency=0.30, panel_normal="+X"),
    SolarPanel(surface_area_m_2=75, cell_efficiency=0.30, panel_normal="+X"),
]

power_loads = [
    PowerLoad(name="Total", power_draw_W=67*1000, duty_cycle=0.4),
]
battery = Battery(
    capacity_Wh=30*1000.0,
    initial_soc_percent=80.0,
    max_charge_percent=95.0,
)

sat = Satellite(
    name=NAME,
    orbital_elements=orbital_elements,
    epoch=EPOCH,
    central_body="Earth",
    use_eclipse=True,
    use_attitude=True,
    attitude_command=attitude_command,
    use_solar_panels=True,
    solar_panels=solar_panels,
    power_loads=power_loads,
    battery=battery,
)
period_s = compute_orbital_period(orbital_elements)
print(f"[{NAME}] period = {period_s / 3600:.3f} hr, propagating {N_ORBITS} orbit(s)")
sat.propagate_history(
    final_time_since_epoch=period_s * N_ORBITS,
    time_step=30,
    time_unit="seconds",
)

history_array = sat.get_history_array()
tlm = Telemetry(history_array)
tlm.summary(scenario_name=NAME)
output_csv = PROJECT_ROOT / "data" / f"{NAME}.csv"
save_history_to_csv(output_csv, history_array)
# print(f"[{NAME}] saved {output_csv}")
# print(f"Average load: {sat.total_power_draw_W:.1f} W")
# print(f"Final battery SOC: {battery.soc_percent:.1f}%")

plot_battery_soc(history_array, time_unit="hours",
                 max_charge_percent=battery.max_charge_percent)
# plot_power(history_array, time_unit="hours")
# plot_altitude(history_array, time_unit="hours")
# plot_eclipse_tracker(history_array, time_unit="hours")
# plot_orbit_3d_plotly(history_array)
