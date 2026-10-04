# Eventually create the power object hierarchy. For now just solar panel.
# Solar panel model, low fidelity no solar degradation, will add in more later
# Eclipse is fully or none (add cylindrical later) 

from dataclasses import dataclass
import numpy as np
from attitude import AttitudeState
from constants import SOLAR_FLUX_W_M2, AU
from environment import get_sat_to_sun_distance, get_sat_to_sun_direction

@dataclass 
class SolarPanel:
    surface_area_m_2: float
    cell_efficiency: float
    panel_normal: str
    
    def compute_inst_power_W(self, attitude, position, in_eclipse):
        # Placeholder for when I add the higher fidelity panel stuff
        if in_eclipse:
            sunlit_factor = 0.0
        else:
            sunlit_factor = 1.0
        incidence = self.compute_panel_sun_incidence(attitude, position)  
        solar_irradiance = self.compute_solar_irradiance(position) 
        
        inst_power_W = sunlit_factor * solar_irradiance * self.surface_area_m_2 * self.cell_efficiency * incidence
        
        return inst_power_W
        
        
    def compute_panel_sun_incidence(self, attitude, position):
        panel_normal_eci = attitude.get_body_axis(self.panel_normal)
        sun_direction_eci = get_sat_to_sun_direction(position)
        
        incidence = max(0.0, np.dot(panel_normal_eci, sun_direction_eci))
        return incidence
    
    def compute_solar_irradiance(self, position):
        sat_sun_distance = get_sat_to_sun_distance(position)
        abs_distance= np.linalg.norm(sat_sun_distance)
        
        solar_irradiance = SOLAR_FLUX_W_M2 * (AU/abs_distance)**2
        return solar_irradiance


@dataclass
class PowerLoad:
    name: str
    power_draw_W: float
    duty_cycle: float = 1.0

    def compute_average_power_W(self):
        return self.power_draw_W * self.duty_cycle


@dataclass
class Battery:
    capacity_Wh: float
    initial_soc_percent: float = 100.0
    max_charge_percent: float = 100.0

    def __post_init__(self):
        self.reset()

    def reset(self):
        self.energy_Wh = self.capacity_Wh * self.initial_soc_percent / 100.0

    @property
    def soc_percent(self):
        return 100.0 * self.energy_Wh / self.capacity_Wh

    def update(self, net_power_W, time_step_s):
        energy_change_Wh = net_power_W * time_step_s / 3600.0
        max_energy_Wh = self.capacity_Wh * self.max_charge_percent / 100.0
        self.energy_Wh = float(np.clip(
            self.energy_Wh + energy_change_Wh, 0.0, max_energy_Wh
        ))
        return self.soc_percent
