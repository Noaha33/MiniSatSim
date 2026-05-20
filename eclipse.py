import numpy as np
from constants import R_EARTH
from enviroment import get_earth_to_sun_direction

# Cylindrical eclipse checker returns 0 if in partial or full eclipse 1 if not
def check_eclipse(sat_position_km):
    earth_sun_vec = get_earth_to_sun_direction()
    
    # Project sat onto sun direction
    r_parallel = np.dot(sat_position_km, earth_sun_vec)

    # Find perpindicular distance from axis 
    r_perp = np.linalg.norm(sat_position_km - r_parallel * earth_sun_vec)

    # If both conditions met sat in eclipse
    if r_parallel < 0 and r_perp < R_EARTH:
        return 1
    return 0