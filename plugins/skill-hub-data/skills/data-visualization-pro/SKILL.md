---
name: data-visualization-pro
description: "Comprehensive Python data visualization specialist covering Plotly (interactive/web), Seaborn (statistical/publication), Matplotlib (foundational/custom), CSV auto-analysis, and dashboard frameworks. Use when creating charts for exploratory analysis, publications, interactive dashboards, or automated CSV summarization. Advises on library selection based on use case: interactive web vs static publication vs fine-grained custom vs streaming."
license: MIT
metadata:
  domain: data-ml
  triggers: data visualization, plotting, charts, Plotly, Seaborn, Matplotlib, Dash, Streamlit, interactive charts, statistical graphics, CSV analysis, dashboard, heatmap, scatter, time series, publication figures, FacetGrid
  role: specialist
  scope: implementation
  output-format: code
  related-skills: data-engineering-pro, pandas-pro
---

# Data Visualization Pro

Python data visualization specialist covering interactive charts (Plotly/Dash), statistical graphics (Seaborn), foundational plots (Matplotlib), automated CSV analysis, and dashboard frameworks (Streamlit, Panel).

## When to Use

- Exploratory data analysis requiring hover, zoom, and web-embeddable charts → Plotly
- Statistical graphics with automatic CI, regression, and faceting → Seaborn
- Publication-quality figures, fine-grained customization, 3D plots → Matplotlib
- Interactive web dashboards with reactive callbacks → Dash or Streamlit
- Automated analysis and visualization of CSV files → auto-analysis pattern
- Real-time/streaming visualizations → Plotly with Dash callbacks

## Library Selection Guide

```
What is the primary requirement?
├── Interactive (hover, zoom, web embed)
│   ├── Static dashboard → Plotly + make_subplots
│   └── Reactive app (callbacks, widgets) → Dash or Streamlit
│
├── Statistical analysis
│   ├── Publication figure → Seaborn (set_context="paper")
│   └── Exploratory EDA → Seaborn pairplot / FacetGrid
│
├── Maximum control / custom layout
│   ├── Multi-panel, GridSpec, 3D → Matplotlib
│   └── Combine libraries → Matplotlib figure + seaborn axes-level
│
└── Automated tabular data summary → Auto-analysis pattern (pandas + seaborn/plotly)
```

## Plotly: Interactive Charts

### API Choice

**Plotly Express (px):** Use for standard charts from DataFrames (1-5 lines). Returns a Figure that accepts all Graph Objects methods.

**Graph Objects (go):** Use for chart types not in px (candlestick, 3D mesh, Sankey), precise multi-trace control, or complex annotations.

```python
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Quick scatter with trendline
fig = px.scatter(df, x='temperature', y='yield', color='region',
                 trendline='ols', title='Yield vs Temperature')

# Mix px and go: add reference line to express figure
fig = px.line(df, x='date', y='revenue')
fig.add_hline(y=target, line_dash='dash', annotation_text='Target')
fig.update_xaxes(rangeslider_visible=True)

# Financial: candlestick
fig = go.Figure(data=[go.Candlestick(
    x=df['date'], open=df['open'],
    high=df['high'], low=df['low'], close=df['close']
)])

# Multi-panel dashboard
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Revenue', 'Orders', 'Distribution', 'Cohorts'),
    specs=[[{'type': 'scatter'}, {'type': 'bar'}],
           [{'type': 'histogram'}, {'type': 'heatmap'}]]
)
fig.add_trace(go.Scatter(x=df['date'], y=df['revenue']), row=1, col=1)
fig.add_trace(go.Bar(x=df['category'], y=df['count']), row=1, col=2)
fig.update_layout(height=700, template='plotly_white')
```

### Interactivity

```python
# Custom hover template
fig.update_traces(
    hovertemplate='<b>%{x}</b><br>Value: %{y:,.0f}<extra></extra>'
)

# Animated over time
fig = px.scatter(df, x='gdp', y='life_exp', size='population',
                 color='continent', animation_frame='year',
                 hover_name='country')

# Dropdown to switch metrics
fig.update_layout(
    updatemenus=[dict(
        buttons=[
            dict(label='Revenue', method='update',
                 args=[{'y': [df['revenue']]}]),
            dict(label='Profit', method='update',
                 args=[{'y': [df['profit']]}]),
        ]
    )]
)
```

