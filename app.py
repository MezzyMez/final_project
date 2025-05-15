import pandas as pd  # type: ignore
import plotly.graph_objs as go  # type: ignore
from dash import Dash, dcc, html, Input, Output, State  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
from datetime import datetime
from dash.dependencies import State

# Load data
DATA_PATH = 'data/processed/cpi_processed.csv'
df = pd.read_csv(DATA_PATH)

# Get unique product groups (excluding All-items)
product_groups = sorted(df['Products and product groups'].unique())
if 'All-items' in product_groups:
    product_groups.remove('All-items')

# Find min and max dates in the data
min_date = pd.to_datetime(df['REF_DATE']).min()
max_date = pd.to_datetime(df['REF_DATE']).max()
default_start = max_date.replace(year=max_date.year - 10)
if default_start < min_date:
    default_start = min_date

# Define province and city lists
province_options = [
    'Alberta', 'British Columbia', 'Manitoba', 'New Brunswick', 'Newfoundland and Labrador',
    'Nova Scotia', 'Ontario', 'Prince Edward Island', 'Quebec', 'Saskatchewan'
]
city_options = [
    'Calgary, Alberta', 'Charlottetown and Summerside, Prince Edward Island', 'Edmonton, Alberta',
    'Halifax, Nova Scotia', 'Iqaluit, Nunavut', 'Montréal, Quebec', 'Ottawa-Gatineau, Ontario part, Ontario/Quebec',
    'Québec, Quebec', 'Regina, Saskatchewan', 'Saint John, New Brunswick', 'Saskatoon, Saskatchewan',
    "St. John's, Newfoundland and Labrador", 'Thunder Bay, Ontario', 'Toronto, Ontario',
    'Vancouver, British Columbia', 'Victoria, British Columbia', 'Whitehorse, Yukon',
    'Winnipeg, Manitoba', 'Yellowknife, Northwest Territories'
]

# Province to cities mapping
province_to_cities = {
    'Alberta': ['Calgary, Alberta', 'Edmonton, Alberta'],
    'British Columbia': ['Vancouver, British Columbia', 'Victoria, British Columbia'],
    'Manitoba': ['Winnipeg, Manitoba'],
    'New Brunswick': ['Saint John, New Brunswick'],
    'Newfoundland and Labrador': ["St. John's, Newfoundland and Labrador"],
    'Nova Scotia': ['Halifax, Nova Scotia'],
    'Ontario': ['Ottawa-Gatineau, Ontario part, Ontario/Quebec', 'Thunder Bay, Ontario', 'Toronto, Ontario'],
    'Prince Edward Island': ['Charlottetown and Summerside, Prince Edward Island'],
    'Quebec': ['Montréal, Quebec', 'Québec, Quebec'],
    'Saskatchewan': ['Regina, Saskatchewan', 'Saskatoon, Saskatchewan'],
}

# All cities list
all_cities = [c for cities in province_to_cities.values() for c in cities]

# App setup with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = 'CPI Interactive Explorer'

