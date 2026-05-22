import numpy as np
from constants import R_EARTH
from environment import get_earth_to_sun_direction

# Cylindrical eclipse checker returns 1 if in partial or full eclipse 0 if not
def check_eclipse(sat_position_km):
    earth_sun_vec = get_earth_to_sun_direction()
    
    # Project sat onto sun direction
    r_parallel = np.dot(sat_position_km, earth_sun_vec)

    # Find perpindicular distance from axis 
    r_perp = np.linalg.norm(sat_position_km - r_parallel * earth_sun_vec)

    # 1 means sat in eclipse 
    # 0 means sat sunlit
    if r_parallel < 0 and r_perp < R_EARTH:
        return 1
    return 0