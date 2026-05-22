from orbit import propagate_keplerian_orbit
import numpy as np
from constants import R_EARTH
from eclipse import check_eclipse
from attitude import AttitudeCommand, update_attitude


class Satellite:
    def __init__(self, 
                name, 
                orbital_elements, 
                epoch, 
                central_body, 
                use_eclipse=True, 
                use_attitude=False, 
                attitude_command = None
                ):
        
        self.name = name
        self.orbital_elements = orbital_elements
        self.epoch = epoch
        self.central_body = central_body
        
        self.use_eclipse = use_eclipse
        self.use_attitude = use_attitude
        self.attitude_command = attitude_command        
        
        self.time_since_epoch = 0.0
        self.position_km = None
        self.velocity_km_s = None
        self.attitude = None
        self.altitude_km = None
        self.speed_km_s = None
        self.in_eclipse = None
        self.history = []
        
        if self.use_attitude and attitude_command is None:
            raise ValueError("To use attitude an attitude command must be given there is no passive attitude propagation yet")

    def propagate_to(self, time_since_epoch):
        self.time_since_epoch = time_since_epoch

        self.position_km, self.velocity_km_s = propagate_keplerian_orbit(
            self.orbital_elements,
            time_since_epoch
        )

        radius_km = np.linalg.norm(self.position_km)
        self.altitude_km = radius_km - R_EARTH
        self.speed_km_s = np.linalg.norm(self.velocity_km_s)
        
        if self.use_eclipse:
            self.in_eclipse = check_eclipse(self.position_km)
        else:
            self.in_eclipse = None
        
        if self.use_attitude:
            self.attitude = update_attitude(position_eci = self.position_km, 
                                            attitude_command = self.attitude_command)
        else:
            self.attitude = None
    
    def propagate_history(self, final_time_since_epoch, time_step, time_unit):
        self.history = []
        if time_unit == "seconds":
            time_step_s = time_step
        elif time_unit == "minutes":
            time_step_s = time_step*60
        elif time_unit == "hours":
            time_step_s = time_step*3600
        else:
            raise ValueError("Acceptable time units are, seconds, minutes and hours")
        
        num_steps = int(final_time_since_epoch/time_step_s)

        times = np.linspace(0.0, final_time_since_epoch, num_steps + 1)

        for time_since_epoch in times:
            self.propagate_to(time_since_epoch)
            self.save_state_to_history()
        
    def save_state_to_history(self):
        self.history.append(self.get_state())

    def get_state(self):
        return {
            "name": self.name,
            "epoch": self.epoch,
            "time_since_epoch": self.time_since_epoch,
            "position_km": self.position_km,
            "velocity_km_s": self.velocity_km_s,
            "altitude_km": self.altitude_km,
            "speed_km_s": self.speed_km_s,
            "in_eclipse": self.in_eclipse,
            "attitude": self.attitude,
        }
        
    # FOR FUTURE TO SELF PLEASE START ADDING FRAMES FOR THE FUTURE    
    def get_position_eci(self):
        return self.position_km
    
    def get_velocity_eci(self):
        return self.velocity_km_s
    
    def get_in_eclipse(self):
        return self.in_eclipse
    
    def get_attitude(self):
        return self.attitude
        
    def get_history_array(self):
        rows = []

        for state in self.history:
            position = state["position_km"]
            velocity = state["velocity_km_s"]

            row = [
                state["time_since_epoch"],
                position[0],
                position[1],
                position[2],
                velocity[0],
                velocity[1],
                velocity[2],
                state["altitude_km"],
                state["speed_km_s"],
                state["in_eclipse"]
            ]
            rows.append(row)
        return np.array(rows)

        