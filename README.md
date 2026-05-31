# MiniSatSimPractice

MiniSatSimPractice is a practice project for my internship.

I plan to model these satellite states:

- Satellite position and velocity in a two-body Keplerian orbit using the 6 orbital elements
- Satellite attitude, assuming it is pointed at the Sun, Earth, or wherever I want perfectly
- Internal temperature using a simplified cubical spacecraft thermal model with radiative heat transfer
- Logic to dictate if a fictitious cooler, heaters, or ADCS are turned on and other random stuff
- Logic to determine the amount of solar power ungimbaled solar panels are generating
- Battery state of charge which dictate power draw states of ficticious components
- Telemetry plotting
- CSV telemetry output

I am starting with the Keplerian orbit first I may add J2, SRB, drag perturbations and a ADCS control system if I want to 

## Current Notes

`plotting.py`, `telemetry.py`, `constants.py` were written with AI. 

All other code has been written by me.

## Requirements

Python dependencies:
```bash
pip install -r requirements.txt
```
Outputs:
- CSV telemetry in `data/`
- MP4 orbit animation in `plots/`
- Interactive plots in browser / matplotlib window

## How to run
Python root: 

The following command runs a simplified orbit propagation of the ISS. Only the orbit and eclipse tracking is modeled. 
'python -m scenarios.iss_sat'