controls = dbc.Card([
    dbc.CardBody([
        html.H2('Canadian CPI Explorer', className='card-title mb-4'),
        dbc.Row([
            dbc.Col([
                html.Label('Country:', className='mb-1'),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': 'Canada', 'value': 'Canada'}],
                    value='Canada',
                    clearable=False,
                    style={'width': '100%'}
                ),
            ], md=4),
            dbc.Col([
                html.Label('Province:', className='mb-1'),
                dcc.Dropdown(
                    id='province-dropdown',
                    options=[{'label': p, 'value': p} for p in province_options],
                    value=None,
                    placeholder='Select a province',
                    style={'width': '100%'}
                ),
            ], md=4),
            dbc.Col([
                html.Label('City:', className='mb-1'),
                dcc.Dropdown(
                    id='city-dropdown',
                    options=[{'label': c, 'value': c} for c in all_cities],
                    value=None,
                    placeholder='Select a city',
                    style={'width': '100%'}
                ),
            ], md=4),
        ], className='mb-3'),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label('Select Product Group:', className='mb-1'),
                    dcc.Dropdown(
                        id='group-dropdown',
                        options=[{'label': g, 'value': g} for g in product_groups],  # type: ignore
                        value='Transportation',
                        style={'width': '100%'}
                    ),
                ])
            ], md=6),
            dbc.Col([
                html.Div([
                    html.Label('Select Date Range:', className='mb-1'),
                    dcc.DatePickerRange(
                        id='date-range',
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        start_date=default_start,
                        end_date=max_date,
                        display_format='YYYY-MM-DD',
                    ),
                ])
            ], md=6),
        ], className='mb-3', align='end'),
        dbc.Row([
            dbc.Col([
                dcc.Checklist(
                    id='rolling-checkbox',
                    options=[{'label': 'Show 6-month rolling average', 'value': 'show_rolling'}],  # type: ignore
                    value=['show_rolling'],
                    className='mb-2',
                    inputStyle={"margin-right": "8px"}
                ),
            ], md=6),
            dbc.Col([
                html.Label('Highlight differences above (absolute value):'),
                dcc.Slider(
                    id='highlight-threshold',
                    min=0,
                    max=10,
                    step=0.1,
                    value=5,
                    marks={i: str(i) for i in range(0, 11)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], md=6),
        ]),
    ])
], className='mb-4 shadow-sm')

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(controls, md=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='selected-group-title', className='text-center mb-1', style={'fontWeight': 'bold', 'fontSize': '1.5rem'}),
            dbc.Row([
                dbc.Col(html.Div(id='correlation-scorecard', className='text-center'), width='auto'),
                dbc.Col(html.Div(id='correlation-coeff', className='text-center'), width='auto'),
                dbc.Col(
                    dbc.Button(
                        "Show Top Correlated Groups",
                        id="open-sidebar-btn",
                        color="info",
                        outline=True,
                        className="ms-3",
                        size="sm",
                        style={
                            'fontWeight': 'bold',
                            'fontSize': '0.95rem',
                            'padding': '0.25em 0.7em',
                            'verticalAlign': 'middle',
                            'lineHeight': '1.1',
                        }
                    ),
                    width="auto"
                ),
            ], justify='center', align='center', className='mb-2'),
        ], md=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='cpi-comparison-graph', style={'marginTop': '0.5rem'}), md=12)
    ]),
    dbc.Offcanvas(
        id="top-correlated-sidebar",
        title="Top 10 Most Highly Correlated Product Groups",
        is_open=False,
        placement="end",
        backdrop=False,
        style={"width": "400px"},
        children=html.Div(id="top-correlated-table", className="p-2")
    ),
    dbc.Row([
        dbc.Col(html.Div(id='summary-stats', style={'marginTop': 20}), md=12)
    ]),
    html.Footer([
        html.Hr(),
        html.Div('© 2024 Canadian CPI Explorer', className='text-center text-muted', style={'fontSize': '0.9rem'})
    ], style={'marginTop': 40})
], fluid=True, style={'maxWidth': 1000, 'margin': 'auto'})

@app.callback(
    Output('city-dropdown', 'options'),
    Output('city-dropdown', 'value'),
    Input('province-dropdown', 'value'),
)
def update_city_options(selected_province):
    if selected_province and selected_province in province_to_cities:
        options = [{'label': c, 'value': c} for c in province_to_cities[selected_province]]
        return options, None  # Reset city selection when province changes
    else:
        options = [{'label': c, 'value': c} for c in all_cities]
        return options, None

@app.callback(
    Output('group-dropdown', 'options'),
    Output('group-dropdown', 'value'),
    Input('country-dropdown', 'value'),
    Input('province-dropdown', 'value'),
    Input('city-dropdown', 'value'),
    State('group-dropdown', 'value'),
)
def update_group_options(country, province, city, current_group):
    # Determine which GEO to use
    if city:
        geo = city
    elif province:
        geo = province
    else:
        geo = country if country else 'Canada'
    # Get product groups available for this GEO
    available_groups = sorted(df[df['GEO'] == geo]['Products and product groups'].unique())
    if 'All-items' in available_groups:
        available_groups.remove('All-items')
    options = [{'label': g, 'value': g} for g in available_groups]
    # Set value to current_group if still available, else default to first available
    value = current_group if current_group in available_groups else (available_groups[0] if available_groups else None)
    return options, value

