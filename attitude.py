from dataclasses import dataclass
import numpy as np
from environment import get_sat_to_sun_direction, get_nadir_point_direction
from math_helpers import normalize

@dataclass 
class AttitudeCommand:
    mode: str
    body_axis: str


# Dataclass to store attitude states 
# negative directions directly determined by current state
@dataclass
class AttitudeState:
    body_x_eci: np.ndarray
    body_y_eci: np.ndarray
    body_z_eci: np.ndarray
    
    @property
    def body_neg_x_eci(self) -> np.ndarray:
        return -self.body_x_eci

    @property
    def body_neg_y_eci(self) -> np.ndarray:
        return -self.body_y_eci

    @property
    def body_neg_z_eci(self) -> np.ndarray:
        return -self.body_z_eci
    
# Tracking method allows user to choose body_axis they desire 
# Depending on mode (sun, nadir, moon, more later) desired body axis will point to to the 
# Desired position in eci coords 
def update_attitude(position_eci, attitude_command):
    mode = attitude_command.mode
    body_axis = attitude_command.body_axis
    if mode == "Sun Track":
        # Returns normalized pointing vector 
        point_vec = get_sat_to_sun_direction(position_eci)
    elif mode == "Nadir Track":
        # Returns normalized pointing vector 
        point_vec = get_nadir_point_direction(position_eci)
    else:
        raise ValueError('Acceptable track modes are "Sun Track" and "Nadir Track"')
    
    # Create vector basis (primary axis is always the vector that should be aligned with the body axis)
    primary_axis, second_axis, third_axis = create_vector_basis(point_vec)
    
    # Create axis map to choose correct triad according to RHR
    axis_map = {
        '+X': (primary_axis, second_axis, third_axis),
        '-X': (-primary_axis, second_axis, -third_axis),
        '+Y': (third_axis, primary_axis, second_axis),
        '-Y': (-third_axis, -primary_axis, second_axis),
        '+Z': (second_axis, third_axis,primary_axis),
        '-Z': (-second_axis, third_axis, -primary_axis),
    }
    
    if body_axis not in axis_map:
        raise ValueError(f"body_axis must be one of {list(axis_map)}")
    
    body_x,body_y,body_z = axis_map[body_axis]
    
    return AttitudeState(body_x_eci=body_x, body_y_eci=body_y, body_z_eci=body_z)
        
def create_vector_basis(point_vec):
    primary_axis = normalize(point_vec)

    # Choose arbitrary vector
    helper_axis = np.array([0.0,0.0,1.0])
    
    # Ensure arbitrary vector is not nearly pointing vector 
    if abs(np.dot(primary_axis, helper_axis)) > 0.99:
        helper_axis = np.array([1.0,0.0,0.0])
    
    # Gram Schmidt Process
    second_axis = normalize(helper_axis - np.dot(helper_axis,primary_axis)*primary_axis)
    third_axis = np.cross(primary_axis,second_axis)
    
    return primary_axis, second_axis, third_axis