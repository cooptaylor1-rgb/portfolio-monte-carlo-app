"""
Institutional-Grade Chart Library
Professional visualizations for wealth management and portfolio analysis
"""

import altair as alt
import pandas as pd
import numpy as np
from typing import Optional, Dict, List

# Professional color schemes
INSTITUTIONAL_COLORS = {
    'primary': '#1B3B5F',      # Salem Navy
    'accent': '#C4A053',       # Salem Gold
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Amber
    'danger': '#EF4444',       # Red
    'neutral': '#6B7280',      # Gray
    'percentiles': {
        'p10': '#EF4444',      # Red for worst case
        'p25': '#F59E0B',      # Amber
        'p50': '#1B3B5F',      # Navy for median
        'p75': '#10B981',      # Green
        'p90': '#059669'       # Dark green for best case
    }
}

def create_institutional_fan_chart(stats_df: pd.DataFrame, 
                                   title: str = "Portfolio Projection",
                                   show_annotations: bool = True,
                                   highlight_median: bool = True) -> alt.Chart:
    """
    Create an institutional-grade fan chart with professional styling.
    
    Features:
    - Confidence intervals with gradient fills
    - Dynamic annotations for key milestones
    - Median line emphasis
    - Clean axis formatting
    - Professional color scheme
    """
    
    # Base chart configuration
    base = alt.Chart(stats_df).encode(
        x=alt.X('Month:Q', 
                title='Years into Retirement',
                scale=alt.Scale(domain=[0, stats_df['Month'].max()]),
                axis=alt.Axis(
                    format='',
                    labelExpr='datum.value % 12 === 0 ? datum.value / 12 : ""',
                    labelFontSize=11,
                    titleFontSize=12,
                    titlePadding=10,
                    grid=True,
                    gridOpacity=0.2
                ))
    )
    
    # P10-P90 band (outermost, lightest)
    p10_p90 = base.mark_area(
        opacity=0.15,
        color=INSTITUTIONAL_COLORS['neutral']
    ).encode(
        y=alt.Y('P10:Q', title='Portfolio Value ($)', 
                axis=alt.Axis(format='$,.0f', labelFontSize=11, titleFontSize=12)),
        y2='P90:Q',
        tooltip=[
            alt.Tooltip('Month:Q', title='Month', format='.0f'),
            alt.Tooltip('P10:Q', title='10th Percentile', format='$,.0f'),
            alt.Tooltip('P90:Q', title='90th Percentile', format='$,.0f')
        ]
    )
    
    # P25-P75 band (middle, medium opacity)
    p25_p75 = base.mark_area(
        opacity=0.25,
        color=INSTITUTIONAL_COLORS['primary']
    ).encode(
        y='P25:Q',
        y2='P75:Q',
        tooltip=[
            alt.Tooltip('Month:Q', title='Month', format='.0f'),
            alt.Tooltip('P25:Q', title='25th Percentile', format='$,.0f'),
            alt.Tooltip('P75:Q', title='75th Percentile', format='$,.0f')
        ]
    )
    
    # Median line (bold and prominent)
    median_line = base.mark_line(
        size=3 if highlight_median else 2,
        color=INSTITUTIONAL_COLORS['primary'],
        strokeDash=[0] if highlight_median else [5, 5]
    ).encode(
        y='Median:Q',
        tooltip=[
            alt.Tooltip('Month:Q', title='Month', format='.0f'),
            alt.Tooltip('Median:Q', title='Median Value', format='$,.0f')
        ]
    )
    
    # P10 line (downside risk)
    p10_line = base.mark_line(
        size=1,
        color=INSTITUTIONAL_COLORS['danger'],
        strokeDash=[3, 3],
        opacity=0.6
    ).encode(
        y='P10:Q',
        tooltip=[
            alt.Tooltip('Month:Q', title='Month', format='.0f'),
            alt.Tooltip('P10:Q', title='10th Percentile (Downside)', format='$,.0f')
        ]
    )
    
    # P90 line (upside potential)
    p90_line = base.mark_line(
        size=1,
        color=INSTITUTIONAL_COLORS['success'],
        strokeDash=[3, 3],
        opacity=0.6
    ).encode(
        y='P90:Q',
        tooltip=[
            alt.Tooltip('Month:Q', title='Month', format='.0f'),
            alt.Tooltip('P90:Q', title='90th Percentile (Upside)', format='$,.0f')
        ]
    )
    
    # Combine layers
    chart = p10_p90 + p25_p75 + p10_line + median_line + p90_line
    
    # Add annotations if requested
    if show_annotations:
        # Find key milestones (e.g., where median crosses zero or specific thresholds)
        final_values = stats_df.iloc[-1]
        
        annotation_data = pd.DataFrame([{
            'Month': stats_df['Month'].max(),
            'Value': final_values['Median'],
            'Label': f"Median: ${final_values['Median']:,.0f}"
        }])
        
        annotation = alt.Chart(annotation_data).mark_text(
            align='right',
            dx=-5,
            dy=-5,
            fontSize=11,
            fontWeight=600,
            color=INSTITUTIONAL_COLORS['primary']
        ).encode(
            x='Month:Q',
            y='Value:Q',
            text='Label:N'
        )
        
        chart = chart + annotation
    
    # Configure chart
    chart = chart.properties(
        width=700,
        height=400,
        title={
            'text': title,
            'fontSize': 16,
            'fontWeight': 600,
            'anchor': 'start',
            'color': INSTITUTIONAL_COLORS['primary']
        }
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        labelColor=INSTITUTIONAL_COLORS['neutral'],
        titleColor=INSTITUTIONAL_COLORS['primary'],
        gridColor='#E5E7EB',
        domainColor='#D1D5DB'
    )
    
    return chart


