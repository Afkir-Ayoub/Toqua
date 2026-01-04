"""
Mock Toqua Ship Kernels API
Using Official Toqua API Formats and Data from https://docs.toqua.ai/docs/speed-fuel-curves with:
    - Slight variations to simulate ML outputs
    - Environmental conditioning effects
"""

import random
from datetime import datetime, timezone

# Config
SAMPLE_SHIPS = [
    {
        "name": "Demo Vessel",
        "imo_number": 9999999,
        "type": "Tanker",
        "country": "SC",
        "build_year": 2015,
        "shipyard": "Toqua Shipyard",
        "dwt": 220000.0,
        "beam": 55.0,
        "loa": 300.0,
        "mcr": 21900.0,
        "max_rpm": 60.0,
        "uuid": "eycrYbrzJNsJecGqKraUCn",
    }
]

CONDITIONING_PARAMS = {
    "wind_speed": 6,  # [m/s]
    "wind_direction": 180,  # [degrees]
    "wave_height": 2,  # [m]
    "wave_direction": 90,  # [degrees]
    "current_speed": 0.5,  # [m/s]
    "current_direction": 0,  # [degrees]
    "mean_draft": 20,  # [m]
    "trim": -1,  # [m]
    "ship_heading": 0,  # [degrees]
    "fuel_specific_energy": 41.5,  # [MJ/kg]
}


def get_list_ships():
    """API endpoint to list all available ships."""
    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_ships": len(SAMPLE_SHIPS),
        "ships": SAMPLE_SHIPS,
    }


def query_mock_api(imo_number, stw_range=None, conditioning_params=None):
    """Generate realistic ship performance data with slight randomness and environmental conditioning."""

    if stw_range is None:
        stw_range = [8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0]

    # Use provided conditioning params or defaults
    if conditioning_params is None:
        conditioning_params = CONDITIONING_PARAMS.copy()
    else:
        # Merge with defaults for any missing values
        params = CONDITIONING_PARAMS.copy()
        params.update(conditioning_params)
        conditioning_params = params

    # Find ship data
    ship = next(
        (s for s in SAMPLE_SHIPS if s["imo_number"] == imo_number), SAMPLE_SHIPS[0]
    )

    # Initialize result arrays with slight randomness around the original values
    results = {
        "sog": [],
        "stw": [],
        "me_rpm": [],
        "me_power": [],
        "me_fo_consumption": [],
        "me_fo_emission": [],
        "errors": [],
    }

    # Original base values with slight variations
    base_values = {
        "sog_base": [
            7.02808,
            8.02808,
            9.02808,
            10.02808,
            11.02808,
            12.02808,
            13.02808,
            None,
            None,
        ],
        "stw": [8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, None, None],
        "me_rpm_base": [
            35.563477161420984,
            38.86856315406255,
            42.3286138994565,
            45.958934292444695,
            49.77248238124245,
            53.780632616735986,
            57.993745359998364,
            None,
            None,
        ],
        "me_power_base": [
            4014.487664675082,
            5034.96591338081,
            6306.250909817854,
            7883.151679670297,
            9830.679471751078,
            12225.665331559763,
            15158.644854083537,
            None,
            None,
        ],
        "me_fo_consumption_base": [
            18.24386889835794,
            22.461921943399787,
            27.57687777045103,
            33.79875072031291,
            41.47119688825557,
            51.21728628254814,
            64.2267638497258,
            None,
            None,
        ],
        "me_fo_emission_base": [
            57.842186342243835,
            71.21552352154902,
            87.43249097121499,
            107.15893915875206,
            131.48442973421427,
            162.38440615881885,
            203.63095478555562,
            None,
            None,
        ],
    }

    errors = []

    for i, stw in enumerate(stw_range):
        if stw is None:
            results["sog"].append(None)
            results["stw"].append(None)
            results["me_rpm"].append(None)
            results["me_power"].append(None)
            results["me_fo_consumption"].append(None)
            results["me_fo_emission"].append(None)
            continue

        # Calculate environmental effects
        env_effects = calculate_environmental_effects(conditioning_params)

        # Use base values with environmental effects and slight random variation (±3%)
        if i < len(base_values["sog_base"]) and base_values["sog_base"][i] is not None:
            sog_variation = random.uniform(0.97, 1.03)  # ±3% variation
            sog = base_values["sog_base"][i] * env_effects["sog_factor"] * sog_variation
            results["sog"].append(round(sog, 5))
        else:
            results["sog"].append(None)

        results["stw"].append(stw)

        # RPM with environmental effects and variation
        if (
            i < len(base_values["me_rpm_base"])
            and base_values["me_rpm_base"][i] is not None
        ):
            rpm_variation = random.uniform(0.98, 1.02)  # ±2% variation
            rpm = (
                base_values["me_rpm_base"][i]
                * env_effects["rpm_factor"]
                * rpm_variation
            )

            # Check RPM limit
            if rpm >= ship["max_rpm"]:
                rpm = ship["max_rpm"] * 0.98
                errors.append(
                    {
                        "error_code": "max_rpm_limit_exceeded",
                        "description": f"Maximum RPM ({ship['max_rpm']} RPM) exceeded.",
                        "indices": [i],
                    }
                )

            results["me_rpm"].append(round(rpm, 5))
        else:
            results["me_rpm"].append(None)

        # Power with environmental effects and variation
        if (
            i < len(base_values["me_power_base"])
            and base_values["me_power_base"][i] is not None
        ):
            power_variation = random.uniform(0.95, 1.05)  # ±5% variation
            power = (
                base_values["me_power_base"][i]
                * env_effects["power_factor"]
                * power_variation
            )

            # Check MCR limit
            if power >= ship["mcr"] * 0.9:
                power = ship["mcr"] * 0.9
                errors.append(
                    {
                        "error_code": "max_mcr_limit_exceeded",
                        "description": f"90% Maximum MCR ({ship['mcr']} kW) exceeded.",
                        "indices": [i],
                    }
                )

            results["me_power"].append(round(power, 2))
        else:
            results["me_power"].append(None)

        # Fuel consumption with environmental effects and variation
        if (
            i < len(base_values["me_fo_consumption_base"])
            and base_values["me_fo_consumption_base"][i] is not None
        ):
            fuel_variation = random.uniform(0.96, 1.04)  # ±4% variation
            fuel_consumption = (
                base_values["me_fo_consumption_base"][i]
                * env_effects["fuel_factor"]
                * fuel_variation
            )
            results["me_fo_consumption"].append(round(fuel_consumption, 2))
        else:
            results["me_fo_consumption"].append(None)

        # Emissions with environmental effects and variation
        if (
            i < len(base_values["me_fo_emission_base"])
            and base_values["me_fo_emission_base"][i] is not None
        ):
            emission_variation = random.uniform(0.96, 1.04)  # ±4% variation
            emissions = (
                base_values["me_fo_emission_base"][i]
                * env_effects["emission_factor"]
                * emission_variation
            )
            results["me_fo_emission"].append(round(emissions, 2))
        else:
            results["me_fo_emission"].append(None)

    results["errors"] = errors
    return results


