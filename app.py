import pandas as pd  # type: ignore
import plotly.graph_objs as go  # type: ignore
from dash import Dash, dcc, html, Input, Output  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
from datetime import datetime

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

# App setup with Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = 'CPI Interactive Explorer'

controls = dbc.Card([
    dbc.CardBody([
        html.H2('Canadian CPI Explorer', className='card-title mb-4'),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label('Select Product Group:', className='mb-1'),
                    dcc.Dropdown(
                        id='group-dropdown',
                        options=[{'label': g, 'value': g} for g in product_groups],  # type: ignore
                        value=product_groups[0],
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
                    options=[{'label': 'Show 6-month rolling average', 'value': 'show_rolling'}],
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
            ], justify='center', align='center', className='mb-2'),
        ], md=12)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='cpi-comparison-graph', style={'marginTop': '0.5rem'}), md=12)
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='summary-stats', style={'marginTop': 20}), md=12)
    ]),
    html.Footer([
        html.Hr(),
        html.Div('© 2024 Canadian CPI Explorer', className='text-center text-muted', style={'fontSize': '0.9rem'})
    ], style={'marginTop': 40})
], fluid=True, style={'maxWidth': 1000, 'margin': 'auto'})

@app.callback(
    Output('cpi-comparison-graph', 'figure'),
    Output('summary-stats', 'children'),
    Output('correlation-scorecard', 'children'),
    Output('correlation-coeff', 'children'),
    Output('selected-group-title', 'children'),
    Input('group-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('rolling-checkbox', 'value'),
    Input('highlight-threshold', 'value')
)
def update_graph(group_name, start_date, end_date, rolling_opts, highlight_thresh):
    df_cpi = df[df['Products and product groups'] == 'All-items']
    df_group = df[df['Products and product groups'] == group_name]
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
    highlight_pos = diff > highlight_thresh
    highlight_neg = diff < -highlight_thresh

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
        title=f'Rate of Change: All-items (CPI) vs. {group_name}',
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
    else:
        scorecard = None

    stats = f"**Summary for {group_name} vs. All-items (CPI):**  \n"
    stats += f"Mean difference: {diff.mean():.2f}%  \n"
    stats += f"Std deviation: {diff.std():.2f}%  \n"
    stats += f"Max difference: {diff.max():.2f}%  \n"
    stats += f"Min difference: {diff.min():.2f}%  \n"
    return fig, dcc.Markdown(stats), scorecard, corr_display, group_name

if __name__ == '__main__':
    app.run(debug=False) 