### Export

```python
fig.write_html('chart.html', include_plotlyjs='cdn')  # small standalone
fig.write_image('chart.png', width=1200, height=700)  # requires kaleido
fig.write_image('chart.svg')  # vector for publications
```

## Seaborn: Statistical Graphics

### Interface Choice

**Function interface:** For quick, single-purpose plots.
**seaborn.objects (so):** Declarative, composable — preferred for complex layered charts.

Prefer **long-form (tidy) DataFrames** — one variable per column, one observation per row.

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Publication defaults
sns.set_theme(style='ticks', context='paper', font_scale=1.1)

# Relational: scatter with semantic mappings
sns.scatterplot(data=df, x='total_bill', y='tip',
                hue='time', size='party_size', style='sex')

# Distribution: histogram + KDE overlay
sns.histplot(data=df, x='values', hue='group',
             stat='density', multiple='stack', kde=True)

# Categorical: violin with internal box
sns.violinplot(data=df, x='day', y='total_bill',
               hue='sex', split=True)

# Matrix: correlation heatmap
corr = df.corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm',
            center=0, square=True, linewidths=0.5)

# Pairwise EDA overview
sns.pairplot(data=df, hue='species', corner=True, diag_kind='kde')
```

### FacetGrid for Small Multiples

```python
# Figure-level functions handle faceting automatically
g = sns.relplot(data=df, x='x', y='y',
                col='region', row='year',
                hue='product', kind='line',
                height=3, aspect=1.4)
g.set_axis_labels('Date', 'Revenue ($)')
g.set_titles('{col_name} | {row_name}')
sns.despine(trim=True)
g.savefig('facet.pdf', dpi=300, bbox_inches='tight')

# Direct FacetGrid for custom plots
g = sns.FacetGrid(df, col='time', row='sex', height=4)
g.map_dataframe(sns.scatterplot, x='total_bill', y='tip', alpha=0.6)
g.add_legend()
```

### Color Palettes

```python
# Categorical — use colorblind-safe
sns.set_palette("colorblind")

# Sequential — perceptually uniform
sns.kdeplot(data=df, x='x', y='y', cmap='mako', fill=True)

# Diverging — for correlation matrices / deviations from center
sns.heatmap(corr, cmap='vlag', center=0)
```

## Matplotlib: Foundational & Custom

Use the **object-oriented interface** (fig, ax = plt.subplots()) for all production code. Reserve pyplot for quick interactive exploration.

```python
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# Standard workflow
fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
ax.plot(x, y, linewidth=2, label='Observed')
ax.fill_between(x, y_low, y_high, alpha=0.2, label='95% CI')
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_title('Title', fontsize=14, fontweight='bold')
ax.legend(frameon=False)
ax.grid(True, alpha=0.3)
fig.savefig('figure.png', dpi=300, bbox_inches='tight')
```

### Complex Multi-Panel Layouts

```python
# Mosaic layout (Python 3.9+)
fig, axes = plt.subplot_mosaic(
    [['main', 'top_right'],
     ['main', 'bottom_right']],
    figsize=(12, 8), constrained_layout=True
)
axes['main'].imshow(heatmap_data, cmap='viridis', aspect='auto')
axes['top_right'].hist(data['column_a'], bins=30)
axes['bottom_right'].boxplot([group_a, group_b, group_c])

# GridSpec for precise control
gs = gridspec.GridSpec(3, 3)
ax_main = fig.add_subplot(gs[:2, :2])   # 2x2 top-left
ax_side = fig.add_subplot(gs[:2, 2])    # right column
ax_bottom = fig.add_subplot(gs[2, :])   # full bottom row
```

### 3D and Scientific

```python
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')

