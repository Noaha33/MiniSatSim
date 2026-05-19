"""
constants.py

Physical and unit conversion constants for MiniSatSimPractice.

Units:
- Distance: km unless otherwise noted
- Time: seconds
- Angles: radians unless otherwise noted
"""

import math

# ----------------------------
# Earth constants
# ----------------------------

# Earth's standard gravitational parameter
# Units: km^3 / s^2
MU_EARTH = 398600.4418

# Mean Earth radius
# Units: km
R_EARTH = 6378.137

# Earth rotation rate
# Units: rad / s
OMEGA_EARTH = 7.2921159e-5

# ----------------------------
# General physical constants
# ----------------------------

# Standard gravity at Earth's surface
# Units: m / s^2
G0 = 9.80665

# Astronomical unit
# Units: km
AU = 149597870.7

# Speed of light
# Units: km / s
C = 299792.458

# ----------------------------
# Time constants
# ----------------------------

SECONDS_PER_MINUTE = 60.0
SECONDS_PER_HOUR = 3600.0
SECONDS_PER_DAY = 86400.0

# ----------------------------
# Angle conversions
# ----------------------------

DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi