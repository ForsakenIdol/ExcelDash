# Run this app with `python dash_app.py` and visit http://127.0.0.1:8050/ in your web browser.
# Viewing the graphs side-by-side seems to be the better option.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

from geophys import geophys_plots
from stoppedpos import stoppedpos

dframe = pd.read_excel("LAS file.xlsx", engine="openpyxl")
bar_filters = ["HOLEID", "REGION", "REGIONPIT", "SUBREGIONPIT", "SURVEY_STATUS"]
positions = dframe[dframe["LAS_READING_DEPTH"].notna()].filter(items=bar_filters).sort_values(["REGION", "REGIONPIT", "SUBREGIONPIT", "SURVEY_STATUS"])

# Generates the table of survey data based on the specified filter values.
def generate_table(dataframe, start_row=0, max_rows=20, filter_survey_value="", filter_region_value="", filter_holeid=""):
    if (filter_survey_value != ""): dataframe = dataframe.loc[dataframe["SURVEY_STATUS"] == filter_survey_value]
    if (filter_region_value != ""): dataframe = dataframe.loc[dataframe["REGION"].str.contains(filter_region_value, na=False)]
    if (filter_holeid != ""): dataframe = dataframe.loc[dataframe["HOLEID"].str.contains(filter_holeid, na=False)]

    if (start_row == "" or start_row < 0): start_row = 0
    elif (start_row >= len(dataframe)): start_row = len(dataframe) - 1
    last_row = min(len(dataframe), start_row + max_rows)
    if (dataframe.size > 0): return html.Div([
            html.P("Showing rows {} - {} out of {} total.".format(start_row + 1, last_row, len(dataframe))),
            html.Table([
            html.Thead([
                html.Tr([html.Th("Row No.")] + [html.Th(col) for col in dataframe.columns])
            ]),
            html.Tbody([
                html.Tr([html.Td(i + 1)] + [
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(start_row, last_row) if (i < len(dataframe))
            ])
        ])
    ], className="app-text")
    else: return html.P("No data for this filter combination.")

# Controls the layout of the 3D plots.
def plot3D(layout, plot_filter="ORE_READING_DIST"):
    region_fig, survey_fig = geophys_plots(plot_filter)
    if (layout == 'side'):
        return html.Div(children=[
            # Left-hand figure
            dcc.Graph(
                id='las-file-figure',
                figure=region_fig,
                className='six columns',
                style={ 'height': '75rem' }
            ),
            # Right-hand figure
            dcc.Graph(
                id='survey-figure',
                figure=survey_fig,
                className='six columns',
                style={ 'height': '75rem' }
            )
        ], className="row")
    elif (layout == 'stacked'):
        return html.Div(children=[
            # Top figure
            dcc.Graph(
                id='las-file-figure',
                figure=region_fig,
                style={ 'height': '100rem' }
            ),
            # Bottom figure
            dcc.Graph(
                id='survey-figure',
                figure=survey_fig,
                style={ 'height': '100rem' }
            )
        ])

def displayTableFilters():
    return (
        html.Div([
            html.Div(["View ", dcc.Input(id='browse-range-count', value=20, type='number', style={ "width": "10rem" }), " rows at a time, starting from row ", dcc.Input(id='browse-range-start', value=1, type='number', style={ "width": "10rem" }), ". You can view a maximum of 500 rows at once."],
                    style={ "marginBottom": "1rem" }),
            html.Div(["Filter by survey status: ", dcc.RadioItems(
                options=[
                    { 'label': 'ALL', 'value': '' },
                    { 'label': 'FULL_SURVEY', 'value': 'FULL_SURVEY' },
                    { 'label': 'PARTIAL_SURVEY', 'value': 'PARTIAL_SURVEY' },
                    { 'label': 'STOPPED_SHORT', 'value': 'STOPPED_SHORT' }
                ], value='', id="survey-filter", style={ "display": "flex" }, labelStyle={ "marginRight": "1.5rem" }
            )], style={ "display": "flex", "marginBottom": "1rem" }),
            html.Div(["Filter by region: ", dcc.Input(id="region-filter", value='', type='text', style={ 'width': '20rem', "marginBottom": "1rem" })]),
            html.Div(["Find a specific hole by ID: ", dcc.Input(id="holeid-filter", value='', type='text', style={ 'width': '20rem', "marginBottom": "1rem" })])
        ])
    )

# Controls the position of the table with respect to the filter input fields.
def displayTable(layout):
    if (layout == 'side'): return html.Div([
            html.Div([displayTableFilters() ], className='six columns'),
            html.Div([
                html.Div(generate_table(positions), id="browse-stopped-positions-values")
            ], className='six columns')
        ], className="row")
    elif (layout == 'stacked'): return html.Div([
            displayTableFilters(),
            html.Div(generate_table(positions), id="browse-stopped-positions-values")
        ])

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(id='app-title', children='LAS Excel File Data', className="app-header"),
    html.Div(children=[
        html.P(children="The following plots serve as a visualization for the data in the LAS Excel file."),
        html.P(children=[
                '''
                Both 3D graphs plot the data with the plotting variable as a function of its position in 2D space, as if one were observing a to-scale model of the mine site.
                Each 3D plot has its own colour legend based on other attributes present in the data.
                Try zooming into parts of the graph or isolating a trace by double-clicking on its corresponding legend entry! You can use the Home button to reset the camera to its default position.
                ''',
                html.Strong("Note that switching the 3D plot filter attribute will incur a significant delay due to the recalculations required for the new 3D plots.")
            ]
        ),
        html.P(children='''
            The 2D graphs on the lower half of the page plot the survey status distributions by region and subregion areas.
            The table at the bottom of the page contains the data used to plot the graphs in this application, with the location-based data removed for simplicity.
            This view is presented for ease of access and does not contain data for drilled holes which do not have LAS data recorded, as this data was not used in any graph.
            To see the entire dataset, open the "LAS file.xlsx" file in the same directory.
        ''')
    ], className="app-text"),
    html.Div([
        html.Div([
            html.Strong("View 3D Graphs: "),
            dcc.RadioItems(
                options=[
                    { 'label': 'Side-by-Side', 'value': 'side' },
                    { 'label': 'Stacked', 'value': 'stacked' }
                ], value='side', id="graphs-3d-view-toggle", style={ "display": "flex" }, labelStyle={ "marginLeft": "1rem" }
            )
        ], style={ "display": "flex", "margin-left": "2rem" }),
        html.Em("There may be a slight delay switching view modes due to the graphs requiring heavy processing power.")
    ], style={ "display": "flex", "justifyContent": "space-evenly", "marginBottom": "1rem" }),
    html.Div([
        html.Strong("Plot Filter: "),
        dcc.RadioItems(
            options=[
                { 'label': 'DRILL_DEPTH', 'value': 'DRILL_DEPTH' },
                { 'label': 'LAS_READING_DEPTH', 'value': 'LAS_READING_DEPTH' },
                { 'label': 'TOO_OREZONE_DRILL', 'value': 'TOO_OREZONE_DRILL' },
                { 'label': 'ORE_READING_DIST', 'value': 'ORE_READING_DIST' },
                { 'label': 'OVERBURDEN', 'value': 'OVERBURDEN_CORRECTED' }
            ], value='ORE_READING_DIST', id='graphs-3d-plot-filter', style={ "display": "flex" }, labelStyle={ "marginLeft": "2rem" }
        )
    ], style={ "display": "flex", "marginRight": "5rem" }),
    html.Div(children=plot3D('stacked'), id="graphs-3d-view"),
    html.Hr(style={ "paddingTop": "1rem", "paddingBottom": "1rem", "color": "black" }),
    html.H2(children="Survey Status", className="app-text"),
    html.Div(children=[
        dcc.Graph(
            id='stopped-pos-groupby-1-figure',
            figure=stoppedpos(1),
            className='six columns',
            style={ 'height': '100rem' }
        ),
        dcc.Graph(
            id='stopped-pos-groupby-2-figure',
            figure=stoppedpos(2),
            className='six columns',
            style={ 'height': '100rem' }
        )
    ], className="row"),
    dcc.Graph(
        id='stopped-pos-groupby-3-figure',
        figure=stoppedpos(3),
        style={ 'height': '100rem' }
    ),
    html.Hr(style={ "paddingTop": "1rem", "paddingBottom": "1rem", "color": "black" }),
    html.H2(children="Browse Stopped Position Data", className="app-text"),
    html.Div([html.Strong("View table relative to filters: "), dcc.RadioItems(
        options=[
            { 'label': 'Stacked', 'value': 'stacked' },
            { 'label': 'Side-by-Side', 'value': 'side' }
        ], value='stacked', id='customize-view-table', style={ "display": "flex" }, labelStyle={ "marginLeft": "2rem" }
    )], style={ "display": "flex", "marginBottom": "2rem" }),
    html.Div(children=displayTable('stacked'), id="view-table")
], style={ "margin": "3rem" })