def create_waterfall_chart(cashflows: pd.DataFrame, 
                           title: str = "Cash Flow Breakdown") -> alt.Chart:
    """
    Create a waterfall chart for visualizing retirement cashflows.
    
    Shows contributions (+) and withdrawals (-) over time.
    """
    
    # Calculate cumulative values for waterfall effect
    cashflows['start'] = cashflows['amount'].cumsum() - cashflows['amount']
    cashflows['end'] = cashflows['amount'].cumsum()
    cashflows['center'] = (cashflows['start'] + cashflows['end']) / 2
    
    # Determine color based on positive/negative
    cashflows['color'] = cashflows['amount'].apply(
        lambda x: INSTITUTIONAL_COLORS['success'] if x > 0 else INSTITUTIONAL_COLORS['danger']
    )
    
    # Base chart
    bars = alt.Chart(cashflows).mark_bar(size=40).encode(
        x=alt.X('category:N', title='', axis=alt.Axis(labelAngle=-45, labelFontSize=11)),
        y=alt.Y('start:Q', title='Cumulative Value ($)', axis=alt.Axis(format='$,.0f')),
        y2='end:Q',
        color=alt.Color('color:N', scale=None),
        tooltip=[
            alt.Tooltip('category:N', title='Category'),
            alt.Tooltip('amount:Q', title='Amount', format='$,.0f'),
            alt.Tooltip('end:Q', title='Running Total', format='$,.0f')
        ]
    )
    
    # Connecting lines
    lines = alt.Chart(cashflows).mark_rule(
        strokeDash=[2, 2],
        color='#9CA3AF',
        size=1
    ).encode(
        x=alt.X('category:N'),
        y='end:Q'
    )
    
    # Value labels
    labels = alt.Chart(cashflows).mark_text(
        dy=-5,
        fontSize=10,
        fontWeight=600
    ).encode(
        x='category:N',
        y='center:Q',
        text=alt.Text('amount:Q', format='$,.0f'),
        color=alt.value(INSTITUTIONAL_COLORS['primary'])
    )
    
    chart = (bars + lines + labels).properties(
        width=600,
        height=350,
        title={
            'text': title,
            'fontSize': 16,
            'fontWeight': 600,
            'anchor': 'start'
        }
    ).configure_view(
        strokeWidth=0
    )
    
    return chart


def create_scenario_comparison_chart(scenarios: Dict[str, pd.DataFrame],
                                     metric: str = 'Median',
                                     title: str = "Scenario Comparison") -> alt.Chart:
    """
    Create an overlay chart comparing multiple scenarios.
    
    Each scenario gets a distinct color and line style.
    """
    
    # Prepare data
    comparison_data = []
    colors_list = [
        INSTITUTIONAL_COLORS['primary'],
        INSTITUTIONAL_COLORS['success'],
        INSTITUTIONAL_COLORS['warning'],
        INSTITUTIONAL_COLORS['danger'],
        INSTITUTIONAL_COLORS['neutral']
    ]
    
    for idx, (scenario_name, stats_df) in enumerate(scenarios.items()):
        scenario_data = stats_df[['Month', metric]].copy()
        scenario_data['Scenario'] = scenario_name
        scenario_data['Color'] = colors_list[idx % len(colors_list)]
        comparison_data.append(scenario_data)
    
    combined_df = pd.concat(comparison_data, ignore_index=True)
    
    # Create chart
    chart = alt.Chart(combined_df).mark_line(size=2.5, point=False).encode(
        x=alt.X('Month:Q', 
                title='Years into Retirement',
                axis=alt.Axis(
                    format='',
                    labelExpr='datum.value % 12 === 0 ? datum.value / 12 : ""',
                    grid=True,
                    gridOpacity=0.2
                )),
        y=alt.Y(f'{metric}:Q', 
                title='Portfolio Value ($)',
                axis=alt.Axis(format='$,.0f')),
        color=alt.Color('Scenario:N',
                       legend=alt.Legend(
                           title='Scenarios',
                           orient='right',
                           titleFontSize=12,
                           labelFontSize=11
                       )),
        strokeDash=alt.StrokeDash('Scenario:N', 
                                  legend=alt.Legend(title=None)),
        tooltip=[
            alt.Tooltip('Scenario:N', title='Scenario'),
            alt.Tooltip('Month:Q', title='Month', format='.0f'),
            alt.Tooltip(f'{metric}:Q', title=f'{metric} Value', format='$,.0f')
        ]
    ).properties(
        width=700,
        height=400,
        title={
            'text': title,
            'fontSize': 16,
            'fontWeight': 600,
            'anchor': 'start'
        }
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        gridColor='#E5E7EB',
        domainColor='#D1D5DB'
    )
    
    return chart