# Contour plot
contour = ax2d.contourf(X, Y, Z, levels=15, cmap='plasma')
ax2d.contour(X, Y, Z, levels=15, colors='white', alpha=0.4)
plt.colorbar(contour, ax=ax2d)
```

## CSV Auto-Analysis Pattern

When a user uploads or references a CSV, immediately run a comprehensive analysis — no prompting needed.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def analyze_csv(file_path: str) -> None:
    df = pd.read_csv(file_path, parse_dates=True, infer_datetime_format=True)

    # 1. Schema overview
    print(f"Shape: {df.shape}   |   Dtypes: {df.dtypes.value_counts().to_dict()}")
    print(f"Missing: {df.isnull().sum()[df.isnull().sum() > 0].to_dict()}")
    print(df.describe().round(2))

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    date_cols = df.select_dtypes(include='datetime').columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # 2. Correlation heatmap (if multiple numeric columns)
    if len(numeric_cols) >= 3:
        sns.heatmap(df[numeric_cols].corr(), annot=True, fmt='.2f',
                    cmap='coolwarm', center=0)
        plt.title('Correlations'); plt.tight_layout(); plt.show()

    # 3. Distributions for numeric columns
    for col in numeric_cols[:6]:
        sns.histplot(data=df, x=col, kde=True)
        plt.title(col); plt.show()

    # 4. Time series (if date columns found)
    for date_col in date_cols[:1]:
        df_sorted = df.sort_values(date_col)
        for num_col in numeric_cols[:2]:
            sns.lineplot(data=df_sorted, x=date_col, y=num_col)
            plt.title(f'{num_col} over {date_col}')
            plt.xticks(rotation=30); plt.tight_layout(); plt.show()

    # 5. Category distributions
    for col in cat_cols[:3]:
        if df[col].nunique() <= 20:
            df[col].value_counts().plot(kind='bar')
            plt.title(col); plt.tight_layout(); plt.show()
```

**Adapt analysis to detected data type:**
- Sales/e-commerce (revenue, products, dates) → time-series trends, product performance
- Customer data (demographics, segments) → distributions, segmentation
- Survey data (categorical responses, ratings) → frequency, cross-tabs
- Operational (timestamps, metrics, status) → time-series, SLA analysis

## Dashboard Frameworks

**Dash (Plotly ecosystem, production-grade):**
```python
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Dropdown(id='metric', options=['revenue', 'profit'], value='revenue'),
    dcc.Graph(id='chart')
])

@app.callback(Output('chart', 'figure'), Input('metric', 'value'))
def update(metric: str):
    return px.line(df, x='date', y=metric)

app.run_server(debug=True)
```

**Streamlit (rapid prototyping):** Use for internal tools and quick demos. Dash for production apps with complex callbacks.
```python
import streamlit as st
metric = st.selectbox('Metric', ['revenue', 'profit'])
st.plotly_chart(px.line(df, x='date', y=metric), use_container_width=True)
```

## Best Practices

**Accessibility:**
- Use colorblind-friendly palettes (`colorblind` in seaborn, `cividis`/`viridis` in matplotlib)
- Add text labels or patterns in addition to color encoding
- Ensure 3:1+ contrast ratio for text on backgrounds

**Performance:**
- For datasets >100K rows, aggregate before plotting; never plot raw rows in Plotly
- `rasterized=True` in matplotlib for dense scatter plots (reduces PDF file size)
- Use `partial_data` pattern in Dash for large streaming datasets

**Publication output:**
```python
sns.set_theme(style='ticks', context='paper', font='serif', font_scale=1.0)
fig.savefig('fig1.pdf', dpi=300, bbox_inches='tight')  # vector for journals
fig.savefig('fig1.png', dpi=600, bbox_inches='tight')  # raster for submissions
```

**Colormap selection:**
- Sequential (`viridis`, `plasma`): ordered, continuous data
- Diverging (`coolwarm`, `vlag`): data with meaningful zero/center
- Qualitative (`Set2`, `colorblind`): categorical groups
- Never use `jet` (perceptually non-uniform, misleading)
