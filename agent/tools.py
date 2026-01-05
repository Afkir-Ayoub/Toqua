"""
Agent Tools for Ship Performance Data Retrieval and Visualization
"""

from langchain_core.tools import tool
from api.mock_api import query_mock_api, get_list_ships
from visualization.graphs import create_speed_fuel_curve
from api.mock_api import CONDITIONING_PARAMS as CONDITIONING_PARAMS_DEFAULT

# Tool 1: Query Ship Performance Data
@tool("get_ship_performance_data")
def get_ship_performance_data(
    imo,
    stw_range=None,
    conditioning_params=None,
):
    """
    Retrieves ship performance simulation data from the Toqua Ship Kernels API.

    This function generates a comprehensive speed-fuel performance profile for a specific vessel
    by simulating operation across multiple speeds under defined environmental conditions.
    Primary use cases: fuel optimization analysis, route planning, vessel performance comparison.

    Args:
        imo (int or str): International Maritime Organization vessel identifier
                        - Must be a valid 7-digit IMO number
                        - Examples: 9765432, "9876543"

        stw_range (list, optional): Speed Through Water simulation points in knots
                                   - List of float values between 8-20 knots
                                   - If None, defaults to [8.0, 9.0, 10.0, ..., 16.0] (1-knot intervals)
                                   - Use broader ranges for detailed analysis, narrower for quick estimates

        conditioning_params (dict, optional): Environmental and operational parameters
                                            - Merged with default values if partially specified
                                            - Default conditions represent typical fair weather, loaded vessel
                                            - Use None values to keep defaults, numeric values to override

        Default conditioning parameters:
            {
                "wind_speed": 6,           # m/s - moderate wind conditions
                "wind_direction": 180,     # degrees - wind from south
                "wave_height": 2,          # m - moderate sea state
                "wave_direction": 90,      # degrees - waves from east
                "current_speed": 0.5,      # m/s - mild current
                "current_direction": 0,    # degrees - current from north
                "mean_draft": 20,          # m - vessel draft (loaded condition)
                "trim": -1,                # m - slight stern trim
                "ship_heading": 0,         # degrees - vessel heading north
                "fuel_specific_energy": 41.5,  # MJ/kg - marine fuel energy content
            }

    Returns:
        dict:
            - status (str): "success" or "error"
            - imo (str): Vessel identifier
            - conditioning_params (dict): Environmental parameters used (subset of conditioning_params)
            - performance_data (dict): Performance metrics:
                * sog (list): Speed Over Ground values [knots]
                * stw (list): Speed Through Water values [knots]
                * me_power (list): Main engine power output [kW]
                * me_rpm (list): Main engine revolutions per minute
                * me_fo_consumption (list): Main engine fuel consumption [MT/day]
                * me_fo_emissions (list): Main engine fuel oil emissions [kg/day]

    Note: This tool should be called before generate_performance_graph for visualization.
    """

    try:
        api_response = query_mock_api(
            imo_number=imo, stw_range=stw_range, conditioning_params=conditioning_params
        )

        return {
            "status": "success",
            "data": {
                "imo": imo,
                "conditioning_params": (
                    conditioning_params if conditioning_params else CONDITIONING_PARAMS_DEFAULT
                ),
                "performance_data": api_response,
            },
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# Tool 2: Display Performance Graph
@tool("display_performance_graph")
def display_performance_graph(imo, conditioning_params, performance_data):
    """
    Generates an interactive Speed vs Fuel Curve graph.

    """
    # Get stw and me_fo_consumption values
    clean_stw = []
    clean_fuel = []

    raw_stw = performance_data.get("stw") or []
    raw_fuel = performance_data.get("me_fo_consumption") or []

    for s, f in zip(raw_stw, raw_fuel):
        if s is not None and f is not None:
            clean_stw.append(s)
            clean_fuel.append(f)

    try:
        # Make the figure
        fig, metadata = create_speed_fuel_curve(
            imo=imo,
            conditioning_params=conditioning_params,
            stw=clean_stw,
            me_fo_consumption=clean_fuel,
        )

        # Display the graph
        if fig:
            return {
                "status": "success",
                "data": {
                    "figure": fig.to_json(),
                    "metadata": metadata,
                },
            }

        return {"status": "error", "message": "Error: Failed to create graph figure."}

    except Exception as e:
        return {"status": "error", "message": f"Error generating graph: {str(e)}"}


# Tool 3: List Available Ships
@tool("list_available_ships")
def list_available_ships():
    """
    Returns a list of available ships with their IMO numbers, names, and other details.

    Returns:
        dict:
            - status (str): "success"
            - ships (list): List of ship dicts with "imo", "name" keys, etc.
    """

    ships = get_list_ships()

    return {"status": "success", "data": {"ships": ships}}
