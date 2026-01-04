"""
Creates interactive Plotly figures from Toqua API data
"""

import plotly.graph_objects as go

def create_speed_fuel_curve(
    imo,
    conditioning_params,
    stw,
    me_fo_consumption,
    title="Speed-Fuel Curve",
):
    """
    Create interactive speed-fuel curve from API data.

    Args:
        imo: IMO number
        stw: List of speed through water values (kn) from API
        me_fo_consumption: List of fuel consumption values (mt/day) from API
        title: Chart title (optional)

    Returns:
        (Plotly Figure object, metadata dict)
    """

    # Filter out None values
    valid_data = [
        (s, f)
        for s, f in zip(stw, me_fo_consumption)
        if s is not None and f is not None
    ]
    stw_clean = [x[0] for x in valid_data]
    fuel_clean = [x[1] for x in valid_data]

    # Add main curve
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=stw_clean,
            y=fuel_clean,
            mode="lines+markers",
            name="Fuel Consumption",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8, symbol="circle"),
            hovertemplate="<b>Speed:</b> %{x:.1f} knots<br>"
            + "<b>Fuel:</b> %{y:.2f} mt/day<br>",
            fill="tozeroy",
            fillcolor="rgba(31, 119, 180, 0.1)",
        )
    )

    # Layout
    fig.update_layout(
        title={
            "text": f"{title}<br><sub>IMO {imo}</sub>",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18},
        },
        xaxis_title="Speed Through Water (Knots)",
        yaxis_title="Fuel Consumption (Tons/Day)",
        hovermode="x unified",
        template="plotly_white",
        height=500,
        margin=dict(l=60, r=40, t=80, b=60),
        font=dict(family="Arial", size=12),
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.1)"),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor="rgba(0,0,0,0.1)"),
    )

    # Annotate minimum fuel point
    if fuel_clean:
        min_idx = fuel_clean.index(min(fuel_clean))
        fig.add_annotation(
            x=stw_clean[min_idx],
            y=fuel_clean[min_idx],
            text=f"Min: {fuel_clean[min_idx]:.1f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor="green",
            ax=0,
            ay=-40,
            bgcolor="rgba(0,255,0,0.1)",
            bordercolor="green",
            borderwidth=1,
        )

    return fig, {
        "imo": imo,
        "conditioning_params": conditioning_params,
        "stw_range": [min(stw_clean), max(stw_clean)] if stw_clean else None,
        "fuel_range": [min(fuel_clean), max(fuel_clean)] if fuel_clean else None,
        "min_fuel_speed": (
            stw_clean[fuel_clean.index(min(fuel_clean))] if fuel_clean else None
        ),
    }
