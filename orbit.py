from dataclasses import dataclass
import math
import numpy as np

from constants import MU_EARTH


@dataclass
class OrbitalElements:
    semi_major_axis_km: float
    eccentricity: float
    inclination_rad: float
    raan_rad: float
    argument_of_perigee_rad: float
    true_anomaly_rad: float
    
    
def compute_orbital_period(orbital_elements: OrbitalElements):
    """
    Outputs orbital period in seconds to simulate a single orbital period easily 
    
    """
    a = orbital_elements.semi_major_axis_km

    if a <= 0:
        raise ValueError("Semi-major axis must be positive.")
    
    period = 2 * math.pi * math.sqrt(a**3/MU_EARTH)
    
    return period


def elements_to_state(orbital_elements: OrbitalElements):
    """
    Outputs position and velocity in km and km_s
    position_km: numpy array [x,y,z]
    velocity same thing
    """
    a = orbital_elements.semi_major_axis_km
    e = orbital_elements.eccentricity
    i = orbital_elements.inclination_rad
    raan = orbital_elements.raan_rad
    arg_perigee = orbital_elements.argument_of_perigee_rad
    true_anomaly = orbital_elements.true_anomaly_rad
    
    if a <= 0:
        raise ValueError("Semi-major axis must be positive.")

    if not (0 <= e < 1):
        raise ValueError("All orbits must be elliptical")
    
    # Semi latus
    p = a * (1 - e**2)
    
    # Radius mag (center of earth)
    r_mag = p / (1 + e*math.cos(true_anomaly))
    # Velocity mag 
    v_mag = math.sqrt(MU_EARTH / p)

    # Compute position and velocity in perifocal frame Qhat and Phat 
    r_perifocal = np.array([
        r_mag * math.cos(true_anomaly),
        r_mag * math.sin(true_anomaly),
        0.0
    ])

    v_perifocal = np.array([
        -v_mag * math.sin(true_anomaly),
        v_mag * (e + math.cos(true_anomaly)),
        0.0
    ])
    
    # Create rotation matricies for perifocal to ECI 
    R3_raan = np.array([
        [math.cos(raan), -math.sin(raan), 0],
        [math.sin(raan),  math.cos(raan), 0],
        [0, 0, 1]
    ])
    
    R1_i = np.array([
        [1, 0, 0],
        [0,  math.cos(i), -math.sin(i)],
        [0,  math.sin(i), math.cos(i)]
    ])
    
    R3_arg_perigee = np.array([
        [math.cos(arg_perigee), -math.sin(arg_perigee), 0],
        [math.sin(arg_perigee),  math.cos(arg_perigee), 0],
        [0, 0, 1]
    ])
    
    rotation_matrix = R3_raan @ R1_i @ R3_arg_perigee
    
    # Transform position and velocity to ECI coordinate frame
    position_km_0 = rotation_matrix @ r_perifocal
    velocity_km_s_0 = rotation_matrix @ v_perifocal
    
    return position_km_0, velocity_km_s_0


def propagate_keplerian_orbit(orbital_elements: OrbitalElements, time_since_epoch):
    # Convert initial orbital elements to initial state
    position_0_km, velocity_0_km_s = elements_to_state(orbital_elements)

    # Propagate to desired time using lagrange coeffs
    position_km, velocity_km_s = propagate_f_and_g(orbital_elements, position_0_km,velocity_0_km_s,time_since_epoch)

    return position_km, velocity_km_s

def propagate_f_and_g(orbital_elements: OrbitalElements, position_0_km, velocity_0_km_s, time_since_epoch):
    # Propagate position and velocity using Lagrange f and g coefficients.

    r0_mag = np.linalg.norm(position_0_km)

    a = orbital_elements.semi_major_axis_km
    e = orbital_elements.eccentricity
    true_anomaly_0 = orbital_elements.true_anomaly_rad

    if a <= 0:
        raise ValueError("Semi-major axis must be positive.")

    if not (0 <= e < 1):
        raise ValueError("Only elliptical orbits are supported.")

    # Convert initial true anomaly to initial eccentric anomaly
    E0 = 2 * math.atan2(
        math.sqrt(1 - e) * math.sin(true_anomaly_0 / 2),
        math.sqrt(1 + e) * math.cos(true_anomaly_0 / 2)
    )

    # Initial mean anomaly
    M0 = E0 - e * math.sin(E0)

    # Mean motion
    n = math.sqrt(MU_EARTH / a**3)

    # Mean anomaly at requested time
    M = M0 + n * time_since_epoch

    # Initial guess for eccentric anomaly
    E = M

    # Solve Kepler's equation
    for _ in range(30):
        f_kepler = E - e * math.sin(E) - M
        f_prime_kepler = 1 - e * math.cos(E)
        correction  = -f_kepler / f_prime_kepler
        E += correction 

        if abs(correction) < 1e-12:
            break
    delta_E = E - E0
        
    # Lagrange f and g coefficients
    f = 1 - (a / r0_mag) * (1 - math.cos(delta_E))

    g = time_since_epoch - math.sqrt(a**3 / MU_EARTH) * (delta_E - math.sin(delta_E))

    # New position
    position_km = f * position_0_km + g * velocity_0_km_s
    r_mag = np.linalg.norm(position_km)

    # Time derivatives of f and g
    f_dot = -math.sqrt(MU_EARTH * a) / (r_mag * r0_mag) * math.sin(delta_E)

    g_dot = 1 - (a / r_mag) * (1 - math.cos(delta_E))

    # New velocity
    velocity_km_s = f_dot * position_0_km + g_dot * velocity_0_km_s

    return position_km, velocity_km_s