def calculate_environmental_effects(conditioning_params):
    """Calculate environmental effects on ship performance based on conditioning parameters."""

    # Wind effects (simplified)
    wind_speed = conditioning_params["wind_speed"]
    wind_direction = conditioning_params["wind_direction"]
    ship_heading = conditioning_params["ship_heading"]

    # Calculate relative wind angle (simplified)
    relative_wind_angle = abs(wind_direction - ship_heading)
    if relative_wind_angle > 180:
        relative_wind_angle = 360 - relative_wind_angle

    # Wind factor: headwind = resistance, tailwind = assistance
    wind_factor = 1.0
    if relative_wind_angle < 90:  # Headwind component
        headwind_factor = (wind_speed * 0.02) * (
            relative_wind_angle / 90
        )  # Max 2% per m/s
        wind_factor += headwind_factor
    elif relative_wind_angle > 270:  # Tailwind component
        tailwind_factor = (wind_speed * 0.01) * (
            (360 - relative_wind_angle) / 90
        )  # Max 1% per m/s
        wind_factor -= tailwind_factor

    # Wave effects
    wave_height = conditioning_params["wave_height"]
    wave_factor = 1.0 + (wave_height * 0.03)  # 3% per meter of wave height

    # Current effects (affects speed over ground)
    current_speed = conditioning_params["current_speed"]
    current_direction = conditioning_params["current_direction"]

    # Calculate current contribution to SOG
    relative_current_angle = abs(current_direction - ship_heading)
    if relative_current_angle > 180:
        relative_current_angle = 360 - relative_current_angle

    # Current factor for SOG (positive if current with ship, negative if against)
    current_sog_factor = 1.0
    if relative_current_angle < 90:  # Following current
        current_sog_factor += (current_speed * 0.1) * (relative_current_angle / 90)
    elif relative_current_angle > 270:  # Head current
        current_sog_factor -= (current_speed * 0.1) * (
            (360 - relative_current_angle) / 90
        )

    # Draft effects (deeper draft = more resistance)
    mean_draft = conditioning_params["mean_draft"]
    draft_factor = 1.0 + (
        (mean_draft - 20) * 0.01
    )  # Baseline 20m, 1% per meter difference

    # Trim effects (slight)
    trim = conditioning_params["trim"]
    trim_factor = 1.0 + (abs(trim) * 0.005)  # 0.5% per meter of trim

    # Calculate combined factors
    power_factor = wind_factor * wave_factor * draft_factor * trim_factor
    fuel_factor = (
        power_factor * 1.1
    )  # Fuel consumption roughly follows power but with overhead
    emission_factor = fuel_factor
    rpm_factor = power_factor**0.8  # RPM less affected than power

    return {
        "sog_factor": current_sog_factor,
        "power_factor": power_factor,
        "fuel_factor": fuel_factor,
        "emission_factor": emission_factor,
        "rpm_factor": rpm_factor,
    }
