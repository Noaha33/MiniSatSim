import numpy as np


def save_history_to_csv(filename, history_array):
    header = "time_s,x_km,y_km,z_km,vx_km_s,vy_km_s,vz_km_s,altitude_km,speed_km_s"

    np.savetxt(
        filename,
        history_array,
        delimiter=",",
        header=header,
        comments=""
    )