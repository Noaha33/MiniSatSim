import numpy as np
from constants import AU
from math_helpers import normalize

# Keep positions as single points for now

SUN_POSITION_ECI_KM = np.array([AU, 0.0, 0.0])
EARTH_POSITION_ECI_KM = np.array([0.0, 0.0, 0.0])

def get_sun_position_eci():
    return SUN_POSITION_ECI_KM

def get_earth_position_eci():
    return EARTH_POSITION_ECI_KM

def get_sat_to_sun_distance(sat_position_km):
    sun_position = get_sun_position_eci()
    return sun_position-sat_position_km

def get_earth_to_sat_distance(sat_position_km):
    earth_position = get_earth_position_eci()
    return earth_position-sat_position_km
    

def get_sat_to_sun_direction(sat_position_km):
    sun_position = get_sun_position_eci()
    sun_vector = sun_position-sat_position_km
    return normalize(sun_vector)

def get_earth_to_sun_direction():
    sun_position = get_sun_position_eci()
    earth_position = get_earth_position_eci()
    sun_vector = sun_position-earth_position
    return normalize(sun_vector)

def get_nadir_point_direction(sat_position_km):
    earth_position = get_earth_position_eci()
    nadir_vector = earth_position - sat_position_km 
    return normalize(nadir_vector)