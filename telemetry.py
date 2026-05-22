from pathlib import Path
import numpy as np

def save_history_to_csv(filename, history_array):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    header = (
    "time_s,"
    "x_km,y_km,z_km,"
    "vx_km_s,vy_km_s,vz_km_s,"
    "altitude_km,speed_km_s,in_eclipse,"
    "body_x_eci_x,body_x_eci_y,body_x_eci_z,"
    "body_y_eci_x,body_y_eci_y,body_y_eci_z,"
    "body_z_eci_x,body_z_eci_y,body_z_eci_z"
    )

    np.savetxt(
        filename,
        history_array,
        delimiter=",",
        header=header,
        comments=""
    )