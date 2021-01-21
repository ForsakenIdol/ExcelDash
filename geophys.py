import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def geophys_plots(plot_filter="ORE_READING_DIST"):
    filters = ["HOLEID",                # 0
            "EAST",                  # 1
            "NORTH",                 # 2
            "RL",                    # 3
            "DRILL_DEPTH",           # 4
            "LAS_READING_DEPTH",     # 5
            "LAS_STOP_DEPTH",        # 6
            "TOO_OREZONE_DRILL",     # 7
            "ORE_READING_DIST",      # 8
            "DATE_DRILLED",          # 9
            "REGION",                # 10
            "REGIONPIT",             # 11
            "SUBREGIONPIT",          # 12
            "OVERBURDEN",            # 13
            "DATE_SURVEYED",         # 14
            "DAYS_OUTSTANDING",      # 15
            "SHORT_LAS",             # 16
            "OVERBURDEN_CORRECTED",  # 17
            "IS_OUTSTANDING",        # 18
            "SURVEY_STATUS"]         # 19

    dframe = pd.read_excel("LAS file.xlsx", engine="openpyxl")
    dframe = dframe[dframe[filters[5]].notna()] # Filter out rows which do not have a LAS_READING_DEPTH value, as these rows are useless.

    # Plot-filter-specific data transformations and filters

    # Filter initially negative values from the "TOO_Ore_zone_DRILL" column.
    if (plot_filter == filters[7]): dframe = dframe.loc[dframe[plot_filter] > 0]

    # For a to-scale direction plot, we want to "reverse" the z-axes signs. Since Plotly doesn't have functionality for doing so in a 3D plot, we'll flip the signs in the dataframe instead.
    dframe[plot_filter] = dframe[plot_filter].mul(-1)

    # [Plot 2 (Bottom / Right)] This trace is colour-coded based on the survey status.
    survey_fig = px.scatter_3d(
                    dframe,
                    x=filters[1], y=filters[2], z=plot_filter, color=filters[19],
                    title="{} - Survey Status".format(plot_filter)
                ).update_traces( marker=dict(size=2) )

    # This is the default color palette that Plotly uses. These traces are colour-coded based on the region.
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']

    # Get all the unique regions in the dataframe.
    regions = []
    for region in dframe["REGION"]:
        if (region not in regions): regions.append(region)

    # Push a plot for each region.
    traces = []
    current_color = 0
    for region in regions:
        this_region = dframe.loc[dframe[filters[10]] == region] # Get the rows which correspond to this particular region
        traces.append(go.Scatter3d(x=this_region[filters[1]], y=this_region[filters[2]], z=this_region[plot_filter],
                                mode="markers", marker=dict(color=colors[current_color], size=2), name="{} ({} points)".format(region, this_region.size),
                                showlegend=True, legendgroup=region))
        current_color = (current_color + 1) % len(colors)

    # For each polygon point, locate its general region based on its region_name, and add it to the corresponding point set.
    points = pd.read_csv("points.csv").dropna()
    sorted_points = points.sort_values(["region_name", "point_order"])
    current_region = ""
    x, y, z = [], [], []
    for row in points.iterrows():
        if (row[1].region_name != current_region):
            if (current_region != ""):
                # Push the current scatter graph, reset the point lists, and update the current_region
                over_region = list(filter(lambda x: x[0] == current_region[0], regions))
                traces.append(go.Scatter3d(name=current_region, x = x, y = y, z = z, mode="markers+lines", marker=dict(color="black", size=2), showlegend=False, legendgroup=over_region[0]))
                x, y, z = [], [], []
            current_region = row[1].region_name
        x.append(row[1].X)
        y.append(row[1].Y)
        z.append(0)

    # Push the last scatter graph
    over_region = list(filter(lambda x: x[0] == current_region[0], regions))
    traces.append(go.Scatter3d(name=current_region, x = x, y = y, z = z, mode="markers+lines", marker=dict(color="black", size=2), showlegend=False, legendgroup=over_region[0]))

    # [Plot 1 (Top / Left)]
    layout = go.Layout(title="{} - Coloured by Region".format(plot_filter), legend=dict(title=plot_filter))
    region_fig = go.Figure(data = traces, layout = layout)
    region_fig.update_layout( scene = dict(xaxis_title = filters[1], yaxis_title = filters[2], zaxis_title = plot_filter) )

    return (region_fig, survey_fig)