def create_success_gauge(probability: float, 
                        threshold_excellent: float = 0.9,
                        threshold_good: float = 0.75,
                        threshold_moderate: float = 0.6) -> alt.Chart:
    """
    Create a professional success probability gauge.
    
    Visual indicator with color coding and risk assessment.
    """
    
    # Determine risk level and color
    if probability >= threshold_excellent:
        color = INSTITUTIONAL_COLORS['success']
        risk_level = 'Excellent'
    elif probability >= threshold_good:
        color = '#10B981'  # Green
        risk_level = 'Good'
    elif probability >= threshold_moderate:
        color = INSTITUTIONAL_COLORS['warning']
        risk_level = 'Moderate'
    else:
        color = INSTITUTIONAL_COLORS['danger']
        risk_level = 'Caution'
    
    # Create gauge data
    gauge_data = pd.DataFrame([
        {'category': 'Success', 'value': probability, 'color': color},
        {'category': 'Risk', 'value': 1 - probability, 'color': '#E5E7EB'}
    ])
    
    # Arc chart
    base = alt.Chart(gauge_data).encode(
        theta=alt.Theta('value:Q', stack=True),
        color=alt.Color('color:N', scale=None, legend=None),
        tooltip=[
            alt.Tooltip('category:N', title='Category'),
            alt.Tooltip('value:Q', title='Probability', format='.1%')
        ]
    )
    
    arc = base.mark_arc(
        innerRadius=80,
        outerRadius=120,
        stroke='white',
        strokeWidth=2
    )
    
    # Center text
    text_data = pd.DataFrame([{
        'text': f'{probability:.1%}',
        'subtitle': risk_level
    }])
    
    center_text = alt.Chart(text_data).mark_text(
        fontSize=32,
        fontWeight=700,
        color=color
    ).encode(
        text='text:N'
    )
    
    subtitle_text = alt.Chart(text_data).mark_text(
        fontSize=14,
        dy=25,
        color=INSTITUTIONAL_COLORS['neutral']
    ).encode(
        text='subtitle:N'
    )
    
    chart = (arc + center_text + subtitle_text).properties(
        width=250,
        height=250,
        title={
            'text': 'Plan Success Probability',
            'fontSize': 14,
            'fontWeight': 600,
            'anchor': 'middle'
        }
    )
    
    return chart


def create_distribution_histogram(final_values: np.ndarray,
                                  title: str = "Ending Portfolio Distribution") -> alt.Chart:
    """
    Create a histogram showing the distribution of final portfolio values.
    
    Includes markers for key percentiles.
    """
    
    # Create bins
    hist, bin_edges = np.histogram(final_values, bins=50)
    hist_data = pd.DataFrame({
        'value': bin_edges[:-1],
        'count': hist,
        'bin_end': bin_edges[1:]
    })
    hist_data['bin_center'] = (hist_data['value'] + hist_data['bin_end']) / 2
    
    # Base histogram
    bars = alt.Chart(hist_data).mark_bar(
        opacity=0.7,
        color=INSTITUTIONAL_COLORS['primary']
    ).encode(
        x=alt.X('value:Q', 
                title='Final Portfolio Value ($)',
                axis=alt.Axis(format='$,.0f')),
        x2='bin_end:Q',
        y=alt.Y('count:Q', title='Frequency'),
        tooltip=[
            alt.Tooltip('bin_center:Q', title='Portfolio Value', format='$,.0f'),
            alt.Tooltip('count:Q', title='Scenarios')
        ]
    )
    
    # Percentile markers
    percentiles = [10, 50, 90]
    percentile_values = np.percentile(final_values, percentiles)
    percentile_data = pd.DataFrame({
        'percentile': [f'P{p}' for p in percentiles],
        'value': percentile_values,
        'y': [hist.max() * 0.8, hist.max() * 0.9, hist.max() * 0.8]
    })
    
    rules = alt.Chart(percentile_data).mark_rule(
        strokeDash=[4, 4],
        size=2
    ).encode(
        x='value:Q',
        color=alt.Color('percentile:N', legend=None),
        tooltip=[
            alt.Tooltip('percentile:N', title='Percentile'),
            alt.Tooltip('value:Q', title='Value', format='$,.0f')
        ]
    )
    
    chart = (bars + rules).properties(
        width=600,
        height=350,
        title={
            'text': title,
            'fontSize': 16,
            'fontWeight': 600,
            'anchor': 'start'
        }
    ).configure_view(
        strokeWidth=0
    )
    
    return chart
