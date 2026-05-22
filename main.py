"""
Current file for running satellite scenarios
I play to more to json and jupyter notebooks in the futire 

This file defines:
- the initial orbit
- the epoch
- the simulation duration
- the timestep
- what outputs/plots to generate
"""

from datetime import datetime
import math

from orbit import OrbitalElements, compute_orbital_period
from satellite import Satellite
from telemetry import save_history_to_csv
from attitude import AttitudeCommand
from plotting import *

# Output options

# Save sat history in /data
SAVE_CSV = True

# Plot Altitude to current non-rotating perfectly spherical earth at [0,0,0]
# I plan to incorperate WGS-84 and accurate altitude calculations 
PLOT_ALTITUDE = True

# Plots Eclipse time history 
# I plan to propagate both earth and sun and use a more accurate eclipse model in the future
PLOT_ECLIPSE = True

# Plots the orbit in matplotlib window
# Laggy unrecommended
PLOT_3D_MATPLOTLIB = True
# Same as above plots in local host browser recommended 
PLOT_3D_PLOTLY = True

# Plots and saves a static frame animation of satellite orbit and eclipse timings 
MAKE_STATIC_ANIMATION_MP4 = True

# Plots and saves a dynamic (frame rotates) frame animation of satellite orbit and eclipse timings 
# Kinda cool but nauseating
MAKE_DYNAMIC_ANIMATION_MP4 = True


# Simulation setup
SATELLITE_NAME = "MiniSat-1"

# Only earth works now but I plan to allow for Sun frame moon orbits ect
CENTRAL_BODY = "Earth"

# Doesnt really do anything yet I plan to add spice files and more accurate orbit prop
EPOCH = datetime(2026, 1, 1, 0, 0, 0)

# Set time step size you can also
TIME_STEP = 5
TIME_UNIT = "minutes"

# Set what percent of orbital period should be modeled 
# 0.5 = half and orbit
# 2.0 = two orbits (no pertubations or anything really intresting yet)
ORBITAL_PERIOD_FRAC = 1

# Set CSV output path
OUTPUT_CSV_FILE = "data/minisat_history.csv"


# Initial orbit
# Set orbital elements 
initial_orbit = OrbitalElements(
    semi_major_axis_km=17000.0,
    eccentricity=0.5,
    inclination_rad=math.radians(81.6),
    raan_rad=math.radians(5.6),
    argument_of_perigee_rad=math.radians(67.7),
    true_anomaly_rad=math.radians(6.7),
)


# ============================================================
# Run simulation
# ============================================================

orbital_period_s = compute_orbital_period(initial_orbit)

attitude_command = AttitudeCommand(
    mode="Sun Track",
    body_axis="+X",
)

attitude_command2 = AttitudeCommand(
    mode="Nadir Track",
    body_axis="+Z",
)

sat = Satellite(
    name=SATELLITE_NAME,
    orbital_elements=initial_orbit,
    epoch=EPOCH,
    central_body=CENTRAL_BODY,
    use_eclipse=True,
    use_attitude=True,
    attitude_command = attitude_command,
)

print(f"Running simulation for {SATELLITE_NAME}")
print(f"Orbital period: {orbital_period_s / 3600:.3f} hours")
print(f"Timestep: {TIME_STEP} {TIME_UNIT}")

sat.propagate_history(
    final_time_since_epoch=orbital_period_s*ORBITAL_PERIOD_FRAC,
    time_step=TIME_STEP,
    time_unit=TIME_UNIT,
)

history_array = sat.get_history_array()

if SAVE_CSV:
    save_history_to_csv(OUTPUT_CSV_FILE, history_array)
    print(f"Saved telemetry to {OUTPUT_CSV_FILE}")

if PLOT_ALTITUDE:
    plot_altitude(history_array, time_unit="hours")

if PLOT_ECLIPSE:
    plot_eclipse_tracker(history_array, time_unit="hours")

if PLOT_3D_MATPLOTLIB:
    plot_orbit_3d(history_array)

if PLOT_3D_PLOTLY:
    plot_orbit_3d_plotly(history_array)

# Max points sets how many points are graphed this can downsize the data
# Loops is animation loops 
# elev and azim set the perspective of the animation 
if MAKE_STATIC_ANIMATION_MP4:
    plot_orbit_animation_mp4(
        history_array,
        name="static",
        fps=30,
        max_points=1300,
        loops=2,
        time_unit="hours",
        elev=90,
        azim=0,
    )

# This is pretty useless right now 
if MAKE_DYNAMIC_ANIMATION_MP4:
    plot_orbit_animation_mp4(
        history_array,
        name="dynamic",
        fps=30,
        max_points=1300,
        loops=1,
        time_unit="hours",
        rotate=True,
    )

print("Simulation complete.")