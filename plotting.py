import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import imageio_ffmpeg
matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()

import plotly.graph_objects as go
from constants import R_EARTH
from environment import get_earth_to_sun_direction
import json
import webbrowser
from pathlib import Path

def plot_eclipse_tracker(history_array, time_unit="minutes"):
    """
    Plots altitude with eclipse periods shaded, plus a binary
    eclipse state plot below.
    """
    time_s = history_array[:, 0]
    altitude_km = history_array[:, 7]

    if history_array.shape[1] < 10:
        raise ValueError("history_array must include in_eclipse column at index 9")

    in_eclipse = history_array[:, 9].astype(int)

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

    fig, (ax1, ax2) = plt.subplots(
        2, 1, sharex=True, figsize=(10, 6),
        gridspec_kw={"height_ratios": [3, 1]}
    )

    # Altitude plot with eclipse shading
    ax1.plot(time, altitude_km, color="C0", linewidth=1.5, label="Altitude")
    ax1.fill_between(
        time, altitude_km.min(), altitude_km.max(),
        where=(in_eclipse == 1),
        alpha=0.25, color="gray", step="post", label="Eclipse"
    )
    ax1.set_ylabel("Altitude [km]")
    ax1.set_title("Satellite Altitude with Eclipse Periods")
    ax1.grid(True)
    ax1.legend(loc="upper right")

    # Eclipse state plot
    ax2.fill_between(time, 0, in_eclipse, step="post", alpha=0.6, color="gray")
    ax2.plot(time, in_eclipse, drawstyle="steps-post", color="black", linewidth=1)
    ax2.set_ylabel("State")
    ax2.set_xlabel(xlabel)
    ax2.set_ylim(-0.1, 1.1)
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["Sunlit", "Eclipse"])
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

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
def plot_orbit_animation_mp4(history_array, name="default",
                              fps=30, max_points=500, show_earth=True,
                              loops=1, time_unit="seconds",
                              elev=25, azim=45, rotate=False,
                              show_body_axes=True, body_axis_scale=0.12):
    """
    Animated 3D orbit using matplotlib, saved as MP4.
    Satellite is yellow when sunlit, red when in eclipse.

    If history_array has 19+ columns, columns 10-18 are interpreted as
    body axes in ECI (body_x[0:3], body_y[3:6], body_z[6:9] each a unit
    vector), and red/green/blue arrows are drawn from the satellite for
    body X/Y/Z respectively.

    Parameters
    ----------
    elev, azim : float
        Camera elevation and azimuth angles in degrees.
    rotate : bool
        If True, the camera slowly rotates around the orbit during playback.
    show_body_axes : bool
        If True and attitude columns are present, draw the body frame.
    body_axis_scale : float
        Body axis arrow length as a fraction of plot half-extent.
    """
    from matplotlib.animation import FuncAnimation, FFMpegWriter
    from matplotlib.lines import Line2D
    
    output_path = f"plots/{name}.orbit_animation.mp4"

    if history_array.shape[1] < 10:
        raise ValueError("history_array must include in_eclipse column at index 9")

    has_attitude = show_body_axes and history_array.shape[1] >= 19
    time_s = history_array[:, 0]

    if time_unit == "seconds":
        time_display = time_s
        time_label = "s"
    elif time_unit == "minutes":
        time_display = time_s / 60.0
        time_label = "min"
    elif time_unit == "hours":
        time_display = time_s / 3600.0
        time_label = "hr"
    else:
        raise ValueError("time_unit must be 'seconds', 'minutes', or 'hours'.")

    # Single downsample index applied to every quantity so they stay aligned
    n_total = len(history_array)
    if n_total > max_points:
        idx = np.linspace(0, n_total - 1, max_points).astype(int)
    else:
        idx = np.arange(n_total)

    x = history_array[idx, 1]
    y = history_array[idx, 2]
    z = history_array[idx, 3]
    time_display = time_display[idx]
    in_eclipse = history_array[idx, 9].astype(int)

    if has_attitude:
        body_x_eci = history_array[idx, 10:13]
        body_y_eci = history_array[idx, 13:16]
        body_z_eci = history_array[idx, 16:19]

    n = len(x)
    total_frames = n * loops

    # White figure
    fig = plt.figure(figsize=(9, 9), facecolor="white")
    ax = fig.add_subplot(111, projection="3d", facecolor="white")

    max_extent = max(np.max(np.abs(x)), np.max(np.abs(y)),
                     np.max(np.abs(z)), R_EARTH)
    axis_limit = 1.1 * max_extent
    arrow_len = body_axis_scale * axis_limit
    ax.set_xlim(-axis_limit, axis_limit)
    ax.set_ylim(-axis_limit, axis_limit)
    ax.set_zlim(-axis_limit, axis_limit)
    ax.set_box_aspect([1, 1, 1])

    # Initial camera angle
    ax.view_init(elev=elev, azim=azim)

    if show_earth:
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 20)
        ex = R_EARTH * np.outer(np.cos(u), np.sin(v))
        ey = R_EARTH * np.outer(np.sin(u), np.sin(v))
        ez = R_EARTH * np.outer(np.ones_like(u), np.cos(v))
        ax.plot_surface(ex, ey, ez, color="royalblue",
                        alpha=0.4, linewidth=0, antialiased=True)

    ax.plot(x, y, z, color="royalblue", linewidth=1, alpha=0.6, label="Orbit")

    sun_dir = get_earth_to_sun_direction()
    sun_pos = sun_dir * 1.05 * max_extent
    ax.scatter(sun_pos[0], sun_pos[1], sun_pos[2],
               color="gold", s=200, edgecolors="orange", linewidths=1.5,
               label="Sun (direction)")

    # Style for white background
    ax.set_xlabel("ECI x [km]", color="black")
    ax.set_ylabel("ECI y [km]", color="black")
    ax.set_zlabel("ECI z [km]", color="black")
    ax.tick_params(colors="black")
    ax.xaxis.pane.set_facecolor((1.0, 1.0, 1.0, 1.0))
    ax.yaxis.pane.set_facecolor((1.0, 1.0, 1.0, 1.0))
    ax.zaxis.pane.set_facecolor((1.0, 1.0, 1.0, 1.0))
    ax.xaxis.pane.set_edgecolor("lightgray")
    ax.yaxis.pane.set_edgecolor("lightgray")
    ax.zaxis.pane.set_edgecolor("lightgray")
    ax.set_title("Satellite Orbit in ECI Frame", color="black")

    sat = ax.scatter([x[0]], [y[0]], [z[0]],
                     color="gold", s=80, edgecolors="black", linewidths=1)

    info_text = ax.text2D(0.02, 0.95, "", transform=ax.transAxes,
                          color="black", fontsize=11,
                          verticalalignment="top",
                          bbox=dict(facecolor="white", alpha=0.8,
                                    edgecolor="black", boxstyle="round,pad=0.4"))

    # Body axis quivers (3D matplotlib quivers can't be updated in place;
    # we remove and recreate them each frame, holding them in a dict).
    body_quivers = {"x": None, "y": None, "z": None}
    body_axis_colors = {"x": "red", "y": "limegreen", "z": "blue"}

    # Legend handles for body axes (proxy artists, since quiver legends are awkward)
    legend_handles, legend_labels = ax.get_legend_handles_labels()
    if has_attitude:
        for axis_name, color in body_axis_colors.items():
            legend_handles.append(Line2D([0], [0], color=color, linewidth=2))
            legend_labels.append(f"Body {axis_name.upper()}")

    ax.legend(legend_handles, legend_labels,
              loc="upper right", facecolor="white", edgecolor="black",
              labelcolor="black")

    def update(frame):
        i = frame % n
        sat._offsets3d = ([x[i]], [y[i]], [z[i]])
        if in_eclipse[i] == 1:
            sat.set_color("red")
            state_str = "ECLIPSE"
            state_color = "red"
        else:
            sat.set_color("gold")
            state_str = "Sunlit"
            state_color = "darkgoldenrod"

        info_text.set_text(f"t = {time_display[i]:.1f} {time_label}\nState: {state_str}")
        info_text.set_color(state_color)

        if has_attitude:
            # Remove last frame's arrows before drawing new ones
            for key, q in body_quivers.items():
                if q is not None:
                    q.remove()
            body_vecs = {"x": body_x_eci, "y": body_y_eci, "z": body_z_eci}
            for key, vecs in body_vecs.items():
                body_quivers[key] = ax.quiver(
                    x[i], y[i], z[i],
                    vecs[i, 0] * arrow_len,
                    vecs[i, 1] * arrow_len,
                    vecs[i, 2] * arrow_len,
                    color=body_axis_colors[key],
                    linewidth=2,
                    arrow_length_ratio=0.25,
                )

        # Slow camera rotation if enabled
        if rotate:
            ax.view_init(elev=elev, azim=azim + frame * (360 / total_frames))

        return sat, info_text

    anim = FuncAnimation(fig, update, frames=total_frames,
                         interval=1000 / fps, blit=False)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    writer = FFMpegWriter(fps=fps, bitrate=2400)
    print(f"Rendering {total_frames} frames ({loops} loop{'s' if loops > 1 else ''}) to {output_path}...")
    anim.save(output_path, writer=writer, dpi=120)
    plt.close(fig)
    print(f"Saved to {output_path}")