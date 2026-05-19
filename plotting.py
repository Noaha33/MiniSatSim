import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from constants import R_EARTH


def plot_altitude(history_array, time_unit="seconds"):
    time_s = history_array[:, 0]
    altitude_km = history_array[:, 7]

    if time_unit == "seconds":
        time = time_s
        xlabel = "Time since epoch [s]"
    elif time_unit == "minutes":
        time = time_s / 60.0
        xlabel = "Time since epoch [min]"
    elif time_unit == "hours":
        time = time_s / 3600.0
        xlabel = "Time since epoch [hr]"
    else:
        raise ValueError("time_unit must be 'seconds', 'minutes', or 'hours'.")

    plt.figure()
    plt.plot(time, altitude_km)
    plt.xlabel(xlabel)
    plt.ylabel("Altitude [km]")
    plt.title("Satellite Altitude vs Time")
    plt.grid(True)
    plt.show()

def plot_orbit_3d(history_array, show_earth=True, max_points=1000):
    x = history_array[:, 1]
    y = history_array[:, 2]
    z = history_array[:, 3]

    # Downsample if there are too many points
    if len(x) > max_points:
        indices = np.linspace(0, len(x) - 1, max_points).astype(int)
        x = x[indices]
        y = y[indices]
        z = z[indices]

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(x, y, z, linewidth=1.5, label="Satellite orbit")

    ax.scatter(x[0], y[0], z[0], s=40, label="Start")
    ax.scatter(x[-1], y[-1], z[-1], s=40, label="End")

    if show_earth:
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 20)

        earth_x = R_EARTH * np.outer(np.cos(u), np.sin(v))
        earth_y = R_EARTH * np.outer(np.sin(u), np.sin(v))
        earth_z = R_EARTH * np.outer(np.ones_like(u), np.cos(v))

        ax.plot_surface(
            earth_x,
            earth_y,
            earth_z,
            alpha=0.3,
            linewidth=0,
            antialiased=False
        )

    max_range = max(
        x.max() - x.min(),
        y.max() - y.min(),
        z.max() - z.min(),
        2 * R_EARTH
    )

    mid_x = 0.5 * (x.max() + x.min())
    mid_y = 0.5 * (y.max() + y.min())
    mid_z = 0.5 * (z.max() + z.min())

    ax.set_xlim(mid_x - max_range / 2, mid_x + max_range / 2)
    ax.set_ylim(mid_y - max_range / 2, mid_y + max_range / 2)
    ax.set_zlim(mid_z - max_range / 2, mid_z + max_range / 2)

    ax.set_box_aspect([1, 1, 1])

    ax.set_xlabel("ECI x [km]")
    ax.set_ylabel("ECI y [km]")
    ax.set_zlabel("ECI z [km]")
    ax.set_title("Satellite Orbit in ECI Frame")

    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.show()

def plot_orbit_3d_plotly(history_array, show_earth=True, max_points=3000):
    """
    Interactive 3D orbit plot using Plotly.

    history_array columns:
    0: time_s
    1: x_km
    2: y_km
    3: z_km
    4: vx_km_s
    5: vy_km_s
    6: vz_km_s
    7: altitude_km
    8: speed_km_s
    """

    x = history_array[:, 1]
    y = history_array[:, 2]
    z = history_array[:, 3]
    time_s = history_array[:, 0]
    altitude_km = history_array[:, 7]
    speed_km_s = history_array[:, 8]

    # Downsample if there are too many points
    if len(x) > max_points:
        indices = np.linspace(0, len(x) - 1, max_points).astype(int)
        x = x[indices]
        y = y[indices]
        z = z[indices]
        time_s = time_s[indices]
        altitude_km = altitude_km[indices]
        speed_km_s = speed_km_s[indices]

    fig = go.Figure()

    # Orbit trajectory
    fig.add_trace(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            name="Orbit",
            line=dict(width=5),
            customdata=np.column_stack((time_s, altitude_km, speed_km_s)),
            hovertemplate=(
                "Time: %{customdata[0]:.1f} s<br>"
                "x: %{x:.2f} km<br>"
                "y: %{y:.2f} km<br>"
                "z: %{z:.2f} km<br>"
                "Altitude: %{customdata[1]:.2f} km<br>"
                "Speed: %{customdata[2]:.4f} km/s"
                "<extra></extra>"
            ),
        )
    )

    # Earth sphere
    if show_earth:
        u = np.linspace(0, 2 * np.pi, 60)
        v = np.linspace(0, np.pi, 30)

        earth_x = R_EARTH * np.outer(np.cos(u), np.sin(v))
        earth_y = R_EARTH * np.outer(np.sin(u), np.sin(v))
        earth_z = R_EARTH * np.outer(np.ones_like(u), np.cos(v))

        fig.add_trace(
            go.Surface(
                x=earth_x,
                y=earth_y,
                z=earth_z,
                name="Earth",
                opacity=0.45,
                showscale=False,
                hoverinfo="skip",
            )
        )

    # Axis scaling
    max_extent = max(
        np.max(np.abs(x)),
        np.max(np.abs(y)),
        np.max(np.abs(z)),
        R_EARTH,
    )

    axis_limit = 1.1 * max_extent

    fig.update_layout(
        title="Satellite Orbit in ECI Frame",
        scene=dict(
            xaxis=dict(title="ECI x [km]", range=[-axis_limit, axis_limit]),
            yaxis=dict(title="ECI y [km]", range=[-axis_limit, axis_limit]),
            zaxis=dict(title="ECI z [km]", range=[-axis_limit, axis_limit]),
            aspectmode="cube",
        ),
        legend=dict(x=0.02, y=0.98),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    # Start and end points
    start_point = np.array([x[0], y[0], z[0]])
    end_point = np.array([x[-1], y[-1], z[-1]])

    start_end_distance = np.linalg.norm(end_point - start_point)

    # Tolerance in km for deciding if start/end overlap
    overlap_tolerance_km = 1.0

    if start_end_distance < overlap_tolerance_km:
        fig.add_trace(
            go.Scatter3d(
                x=[x[0]],
                y=[y[0]],
                z=[z[0]],
                mode="markers",
                name="Start / End",
                marker=dict(size=7),
                hovertemplate=(
                    "Start / End<br>"
                    "x: %{x:.2f} km<br>"
                    "y: %{y:.2f} km<br>"
                    "z: %{z:.2f} km"
                    "<extra></extra>"
                ),
            )
        )
    else:
        fig.add_trace(
            go.Scatter3d(
                x=[x[0]],
                y=[y[0]],
                z=[z[0]],
                mode="markers",
                name="Start",
                marker=dict(size=7),
                hovertemplate=(
                    "Start<br>"
                    "x: %{x:.2f} km<br>"
                    "y: %{y:.2f} km<br>"
                    "z: %{z:.2f} km"
                    "<extra></extra>"
                ),
            )
        )

        fig.add_trace(
            go.Scatter3d(
                x=[x[-1]],
                y=[y[-1]],
                z=[z[-1]],
                mode="markers",
                name="End",
                marker=dict(size=7),
                hovertemplate=(
                    "End<br>"
                    "x: %{x:.2f} km<br>"
                    "y: %{y:.2f} km<br>"
                    "z: %{z:.2f} km"
                    "<extra></extra>"
                ),
            )
        )
    fig.show()