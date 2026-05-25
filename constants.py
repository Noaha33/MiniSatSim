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

# Earth equatorial radius (WGS-84)
# Units: km
R_EARTH_EQUATORIAL = 6378.137

# Earth polar radius (WGS-84)
# Units: km
R_EARTH_POLAR = 6356.752

# Earth flattening (WGS-84)
# Units: dimensionless
EARTH_FLATTENING = 1.0 / 298.257223563

# Earth eccentricity squared (WGS-84)
# Units: dimensionless
EARTH_E2 = 6.69437999014e-3

# Earth J2 zonal harmonic
# Units: dimensionless
J2_EARTH = 1.08262668e-3

# Earth J3 zonal harmonic
# Units: dimensionless
J3_EARTH = -2.53265648e-6

# Earth J4 zonal harmonic
# Units: dimensionless
J4_EARTH = -1.61962159e-6

# Earth mass
# Units: kg
M_EARTH = 5.9722e24

# Earth surface gravity
# Units: m / s^2
G_EARTH_SURFACE = 9.80665

# Earth albedo (Bond albedo, average)
# Units: dimensionless
EARTH_ALBEDO = 0.30

# Earth IR emission (average outgoing longwave radiation)
# Units: W / m^2
EARTH_IR_FLUX = 237.0

# ----------------------------
# Sun constants
# ----------------------------

# Sun's standard gravitational parameter
# Units: km^3 / s^2
MU_SUN = 1.32712440018e11

# Sun radius
# Units: km
R_SUN = 695700.0

# Sun mass
# Units: kg
M_SUN = 1.98892e30

# Solar irradiance at 1 AU (solar constant)
# Units: W / m^2
SOLAR_FLUX_W_M2 = 1361.0

# Solar luminosity
# Units: W
L_SUN = 3.828e26

# ----------------------------
# Moon constants
# ----------------------------

# Moon's standard gravitational parameter
# Units: km^3 / s^2
MU_MOON = 4902.800066

# Moon radius
# Units: km
R_MOON = 1737.4

# Moon mass
# Units: kg
M_MOON = 7.342e22

# Mean Earth-Moon distance
# Units: km
EARTH_MOON_DISTANCE = 384400.0

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

# Speed of light
# Units: m / s
C_M_S = 299792458.0

# Universal gravitational constant
# Units: m^3 / (kg * s^2)
G_UNIVERSAL = 6.67430e-11

# Stefan-Boltzmann constant
# Units: W / (m^2 * K^4)
SIGMA_SB = 5.670374419e-8

# Boltzmann constant
# Units: J / K
K_BOLTZMANN = 1.380649e-23

# Planck constant
# Units: J * s
H_PLANCK = 6.62607015e-34

# Avogadro's number
# Units: 1 / mol
N_AVOGADRO = 6.02214076e23

# Universal gas constant
# Units: J / (mol * K)
R_GAS = 8.314462618

# Elementary charge
# Units: C
E_CHARGE = 1.602176634e-19

# ----------------------------
# Thermal constants
# ----------------------------

# Absolute zero in Celsius
# Units: deg C
ABSOLUTE_ZERO_C = -273.15

# Celsius to Kelvin offset
# Units: K
CELSIUS_TO_KELVIN = 273.15

# Typical spacecraft surface emissivities (dimensionless)
EMISSIVITY_BLACK_PAINT = 0.90
EMISSIVITY_WHITE_PAINT = 0.85
EMISSIVITY_MLI = 0.03
EMISSIVITY_ALUMINUM_POLISHED = 0.05
EMISSIVITY_SOLAR_CELL = 0.85

# Typical spacecraft surface absorptivities (dimensionless)
ABSORPTIVITY_BLACK_PAINT = 0.95
ABSORPTIVITY_WHITE_PAINT = 0.20
ABSORPTIVITY_MLI = 0.40
ABSORPTIVITY_ALUMINUM_POLISHED = 0.15
ABSORPTIVITY_SOLAR_CELL = 0.85

# Deep space background temperature (cosmic microwave background)
# Units: K
T_DEEP_SPACE = 2.7

# ----------------------------
# Time constants
# ----------------------------

SECONDS_PER_MINUTE = 60.0
SECONDS_PER_HOUR = 3600.0
SECONDS_PER_DAY = 86400.0
SECONDS_PER_WEEK = 604800.0
SECONDS_PER_YEAR_JULIAN = 31557600.0  # 365.25 days

MINUTES_PER_HOUR = 60.0
MINUTES_PER_DAY = 1440.0

HOURS_PER_DAY = 24.0
DAYS_PER_YEAR_JULIAN = 365.25

# Julian date of J2000 epoch (2000-01-01 12:00:00 TT)
JD_J2000 = 2451545.0

# Julian date of Unix epoch (1970-01-01 00:00:00 UTC)
JD_UNIX_EPOCH = 2440587.5

# ----------------------------
# Angle conversions
# ----------------------------

DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi

ARCSEC2RAD = math.pi / (180.0 * 3600.0)
RAD2ARCSEC = (180.0 * 3600.0) / math.pi

ARCMIN2RAD = math.pi / (180.0 * 60.0)
RAD2ARCMIN = (180.0 * 60.0) / math.pi

TWO_PI = 2.0 * math.pi
HALF_PI = math.pi / 2.0

# ----------------------------
# Distance conversions
# ----------------------------

KM_TO_M = 1000.0
M_TO_KM = 1.0 / 1000.0

KM_TO_AU = 1.0 / AU
AU_TO_KM = AU

KM_TO_MI = 0.621371
MI_TO_KM = 1.609344

M_TO_FT = 3.28084
FT_TO_M = 0.3048

# ----------------------------
# Mass conversions
# ----------------------------

KG_TO_G = 1000.0
G_TO_KG = 1.0 / 1000.0

KG_TO_LB = 2.20462
LB_TO_KG = 0.453592

# ----------------------------
# Energy / power conversions
# ----------------------------

J_TO_WH = 1.0 / 3600.0
WH_TO_J = 3600.0

J_TO_KWH = 1.0 / 3.6e6
KWH_TO_J = 3.6e6

W_TO_KW = 1.0 / 1000.0
KW_TO_W = 1000.0

# ----------------------------
# Pressure conversions
# ----------------------------

PA_TO_KPA = 1.0 / 1000.0
KPA_TO_PA = 1000.0

PA_TO_BAR = 1.0 / 1e5
BAR_TO_PA = 1e5

PA_TO_PSI = 1.0 / 6894.757
PSI_TO_PA = 6894.757

# ----------------------------
# Numerical tolerances
# ----------------------------

# General floating-point comparison tolerance
EPSILON = 1e-12

# Tolerance for Kepler's equation solver convergence
KEPLER_TOLERANCE = 1e-12

# Maximum iterations for iterative solvers
MAX_ITERATIONS = 100