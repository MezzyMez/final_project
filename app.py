import pandas as pd
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output
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

# App setup
app = Dash(__name__)
app.title = 'CPI Interactive Explorer'

app.layout = html.Div([
    html.H1('Canadian CPI Explorer'),
    html.Label('Select Product Group:'),
    dcc.Dropdown(
        id='group-dropdown',
        options=[{'label': g, 'value': g} for g in product_groups],
        value=product_groups[0],
        style={'width': '60%'}
    ),
    html.Label('Select Date Range:'),
    dcc.DatePickerRange(
        id='date-range',
        min_date_allowed=min_date,
        max_date_allowed=max_date,
        start_date=default_start,
        end_date=max_date,
        display_format='YYYY-MM-DD',
        style={'marginBottom': 20}
    ),
    dcc.Graph(id='cpi-comparison-graph'),
    html.Div(id='summary-stats', style={'marginTop': 30})
], style={'maxWidth': 900, 'margin': 'auto'})

@app.callback(
    Output('cpi-comparison-graph', 'figure'),
    Output('summary-stats', 'children'),
    Input('group-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_graph(group_name, start_date, end_date):
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
    diff = merged['Rate_of_Change_Group'] - merged['Rate_of_Change_CPI']
    highlight_thresh = 2
    highlight_pos = diff > highlight_thresh
    highlight_neg = diff < -highlight_thresh

    # Bar traces
    bars = go.Bar(
        x=merged['REF_DATE'],
        y=diff,
        marker_color=['red' if p else 'blue' if n else 'orange' for p, n in zip(highlight_pos, highlight_neg)],
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
        line=dict(color='black'),
        hovertemplate='Date: %{x|%Y-%m}<br>CPI: %{y:.2f}%<extra></extra>'
    )
    line_group = go.Scatter(
        x=merged['REF_DATE'],
        y=merged['Rate_of_Change_Group'],
        mode='lines',
        name=group_name,
        line=dict(color='seagreen'),
        hovertemplate=f'Date: %{{x|%Y-%m}}<br>{group_name}: %{{y:.2f}}%<extra></extra>'
    )
    # Annotations for max/min diff
    annotations = []
    if not diff.empty:
        max_idx = diff.idxmax()
        min_idx = diff.idxmin()
        annotations = [
            dict(x=merged['REF_DATE'][max_idx], y=diff[max_idx],
                 text=f"{diff[max_idx]:.1f}%", showarrow=True, arrowhead=1, ax=0, ay=-30, font=dict(color='red', size=12)),
            dict(x=merged['REF_DATE'][min_idx], y=diff[min_idx],
                 text=f"{diff[min_idx]:.1f}%", showarrow=True, arrowhead=1, ax=0, ay=30, font=dict(color='blue', size=12)),
        ]
    fig = go.Figure([bars, line_cpi, line_group])
    fig.update_layout(
        title=f'Rate of Change: All-items (CPI) vs. {group_name}',
        xaxis_title='Date',
        yaxis_title='Monthly Rate of Change (%)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified',
        annotations=annotations,
        bargap=0.1,
        height=600
    )
    # Summary stats
    stats = f"**Summary for {group_name} vs. All-items (CPI):**  \n"
    stats += f"Mean difference: {diff.mean():.2f}%  \n"
    stats += f"Std deviation: {diff.std():.2f}%  \n"
    stats += f"Max difference: {diff.max():.2f}%  \n"
    stats += f"Min difference: {diff.min():.2f}%"
    return fig, dcc.Markdown(stats)

if __name__ == '__main__':
    app.run(debug=False) 