@app.callback(
    Output('cpi-comparison-graph', 'figure'),
    Output('summary-stats', 'children'),
    Output('correlation-scorecard', 'children'),
    Output('correlation-coeff', 'children'),
    Output('selected-group-title', 'children'),
    Output('top-correlated-table', 'children'),
    Input('group-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('rolling-checkbox', 'value'),
    Input('highlight-threshold', 'value'),
    Input('province-dropdown', 'value'),
    Input('city-dropdown', 'value'),
)
def update_graph(group_name, start_date, end_date, rolling_opts, highlight_thresh, province, city):
    # Determine which GEO to use
    if city:
        geo = city
    elif province:
        geo = province
    else:
        geo = 'Canada'
    df_cpi = df[(df['Products and product groups'] == 'All-items') & (df['GEO'] == geo)]
    df_group = df[(df['Products and product groups'] == group_name) & (df['GEO'] == geo)]
    merged = pd.merge(
        df_cpi[['REF_DATE', 'Rate_of_Change']],
        df_group[['REF_DATE', 'Rate_of_Change']],
        on='REF_DATE',
        suffixes=('_CPI', '_Group')
    )
    merged['REF_DATE'] = pd.to_datetime(merged['REF_DATE'])
    # Filter by date range
    if start_date is not None:
        merged = merged[merged['REF_DATE'] >= pd.to_datetime(start_date)]
    if end_date is not None:
        merged = merged[merged['REF_DATE'] <= pd.to_datetime(end_date)]
    if 'show_rolling' in rolling_opts:
        rolling_cpi = merged['Rate_of_Change_CPI'].rolling(6, min_periods=1).mean()
        rolling_group = merged['Rate_of_Change_Group'].rolling(6, min_periods=1).mean()
        diff = rolling_group - rolling_cpi
    else:
        diff = merged['Rate_of_Change_Group'] - merged['Rate_of_Change_CPI']
    highlight_pos = (diff > highlight_thresh).tolist()
    highlight_neg = (diff < -highlight_thresh).tolist()

    # Bar traces
    bars = go.Bar(
        x=merged['REF_DATE'],
        y=diff,
        marker_color=[
            '#FFB3B3' if p else '#B3C6FF' if n else '#7FDBFF'
            for p, n in zip(highlight_pos, highlight_neg)
        ],
        opacity=0.7,
        name=f'Difference ({group_name} - All-items)',
        hovertemplate='Date: %{x|%Y-%m}<br>Diff: %{y:.2f}%<extra></extra>'
    )
    # Line traces
    line_cpi = go.Scatter(
        x=merged['REF_DATE'],
        y=merged['Rate_of_Change_CPI'],
        mode='lines',
        name='All-items (CPI)',
        line=dict(color='#CCCCCC'),  # lighter grey
        hovertemplate='Date: %{x|%Y-%m}<br>CPI: %{y:.2f}%<extra></extra>'
    )
    line_group = go.Scatter(
        x=merged['REF_DATE'],
        y=merged['Rate_of_Change_Group'],
        mode='lines',
        name=group_name,
        line=dict(color='black'),  # black
        hovertemplate=f'Date: %{{x|%Y-%m}}<br>{group_name}: %{{y:.2f}}%<extra></extra>'
    )
    # Rolling averages
    rolling_traces = []
    if 'show_rolling' in rolling_opts:
        rolling_cpi = merged['Rate_of_Change_CPI'].rolling(6, min_periods=1).mean()
        rolling_group = merged['Rate_of_Change_Group'].rolling(6, min_periods=1).mean()
        rolling_traces = [
            go.Scatter(
                x=merged['REF_DATE'],
                y=rolling_cpi,
                mode='lines',
                name='All-items (CPI) 6mo avg',
                line=dict(color='#CCCCCC'),  # solid lighter grey
                hovertemplate='Date: %{x|%Y-%m}<br>CPI 6mo avg: %{y:.2f}%<extra></extra>'
            ),
            go.Scatter(
                x=merged['REF_DATE'],
                y=rolling_group,
                mode='lines',
                name=f'{group_name} 6mo avg',
                line=dict(color='black'),  # solid black
                hovertemplate=f'Date: %{{x|%Y-%m}}<br>{group_name} 6mo avg: %{{y:.2f}}%<extra></extra>'
            )
        ]
    # Annotations for all standout differences
    annotations = []
    for i, (date, d, p, n) in enumerate(zip(merged['REF_DATE'], diff, highlight_pos, highlight_neg)):
        if p or n:
            color = 'red' if p else 'blue'
            offset = -30 if p else 30
            annotations.append(dict(
                x=date, y=d,
                text=f"{d:.1f}%",
                showarrow=True, arrowhead=1, ax=0, ay=offset,
                font=dict(color=color, size=11)
            ))
    # Only show rolling or actual lines, not both
    if 'show_rolling' in rolling_opts:
        fig = go.Figure([bars] + rolling_traces)
    else:
        fig = go.Figure([bars, line_cpi, line_group])
    fig.update_layout(
        title=f'Rate of Change: {group_name} vs. All-items (CPI)',
        xaxis_title='Date',
        yaxis_title='Monthly Rate of Change (%)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified',
        annotations=annotations,
        bargap=0.1,
        height=600,
        font=dict(family='"Open Sans", "Helvetica Neue", Arial, sans-serif', size=15)
    )
    # Summary stats
    corr = merged['Rate_of_Change_Group'].corr(merged['Rate_of_Change_CPI'])
    corr_display = dbc.Badge([
        html.Span('Correlation coefficient: ', style={'fontWeight': 'bold'}),
        html.Span(f'{corr:.2f}', style={'fontWeight': 'bold'})
    ], color='info', className='ms-2', style={'fontSize': '1.2rem', 'fontWeight': 'bold', 'padding': '0.7em 1.2em', 'verticalAlign': 'middle'})

    # Calculate correlations for all product groups for the selected date range
    all_corrs = []
    all_corrs_dict = {}
    for group in product_groups:
        group_df = df[df['Products and product groups'] == group]
        merged_all = pd.merge(
            df_cpi[['REF_DATE', 'Rate_of_Change']],
            group_df[['REF_DATE', 'Rate_of_Change']],
            on='REF_DATE',
            suffixes=('_CPI', '_Group')
        )
        merged_all['REF_DATE'] = pd.to_datetime(merged_all['REF_DATE'])
        # Filter by date range
        if start_date is not None:
            merged_all = merged_all[merged_all['REF_DATE'] >= pd.to_datetime(start_date)]
        if end_date is not None:
            merged_all = merged_all[merged_all['REF_DATE'] <= pd.to_datetime(end_date)]
        if len(merged_all) > 1:
            c = merged_all['Rate_of_Change_Group'].corr(merged_all['Rate_of_Change_CPI'])
            if pd.notnull(c):
                all_corrs.append(c)
                all_corrs_dict[group] = c
    # Compute percentile
    if len(all_corrs) > 0:
        sorted_corrs = sorted(all_corrs)
        rank = sum(corr > x for x in sorted_corrs) / len(sorted_corrs)
        if rank >= 2/3:
            score_label = 'High'
            score_color = 'success'
        elif rank >= 1/3:
            score_label = 'Medium'
            score_color = 'warning'
        else:
            score_label = 'Low'
            score_color = 'danger'
        scorecard = dbc.Badge(f'{score_label} correlation', color=score_color, className='ms-2', style={'fontSize': '1.2rem', 'fontWeight': 'bold', 'padding': '0.7em 1.2em', 'verticalAlign': 'middle'})
        # Top 10 correlated groups table with title and ranking
        top_corr = sorted(all_corrs_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        table_header = [html.Thead(html.Tr([html.Th('Rank'), html.Th('Product Group'), html.Th('Correlation')]))]
        table_rows = []
        for idx, (group, val) in enumerate(top_corr, 1):
            if group == group_name:
                row = html.Tr([
                    html.Td(dbc.Badge(f"#{idx}", color='primary', className='me-2', style={'fontWeight': 'bold'})),
                    html.Td(dbc.Badge(group, color='primary', className='me-2', style={'fontWeight': 'bold'})),
                    html.Td(html.B(f'{val:.2f}'))
                ], style={'backgroundColor': '#f5f5f5'})
            else:
                row = html.Tr([
                    html.Td(f"#{idx}"),
                    html.Td(group),
                    html.Td(f'{val:.2f}')
                ])
            table_rows.append(row)
        table_body = [html.Tbody(table_rows)]
        top_corr_table = dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True, striped=True, className='mt-2')
    else:
        scorecard = None
        top_corr_table = None

    stats = f"**Summary for {group_name} vs. All-items (CPI):**  \n"
    stats += f"Mean difference: {diff.mean():.2f}%  \n"
    stats += f"Std deviation: {diff.std():.2f}%  \n"
    stats += f"Max difference: {diff.max():.2f}%  \n"
    stats += f"Min difference: {diff.min():.2f}%  \n"
    return fig, dcc.Markdown(stats), scorecard, corr_display, group_name, top_corr_table

@app.callback(
    Output("top-correlated-sidebar", "is_open"),
    Input("open-sidebar-btn", "n_clicks"),
    State("top-correlated-sidebar", "is_open"),
    prevent_initial_call=True
)
def toggle_sidebar(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run(debug=False) 