# Callbacks

@app.callback(
    Output(component_id='browse-stopped-positions-values', component_property='children'),
    Input(component_id='browse-range-start', component_property='value'),
    Input(component_id='browse-range-count', component_property='value'),
    Input(component_id='survey-filter', component_property='value'),
    Input(component_id='region-filter', component_property='value'),
    Input(component_id='holeid-filter', component_property='value')
)
def change_browse_range(rangeStart, rangeCount, surveyValue, regionValue, holeidValue):
    ctx = dash.callback_context
    if ctx.triggered:
        correctedCount = rangeCount
        if (rangeCount <= 0): correctedCount = 1
        elif (rangeCount > 500): correctedCount = 500
        return generate_table(positions, start_row=rangeStart - 1, max_rows=correctedCount, filter_survey_value=surveyValue,
                              filter_region_value=regionValue.upper(), filter_holeid=holeidValue.upper())
    else: return generate_table(positions) # The other arguments take on their default values.

@app.callback(
    Output(component_id="graphs-3d-view", component_property="children"),
    Input(component_id="graphs-3d-view-toggle", component_property="value"),
    Input(component_id="graphs-3d-plot-filter", component_property="value")
)
def change_graph_view(toggleValue, plotFilter):
    return plot3D(toggleValue, plot_filter=plotFilter)

@app.callback(
    Output(component_id='view-table', component_property='children'),
    Input(component_id='customize-view-table', component_property='value')
)
def change_table_view(value):
    return displayTable(value)

if __name__ == '__main__':
    app.run_server(debug=True)