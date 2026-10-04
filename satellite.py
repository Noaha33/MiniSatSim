from orbit import propagate_keplerian_orbit
import numpy as np
from constants import R_EARTH
from eclipse import check_eclipse
from attitude import AttitudeCommand, update_attitude
from power import SolarPanel

class Satellite:
    def __init__(self, 
                name, 
                orbital_elements, 
                epoch, 
                central_body, 
                use_eclipse=True, 
                use_attitude=False, 
                attitude_command = None,
                use_solar_panels = False,
                solar_panels = None,
                power_loads = None,
                battery = None,
                ):
        
        self.name = name
        self.orbital_elements = orbital_elements
        self.epoch = epoch
        self.central_body = central_body
        self.solar_panels = solar_panels if solar_panels is not None else []
        
        self.power_loads = power_loads if power_loads is not None else []
        self.battery = battery
        self.total_power_draw_W = 0.0
        self.net_power_W = 0.0
        self.battery_soc_percent = battery.soc_percent if battery is not None else np.nan
        self._power_time_s = None
        self._previous_net_power_W = None

        self.use_eclipse = use_eclipse
        self.use_attitude = use_attitude
        self.attitude_command = attitude_command 
        self.use_solar_panels = use_solar_panels      
        
        self.time_since_epoch = 0.0
        self.position_km = None
        self.velocity_km_s = None
        self.attitude = None
        self.altitude_km = None
        self.speed_km_s = None
        self.in_eclipse = None
        self.instantaneous_power_W = None
        self.history = []
        
        if self.use_attitude and attitude_command is None:
            raise ValueError("To use attitude an attitude command must be given there is no passive attitude propagation yet")

        if self.use_solar_panels and (not self.use_eclipse or not self.use_attitude):
            raise ValueError("To use solar panel model eclipse and attitude modeling are required")
        
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
        
        if self.use_solar_panels:
            self.instantaneous_power_W = 0
            
            for panel in self.solar_panels:
                self.instantaneous_power_W += panel.compute_inst_power_W(
                    self.attitude,
                    self.position_km,
                    self.in_eclipse
                )    
        else: 
            self.instantaneous_power_W = None
        self.total_power_draw_W = sum(
            load.compute_average_power_W() for load in self.power_loads
        )
        generated_power_W = self.instantaneous_power_W if self.use_solar_panels else 0.0
        self.net_power_W = generated_power_W - self.total_power_draw_W
        if self.battery is not None:
            if self._power_time_s is not None:
                # Treat the previous sample's power as constant over this interval.
                self.battery.update(
                    self._previous_net_power_W,
                    time_since_epoch - self._power_time_s,
                )
            self.battery_soc_percent = self.battery.soc_percent
        self._power_time_s = time_since_epoch
        self._previous_net_power_W = self.net_power_W

    def propagate_history(self, final_time_since_epoch, time_step, time_unit):
        self.history = []
        self._power_time_s = None
        self._previous_net_power_W = None
        if self.battery is not None:
            self.battery.reset()
        if time_unit == "seconds":
            time_step_s = time_step
        elif time_unit == "minutes":
            time_step_s = time_step*60
        elif time_unit == "hours":
            time_step_s = time_step*3600
        else:
            raise ValueError("Acceptable time units are, seconds, minutes and hours")
        
        if not np.isfinite(time_step_s) or time_step_s <= 0:
            raise ValueError("time_step must be finite and positive")
        if not np.isfinite(final_time_since_epoch) or final_time_since_epoch < 0:
            raise ValueError("final_time_since_epoch must be finite and nonnegative")
        times = np.append(np.arange(0.0, final_time_since_epoch, time_step_s),
                          final_time_since_epoch)

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
            "instantaneous_power_W": self.instantaneous_power_W,
            "total_power_draw_W": self.total_power_draw_W,
            "net_power_W": self.net_power_W,
            "battery_soc_percent": self.battery_soc_percent
        }
        
    # FOR FUTURE TO SELF PLEASE START ADDING FRAMES FOR THE FUTURE    
    def get_position_eci(self):
        return self.position_km
    
    def get_velocity_eci(self):
        return self.velocity_km_s
    
    def get_in_eclipse(self):
        return self.in_eclipse
    
    def get_attitude_axes_for_telemetry(self, attitude):
        if attitude is None:
            nan_axis = np.array([np.nan, np.nan, np.nan])
            return nan_axis, nan_axis, nan_axis

        return attitude.body_x_eci, attitude.body_y_eci, attitude.body_z_eci
    
    def get_attitude(self):
        return self.attitude
        
    def get_history_array(self):
        from telemetry import history_to_array
        return history_to_array(self.history)
