import math
from dataclasses import dataclass
from typing import List, Tuple
from datetime import date, datetime
import io
import base64
import hashlib

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from io import BytesIO
import xlsxwriter
import zipfile

# Institutional-grade modules
from charts_institutional import (
    create_institutional_fan_chart,
    create_waterfall_chart,
    create_scenario_comparison_chart,
    create_success_gauge,
    create_distribution_histogram,
    INSTITUTIONAL_COLORS
)
from scenario_intelligence import (
    INSTITUTIONAL_SCENARIOS,
    AssumptionValidator,
    ScenarioDifferential,
    calculate_required_capital,
    assess_glidepath
)

# AI-powered analysis modules
from ai_engine import AIAnalysisEngine, AIResearchAssistant
from ai_stress_audit import StressTestBuilder, AuditTrailSystem

# Production infrastructure modules
from config import config
from observability import health_checker, metrics, structured_logger, track_request, track_simulation, new_correlation_id, correlation_context
from security import InputValidator, default_rate_limiter, RateLimitExceeded, SecurityHeaders

# Salem Investment Counselors Color Scheme
SALEM_GOLD = "#C4A053"  # Gold/tan from logo
SALEM_NAVY = "#1B3B5F"  # Dark blue/navy
SALEM_LIGHT_GOLD = "#D4B87D"  # Lighter gold accent
SALEM_DARK_NAVY = "#0F2540"  # Darker navy


def apply_salem_styling():
    """Apply Apple-inspired premium styling with Salem Investment Counselors branding + Phase 5 enhancements."""
    st.markdown(f"""
    <style>
        /* Import SF Pro Display font (Apple's signature font) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* ===== PHASE 5: SIMPLIFICATION & POLISH - Typography Optimization ===== */
        /* Global text color and typography - Apple style */
        body, html, .stApp, .main, [data-testid="stAppViewContainer"] {{
            color: {SALEM_NAVY} !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', 'SF Pro Display', sans-serif !important;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* Main app background - subtle gradient like Apple products */
        .main {{
            background: linear-gradient(to bottom, #fafafa 0%, #ffffff 100%);
            padding: 0.75rem 1.5rem;  /* PHASE 5: Tighter padding */
        }}
        .stApp {{
            background: linear-gradient(to bottom, #fafafa 0%, #ffffff 100%);
        }}
        
        /* Logo image - crisp and clear */
        img {{
            image-rendering: -webkit-optimize-contrast;
            image-rendering: high-quality;
            -ms-interpolation-mode: bicubic;
            max-width: 100%;
            height: auto;
        }}
        
        /* Specific styling for Salem logo */
        [data-testid="stImage"] img {{
            image-rendering: auto;
            -webkit-backface-visibility: hidden;
            backface-visibility: hidden;
            transform: translateZ(0);
        }}
        
        .stMarkdown, p, span, div {{
            color: {SALEM_NAVY} !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            font-size: 1rem !important;
            line-height: 1.5 !important;  /* PHASE 5: Better readability */
            letter-spacing: -0.01em;  /* PHASE 5: Tighter tracking */
            margin-bottom: 0.5rem !important;  /* PHASE 5: Reduced spacing */
        }}
        
        /* ===== PHASE 5: Enhanced Metrics with Animations ===== */
        /* Metrics - Apple card style with subtle shadows */
        .stMetric {{
            background: rgba(255, 255, 255, 0.95);
            padding: 14px 16px;  /* PHASE 5: Tighter padding */
            border-radius: 12px;
            border: 1px solid rgba(196, 160, 83, 0.2);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0,0,0,0.02);
            backdrop-filter: blur(20px);
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);  /* PHASE 5: Faster transition */
        }}
        .stMetric:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(196, 160, 83, 0.3);
        }}
        .stMetric label {{
            color: {SALEM_NAVY} !important;
            font-size: 0.8125rem !important;  /* PHASE 5: Slightly smaller */
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            opacity: 0.7;
        }}
        .stMetric [data-testid=\"stMetricValue\"] {{
            color: {SALEM_NAVY} !important;
            font-size: 1.875rem !important;  /* PHASE 5: Slightly smaller for density */
            font-weight: 700 !important;
            letter-spacing: -0.03em;
            margin: 2px 0;  /* PHASE 5: Tighter margins */
        }}
        .stMetric [data-testid=\"stMetricDelta\"] {{
            color: {SALEM_GOLD} !important;
            font-size: 0.9375rem !important;  /* PHASE 5: Proportionally smaller */
            font-weight: 600;
        }}
        
        /* ===== PHASE 5: Simplified Headers with Tighter Spacing ===== */
        h1 {{
            color: {SALEM_NAVY} !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            font-weight: 700 !important;
            font-size: 2.25rem !important;  /* PHASE 5: Slightly smaller */
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.04em;
            line-height: 1.1;
        }}
        h2 {{
            color: {SALEM_NAVY} !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            font-weight: 700 !important;
            font-size: 1.625rem !important;  /* PHASE 5: Slightly smaller */
            margin-top: 1rem !important;  /* PHASE 5: Reduced top margin */
            margin-bottom: 0.5rem !important;  /* PHASE 5: Reduced bottom margin */
            letter-spacing: -0.03em;
            line-height: 1.2;
            border: none;
            padding-bottom: 0;
        }}
        h3 {{
            color: {SALEM_NAVY} !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            font-weight: 600 !important;
            font-size: 1.125rem !important;  /* PHASE 5: Slightly smaller */
            letter-spacing: -0.02em;
            margin-top: 0.5rem !important;  /* PHASE 5: Reduced top margin */
            margin-bottom: 0.25rem !important;
        }}
        h4 {{
            color: {SALEM_NAVY} !important;
            font-size: 1.0625rem !important;  /* PHASE 5: Slightly smaller */
            font-weight: 600 !important;
            letter-spacing: -0.02em;
            margin-top: 0.375rem !important;  /* PHASE 5: Reduced top margin */
            margin-bottom: 0.25rem !important;
        }}
        
        /* ===== PHASE 5: Faster Button Animations ===== */
        /* Buttons - Apple style with smooth animations */
        .stButton>button {{
            background: linear-gradient(180deg, {SALEM_GOLD} 0%, #B89648 100%);
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 10px 24px !important;
            border-radius: 12px !important;
            font-size: 1rem !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;  /* PHASE 5: Faster */
            box-shadow: 0 2px 12px rgba(196, 160, 83, 0.3) !important;
            letter-spacing: -0.01em;
        }}
        .stButton>button:hover {{
            background: linear-gradient(180deg, #D4B87D 0%, {SALEM_GOLD} 100%) !important;
            box-shadow: 0 4px 20px rgba(196, 160, 83, 0.4) !important;
            transform: translateY(-1px) !important;
        }}
        .stButton>button:active {{
            background: linear-gradient(180deg, #B89648 0%, #A88540 100%) !important;
            box-shadow: 0 2px 8px rgba(196, 160, 83, 0.3) !important;
            transform: translateY(0px) !important;
        }}
        
        /* Download button styling - Apple style secondary button */
        .stDownloadButton>button {{
            background: white !important;
            color: {SALEM_GOLD} !important;
            font-weight: 600 !important;
            border: 2px solid {SALEM_GOLD} !important;
            padding: 10px 24px !important;
            border-radius: 12px !important;
            font-size: 1rem !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;  /* PHASE 5: Faster */
            box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
            letter-spacing: -0.01em;
        }}
        .stDownloadButton>button:hover {{
            background: rgba(196, 160, 83, 0.1) !important;
            border-color: {SALEM_GOLD} !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.12) !important;
            transform: translateY(-1px) !important;
        }}
        .stDownloadButton>button:active {{
            background: rgba(196, 160, 83, 0.2) !important;
            transform: translateY(0px) !important;
        }}
        
        /* ===== PHASE 5: Enhanced Chart Containers ===== */
        /* Chart containers - Apple card style */
        [data-testid="stVegaLiteChart"] {{
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(196, 160, 83, 0.15) !important;
            border-radius: 12px !important;
            padding: 10px !important;  /* PHASE 5: Tighter padding */
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0,0,0,0.02) !important;
            backdrop-filter: blur(20px);
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);  /* PHASE 5: Faster */
            overflow: hidden !important;
            max-width: 100% !important;
        }}
        [data-testid="stVegaLiteChart"]:hover {{
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
        }}
        
        /* Chart canvas */
        [data-testid="stVegaLiteChart"] canvas,
        [data-testid="stVegaLiteChart"] svg {{
            background-color: transparent !important;
            max-width: 100% !important;
            height: auto !important;
        }}
        
        /* Chart panel */
        .vega-embed {{
            background-color: transparent !important;
            width: 100% !important;
            overflow: hidden !important;
        }}
        .vega-embed details {{
            background-color: transparent !important;
        }}
        
        /* Sidebar - Apple style with frosted glass effect */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(248, 249, 250, 0.98) 0%, rgba(255, 255, 255, 0.95) 100%);
            border-right: 1px solid rgba(196, 160, 83, 0.2);
            backdrop-filter: blur(40px);
            padding: 1rem 1rem;
        }}
        section[data-testid="stSidebar"] .stMarkdown {{
            color: {SALEM_NAVY} !important;
            margin-bottom: 0.25rem !important;
        }}
        
        /* Tighter spacing for input groups */
        section[data-testid="stSidebar"] .element-container {{
            margin-bottom: 0.5rem !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{
            gap: 0.25rem !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            gap: 0.25rem !important;
        }}
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {{
            color: {SALEM_NAVY} !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
            margin-top: 0.75rem !important;
            margin-bottom: 0.25rem !important;
        }}
        section[data-testid="stSidebar"] label {{
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            opacity: 0.8;
            margin-bottom: 4px !important;
        }}
        
        /* Sidebar inputs - Apple style */
        section[data-testid="stSidebar"] input[type="text"],
        section[data-testid="stSidebar"] input[type="number"] {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(196, 160, 83, 0.3) !important;
            border-radius: 10px !important;
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
            padding: 8px 12px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
            margin-bottom: 0 !important;
        }}
        
        section[data-testid="stSidebar"] input[type="text"]:focus,
        section[data-testid="stSidebar"] input[type="number"]:focus {{
            border-color: {SALEM_GOLD} !important;
            outline: none !important;
            box-shadow: 0 4px 16px rgba(196, 160, 83, 0.2) !important;
            background-color: white !important;
        }}
        
        /* Date input */
        section[data-testid="stSidebar"] [data-baseweb="base-input"] {{
            background-color: transparent !important;
            border: none !important;
        }}
        
        section[data-testid="stSidebar"] input[type="date"] {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(196, 160, 83, 0.3) !important;
            border-radius: 10px !important;
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
            padding: 8px 12px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
        }}
        
        /* Textarea */
        section[data-testid="stSidebar"] textarea {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(196, 160, 83, 0.3) !important;
            border-radius: 10px !important;
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
            padding: 8px 12px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
        }}
        
        /* Selectbox */
        section[data-testid="stSidebar"] [data-baseweb="select"] {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(196, 160, 83, 0.3) !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        
        section[data-testid="stSidebar"] [data-baseweb="select"]:hover {{
            border-color: rgba(196, 160, 83, 0.5) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        }}
        
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background-color: transparent !important;
            border: none !important;
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            letter-spacing: -0.01em !important;
        }}
        
        /* Main content area selectbox */
        .main [data-baseweb="select"] {{
            background-color: rgba(27, 59, 95, 0.95) !important;
            border: 1px solid rgba(196, 160, 83, 0.3) !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        
        .main [data-baseweb="select"]:hover {{
            border-color: rgba(196, 160, 83, 0.5) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        }}
        
        .main [data-baseweb="select"] > div {{
            background-color: transparent !important;
            border: none !important;
            color: white !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
        }}
        
        .main [data-baseweb="select"] svg {{
            fill: white !important;
        }}
        
        /* Main content area selectbox text styling */
        .main [data-baseweb="select"] [role="combobox"] {{
            color: white !important;
        }}
        
        .main [data-baseweb="select"] input {{
            color: white !important;
        }}
        
        /* Sidebar slider */
        section[data-testid="stSidebar"] [data-testid="stSlider"] {{
            padding: 8px 0 !important;
            margin-bottom: 0 !important;
        }}
        
        section[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{
            background: linear-gradient(135deg, {SALEM_GOLD} 0%, #B89648 100%) !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(196, 160, 83, 0.3) !important;
            width: 18px !important;
            height: 18px !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        
        section[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"]:hover {{
            transform: scale(1.1) !important;
            box-shadow: 0 4px 12px rgba(196, 160, 83, 0.4) !important;
        }}
        
        section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
            background: linear-gradient(90deg, {SALEM_GOLD} 0%, rgba(196, 160, 83, 0.3) 100%) !important;
            height: 4px !important;
            border-radius: 2px !important;
        }}
        
        section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] > div {{
            background-color: rgba(196, 160, 83, 0.15) !important;
            height: 4px !important;
            border-radius: 2px !important;
        }}
        
        /* Ensure text visibility in all inputs */
        section[data-testid="stSidebar"] input::placeholder {{
            color: rgba(27, 59, 95, 0.5) !important;
            letter-spacing: -0.01em !important;
        }}
        
        /* Radio buttons and checkboxes */
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            letter-spacing: -0.01em !important;
        }}
        
        [data-testid="stCheckbox"] {{
            padding: 6px 0 !important;
            margin-bottom: 0 !important;
        }}
        
        [data-testid="stCheckbox"] > label {{
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            letter-spacing: -0.01em !important;
        }}
        
        [data-testid="stCheckbox"] input[type="checkbox"] {{
            border: 1px solid rgba(196, 160, 83, 0.4) !important;
            border-radius: 4px !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        
        [data-testid="stCheckbox"] input[type="checkbox"]:checked {{
            background-color: {SALEM_GOLD} !important;
            border-color: {SALEM_GOLD} !important;
        }}
        
        /* Dataframes - Apple-inspired tables */
        .dataframe {{
            font-size: 0.95rem !important;
            color: {SALEM_NAVY} !important;
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(196, 160, 83, 0.2) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
            letter-spacing: -0.01em !important;
        }}
        
        .dataframe th {{
            background: linear-gradient(180deg, {SALEM_NAVY} 0%, #152D4A 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 12px 16px !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            border: none !important;
        }}
        
        .dataframe td {{
            padding: 10px 16px !important;
            border-bottom: 1px solid rgba(196, 160, 83, 0.1) !important;
            background-color: transparent !important;
            color: {SALEM_NAVY} !important;
            font-weight: 400 !important;
        }}
        
        .dataframe tr:hover td {{
            background-color: rgba(196, 160, 83, 0.05) !important;
        }}
        
        .dataframe tr:last-child td {{
            border-bottom: none !important;
        }}
        
        /* Tab Navigation - Apple style tabs */
        .stTabs {{
            background: transparent;
            margin-top: 1rem;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: rgba(255, 255, 255, 0.6);
            padding: 8px;
            border-radius: 16px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            backdrop-filter: blur(20px);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            color: {SALEM_NAVY};
            font-weight: 500;
            font-size: 0.95rem;
            transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
            letter-spacing: -0.01em;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(196, 160, 83, 0.1);
            color: {SALEM_GOLD};
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: linear-gradient(180deg, {SALEM_GOLD} 0%, #B89648 100%);
            color: white;
            font-weight: 600;
            box-shadow: 0 4px 16px rgba(196, 160, 83, 0.4);
        }}
        
        .stTabs [data-baseweb="tab-panel"] {{
            background: transparent;
            padding: 24px 0;
        }}
        
        /* Tab content containers */
        .stTabs [data-baseweb="tab-panel"] > div {{
            background: rgba(255, 255, 255, 0.5);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        }}
        
        /* Card-like containers for sections */
        .element-container {{
            transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
        }}
        
        /* Info/Success/Warning/Error boxes */
        .stAlert {{
            border-radius: 12px;
            border: none;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            padding: 16px 20px;
            backdrop-filter: blur(20px);
        }}
        
        [data-testid="stMarkdownContainer"] {{
            color: {SALEM_NAVY} !important;
        }}
        
        /* Dividers - subtle Apple style */
        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, rgba(196, 160, 83, 0.3) 50%, transparent 100%);
            margin: 24px 0;
        }}
        
        /* Streamlit dataframe container */
        [data-testid="stDataFrame"] {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(196, 160, 83, 0.2) !important;
            border-radius: 12px !important;
            padding: 0px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
            overflow: hidden !important;
        }}
        
        /* Force clean background on dataframe divs */
        [data-testid="stDataFrame"] > div {{
            background-color: transparent !important;
        }}
        
        /* Styled dataframe specific styling */
        [data-testid="stDataFrame"] table {{
            background-color: transparent !important;
        }}
        [data-testid="stDataFrame"] thead {{
            background: linear-gradient(180deg, {SALEM_NAVY} 0%, #152D4A 100%) !important;
        }}
        [data-testid="stDataFrame"] thead th {{
            background: transparent !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 16px 20px !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }}
        [data-testid="stDataFrame"] tbody {{
            background-color: transparent !important;
        }}
        [data-testid="stDataFrame"] tbody tr {{
            background-color: transparent !important;
            transition: background-color 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        [data-testid="stDataFrame"] tbody tr:hover {{
            background-color: rgba(196, 160, 83, 0.05) !important;
        }}
        [data-testid="stDataFrame"] tbody td {{
            background-color: transparent !important;
            color: {SALEM_NAVY} !important;
            font-weight: 400 !important;
            padding: 14px 20px !important;
            border-bottom: 1px solid rgba(196, 160, 83, 0.1) !important;
            font-size: 0.95rem !important;
            letter-spacing: -0.01em !important;
        }}
        
        /* Force text color in all table elements - override Streamlit defaults */
        [data-testid="stDataFrame"] td, 
        [data-testid="stDataFrame"] th,
        [data-testid="stDataFrame"] span,
        [data-testid="stDataFrame"] div {{
            color: {SALEM_NAVY} !important;
        }}
        [data-testid="stDataFrame"] tbody td * {{
            color: {SALEM_NAVY} !important;
        }}
        
        /* Target Streamlit's internal table structure */
        div[data-testid="stDataFrame"] table tbody tr td {{
            color: {SALEM_NAVY} !important;
        }}
        
        /* Target all possible text containers in tables */
        [data-testid="stDataFrame"] .css-0,
        [data-testid="stDataFrame"] [class*="css-"],
        [data-testid="stDataFrame"] table,
        [data-testid="stDataFrame"] table * {{
            color: {SALEM_NAVY} !important;
        }}
        
        /* Streamlit styled table cells */
        .dataframe tbody td {{
            color: {SALEM_NAVY} !important;
            background-color: transparent !important;
        }}
        .dataframe tbody th {{
            color: {SALEM_NAVY} !important;
        }}
        
        /* Generic table styling */
        table tbody td, table tbody th {{
            color: {SALEM_NAVY} !important;
        }}
        
        /* Style element within dataframes */
        [data-testid="stDataFrame"] .element-container {{
            color: {SALEM_NAVY} !important;
        }}
        
        /* Remove any color styles that might be inline */
        [data-testid="stDataFrame"] [style*="color"] {{
            color: {SALEM_NAVY} !important;
        }}
        [data-testid="stDataFrame"] tbody tr:hover {{
            background-color: #f8f9fa !important;
        }}
        [data-testid="stDataFrame"] tbody tr:hover td {{
            background-color: #f8f9fa !important;
        }}
        
        /* Chart action buttons (fullscreen, download, etc) */
        .vega-embed {{
            background-color: transparent !important;
        }}
        .vega-embed details {{
            background-color: transparent !important;
        }}
        .vega-embed summary {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: {SALEM_NAVY} !important;
            border: 1px solid rgba(196, 160, 83, 0.3) !important;
            border-radius: 8px !important;
            padding: 8px 14px !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            letter-spacing: -0.01em !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06) !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        .vega-embed summary:hover {{
            background-color: rgba(196, 160, 83, 0.1) !important;
            border-color: rgba(196, 160, 83, 0.5) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08) !important;
        }}
        
        /* Chart menu items */
        .vega-embed details[open] summary {{
            background: linear-gradient(180deg, {SALEM_GOLD} 0%, #B89648 100%) !important;
            color: white !important;
            border-color: {SALEM_GOLD} !important;
        }}
        .vega-actions {{
            background-color: rgba(255, 255, 255, 0.98) !important;
            border: 1px solid rgba(196, 160, 83, 0.2) !important;
            border-radius: 10px !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
            backdrop-filter: blur(20px) !important;
            overflow: hidden !important;
        }}
        .vega-actions a {{
            background-color: transparent !important;
            color: {SALEM_NAVY} !important;
            padding: 12px 16px !important;
            border-bottom: 1px solid rgba(196, 160, 83, 0.1) !important;
            font-weight: 500 !important;
            display: block !important;
            text-decoration: none !important;
            letter-spacing: -0.01em !important;
            transition: all 0.15s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        .vega-actions a:hover {{
            background-color: rgba(196, 160, 83, 0.08) !important;
            color: {SALEM_NAVY} !important;
        }}
        .vega-actions a:last-child {{
            border-bottom: none !important;
        }}
        
        /* Expander - clean and minimal */
        .streamlit-expanderHeader {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(196, 160, 83, 0.25) !important;
            border-radius: 10px !important;
            color: {SALEM_NAVY} !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            padding: 14px 18px !important;
            letter-spacing: -0.01em !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        .streamlit-expanderHeader:hover {{
            background-color: rgba(196, 160, 83, 0.08) !important;
            border-color: rgba(196, 160, 83, 0.4) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06) !important;
        }}
        
        [data-testid="stExpander"] {{
            border: 1px solid rgba(196, 160, 83, 0.2) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        }}
        
        [data-testid="stExpander"] > div {{
            background-color: rgba(255, 255, 255, 0.95) !important;
        }}
        
        /* Captions - readable gray */
        .caption, [data-testid="stCaptionContainer"] {{
            color: rgba(27, 59, 95, 0.7) !important;
            font-size: 0.9rem !important;
            font-weight: 400 !important;
            letter-spacing: -0.01em !important;
        }}
        
        /* Info boxes - clean with gold accent */
        .stAlert {{
            background-color: rgba(196, 160, 83, 0.08) !important;
            border-left: 3px solid {SALEM_GOLD} !important;
            border-radius: 8px !important;
            color: {SALEM_NAVY} !important;
            font-size: 0.95rem !important;
            padding: 12px 14px !important;
            letter-spacing: -0.01em !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        }}
        .stAlert * {{
            color: {SALEM_NAVY} !important;
        }}
        
        /* Tabs - minimal and elegant */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px !important;
            background-color: rgba(248, 249, 250, 0.5) !important;
            padding: 4px !important;
            border-radius: 10px !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent !important;
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-size: 0.95rem !important;
            letter-spacing: -0.01em !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: rgba(196, 160, 83, 0.1) !important;
        }}
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(180deg, {SALEM_GOLD} 0%, #B89648 100%) !important;
            color: white !important;
            box-shadow: 0 2px 8px rgba(196, 160, 83, 0.3) !important;
        }}
        
        /* Dividers */
        hr {{
            border: none !important;
            border-top: 1px solid rgba(196, 160, 83, 0.2) !important;
            margin: 1.5rem 0 !important;
        }}
        
        /* Main content inputs - Apple style (same as sidebar but for main area) */
        .main input[type="text"],
        .main input[type="number"],
        .main input[type="date"] {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(196, 160, 83, 0.3) !important;
            border-radius: 10px !important;
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
            padding: 8px 12px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1);
        }}
        
        .main input[type="text"]:focus,
        .main input[type="number"]:focus,
        .main input[type="date"]:focus {{
            border-color: {SALEM_GOLD} !important;
            outline: none !important;
            box-shadow: 0 4px 16px rgba(196, 160, 83, 0.2) !important;
            background-color: white !important;
        }}
        
        .main input::placeholder {{
            color: rgba(27, 59, 95, 0.5) !important;
            letter-spacing: -0.01em !important;
        }}
        
        /* Main content labels */
        .main label {{
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            opacity: 0.8;
            margin-bottom: 4px !important;
        }}
        
        /* Main content sliders */
        .main [data-testid="stSlider"] {{
            padding: 8px 0 !important;
        }}
        
        .main [data-testid="stSlider"] [role="slider"] {{
            background: linear-gradient(135deg, {SALEM_GOLD} 0%, #B89648 100%) !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(196, 160, 83, 0.3) !important;
            width: 18px !important;
            height: 18px !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        
        .main [data-testid="stSlider"] [role="slider"]:hover {{
            transform: scale(1.1) !important;
            box-shadow: 0 4px 12px rgba(196, 160, 83, 0.4) !important;
        }}
        
        .main [data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
            background: linear-gradient(90deg, {SALEM_GOLD} 0%, rgba(196, 160, 83, 0.3) 100%) !important;
            height: 4px !important;
            border-radius: 2px !important;
        }}
        
        .main [data-testid="stSlider"] [data-baseweb="slider"] > div {{
            background-color: rgba(196, 160, 83, 0.15) !important;
            height: 4px !important;
            border-radius: 2px !important;
        }}
        
        /* Main content selectboxes */
        .main [data-baseweb="select"] {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(196, 160, 83, 0.3) !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
            transition: all 0.2s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
        }}
        
        .main [data-baseweb="select"]:hover {{
            border-color: rgba(196, 160, 83, 0.5) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        }}
        
        .main [data-baseweb="select"] > div {{
            background-color: transparent !important;
            border: none !important;
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            letter-spacing: -0.01em !important;
        }}
        
        /* Main content radio buttons */
        .main [data-testid="stRadio"] {{
            padding: 6px 0 !important;
        }}
        
        .main [data-testid="stRadio"] > label {{
            color: {SALEM_NAVY} !important;
            font-weight: 500 !important;
            letter-spacing: -0.01em !important;
        }}
        
        /* Tighter spacing for input sections in main content */
        .main .element-container {{
            margin-bottom: 0.5rem !important;
        }}
        
        .main [data-testid="stVerticalBlock"] > div {{
            gap: 0.25rem !important;
        }}
        
        /* Input container backgrounds - subtle card style */
        .main > div > div > div {{
            padding: 1rem;
            border-radius: 12px;
        }}
    </style>
    """, unsafe_allow_html=True)


# -----------------------------
# Core dataclasses
# -----------------------------

@dataclass
class ClientInfo:
    client_name: str = ""
    report_date: date = date.today()
    advisor_name: str = ""
    client_id: str = ""
    client_notes: str = ""


@dataclass
class ModelInputs:
    starting_portfolio: float = 4_500_000.0
    years_to_model: int = 30
    current_age: int = 48
    horizon_age: int = 78

    monthly_spending: float = -20_000.0  # negative = withdrawal
    inflation_annual: float = 0.03

    equity_pct: float = 0.70
    fi_pct: float = 0.25
    cash_pct: float = 0.05

    equity_return_annual: float = 0.10
    fi_return_annual: float = 0.03
    cash_return_annual: float = 0.02

    equity_vol_annual: float = 0.15
    fi_vol_annual: float = 0.05
    cash_vol_annual: float = 0.01

    n_scenarios: int = 200

    spending_rule: int = 1       # 1=fixed $, 2=% of portfolio
    spending_pct_annual: float = 0.04  # if rule=2

    one_time_cf: float = 0.0
    one_time_cf_month: int = 0   # 0 = ignore
    
    # Tax-advantaged account modeling
    taxable_pct: float = 0.33  # % of portfolio in taxable accounts
    ira_pct: float = 0.50      # % in traditional IRA/401k
    roth_pct: float = 0.17     # % in Roth IRA
    tax_rate: float = 0.25     # marginal tax rate for withdrawals
    rmd_age: int = 73          # RMD starting age
    
    # Income sources
    social_security_monthly: float = 0.0
    ss_start_age: int = 67
    pension_monthly: float = 0.0
    pension_start_age: int = 65
    regular_income_monthly: float = 0.0
    other_income_monthly: float = 0.0
    other_income_start_age: int = 65
    
    # Couple/longevity planning
    is_couple: bool = False
    spouse_age: int = 48
    spouse_horizon_age: int = 78
    spouse_ss_monthly: float = 0.0
    spouse_ss_start_age: int = 67
    
    # Healthcare costs
    healthcare_monthly: float = 0.0
    healthcare_start_age: int = 65
    healthcare_inflation: float = 0.05  # healthcare inflation typically higher
    
    # Tax optimization
    roth_conversion_annual: float = 0.0
    roth_conversion_start_age: int = 60
    roth_conversion_end_age: int = 70
    
    # Estate planning
    estate_tax_exemption: float = 13_610_000.0  # 2024 exemption
    estate_tax_rate: float = 0.40
    legacy_goal: float = 0.0
    
    # Longevity planning
    use_actuarial_tables: bool = False
    health_adjustment: str = "average"  # "excellent", "average", "poor"
    
    # Dynamic asset allocation (glide path)
    use_glide_path: bool = False
    target_equity_pct: float = 0.40  # target equity % at end
    glide_start_age: int = 65
    
    # Multiple one-time cash flows
    cash_flows: list = None  # List of (month, amount, description) tuples
    
    # Lifestyle spending phases
    use_lifestyle_phases: bool = False
    go_go_end_age: int = 75
    go_go_spending_multiplier: float = 1.0
    slow_go_end_age: int = 85
    slow_go_spending_multiplier: float = 0.80
    no_go_spending_multiplier: float = 0.60
    
    # Guardrails strategy
    use_guardrails: bool = False
    upper_guardrail: float = 0.20  # increase spending by this % if portfolio grows
    lower_guardrail: float = 0.15  # decrease spending by this % if portfolio shrinks
    guardrail_adjustment: float = 0.10  # spending adjustment amount


@dataclass
class StressTestScenario:
    name: str
    return_delta: float    # additive annual return change (e.g. -0.02 = -2%)
    spending_delta: float  # multiplicative change in spending (e.g. 0.10 = +10%
    inflation_delta: float # additive annual inflation change (e.g. 0.01 = +1%)
    first_year_drawdown: float = 0.0  # percentage drawdown applied at end of month 12 (e.g. 0.20 = 20% drop)
    custom_year1_return: float | None = None  # custom return for year 1 (overrides return_delta)
    custom_year2_return: float | None = None  # custom return for year 2 (overrides return_delta)
    custom_year3_return: float | None = None  # custom return for year 3 (overrides return_delta)
    inflation_years: int | None = None  # number of years to apply inflation_delta (None = all years)


@dataclass
class FinancialGoal:
    name: str
    target_amount: float
    target_age: int


# -----------------------------
# Core simulation helpers
# -----------------------------

def compute_portfolio_return_and_vol(inputs: ModelInputs) -> Tuple[float, float]:
    """Expected annual return and volatility for the blended portfolio.

    Expected annual return = weighted average of asset returns.
    Annual volatility = sqrt(sum((weight * vol)^2)) with zero correlations.
    """
    w_eq, w_fi, w_c = inputs.equity_pct, inputs.fi_pct, inputs.cash_pct

    expected_return = (
        w_eq * inputs.equity_return_annual +
        w_fi * inputs.fi_return_annual +
        w_c * inputs.cash_return_annual
    )

    variance = (
        (w_eq * inputs.equity_vol_annual) ** 2 +
        (w_fi * inputs.fi_vol_annual) ** 2 +
        (w_c * inputs.cash_vol_annual) ** 2
    )
    vol = math.sqrt(variance)
    return expected_return, vol


def generate_monte_carlo_cache_key(inputs: ModelInputs, seed: int | None = None) -> str:
    """Generate a unique cache key for Monte Carlo inputs."""
    key_data = f"{inputs.starting_portfolio}_{inputs.equity_pct}_{inputs.fi_pct}_{inputs.cash_pct}_" \
               f"{inputs.equity_return_annual}_{inputs.fi_return_annual}_{inputs.cash_return_annual}_" \
               f"{inputs.equity_vol_annual}_{inputs.fi_vol_annual}_{inputs.cash_vol_annual}_" \
               f"{inputs.inflation_annual}_{inputs.monthly_spending}_{inputs.years_to_model}_" \
               f"{inputs.n_scenarios}_{inputs.spending_rule}_{inputs.spending_pct_annual}_" \
               f"{inputs.social_security_monthly}_{inputs.ss_start_age}_{inputs.pension_monthly}_" \
               f"{inputs.pension_start_age}_{inputs.regular_income_monthly}_{inputs.other_income_monthly}_" \
               f"{inputs.other_income_start_age}_{inputs.current_age}_{seed}"
    return hashlib.md5(key_data.encode()).hexdigest()


@st.cache_data(ttl=3600, show_spinner="Running Monte Carlo simulation...")
def run_monte_carlo_cached(cache_key: str, inputs: ModelInputs, seed: int | None = None):
    """Cached wrapper for Monte Carlo simulation."""
    return run_monte_carlo(inputs, seed)


def run_monte_carlo(inputs: ModelInputs, seed: int | None = None):
    """
    Monthly Monte Carlo model using optimized vectorized implementation.
    Returns (paths_df, stats_df, metrics_dict).
    
    This function delegates to the vectorized implementation for 10-50x speedup
    while maintaining identical financial calculation results.
    """
    from performance_optimizer import run_monte_carlo_vectorized, perf_monitor
    
    # Import performance monitoring
    track_operation = perf_monitor.track_operation
    
    with track_operation("monte_carlo_simulation"):
        # Portfolio-level parameters (annual -> monthly)
        exp_ann, vol_ann = compute_portfolio_return_and_vol(inputs)
        mu_month = (1 + exp_ann) ** (1 / 12) - 1        # geometric monthly mean
        sigma_month = vol_ann / math.sqrt(12)           # monthly vol
        monthly_inflation = (1 + inputs.inflation_annual) ** (1 / 12) - 1
        n_months = inputs.years_to_model * 12
        
        # Prepare income streams dictionary for vectorized function
        income_streams = {}
        
        if inputs.social_security_monthly > 0:
            income_streams['social_security'] = {
                'monthly_amount': inputs.social_security_monthly,
                'start_age': inputs.ss_start_age
            }
        
        if inputs.pension_monthly > 0:
            income_streams['pension'] = {
                'monthly_amount': inputs.pension_monthly,
                'start_age': inputs.pension_start_age
            }
        
        if inputs.regular_income_monthly > 0:
            income_streams['regular_income'] = {
                'monthly_amount': inputs.regular_income_monthly,
                'start_age': inputs.current_age  # Available from start
            }
        
        if inputs.other_income_monthly > 0:
            income_streams['other_income'] = {
                'monthly_amount': inputs.other_income_monthly,
                'start_age': inputs.other_income_start_age
            }
        
        if inputs.is_couple and inputs.spouse_ss_monthly > 0:
            income_streams['spouse_ss'] = {
                'monthly_amount': inputs.spouse_ss_monthly,
                'start_age': inputs.spouse_ss_start_age,
                'is_spouse': True,
                'spouse_age_offset': inputs.spouse_age - inputs.current_age
            }
        
        if inputs.healthcare_monthly > 0:
            income_streams['healthcare'] = {
                'monthly_amount': -inputs.healthcare_monthly,  # Negative for expense
                'start_age': inputs.healthcare_start_age,
                'inflation': inputs.healthcare_inflation
            }
        
        if inputs.one_time_cf_month and inputs.one_time_cf != 0:
            income_streams['one_time'] = {
                'monthly_amount': inputs.one_time_cf,
                'specific_month': inputs.one_time_cf_month
            }
        
        # Call vectorized implementation
        values, stats_df, metrics = run_monte_carlo_vectorized(
            starting_portfolio=inputs.starting_portfolio,
            monthly_spending=inputs.monthly_spending,
            mu_month=mu_month,
            sigma_month=sigma_month,
            monthly_inflation=monthly_inflation,
            n_scenarios=inputs.n_scenarios,
            n_months=n_months,
            income_streams=income_streams,
            spending_rule=inputs.spending_rule,
            spending_pct_annual=inputs.spending_pct_annual,
            current_age=inputs.current_age,
            seed=seed
        )
        
        # Convert to DataFrame with proper labeling (for compatibility with existing code)
        months_index = np.arange(1, n_months + 1)
        columns = [f"Scenario_{i+1}" for i in range(inputs.n_scenarios)]
        paths_df = pd.DataFrame(values, index=months_index, columns=columns)
        paths_df.index.name = "Month"
        
        return paths_df, stats_df, metrics


def create_success_gauge(probability: float, title: str = "Plan Success Probability"):
    """Create an enhanced visual gauge for success probability with risk zones."""
    # Determine color and status based on probability thresholds
    if probability >= 0.90:
        color = "#10B981"  # Emerald green
        status = "Excellent"
        risk_level = "Very Low Risk"
    elif probability >= 0.85:
        color = "#059669"  # Green
        status = "Very Good"
        risk_level = "Low Risk"
    elif probability >= 0.75:
        color = SALEM_GOLD
        status = "Good"
        risk_level = "Moderate Risk"
    elif probability >= 0.65:
        color = "#F59E0B"  # Amber
        status = "Fair"
        risk_level = "Elevated Risk"
    elif probability >= 0.50:
        color = "#F97316"  # Orange
        status = "Concerning"
        risk_level = "High Risk"
    else:
        color = "#EF4444"  # Red
        status = "At Risk"
        risk_level = "Critical Risk"
    
    # Create enhanced gauge visualization
    gauge_data = pd.DataFrame([
        {"category": "Success", "value": probability * 100, "order": 1, "label": f"{probability*100:.1f}%"},
        {"category": "Risk", "value": (1 - probability) * 100, "order": 2, "label": f"{(1-probability)*100:.1f}%"}
    ])
    
    # Main gauge chart
    gauge = alt.Chart(gauge_data).mark_arc(
        innerRadius=70,
        outerRadius=110,
        cornerRadius=5
    ).encode(
        theta=alt.Theta("value:Q", stack=True),
        color=alt.Color(
            "category:N",
            scale=alt.Scale(
                domain=["Success", "Risk"],
                range=[color, "#F3F4F6"]
            ),
            legend=None
        ),
        order=alt.Order("order:Q"),
        tooltip=[
            alt.Tooltip("category:N", title="Category"),
            alt.Tooltip("label:N", title="Percentage")
        ]
    )
    
    # Center text with percentage
    text = alt.Chart(pd.DataFrame([{
        "x": 0,
        "y": 0,
        "text": f"{probability*100:.0f}%",
        "subtext": status
    }])).mark_text(
        align="center",
        baseline="middle",
        fontSize=36,
        fontWeight=700,
        color=color
    ).encode(
        x=alt.value(125),
        y=alt.value(125),
        text="text:N"
    )
    
    # Status subtext
    subtext = alt.Chart(pd.DataFrame([{
        "x": 0,
        "y": 0,
        "text": status
    }])).mark_text(
        align="center",
        baseline="top",
        fontSize=14,
        fontWeight=600,
        color=SALEM_NAVY
    ).encode(
        x=alt.value(125),
        y=alt.value(150),
        text="text:N"
    )
    
    # Risk level indicator
    risk_text = alt.Chart(pd.DataFrame([{
        "x": 0,
        "y": 0,
        "text": risk_level
    }])).mark_text(
        align="center",
        baseline="bottom",
        fontSize=11,
        fontWeight=500,
        color="#6B7280"
    ).encode(
        x=alt.value(125),
        y=alt.value(105),
        text="text:N"
    )
    
    chart = (gauge + text + subtext + risk_text).properties(
        width=250,
        height=250,
        title={
            "text": title,
            "fontSize": 18,
            "fontWeight": 700,
            "color": SALEM_NAVY,
            "anchor": "middle"
        }
    ).configure_view(
        strokeWidth=0
    )
    
    return chart


def fan_chart(stats_df: pd.DataFrame, title: str = "Portfolio Value – Monte Carlo Fan Chart"):
    # Add Year column for x-axis
    df = stats_df.copy()
    df["Year"] = df["Month"] / 12.0
    
    # Enhanced tooltip data
    df["P10_formatted"] = df["P10"].apply(lambda x: f"${x:,.0f}")
    df["P25_formatted"] = df["P25"].apply(lambda x: f"${x:,.0f}")
    df["Median_formatted"] = df["Median"].apply(lambda x: f"${x:,.0f}")
    df["P75_formatted"] = df["P75"].apply(lambda x: f"${x:,.0f}")
    df["P90_formatted"] = df["P90"].apply(lambda x: f"${x:,.0f}")
    
    base = alt.Chart(df).encode(
        x=alt.X("Year:Q", title="Year", 
               axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
    )

    # Enhanced tooltips for all layers
    tooltip = [
        alt.Tooltip("Year:Q", title="Year", format=".1f"),
        alt.Tooltip("P10_formatted:N", title="10th Percentile (Worst)"),
        alt.Tooltip("P25_formatted:N", title="25th Percentile"),
        alt.Tooltip("Median_formatted:N", title="Median (50th)"),
        alt.Tooltip("P75_formatted:N", title="75th Percentile"),
        alt.Tooltip("P90_formatted:N", title="90th Percentile (Best)")
    ]

    band_10_90 = base.mark_area(opacity=0.15, color=SALEM_LIGHT_GOLD).encode(
        y=alt.Y("P10:Q", title="Portfolio Value", 
               axis=alt.Axis(format="$,.0f", labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
        y2="P90:Q",
        tooltip=tooltip
    )

    band_25_75 = base.mark_area(opacity=0.3, color=SALEM_GOLD).encode(
        y="P25:Q",
        y2="P75:Q",
        tooltip=tooltip
    )

    median_line = base.mark_line(size=3, color=SALEM_NAVY).encode(
        y="Median:Q",
        tooltip=tooltip
    )

    chart = (band_10_90 + band_25_75 + median_line).properties(
        title={
            "text": title,
            "fontSize": 18,
            "fontWeight": 700,
            "color": SALEM_NAVY
        },
        width="container",
        height=450
    ).configure_axis(
        gridColor="#dee2e6",
        domainColor=SALEM_NAVY,
        domainWidth=2,
        labelColor=SALEM_NAVY,
        titleColor=SALEM_NAVY
    ).configure_view(
        strokeWidth=0,
        fill="white"
    ).configure(
        background="white",
        padding={"left": 10, "right": 10, "top": 10, "bottom": 10}
    ).interactive()
    return chart


def depletion_probability_chart(paths_df: pd.DataFrame, title: str = "Probability of Portfolio Depletion Over Time"):
    """Create a chart showing the probability of portfolio depletion at each time point."""
    months = len(paths_df)
    depletion_probs = []
    
    for month in range(1, months + 1):
        # Count how many scenarios have depleted by this month
        month_values = paths_df.iloc[month - 1]
        depleted = (month_values <= 0).sum()
        prob = depleted / len(month_values) * 100
        depletion_probs.append({"Month": month, "Year": month / 12.0, "Probability": prob})
    
    df = pd.DataFrame(depletion_probs)
    
    # Enhanced tooltip with risk assessment
    df["Risk_Level"] = df["Probability"].apply(
        lambda p: "Low Risk" if p < 10 else "Moderate Risk" if p < 25 else "High Risk"
    )
    df["Probability_formatted"] = df["Probability"].apply(lambda p: f"{p:.1f}%")
    
    chart = (
        alt.Chart(df)
        .mark_area(opacity=0.6, color="#c94c4c", line={"color": SALEM_DARK_NAVY, "size": 2})
        .encode(
            x=alt.X("Year:Q", title="Year", 
                   axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
            y=alt.Y("Probability:Q", title="Probability of Depletion (%)", 
                   scale=alt.Scale(domain=[0, 100]),
                   axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
            tooltip=[
                alt.Tooltip("Year:Q", title="Year", format=".1f"),
                alt.Tooltip("Probability_formatted:N", title="Depletion Risk"),
                alt.Tooltip("Risk_Level:N", title="Risk Assessment")
            ]
        )
        .properties(
            title={
                "text": title,
                "fontSize": 18,
                "fontWeight": 700,
                "color": SALEM_NAVY
            },
            width="container",
            height=350
        )
        .configure_axis(
            gridColor="#dee2e6",
            domainColor=SALEM_NAVY,
            domainWidth=2,
            labelColor=SALEM_NAVY,
            titleColor=SALEM_NAVY
        )
        .configure_view(
            strokeWidth=0,
            fill="white"
        )
        .configure(
            background="white",
            padding={"left": 10, "right": 10, "top": 10, "bottom": 10}
        )
        .interactive()
    )
    return chart


def calculate_goal_probabilities(paths_df: pd.DataFrame, goals: List[FinancialGoal], current_age: int) -> pd.DataFrame:
    """Calculate the probability of achieving each financial goal."""
    goal_results = []
    
    for goal in goals:
        years_from_now = goal.target_age - current_age
        if years_from_now <= 0 or years_from_now * 12 > len(paths_df):
            continue
        
        target_month = int(years_from_now * 12)
        month_values = paths_df.iloc[target_month - 1]
        prob_success = (month_values >= goal.target_amount).sum() / len(month_values) * 100
        
        goal_results.append({
            "Goal": goal.name,
            "Target Amount": goal.target_amount,
            "Target Age": goal.target_age,
            "Probability of Success": prob_success
        })
    
    return pd.DataFrame(goal_results)


def create_goal_confidence_chart(goal_results: pd.DataFrame):
    """Create visual confidence meters for financial goals."""
    if goal_results.empty:
        return None
    
    goal_results = goal_results.copy()
    goal_results["Status"] = goal_results["Probability of Success"].apply(
        lambda x: "High Confidence" if x >= 85 else "Moderate" if x >= 70 else "At Risk"
    )
    
    chart = alt.Chart(goal_results).mark_bar(cornerRadius=8).encode(
        y=alt.Y("Goal:N", title=None, sort="-x"),
        x=alt.X("Probability of Success:Q", title="Success Probability (%)", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color(
            "Status:N",
            scale=alt.Scale(
                domain=["High Confidence", "Moderate", "At Risk"],
                range=["#28a745", SALEM_GOLD, "#dc3545"]
            ),
            legend=alt.Legend(title="Confidence Level")
        ),
        tooltip=["Goal", "Probability of Success", "Target Amount", "Target Age"]
    ).properties(
        width="container",
        height=max(200, len(goal_results) * 60),
        title={
            "text": "Financial Goal Confidence Levels",
            "fontSize": 18,
            "fontWeight": 700,
            "color": SALEM_NAVY
        }
    ).configure_axis(
        gridColor="#dee2e6",
        domainColor=SALEM_NAVY,
        labelColor=SALEM_NAVY,
        titleColor=SALEM_NAVY
    )
    
    return chart


def sensitivity_analysis(inputs: ModelInputs) -> pd.DataFrame:
    """Run sensitivity analysis on key variables."""
    base_exp_ann, _ = compute_portfolio_return_and_vol(inputs)
    
    # Variables to test and their ranges
    sensitivity_results = []
    
    # Test return variations (-2%, -1%, base, +1%, +2%)
    for return_delta in [-0.02, -0.01, 0, 0.01, 0.02]:
        test_inputs = ModelInputs(**{k: v for k, v in inputs.__dict__.items()})
        test_inputs.equity_return_annual = inputs.equity_return_annual + return_delta
        test_inputs.fi_return_annual = inputs.fi_return_annual + return_delta
        
        paths, stats, metrics = run_monte_carlo(test_inputs, seed=42)
        
        sensitivity_results.append({
            "Variable": "Portfolio Return",
            "Change": f"{return_delta*100:+.0f}%",
            "Value": f"{(base_exp_ann + return_delta)*100:.1f}%",
            "Median Ending": metrics["ending_median"],
            "P10 Ending": metrics["ending_p10"],
            "Success Prob": metrics["prob_never_depleted"] * 100,
            "Sort": return_delta
        })
    
    # Test spending variations (-20%, -10%, base, +10%, +20%)
    for spend_delta in [-0.20, -0.10, 0, 0.10, 0.20]:
        test_inputs = ModelInputs(**{k: v for k, v in inputs.__dict__.items()})
        test_inputs.monthly_spending = inputs.monthly_spending * (1 + spend_delta)
        
        paths, stats, metrics = run_monte_carlo(test_inputs, seed=42)
        
        sensitivity_results.append({
            "Variable": "Monthly Spending",
            "Change": f"{spend_delta*100:+.0f}%",
            "Value": f"${-test_inputs.monthly_spending:,.0f}",
            "Median Ending": metrics["ending_median"],
            "P10 Ending": metrics["ending_p10"],
            "Success Prob": metrics["prob_never_depleted"] * 100,
            "Sort": spend_delta
        })
    
    # Test portfolio value variations (-20%, -10%, base, +10%, +20%)
    for portfolio_delta in [-0.20, -0.10, 0, 0.10, 0.20]:
        test_inputs = ModelInputs(**{k: v for k, v in inputs.__dict__.items()})
        test_inputs.starting_portfolio = inputs.starting_portfolio * (1 + portfolio_delta)
        
        paths, stats, metrics = run_monte_carlo(test_inputs, seed=42)
        
        sensitivity_results.append({
            "Variable": "Starting Portfolio",
            "Change": f"{portfolio_delta*100:+.0f}%",
            "Value": f"${test_inputs.starting_portfolio:,.0f}",
            "Median Ending": metrics["ending_median"],
            "P10 Ending": metrics["ending_p10"],
            "Success Prob": metrics["prob_never_depleted"] * 100,
            "Sort": portfolio_delta
        })
    
    return pd.DataFrame(sensitivity_results)


def sensitivity_chart(sensitivity_df: pd.DataFrame, metric: str = "Median Ending"):
    """Create visualization of sensitivity analysis."""
    chart = (
        alt.Chart(sensitivity_df)
        .mark_bar(cornerRadius=4)
        .encode(
            x=alt.X("Change:N", title="Change from Base Case", sort=None, 
                   axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
            y=alt.Y(f"{metric}:Q", title=metric, 
                   axis=alt.Axis(format="$,.0f", labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
            color=alt.Color("Variable:N", title="Variable", 
                          scale=alt.Scale(range=[SALEM_NAVY, SALEM_GOLD, SALEM_LIGHT_GOLD])),
            tooltip=["Variable", "Change", "Value", f"{metric}:Q"],
            xOffset="Variable:N"
        )
        .properties(
            width="container",
            height=450,
            title={
                "text": f"Sensitivity Analysis: {metric}",
                "fontSize": 18,
                "fontWeight": 700,
                "color": SALEM_NAVY
            }
        )
        .configure_axis(
            gridColor="#dee2e6",
            domainColor=SALEM_NAVY,
            domainWidth=2,
            labelColor=SALEM_NAVY,
            titleColor=SALEM_NAVY
        )
        .configure_legend(
            titleFontSize=14,
            labelFontSize=13,
            titleColor=SALEM_NAVY,
            labelColor=SALEM_NAVY
        )
        .configure_view(
            strokeWidth=0,
            fill="white"
        )
        .configure(
            background="white",
            padding={"left": 10, "right": 10, "top": 10, "bottom": 10}
        )
    )
    return chart


def create_sensitivity_heat_map(inputs: ModelInputs) -> alt.Chart:
    """Create a heat map showing how success probability changes with multiple variables."""
    # Test combinations of spending and portfolio return
    spending_levels = [-0.20, -0.10, 0, 0.10, 0.20]  # -20% to +20%
    return_deltas = [-0.02, -0.01, 0, 0.01, 0.02]  # -2% to +2%
    
    heat_map_data = []
    
    for spend_delta in spending_levels:
        for return_delta in return_deltas:
            test_inputs = ModelInputs(**{k: v for k, v in inputs.__dict__.items()})
            test_inputs.monthly_spending = inputs.monthly_spending * (1 + spend_delta)
            test_inputs.equity_return_annual = inputs.equity_return_annual + return_delta
            test_inputs.fi_return_annual = inputs.fi_return_annual + return_delta
            test_inputs.cash_return_annual = inputs.cash_return_annual + return_delta
            
            _, _, metrics = run_monte_carlo(test_inputs, seed=42)
            
            heat_map_data.append({
                "Spending Change": f"{spend_delta*100:+.0f}%",
                "Return Change": f"{return_delta*100:+.1f}%",
                "Success Probability": metrics["prob_never_depleted"] * 100,
                "Spending_Sort": spend_delta,
                "Return_Sort": return_delta
            })
    
    heat_df = pd.DataFrame(heat_map_data)
    
    chart = alt.Chart(heat_df).mark_rect().encode(
        x=alt.X("Return Change:N", title="Annual Return Change", sort=alt.EncodingSortField(field="Return_Sort", order="ascending")),
        y=alt.Y("Spending Change:N", title="Monthly Spending Change", sort=alt.EncodingSortField(field="Spending_Sort", order="descending")),
        color=alt.Color(
            "Success Probability:Q",
            title="Success %",
            scale=alt.Scale(
                domain=[0, 50, 75, 85, 100],
                range=["#dc3545", "#ffc107", SALEM_GOLD, SALEM_LIGHT_GOLD, "#28a745"]
            )
        ),
        tooltip=["Spending Change", "Return Change", alt.Tooltip("Success Probability:Q", format=".1f")]
    ).properties(
        width=600,
        height=400,
        title={
            "text": "Sensitivity Heat Map: Success Probability",
            "subtitle": "How spending and return changes impact plan success",
            "fontSize": 18,
            "fontWeight": 700,
            "color": SALEM_NAVY
        }
    ).configure_axis(
        labelColor=SALEM_NAVY,
        titleColor=SALEM_NAVY,
        labelFontSize=12,
        titleFontSize=14
    )
    
    return chart


# -----------------------------
# Helper input formatters
# -----------------------------

def _dollar_input(label: str, default_value: float, key: str, help: str | None = None) -> float:
    """Text input that shows/accepts a dollar amount like $20,000."""
    default_str = f"${default_value:,.0f}"
    s = st.text_input(label, value=default_str, key=key, help=help)

    try:
        clean = (
            s.replace("$", "")
             .replace(",", "")
             .replace(" ", "")
             .replace("(", "-")
             .replace(")", "")
        )
        if clean == "":
            return default_value
        return float(clean)
    except ValueError:
        st.warning(f"Could not parse '{s}' as a dollar amount. Using {default_str}.")
        return default_value


def _percent_input(label: str, default_fraction: float, key: str, help: str | None = None) -> float:
    """Text input for percents. Shows '3%' for 0.03, returns 0.03."""
    default_str = f"{default_fraction * 100:.1f}%"
    s = st.text_input(label, value=default_str, key=key, help=help)

    try:
        clean = s.replace("%", "").strip()
        if clean == "":
            return default_fraction
        return float(clean) / 100.0
    except ValueError:
        st.warning(f"Could not parse '{s}' as a percent. Using {default_str}.")
        return default_fraction


# -----------------------------
# Quick Win Features
# -----------------------------

def calculate_rmd_projections(inputs: ModelInputs) -> pd.DataFrame:
    """Calculate Required Minimum Distribution projections."""
    rmd_data = []
    
    # IRS Uniform Lifetime Table (simplified)
    life_expectancy_factors = {
        73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7, 77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2,
        81: 19.4, 82: 18.5, 83: 17.7, 84: 16.8, 85: 16.0, 86: 15.2, 87: 14.4, 88: 13.7,
        89: 12.9, 90: 12.2, 91: 11.5, 92: 10.8, 93: 10.1, 94: 9.5, 95: 8.9, 96: 8.4,
        97: 7.8, 98: 7.3, 99: 6.8, 100: 6.4
    }
    
    ira_balance = inputs.starting_portfolio * inputs.ira_pct
    
    for age in range(inputs.current_age, inputs.horizon_age + 1):
        if age >= inputs.rmd_age and age in life_expectancy_factors:
            factor = life_expectancy_factors[age]
            rmd_amount = ira_balance / factor
            tax_on_rmd = rmd_amount * inputs.tax_rate
            
            rmd_data.append({
                "Age": age,
                "Year": age - inputs.current_age + 1,
                "IRA Balance": ira_balance,
                "RMD Amount": rmd_amount,
                "Tax on RMD": tax_on_rmd,
                "After-Tax RMD": rmd_amount - tax_on_rmd
            })
            
            # Simplified growth assumption
            ira_balance = (ira_balance - rmd_amount) * 1.05
    
    return pd.DataFrame(rmd_data)


def create_rmd_chart(rmd_df: pd.DataFrame) -> alt.Chart:
    """Create visualization of RMD projections."""
    if rmd_df.empty:
        return None
    
    chart = alt.Chart(rmd_df).mark_bar(color=SALEM_GOLD).encode(
        x=alt.X("Age:O", title="Age"),
        y=alt.Y("RMD Amount:Q", title="Required Minimum Distribution", axis=alt.Axis(format="$,.0f")),
        tooltip=[
            alt.Tooltip("Age:O"),
            alt.Tooltip("RMD Amount:Q", format="$,.0f"),
            alt.Tooltip("Tax on RMD:Q", format="$,.0f"),
            alt.Tooltip("After-Tax RMD:Q", format="$,.0f")
        ]
    ).properties(
        width="container",
        height=350,
        title={
            "text": "Required Minimum Distribution Projections",
            "fontSize": 18,
            "fontWeight": 700,
            "color": SALEM_NAVY
        }
    ).configure_axis(
        gridColor="#dee2e6",
        domainColor=SALEM_NAVY,
        labelColor=SALEM_NAVY,
        titleColor=SALEM_NAVY
    )
    
    return chart


def run_historical_backtest(inputs: ModelInputs, start_year: int) -> Tuple[pd.DataFrame, dict]:
    """Run simulation using historical returns from a specific starting year."""
    # Historical annual returns (simplified - real data would be more extensive)
    historical_returns = {
        1929: [-0.083, -0.249, -0.434, -0.082, 0.540, -0.013, 0.471, 0.339, 0.310, 0.284],
        2000: [-0.091, -0.119, -0.220, 0.287, 0.108, 0.049, 0.157, 0.055, -0.370, 0.265],
        2008: [-0.370, 0.265, 0.150, 0.021, 0.160, 0.321, 0.136, 0.114, 0.215, -0.043],
        2022: [-0.180, 0.264, 0.260, 0.100, 0.120, 0.100, 0.100, 0.100, 0.100, 0.100]
    }
    
    # Use historical sequence if available, otherwise use assumptions
    if start_year in historical_returns:
        return_sequence = historical_returns[start_year]
    else:
        # Fall back to Monte Carlo
        return run_monte_carlo(inputs, seed=start_year)
    
    # Run deterministic simulation with historical returns
    months = inputs.years_to_model * 12
    values = []
    val = inputs.starting_portfolio
    spending = inputs.monthly_spending
    monthly_inflation = (1 + inputs.inflation_annual) ** (1 / 12) - 1
    
    for month in range(1, months + 1):
        # Apply cash flow
        if inputs.spending_rule == 1:
            cf = spending
        else:
            cf = -val * (inputs.spending_pct_annual / 12.0)
        
        val = max(val + cf, 0.0)
        
        # Apply historical return for this year
        year_index = (month - 1) // 12
        if year_index < len(return_sequence):
            annual_return = return_sequence[year_index]
            monthly_return = (1 + annual_return) ** (1/12) - 1
        else:
            # After historical data, use expected return
            exp_ann, _ = compute_portfolio_return_and_vol(inputs)
            monthly_return = (1 + exp_ann) ** (1/12) - 1
        
        val = max(val * (1 + monthly_return), 0.0)
        values.append(val)
        
        if inputs.spending_rule == 1:
            spending *= (1 + monthly_inflation)
    
    df = pd.DataFrame({"Month": range(1, months + 1), "Value": values})
    
    metrics = {
        "ending_value": values[-1],
        "min_value": min(values),
        "max_drawdown": (max(values) - min(values)) / max(values) if max(values) > 0 else 0
    }
    
    return df, metrics


def create_historical_comparison_chart(scenarios: dict) -> alt.Chart:
    """Create chart comparing historical scenarios."""
    all_data = []
    
    for scenario_name, data in scenarios.items():
        df = data["df"]
        df_copy = df.copy()
        df_copy["Scenario"] = scenario_name
        df_copy["Year"] = df_copy["Month"] / 12
        all_data.append(df_copy)
    
    combined_df = pd.concat(all_data)
    
    chart = alt.Chart(combined_df).mark_line(size=3).encode(
        x=alt.X("Year:Q", title="Year"),
        y=alt.Y("Value:Q", title="Portfolio Value", axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Scenario:N", scale=alt.Scale(range=[SALEM_NAVY, "#dc3545", SALEM_GOLD, SALEM_LIGHT_GOLD])),
        tooltip=["Scenario", "Year", alt.Tooltip("Value:Q", format="$,.0f")]
    ).properties(
        width="container",
        height=450,
        title={
            "text": "Historical Backtest: What if you retired in...",
            "fontSize": 18,
            "fontWeight": 700,
            "color": SALEM_NAVY
        }
    ).configure_axis(
        gridColor="#dee2e6",
        domainColor=SALEM_NAVY,
        labelColor=SALEM_NAVY,
        titleColor=SALEM_NAVY
    )
    
    return chart


def calculate_social_security_optimization(
    monthly_benefit_at_67: float,
    current_age: int,
    horizon_age: int
) -> pd.DataFrame:
    """Compare Social Security claiming strategies."""
    results = []
    
    # Reduction/increase factors
    claim_ages = [62, 65, 67, 70]
    factors = {62: 0.70, 65: 0.867, 67: 1.0, 70: 1.24}  # Approximate factors
    
    for claim_age in claim_ages:
        if claim_age < current_age:
            continue
            
        adjusted_benefit = monthly_benefit_at_67 * factors[claim_age]
        years_receiving = max(0, horizon_age - claim_age)
        total_received = adjusted_benefit * 12 * years_receiving
        
        # Calculate breakeven vs age 67
        if claim_age != 67:
            benefit_67 = monthly_benefit_at_67 * 12 * max(0, horizon_age - 67)
            difference = total_received - benefit_67
        else:
            difference = 0
        
        results.append({
            "Claiming Age": claim_age,
            "Monthly Benefit": adjusted_benefit,
            "Years Receiving": years_receiving,
            "Lifetime Total": total_received,
            "vs Age 67": difference
        })
    
    return pd.DataFrame(results)


def create_ss_optimization_chart(ss_df: pd.DataFrame) -> alt.Chart:
    """Create visualization of Social Security claiming strategies."""
    if ss_df.empty:
        return None
    
    chart = alt.Chart(ss_df).mark_bar(cornerRadius=4).encode(
        x=alt.X("Claiming Age:O", title="Claiming Age"),
        y=alt.Y("Lifetime Total:Q", title="Total Lifetime Benefits", axis=alt.Axis(format="$,.0f")),
        color=alt.Color(
            "Claiming Age:O",
            scale=alt.Scale(range=["#dc3545", SALEM_LIGHT_GOLD, SALEM_GOLD, "#28a745"]),
            legend=None
        ),
        tooltip=[
            "Claiming Age",
            alt.Tooltip("Monthly Benefit:Q", format="$,.0f"),
            alt.Tooltip("Lifetime Total:Q", format="$,.0f"),
            alt.Tooltip("vs Age 67:Q", format="$+,.0f")
        ]
    ).properties(
        width="container",
        height=350,
        title={
            "text": "Social Security Claiming Strategy Comparison",
            "fontSize": 18,
            "fontWeight": 700,
            "color": SALEM_NAVY
        }
    ).configure_axis(
        gridColor="#dee2e6",
        domainColor=SALEM_NAVY,
        labelColor=SALEM_NAVY,
        titleColor=SALEM_NAVY
    )
    
    return chart


def get_assumption_preset(preset_name: str) -> dict:
    """Return assumption presets from industry standards."""
    presets = {
        "CFP Board (Conservative)": {
            "equity_return": 0.062,
            "fi_return": 0.023,
            "cash_return": 0.015,
            "equity_vol": 0.18,
            "fi_vol": 0.06,
            "cash_vol": 0.01,
            "inflation": 0.025
        },
        "Morningstar (Moderate)": {
            "equity_return": 0.075,
            "fi_return": 0.030,
            "cash_return": 0.020,
            "equity_vol": 0.17,
            "fi_vol": 0.055,
            "cash_vol": 0.01,
            "inflation": 0.022
        },
        "Vanguard (Historical)": {
            "equity_return": 0.095,
            "fi_return": 0.042,
            "cash_return": 0.025,
            "equity_vol": 0.16,
            "fi_vol": 0.05,
            "cash_vol": 0.01,
            "inflation": 0.030
        },
        "Conservative": {
            "equity_return": 0.055,
            "fi_return": 0.020,
            "cash_return": 0.015,
            "equity_vol": 0.15,
            "fi_vol": 0.05,
            "cash_vol": 0.01,
            "inflation": 0.030
        },
        "Aggressive": {
            "equity_return": 0.100,
            "fi_return": 0.035,
            "cash_return": 0.020,
            "equity_vol": 0.20,
            "fi_vol": 0.07,
            "cash_vol": 0.01,
            "inflation": 0.025
        }
    }
    
    return presets.get(preset_name, presets["Morningstar (Moderate)"])


# -----------------------------
# Main page inputs (formerly sidebar)
# -----------------------------

def main_page_inputs() -> Tuple[ClientInfo, ModelInputs, List[StressTestScenario]]:
    st.header("Client Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        client_name = st.text_input(
            "Client Name",
            value="",
            key="client_name",
            placeholder="John & Jane Doe"
        )
    
    with col2:
        advisor_name = st.text_input(
            "Advisor Name",
            value="",
            key="advisor_name",
            placeholder="Advisor Name"
        )
    
    with col3:
        report_date = st.date_input(
            "Report Date",
            value=date.today(),
            key="report_date"
        )
    
    client_info = ClientInfo(
        client_name=client_name,
        report_date=report_date,
        advisor_name=advisor_name
    )
    
    st.markdown("---")
    st.header("Model Inputs")

    # --- Client & Horizon ---
    st.subheader("Client & Horizon")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        current_age = st.number_input(
            "Current Age",
            min_value=0,
            max_value=120,
            value=48,
            step=1,
            key="current_age",
        )

    with col2:
        horizon_age = st.number_input(
            "Plan Horizon Age",
            min_value=current_age,
            max_value=120,
            value=78,
            step=1,
            key="horizon_age",
        )

    with col3:
        starting_portfolio = _dollar_input(
            "Starting Portfolio Value",
            default_value=4_500_000.0,
            key="starting_portfolio",
        )

    years_to_model = horizon_age - current_age
    
    # --- Couple Planning ---
    st.subheader("Couple/Longevity Planning")
    
    is_couple = st.checkbox(
        "Joint Life Expectancy (Couple)",
        value=False,
        key="is_couple",
        help="Model for a couple with joint life expectancy"
    )
    
    col1, col2, col3 = st.columns(3)
    
    if is_couple:
        with col1:
            spouse_age = st.number_input(
                "Spouse Age",
                min_value=0,
                max_value=120,
                value=48,
                step=1,
                key="spouse_age",
            )
        with col2:
            spouse_horizon_age = st.number_input(
                "Spouse Horizon Age",
                min_value=spouse_age,
                max_value=120,
                value=78,
                step=1,
                key="spouse_horizon_age",
            )
        
        # Update years to model based on longer-living spouse
        years_to_model = max(horizon_age - current_age, spouse_horizon_age - spouse_age)
        
        with col3:
            spouse_ss_monthly = _dollar_input(
                "Spouse Social Security (Monthly)",
                default_value=0.0,
                key="spouse_ss_monthly",
            )
        
        
        spouse_ss_start_age = st.number_input(
            "Spouse SS Start Age",
            min_value=62,
            max_value=70,
            value=67,
            step=1,
            key="spouse_ss_start_age",
        ) if spouse_ss_monthly > 0 else 67
    else:
        spouse_age = current_age
        spouse_horizon_age = horizon_age
        spouse_ss_monthly = 0.0
        spouse_ss_start_age = 67
    
    # --- Spending & Inflation ---
    st.subheader("Spending")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        spending_rule = st.radio(
            "Spending Rule",
            options=[1, 2],
            format_func=lambda x: "1 – Fixed $ (inflation-adjusted)" if x == 1 else "2 – % of Portfolio",
            key="spending_rule",
        )
    
    with col2:
        monthly_spend_abs = _dollar_input(
            "Monthly Spending",
            default_value=20_000.0,
            key="monthly_spending",
            help="Enter the monthly spending amount. It will be treated as a withdrawal.",
        )

    with col3:
        spending_pct_annual = _percent_input(
            "Percent of Portfolio (Annual, if Rule = 2)",
            default_fraction=0.04,
            key="spending_pct_annual",
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        healthcare_monthly = _dollar_input(
            "Monthly Healthcare Costs",
            default_value=0.0,
            key="healthcare_monthly",
            help="Monthly healthcare expenses (e.g., premiums, out-of-pocket)"
        )
    
    with col2:
        healthcare_start_age = st.number_input(
            "Healthcare Start Age",
            min_value=current_age,
            max_value=horizon_age,
            value=65,
            step=1,
            key="healthcare_start_age",
        )
    
    with col3:
        healthcare_inflation = _percent_input(
            "Healthcare Inflation Rate",
            default_fraction=0.05,
            key="healthcare_inflation",
            help="Healthcare costs typically inflate faster than general inflation"
        )
    
    monthly_spending = -abs(monthly_spend_abs)  # withdrawals negative

    # Set inflation to 0 since we're using real returns
    inflation_annual = 0.0
    
    # --- Tax-Advantaged Accounts ---
    st.subheader("Account Type Breakdown")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        taxable_pct_slider = st.slider(
            "Taxable Accounts %",
            min_value=0,
            max_value=100,
            value=35,
            step=5,
            key="taxable_pct",
            help="Investments in taxable brokerage accounts"
        )
    with col2:
        ira_pct_slider = st.slider(
            "Traditional IRA/401k %",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            key="ira_pct",
            help="Pre-tax retirement accounts (subject to RMDs)"
        )
    with col3:
        roth_pct_slider = st.slider(
            "Roth IRA %",
            min_value=0,
            max_value=100,
            value=15,
            step=5,
            key="roth_pct",
            help="After-tax retirement accounts (no RMDs)"
        )
    
    taxable_pct = taxable_pct_slider / 100.0
    ira_pct = ira_pct_slider / 100.0
    roth_pct = roth_pct_slider / 100.0
    
    account_sum = taxable_pct + ira_pct + roth_pct
    if abs(account_sum - 1.0) > 1e-6:
        st.warning(
            f"Account breakdown totals {account_sum*100:.1f}% (should be 100%)."
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        tax_rate = _percent_input(
            "Marginal Tax Rate",
            default_fraction=0.25,
            key="tax_rate",
            help="Tax rate applied to traditional IRA/401k withdrawals"
        )
    
    with col2:
        rmd_age = st.number_input(
            "RMD Starting Age",
            min_value=70,
            max_value=75,
            value=73,
            step=1,
            key="rmd_age",
            help="Age when Required Minimum Distributions begin"
        )
    
    # --- Tax Optimization ---
    with st.expander("Tax Optimization (Roth Conversions)", expanded=False):
        st.caption("Model Roth IRA conversion strategy to optimize lifetime tax burden")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            roth_conversion_annual = _dollar_input(
                "Annual Roth Conversion Amount",
                default_value=0.0,
                key="roth_conversion_annual",
                help="Amount to convert from Traditional IRA to Roth IRA each year"
            )
        with col2:
            roth_conversion_start_age = st.number_input(
                "Start Conversions at Age",
                min_value=current_age,
                max_value=horizon_age,
                value=60,
                step=1,
                key="roth_conversion_start_age"
            ) if roth_conversion_annual > 0 else 60
        with col3:
            roth_conversion_end_age = st.number_input(
                "End Conversions at Age",
                min_value=current_age,
                max_value=horizon_age,
                value=70,
                step=1,
                key="roth_conversion_end_age"
            ) if roth_conversion_annual > 0 else 70
    
    # --- Estate Planning ---
    with st.expander("Estate Planning", expanded=False):
        st.caption("Model estate tax implications and legacy goals")
        
        col1, col2 = st.columns(2)
        with col1:
            estate_tax_exemption = _dollar_input(
                "Estate Tax Exemption",
                default_value=13_610_000.0,
                key="estate_tax_exemption",
                help="Federal estate tax exemption (2024: $13.61M)"
            )
            estate_tax_rate = _percent_input(
                "Estate Tax Rate",
                default_fraction=0.40,
                key="estate_tax_rate",
                help="Federal estate tax rate on amounts above exemption"
            )
        with col2:
            legacy_goal = _dollar_input(
                "Legacy Goal (Desired Bequest)",
                default_value=0.0,
                key="legacy_goal",
                help="Target amount to leave to heirs/charity"
            )
    
    # --- Longevity Planning ---
    with st.expander("Longevity Planning", expanded=False):
        st.caption("Adjust life expectancy based on health and actuarial data")
        
        col1, col2 = st.columns(2)
        with col1:
            use_actuarial_tables = st.checkbox(
                "Use Actuarial Life Tables",
                value=False,
                key="use_actuarial_tables",
                help="Adjust horizon based on statistical life expectancy"
            )
        with col2:
            health_adjustment = st.selectbox(
                "Health Status",
                options=["excellent", "average", "poor"],
                index=1,
                key="health_adjustment",
                help="Adjust life expectancy based on health status"
            )
        
        if use_actuarial_tables:
            st.info(f"Based on actuarial tables and {health_adjustment} health, planning horizon may be adjusted.")
    
    # --- Income Sources ---
    st.subheader("Income Sources")
    
    col1, col2 = st.columns(2)
    
    with col1:
        regular_income_monthly = _dollar_input(
            "Regular Income (Monthly)",
            default_value=0.0,
            key="regular_income_monthly",
            help="Salary, wages, or other regular income"
        )
    
    with col2:
        ss_monthly = _dollar_input(
            "Social Security (Monthly)",
            default_value=0.0,
            key="ss_monthly",
            help="Expected monthly Social Security benefit"
        )
    
    ss_start_age = st.number_input(
        "Social Security Start Age",
        min_value=62,
        max_value=70,
        value=67,
        step=1,
        key="ss_start_age",
    ) if ss_monthly > 0 else 67
    
    col1, col2 = st.columns(2)
    
    with col1:
        pension_monthly = _dollar_input(
            "Pension (Monthly)",
            default_value=0.0,
            key="pension_monthly",
            help="Expected monthly pension benefit"
        )
    
        pension_start_age = st.number_input(
            "Pension Start Age",
            min_value=50,
            max_value=75,
            value=65,
            step=1,
            key="pension_start_age",
        ) if pension_monthly > 0 else 65
    
    with col2:
        other_income_monthly = _dollar_input(
            "Other Income (Monthly)",
            default_value=0.0,
            key="other_income_monthly",
            help="Rental income, part-time work, etc."
        )
    
        other_income_start_age = st.number_input(
            "Other Income Start Age",
            min_value=current_age,
            max_value=horizon_age,
            value=65,
            step=1,
            key="other_income_start_age",
        ) if other_income_monthly > 0 else 65

    # --- Allocation ---
    st.subheader("Allocation")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        equity_pct_slider = st.slider(
            "Equity %",
            min_value=0,
            max_value=100,
            value=70,
            step=5,
            key="equity_pct",
        )
    with col2:
        fi_pct_slider = st.slider(
            "Fixed Income %",
            min_value=0,
            max_value=100,
            value=25,
            step=5,
            key="fi_pct",
        )
    with col3:
        cash_pct_slider = st.slider(
            "Cash %",
            min_value=0,
            max_value=100,
            value=5,
            step=5,
            key="cash_pct",
        )

    equity_pct = equity_pct_slider / 100.0
    fi_pct = fi_pct_slider / 100.0
    cash_pct = cash_pct_slider / 100.0

    alloc_sum = equity_pct + fi_pct + cash_pct
    if abs(alloc_sum - 1.0) > 1e-6:
        st.warning(
            f"Allocation totals {alloc_sum*100:.1f}% (should be 100%). "
            "Consider adjusting Equity / Fixed Income / Cash."
        )
    
    # --- Dynamic Asset Allocation (Glide Path) ---
    with st.expander("Dynamic Allocation (Glide Path)", expanded=False):
        use_glide_path = st.checkbox(
            "Use Dynamic Allocation Glide Path",
            value=False,
            key="use_glide_path",
            help="Automatically reduce equity exposure over time"
        )
        
        if use_glide_path:
            col1, col2 = st.columns(2)
            with col1:
                target_equity_pct = st.slider(
                    "Target Equity % (at end)",
                    min_value=0,
                    max_value=100,
                    value=40,
                    step=5,
                    key="target_equity_pct"
                )
            with col2:
                glide_start_age = st.number_input(
                    "Start Glide Path at Age",
                    min_value=current_age,
                    max_value=horizon_age,
                    value=65,
                    step=1,
                    key="glide_start_age"
                )
        else:
            target_equity_pct = equity_pct
            glide_start_age = horizon_age

    # --- Return Assumptions ---
    st.subheader("Return Assumptions (Annual, Real)")
    
    # Assumption Presets
    preset_options = [
        "Custom",
        "CFP Board (Conservative)",
        "Morningstar (Moderate)",
        "Vanguard (Historical)",
        "Conservative",
        "Aggressive"
    ]
    
    selected_preset = st.selectbox(
        "Load Assumption Preset",
        options=preset_options,
        index=0,
        key="assumption_preset",
        help="Load industry-standard assumptions or use custom values"
    )
    
    # Load preset values if selected
    if selected_preset != "Custom":
        preset_values = get_assumption_preset(selected_preset)
        equity_return_default = preset_values["equity_return"]
        fi_return_default = preset_values["fi_return"]
        cash_return_default = preset_values["cash_return"]
        equity_vol_default = preset_values["equity_vol"]
        fi_vol_default = preset_values["fi_vol"]
        cash_vol_default = preset_values["cash_vol"]
        st.info(f"Loaded {selected_preset} assumptions")
    else:
        equity_return_default = 0.10
        fi_return_default = 0.03
        cash_return_default = 0.02
        equity_vol_default = 0.15
        fi_vol_default = 0.05
        cash_vol_default = 0.01
    
    # Use a safe key suffix (replace spaces and parentheses)
    key_suffix = selected_preset.replace(" ", "_").replace("(", "").replace(")", "")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        equity_return_annual = _percent_input(
            "Equity Return",
            default_fraction=equity_return_default,
            key=f"equity_return_{key_suffix}",
        )
    with col2:
        fi_return_annual = _percent_input(
            "Fixed Income Return",
            default_fraction=fi_return_default,
            key=f"fi_return_{key_suffix}",
        )
    with col3:
        cash_return_annual = _percent_input(
            "Cash Return",
            default_fraction=cash_return_default,
            key=f"cash_return_{key_suffix}",
        )

    # --- Volatility Assumptions ---
    st.subheader("Volatility (Annual)")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        equity_vol_annual = _percent_input(
            "Equity Volatility",
            default_fraction=equity_vol_default,
            key=f"equity_vol_{key_suffix}",
        )
    with col2:
        fi_vol_annual = _percent_input(
            "Fixed Income Volatility",
            default_fraction=fi_vol_default,
            key=f"fi_vol_{key_suffix}",
        )
    with col3:
        cash_vol_annual = _percent_input(
            "Cash Volatility",
            default_fraction=cash_vol_default,
            key=f"cash_vol_{key_suffix}",
        )

    # --- Monte Carlo Settings ---
    st.subheader("Monte Carlo Settings")
    
    n_scenarios = st.slider(
        "Number of Scenarios",
        min_value=50,
        max_value=2000,
        value=200,
        step=50,
        key="n_scenarios",
    )

    # --- One-Time Cash Flow ---
    st.subheader("One-Time Cash Flow")
    
    col1, col2 = st.columns(2)

    with col1:
        one_time_cf = _dollar_input(
            "One-Time Cash Flow",
            default_value=0.0,
            key="one_time_cf",
            help="Positive = inflow, negative = outflow.",
        )

    with col2:
        one_time_cf_month = st.number_input(
            "One-Time Cash Flow Month (1 = first month, 0 = never)",
            min_value=0,
            max_value=max(years_to_model * 12, 0),
            value=0,
            step=1,
            key="one_time_cf_month",
        )
    
    # --- Multiple Cash Flows ---
    with st.expander("Multiple One-Time Cash Flows", expanded=False):
        st.caption("Model multiple one-time events like home purchases, inheritances, college tuition, etc.")
        num_cash_flows = st.number_input(
            "Number of Additional Cash Flows",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            key="num_cash_flows"
        )
        
        cash_flows = []
        for i in range(num_cash_flows):
            st.markdown(f"**Cash Flow {i+1}**")
            col1, col2, col3 = st.columns(3)
            with col1:
                cf_desc = st.text_input(
                    f"Description {i+1}",
                    value=f"Event {i+1}",
                    key=f"cf_desc_{i}"
                )
            with col2:
                cf_amount = _dollar_input(
                    f"Amount {i+1}",
                    default_value=0.0,
                    key=f"cf_amount_{i}",
                    help="Positive = inflow, negative = outflow"
                )
            with col3:
                cf_month = st.number_input(
                    f"Month {i+1}",
                    min_value=1,
                    max_value=max(years_to_model * 12, 1),
                    value=12,
                    step=1,
                    key=f"cf_month_{i}"
                )
            cash_flows.append((cf_month, cf_amount, cf_desc))
    
    # --- Lifestyle Spending Phases ---
    with st.expander("Lifestyle Spending Phases", expanded=False):
        use_lifestyle_phases = st.checkbox(
            "Use Lifestyle Phase Spending",
            value=False,
            key="use_lifestyle_phases",
            help="Model different spending levels for go-go, slow-go, and no-go retirement years"
        )
        
        if use_lifestyle_phases:
            st.markdown("**Go-Go Years** (Active retirement, higher spending)")
            col1, col2 = st.columns(2)
            with col1:
                go_go_end_age = st.number_input(
                    "Go-Go Phase Ends at Age",
                    min_value=current_age,
                    max_value=horizon_age,
                    value=75,
                    step=1,
                    key="go_go_end_age"
                )
            with col2:
                go_go_spending_multiplier = st.slider(
                    "Spending Multiplier",
                    min_value=0.5,
                    max_value=2.0,
                    value=1.0,
                    step=0.05,
                    key="go_go_mult"
                )
            
            st.markdown("**Slow-Go Years** (Moderate activity, reduced spending)")
            col1, col2 = st.columns(2)
            with col1:
                slow_go_end_age = st.number_input(
                    "Slow-Go Phase Ends at Age",
                    min_value=go_go_end_age,
                    max_value=horizon_age,
                    value=85,
                    step=1,
                    key="slow_go_end_age"
                )
            with col2:
                slow_go_spending_multiplier = st.slider(
                    "Spending Multiplier",
                    min_value=0.5,
                    max_value=2.0,
                    value=0.80,
                    step=0.05,
                    key="slow_go_mult"
                )
            
            st.markdown("**No-Go Years** (Lower activity, lowest spending)")
            no_go_spending_multiplier = st.slider(
                "Spending Multiplier",
                min_value=0.5,
                max_value=2.0,
                value=0.60,
                step=0.05,
                key="no_go_mult"
            )
        else:
            go_go_end_age = 75
            go_go_spending_multiplier = 1.0
            slow_go_end_age = 85
            slow_go_spending_multiplier = 0.80
            no_go_spending_multiplier = 0.60
    
    # --- Guardrails Strategy ---
    with st.expander("Dynamic Spending Guardrails", expanded=False):
        use_guardrails = st.checkbox(
            "Use Guardrails Strategy",
            value=False,
            key="use_guardrails",
            help="Automatically adjust spending based on portfolio performance"
        )
        
        if use_guardrails:
            col1, col2, col3 = st.columns(3)
            with col1:
                upper_guardrail = _percent_input(
                    "Upper Guardrail (increase threshold)",
                    default_fraction=0.20,
                    key="upper_guardrail",
                    help="If portfolio exceeds initial value by this %, increase spending"
                )
            with col2:
                lower_guardrail = _percent_input(
                    "Lower Guardrail (decrease threshold)",
                    default_fraction=0.15,
                    key="lower_guardrail",
                    help="If portfolio falls below initial value by this %, decrease spending"
                )
            with col3:
                guardrail_adjustment = _percent_input(
                    "Spending Adjustment Amount",
                    default_fraction=0.10,
                    key="guardrail_adjustment",
                    help="Amount to adjust spending when guardrails are triggered"
                )
        else:
            upper_guardrail = 0.20
            lower_guardrail = 0.15
            guardrail_adjustment = 0.10
    
    # --- Financial Goals ---
    st.subheader("Financial Goals")
    
    financial_goals = []
    
    num_goals = st.number_input(
        "Number of Goals",
        min_value=0,
        max_value=5,
        value=0,
        step=1,
        key="num_goals",
        help="Track probability of achieving specific financial milestones"
    )
    
    for i in range(num_goals):
        st.markdown(f"**Goal {i+1}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            goal_name = st.text_input(
                f"Goal Name {i+1}",
                value=f"Goal {i+1}",
                key=f"goal_name_{i}"
            )
        with col2:
            goal_amount = _dollar_input(
                f"Target Amount {i+1}",
                default_value=1_000_000.0,
                key=f"goal_amount_{i}",
                help="Portfolio value needed at target age"
            )
        with col3:
            goal_age = st.number_input(
                f"Target Age {i+1}",
                min_value=current_age,
                max_value=horizon_age,
                value=min(current_age + 10, horizon_age),
                step=1,
                key=f"goal_age_{i}"
            )
        financial_goals.append(FinancialGoal(
            name=goal_name,
            target_amount=goal_amount,
            target_age=goal_age
        ))

    # Stress scenarios are now defined in the Stress Tests section after running simulation
    stress_scenarios: List[StressTestScenario] = []

    model_inputs = ModelInputs(
        starting_portfolio=starting_portfolio,
        years_to_model=years_to_model,
        current_age=current_age,
        horizon_age=horizon_age,
        monthly_spending=monthly_spending,
        inflation_annual=inflation_annual,
        equity_pct=equity_pct,
        fi_pct=fi_pct,
        cash_pct=cash_pct,
        equity_return_annual=equity_return_annual,
        fi_return_annual=fi_return_annual,
        cash_return_annual=cash_return_annual,
        equity_vol_annual=equity_vol_annual,
        fi_vol_annual=fi_vol_annual,
        cash_vol_annual=cash_vol_annual,
        n_scenarios=n_scenarios,
        spending_rule=spending_rule,
        spending_pct_annual=spending_pct_annual,
        one_time_cf=one_time_cf,
        one_time_cf_month=one_time_cf_month,
        taxable_pct=taxable_pct,
        ira_pct=ira_pct,
        roth_pct=roth_pct,
        tax_rate=tax_rate,
        rmd_age=rmd_age,
        social_security_monthly=ss_monthly,
        ss_start_age=ss_start_age,
        pension_monthly=pension_monthly,
        pension_start_age=pension_start_age,
        regular_income_monthly=regular_income_monthly,
        other_income_monthly=other_income_monthly,
        other_income_start_age=other_income_start_age,
        is_couple=is_couple,
        spouse_age=spouse_age,
        spouse_horizon_age=spouse_horizon_age,
        spouse_ss_monthly=spouse_ss_monthly,
        spouse_ss_start_age=spouse_ss_start_age,
        healthcare_monthly=healthcare_monthly,
        healthcare_start_age=healthcare_start_age,
        healthcare_inflation=healthcare_inflation,
        roth_conversion_annual=roth_conversion_annual if 'roth_conversion_annual' in locals() else 0.0,
        roth_conversion_start_age=roth_conversion_start_age if 'roth_conversion_start_age' in locals() else 60,
        roth_conversion_end_age=roth_conversion_end_age if 'roth_conversion_end_age' in locals() else 70,
        estate_tax_exemption=estate_tax_exemption if 'estate_tax_exemption' in locals() else 13_610_000.0,
        estate_tax_rate=estate_tax_rate if 'estate_tax_rate' in locals() else 0.40,
        legacy_goal=legacy_goal if 'legacy_goal' in locals() else 0.0,
        use_actuarial_tables=use_actuarial_tables if 'use_actuarial_tables' in locals() else False,
        health_adjustment=health_adjustment if 'health_adjustment' in locals() else "average",
        use_glide_path=use_glide_path,
        target_equity_pct=target_equity_pct / 100.0 if use_glide_path else equity_pct,
        glide_start_age=glide_start_age,
        cash_flows=cash_flows if 'cash_flows' in locals() and len(cash_flows) > 0 else None,
        use_lifestyle_phases=use_lifestyle_phases,
        go_go_end_age=go_go_end_age,
        go_go_spending_multiplier=go_go_spending_multiplier,
        slow_go_end_age=slow_go_end_age,
        slow_go_spending_multiplier=slow_go_spending_multiplier,
        no_go_spending_multiplier=no_go_spending_multiplier,
        use_guardrails=use_guardrails,
        upper_guardrail=upper_guardrail,
        lower_guardrail=lower_guardrail,
        guardrail_adjustment=guardrail_adjustment,
    )

    return client_info, model_inputs, stress_scenarios, financial_goals


# -----------------------------
# Stress Test Input UI
# -----------------------------

def stress_test_inputs() -> List[StressTestScenario]:
    """Display stress test scenario inputs and return configured scenarios."""
    st.subheader("Stress Test Scenarios (vs Base)")
    st.caption("Define custom stress scenarios to test portfolio resilience under different market conditions.")

    default_labels = ["Mild Downturn", "Severe Downturn", "High Inflation", "Early Bear Market Shock"]
    default_return_deltas = [-0.02, -0.04, 0.00, 0.00]  # -2%, -4%, 0%, 0%
    default_spend_deltas = [0.00, 0.05, 0.00, 0.00]     # 0%, +5%, 0%, 0%
    default_infl_deltas = [0.00, 0.00, 0.02, 0.00]      # 0%, 0%, +2%, 0%
    default_drawdowns = [0.00, 0.00, 0.00, 0.00]        # 0%, 0%, 0%, 0%

    stress_scenarios: List[StressTestScenario] = []

    for i in range(4):
        st.markdown(f"**Scenario {i+1}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            label = st.text_input(
                "Name",
                value=default_labels[i],
                key=f"st_label_{i}",
            )

        # Scenario 4 has different inputs (custom year returns)
        if i == 3:
            with col2:
                year1_return = _percent_input(
                    "Year 1 Return",
                    default_fraction=-0.10,
                    key=f"st_y1ret_{i}",
                    help="Annual return for year 1 (e.g., -10% = -0.10).",
                )
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                year2_return = _percent_input(
                    "Year 2 Return",
                    default_fraction=-0.05,
                    key=f"st_y2ret_{i}",
                    help="Annual return for year 2 (e.g., -5% = -0.05).",
                )
            with col4:
                year3_return = _percent_input(
                    "Year 3 Return",
                    default_fraction=0.15,
                    key=f"st_y3ret_{i}",
                    help="Annual return for year 3 (e.g., 15% = 0.15). After year 3, returns to baseline.",
                )
            
            with col5:
                spending_delta = _percent_input(
                    "Spending Change",
                    default_fraction=default_spend_deltas[i],
                    key=f"st_spend_{i}",
                    help="Change in ongoing spending level vs base.",
                )
            
            if label.strip():
                stress_scenarios.append(
                    StressTestScenario(
                        name=label.strip(),
                        return_delta=0.0,
                        spending_delta=spending_delta,
                        inflation_delta=0.0,
                        first_year_drawdown=0.0,
                        custom_year1_return=year1_return,
                        custom_year2_return=year2_return,
                        custom_year3_return=year3_return,
                    )
                )
        else:
            with col2:
                return_delta = _percent_input(
                    "Return Change (annual)",
                    default_fraction=default_return_deltas[i],
                    key=f"st_ret_{i}",
                    help="Additive change vs base portfolio expected return.",
                )
            
            col3, col4, col5 = st.columns(3)

            with col3:
                spending_delta = _percent_input(
                    "Spending Change",
                    default_fraction=default_spend_deltas[i],
                    key=f"st_spend_{i}",
                    help="Change in ongoing spending level vs base.",
                )

            with col4:
                infl_delta = _percent_input(
                    "Inflation Change",
                    default_fraction=default_infl_deltas[i],
                    key=f"st_infl_{i}",
                    help="Additive change to annual inflation vs base.",
                )

            with col5:
                drawdown = _percent_input(
                    "First Year Drawdown",
                    default_fraction=default_drawdowns[i],
                    key=f"st_drawdown_{i}",
                    help="Portfolio drawdown at end of first year (e.g., 20% = portfolio drops 20% at month 12).",
                )

            if label.strip():
                stress_scenarios.append(
                    StressTestScenario(
                        name=label.strip(),
                        return_delta=return_delta,
                        spending_delta=spending_delta,
                        inflation_delta=infl_delta,
                        first_year_drawdown=drawdown,
                        inflation_years=10 if i == 2 else None,  # Scenario 3 (index 2) applies inflation for 10 years only
                    )
                )

        st.markdown("---")
    
    return stress_scenarios


# -----------------------------
# Stress-test engine & charts
# -----------------------------

def run_stress_tests(
    inputs: ModelInputs,
    stress_scenarios: List[StressTestScenario],
) -> dict:
    """Monte Carlo stress-test projections.

    Uses Monte Carlo simulation with random returns for each scenario, applying:
    - expected return (return_delta or custom year returns)
    - spending level (spending_delta)
    - inflation (inflation_delta)
    
    Returns a dict with keys as scenario names and values as stats DataFrames.
    """
    if not stress_scenarios:
        return {}

    months = inputs.years_to_model * 12
    base_exp_ann, base_vol = compute_portfolio_return_and_vol(inputs)
    
    results = {}

    for sc in stress_scenarios:
        values = np.zeros((months, inputs.n_scenarios), dtype=float)

        for j in range(inputs.n_scenarios):
            val = inputs.starting_portfolio
            spending = inputs.monthly_spending * (1 + sc.spending_delta)

            for m in range(months):
                month_no = m + 1
                current_month_age = inputs.current_age + (month_no / 12.0)
                
                # Determine inflation rate based on inflation_years setting
                if sc.inflation_years is not None and month_no > (sc.inflation_years * 12):
                    infl_ann = inputs.inflation_annual
                else:
                    infl_ann = max(inputs.inflation_annual + sc.inflation_delta, 0.0)
                
                monthly_infl = (1 + infl_ann) ** (1 / 12) - 1
                
                # Determine expected return based on custom year returns or return_delta
                if sc.custom_year1_return is not None:
                    if month_no <= 12:
                        exp_ann = sc.custom_year1_return
                    elif month_no <= 24:
                        exp_ann = sc.custom_year2_return
                    elif month_no <= 36:
                        exp_ann = sc.custom_year3_return
                    else:
                        exp_ann = base_exp_ann
                else:
                    exp_ann = base_exp_ann + sc.return_delta
                
                exp_ann = max(exp_ann, -0.99)
                
                # Use the same volatility for stress tests
                mu_month = (1 + exp_ann) ** (1 / 12) - 1
                sigma_month = base_vol / math.sqrt(12)

                if inputs.spending_rule == 1:
                    cf = spending
                else:
                    cf = -val * (inputs.spending_pct_annual / 12.0)

                # Add income sources based on age
                if inputs.social_security_monthly > 0 and current_month_age >= inputs.ss_start_age:
                    cf += inputs.social_security_monthly
                
                if inputs.pension_monthly > 0 and current_month_age >= inputs.pension_start_age:
                    cf += inputs.pension_monthly
                
                if inputs.other_income_monthly > 0 and current_month_age >= inputs.other_income_start_age:
                    cf += inputs.other_income_monthly
                
                # Add spouse Social Security if applicable
                if inputs.is_couple and inputs.spouse_ss_monthly > 0:
                    spouse_current_age = inputs.spouse_age + (month_no / 12.0)
                    if spouse_current_age >= inputs.spouse_ss_start_age:
                        cf += inputs.spouse_ss_monthly
                
                # Subtract healthcare costs if applicable
                if inputs.healthcare_monthly > 0 and current_month_age >= inputs.healthcare_start_age:
                    healthcare_months = month_no - ((inputs.healthcare_start_age - inputs.current_age) * 12)
                    if healthcare_months > 0:
                        monthly_hc_infl = (1 + inputs.healthcare_inflation) ** (1 / 12) - 1
                        inflated_hc = inputs.healthcare_monthly * ((1 + monthly_hc_infl) ** healthcare_months)
                        cf -= inflated_hc
                    else:
                        cf -= inputs.healthcare_monthly

                if inputs.one_time_cf_month and month_no == inputs.one_time_cf_month:
                    cf += inputs.one_time_cf

                val = max(val + cf, 0.0)
                
                # Apply random return
                rnd = np.random.normal(mu_month, sigma_month)
                val = max(val * (1.0 + rnd), 0.0)

                # Apply first-year drawdown at end of month 12
                if month_no == 12 and sc.first_year_drawdown > 0:
                    val = max(val * (1 - sc.first_year_drawdown), 0.0)

                values[m, j] = val

                if inputs.spending_rule == 1:
                    spending *= (1 + monthly_infl)

        # Create stats DataFrame for this scenario
        months_index = np.arange(1, months + 1)
        columns = [f"Scenario_{i+1}" for i in range(inputs.n_scenarios)]
        paths_df = pd.DataFrame(values, index=months_index, columns=columns)
        paths_df.index.name = "Month"
        
        stats_df = pd.DataFrame({
            "Month": months_index,
            "P10": np.percentile(values, 10, axis=1),
            "P25": np.percentile(values, 25, axis=1),
            "Median": np.percentile(values, 50, axis=1),
            "P75": np.percentile(values, 75, axis=1),
            "P90": np.percentile(values, 90, axis=1),
        })
        
        results[sc.name] = {"stats": stats_df, "paths": paths_df}

    return results


def stress_test_charts(stress_results: dict):
    """Create fan charts and depletion charts for each stress test scenario."""
    if not stress_results:
        return []
    
    charts = []
    for scenario_name, data in stress_results.items():
        fan = fan_chart(data["stats"], title=f"{scenario_name} - Monte Carlo Fan Chart")
        depletion = depletion_probability_chart(data["paths"], title=f"{scenario_name} - Depletion Probability")
        charts.append((scenario_name, fan, depletion))
    
    return charts


# -----------------------------
# PDF Report Generation
# -----------------------------

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple for ReportLab."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def generate_enhanced_pdf_report(client_info, inputs, stats_df, metrics, paths_df, 
                                goal_results, selected_sections, phase4_data=None, branding=None):
    """Generate an enhanced PDF report with Phase 4 analytics and custom branding."""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    
    # Get branding colors or use defaults
    if branding and 'primary_color' in branding:
        primary_rgb = hex_to_rgb(branding['primary_color'])
        accent_rgb = hex_to_rgb(branding['accent_color'])
        firm_name = branding.get('firm_name', 'Salem Investment Counselors')
    else:
        primary_rgb = hex_to_rgb(SALEM_NAVY)
        accent_rgb = hex_to_rgb(SALEM_GOLD)
        firm_name = 'Salem Investment Counselors'
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.Color(*primary_rgb),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.Color(*primary_rgb),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.Color(*primary_rgb),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.Color(*primary_rgb),
        spaceAfter=6
    )
    
    # Title Page
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("Portfolio Analysis Report", title_style))
    story.append(Paragraph("Monte Carlo Simulation & Advanced Analytics", heading_style))
    story.append(Spacer(1, 0.5*inch))
    
    if client_info.client_name:
        story.append(Paragraph(f"<b>Client:</b> {client_info.client_name}", body_style))
    if branding and branding.get('advisor_name'):
        story.append(Paragraph(f"<b>Advisor:</b> {branding['advisor_name']}", body_style))
    story.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"<i>{firm_name}</i>", body_style))
    if branding and branding.get('advisor_email'):
        story.append(Paragraph(f"<i>{branding['advisor_email']}</i>", body_style))
    story.append(PageBreak())
    
    # Executive Summary
    if 'executive_summary' in selected_sections:
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Starting Portfolio', f"${inputs.starting_portfolio:,.0f}"],
            ['Planning Horizon', f"{inputs.years_to_model} years"],
            ['Monthly Spending', f"${-inputs.monthly_spending:,.0f}"],
            ['Success Probability', f"{metrics['prob_never_depleted']*100:.1f}%"],
            ['Median Ending Portfolio', f"${metrics['ending_median']:,.0f}"],
            ['10th Percentile Ending', f"${metrics['ending_p10']:,.0f}"],
            ['90th Percentile Ending', f"${metrics['ending_p90']:,.0f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*primary_rgb)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(*accent_rgb)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        story.append(PageBreak())
    
    # Phase 4 Analytics Section
    if phase4_data:
        story.append(Paragraph("Advanced Analytics", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Historical Stress Scenarios
        if phase4_data.get('historical'):
            hist_data = phase4_data['historical']
            story.append(Paragraph("Historical Stress Scenario Analysis", subheading_style))
            story.append(Paragraph(f"Scenario: {hist_data['scenario']}", body_style))
            story.append(Spacer(1, 0.1*inch))
            
            last_month = inputs.years_to_model * 12
            hist_ending = hist_data['data']['stats'][hist_data['data']['stats']['Month'] == last_month].iloc[0]
            
            hist_table_data = [
                ['Metric', 'Value'],
                ['Median Ending Portfolio', f"${hist_ending['Median']:,.0f}"],
                ['10th Percentile', f"${hist_ending['P10']:,.0f}"],
                ['90th Percentile', f"${hist_ending['P90']:,.0f}"],
            ]
            
            hist_table = Table(hist_table_data, colWidths=[3*inch, 2.5*inch])
            hist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*accent_rgb)),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(hist_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Rebalancing Analysis
        if phase4_data.get('rebalancing'):
            rebal_data = phase4_data['rebalancing']
            story.append(Paragraph("Dynamic Rebalancing Strategy Analysis", subheading_style))
            story.append(Spacer(1, 0.1*inch))
            
            rebal_table_data = [['Strategy', 'Median Ending', 'Avg Rebalances']]
            for strat_name, result in rebal_data.items():
                last_month = inputs.years_to_model * 12
                ending = result['stats'][result['stats']['Month'] == last_month].iloc[0]
                rebal_table_data.append([
                    strat_name,
                    f"${ending['Median']:,.0f}",
                    f"{result['rebalance_count']:.1f}"
                ])
            
            rebal_table = Table(rebal_table_data, colWidths=[2*inch, 2*inch, 1.5*inch])
            rebal_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*accent_rgb)),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(rebal_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Tax-Efficient Withdrawal Strategies
        if phase4_data.get('tax'):
            tax_data = phase4_data['tax']
            story.append(Paragraph("Tax-Efficient Withdrawal Strategy Analysis", subheading_style))
            story.append(Spacer(1, 0.1*inch))
            
            tax_table_data = [['Strategy', 'Total Tax', 'Effective Rate', 'Savings']]
            for strat_name, result in tax_data.items():
                savings = result.get('tax_savings_vs_naive', 0)
                tax_table_data.append([
                    strat_name,
                    f"${result['total_tax']:,.0f}",
                    f"{result['effective_tax_rate']*100:.1f}%",
                    f"${savings:,.0f}" if savings > 0 else "Baseline"
                ])
            
            tax_table = Table(tax_table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            tax_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*accent_rgb)),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(tax_table)
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
    
    # Portfolio Assumptions
    if 'assumptions' in selected_sections:
        story.append(Paragraph("Portfolio Assumptions", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        assumptions_data = [
            ['Parameter', 'Value'],
            ['Equity Allocation', f"{inputs.equity_pct*100:.1f}%"],
            ['Fixed Income Allocation', f"{inputs.fi_pct*100:.1f}%"],
            ['Cash Allocation', f"{inputs.cash_pct*100:.1f}%"],
            ['Equity Expected Return', f"{inputs.equity_return_annual*100:.1f}%"],
            ['Fixed Income Return', f"{inputs.fi_return_annual*100:.1f}%"],
            ['Inflation Rate', f"{inputs.inflation_annual*100:.1f}%"],
            ['Number of Simulations', f"{inputs.n_scenarios:,}"],
        ]
        
        assumptions_table = Table(assumptions_data, colWidths=[3*inch, 2.5*inch])
        assumptions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*primary_rgb)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(*accent_rgb)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(assumptions_table)
        story.append(PageBreak())
    
    # Disclaimer
    if branding and branding.get('disclaimer'):
        story.append(Spacer(1, 0.5*inch))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_JUSTIFY
        )
        story.append(Paragraph("<b>Disclaimer:</b>", disclaimer_style))
        story.append(Paragraph(branding['disclaimer'], disclaimer_style))
    
    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

def generate_pdf_report(client_info, inputs, metrics, stats_df, paths_df, stress_results, 
                       financial_goals, goal_results, selected_sections):
    """Generate a PDF report with selected sections."""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    
    # Define colors
    salem_gold_rgb = hex_to_rgb(SALEM_GOLD)
    salem_navy_rgb = hex_to_rgb(SALEM_NAVY)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.Color(*salem_navy_rgb),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.Color(*salem_navy_rgb),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderColor=colors.Color(*salem_gold_rgb),
        borderWidth=2,
        borderPadding=5
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.Color(*salem_navy_rgb),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.Color(*salem_navy_rgb),
        spaceAfter=6
    )
    
    # Title Page
    if 'title_page' in selected_sections:
        story.append(Spacer(1, 1.5*inch))
        story.append(Paragraph("Portfolio Growth Analysis", title_style))
        story.append(Paragraph("Monte Carlo Scenario Analysis", heading_style))
        story.append(Spacer(1, 0.5*inch))
        
        if client_info.client_name:
            story.append(Paragraph(f"<b>Client:</b> {client_info.client_name}", body_style))
        if client_info.advisor_name:
            story.append(Paragraph(f"<b>Advisor:</b> {client_info.advisor_name}", body_style))
        story.append(Paragraph(f"<b>Report Date:</b> {client_info.report_date.strftime('%B %d, %Y')}", body_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("<i>Salem Investment Counselors</i>", body_style))
        story.append(PageBreak())
    
    # Executive Summary
    if 'executive_summary' in selected_sections:
        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Starting Portfolio', f"${inputs.starting_portfolio:,.0f}"],
            ['Planning Horizon', f"{inputs.years_to_model} years (Age {inputs.current_age} to {inputs.horizon_age})"],
            ['Monthly Spending (initial)', f"${-inputs.monthly_spending:,.0f}"],
            ['Median Ending Portfolio', f"${metrics['ending_median']:,.0f}"],
            ['10th Percentile Ending', f"${metrics['ending_p10']:,.0f}"],
            ['90th Percentile Ending', f"${metrics['ending_p90']:,.0f}"],
            ['Success Probability', f"{metrics['prob_never_depleted']*100:.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*salem_navy_rgb)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.Color(*salem_navy_rgb)),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(*salem_gold_rgb)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        story.append(PageBreak())
    
    # Portfolio Assumptions
    if 'assumptions' in selected_sections:
        story.append(Paragraph("Portfolio Assumptions", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        exp_ann, vol_ann = compute_portfolio_return_and_vol(inputs)
        
        assumptions_data = [
            ['Parameter', 'Value'],
            ['Asset Allocation', ''],
            ['  Equity', f"{inputs.equity_pct*100:.1f}%"],
            ['  Fixed Income', f"{inputs.fi_pct*100:.1f}%"],
            ['  Cash', f"{inputs.cash_pct*100:.1f}%"],
            ['Expected Returns (Real)', ''],
            ['  Equity', f"{inputs.equity_return_annual*100:.1f}%"],
            ['  Fixed Income', f"{inputs.fi_return_annual*100:.1f}%"],
            ['  Cash', f"{inputs.cash_return_annual*100:.1f}%"],
            ['Volatility', ''],
            ['  Equity', f"{inputs.equity_vol_annual*100:.1f}%"],
            ['  Fixed Income', f"{inputs.fi_vol_annual*100:.1f}%"],
            ['  Cash', f"{inputs.cash_vol_annual*100:.1f}%"],
            ['Portfolio Metrics', ''],
            ['  Expected Return', f"{exp_ann*100:.2f}%"],
            ['  Volatility', f"{vol_ann*100:.2f}%"],
            ['Other Assumptions', ''],
            ['  Inflation Rate', f"{inputs.inflation_annual*100:.1f}%"],
            ['  Number of Scenarios', f"{inputs.n_scenarios}"],
        ]
        
        assumptions_table = Table(assumptions_data, colWidths=[3*inch, 2.5*inch])
        assumptions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*salem_navy_rgb)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.Color(*salem_navy_rgb)),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(*salem_gold_rgb)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(assumptions_table)
        story.append(Spacer(1, 0.3*inch))
        story.append(PageBreak())
    
    # Financial Goals
    if 'financial_goals' in selected_sections and financial_goals and goal_results is not None and not goal_results.empty:
        story.append(Paragraph("Financial Goal Analysis", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        goal_data = [['Goal', 'Target Amount', 'Target Age', 'Success Probability']]
        for _, row in goal_results.iterrows():
            goal_data.append([
                row['Goal'],
                f"${row['Target Amount']:,.0f}",
                f"{int(row['Target Age'])}",
                f"{row['Probability of Success']:.1f}%"
            ])
        
        goal_table = Table(goal_data, colWidths=[2*inch, 1.5*inch, 1.2*inch, 1.5*inch])
        goal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*salem_navy_rgb)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.Color(*salem_navy_rgb)),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(*salem_gold_rgb)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(goal_table)
        story.append(Spacer(1, 0.3*inch))
        story.append(PageBreak())
    
    # Stress Test Results
    if 'stress_tests' in selected_sections and stress_results:
        story.append(Paragraph("Stress Test Results", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        last_month = inputs.years_to_model * 12
        stress_data = [['Scenario', '10th Percentile', 'Median', '90th Percentile']]
        
        for scenario_name, data in stress_results.items():
            ending_row = data["stats"][data["stats"]["Month"] == last_month].iloc[0]
            stress_data.append([
                scenario_name,
                f"${ending_row['P10']:,.0f}",
                f"${ending_row['Median']:,.0f}",
                f"${ending_row['P90']:,.0f}"
            ])
        
        stress_table = Table(stress_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        stress_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*salem_navy_rgb)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.Color(*salem_navy_rgb)),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.Color(*salem_gold_rgb)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(stress_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<i>Note: All values represent ending portfolio values at the end of the planning horizon.</i>", body_style))
        story.append(PageBreak())
    
    # Disclaimer
    if 'disclaimer' in selected_sections:
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Important Disclosures", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        disclaimer_text = """
        This Monte Carlo analysis is provided for informational and educational purposes only. 
        The projections and probability estimates are based on historical data and assumptions about future market conditions. 
        Actual results may differ materially from these projections. Past performance does not guarantee future results. 
        This analysis does not constitute investment advice, tax advice, or legal advice. Please consult with qualified 
        professionals regarding your specific financial situation.
        
        <br/><br/>
        
        The Monte Carlo simulation uses random sampling to model potential outcomes based on the specified assumptions. 
        The probability estimates reflect the frequency of outcomes in the simulated scenarios and should not be interpreted 
        as guarantees or predictions of actual future performance.
        """
        
        story.append(Paragraph(disclaimer_text, body_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_interactive_html_report(client_info, inputs, stats_df, metrics, paths_df,
                                    goal_results=None, phase4_data=None, branding=None):
    """Generate a standalone interactive HTML report with embedded Altair charts."""
    
    # Get branding
    firm_name = branding.get('firm_name', 'Salem Investment Counselors') if branding else 'Salem Investment Counselors'
    primary_color = branding.get('primary_color', SALEM_NAVY) if branding else SALEM_NAVY
    accent_color = branding.get('accent_color', SALEM_GOLD) if branding else SALEM_GOLD
    
    # Create fan chart
    fan_chart_obj = fan_chart(stats_df, title="Portfolio Projection")
    fan_chart_json = fan_chart_obj.to_json()
    
    # Create depletion chart
    depletion_chart_obj = depletion_probability_chart(paths_df, title="Depletion Risk Over Time")
    depletion_chart_json = depletion_chart_obj.to_json()
    
    # Build HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Analysis Report - {client_info.client_name if client_info and client_info.client_name else 'Client'}</title>
    <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: {primary_color};
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: {primary_color};
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid {accent_color};
        }}
        .section h3 {{
            color: {primary_color};
            font-size: 1.4em;
            margin-top: 20px;
            margin-bottom: 15px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, {primary_color} 0%, {accent_color} 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-card .label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: {primary_color};
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        .disclaimer {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Portfolio Analysis Report</h1>
            <p>Monte Carlo Simulation & Advanced Analytics</p>
            <p style="margin-top: 10px; font-size: 1em;">
                {f"Client: {client_info.client_name}" if client_info and client_info.client_name else ""}
                {f" | Advisor: {branding.get('advisor_name')}" if branding and branding.get('advisor_name') else ""}
            </p>
            <p style="font-size: 0.9em;">{datetime.now().strftime('%B %d, %Y')}</p>
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="label">Success Probability</div>
                    <div class="value">{metrics['prob_never_depleted']*100:.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="label">Starting Portfolio</div>
                    <div class="value">${inputs.starting_portfolio:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="label">Median Ending</div>
                    <div class="value">${metrics['ending_median']:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="label">Planning Horizon</div>
                    <div class="value">{inputs.years_to_model} Years</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Portfolio Projection</h2>
            <div class="chart-container">
                <div id="fan-chart"></div>
            </div>
        </div>

        <div class="section">
            <h2>Depletion Risk Analysis</h2>
            <div class="chart-container">
                <div id="depletion-chart"></div>
            </div>
        </div>

        <div class="section">
            <h2>Portfolio Assumptions</h2>
            <table>
                <tr><th>Parameter</th><th>Value</th></tr>
                <tr><td>Equity Allocation</td><td>{inputs.equity_pct*100:.1f}%</td></tr>
                <tr><td>Fixed Income Allocation</td><td>{inputs.fi_pct*100:.1f}%</td></tr>
                <tr><td>Cash Allocation</td><td>{inputs.cash_pct*100:.1f}%</td></tr>
                <tr><td>Expected Equity Return</td><td>{inputs.equity_return_annual*100:.1f}%</td></tr>
                <tr><td>Expected FI Return</td><td>{inputs.fi_return_annual*100:.1f}%</td></tr>
                <tr><td>Inflation Rate</td><td>{inputs.inflation_annual*100:.1f}%</td></tr>
                <tr><td>Monthly Spending</td><td>${-inputs.monthly_spending:,.0f}</td></tr>
                <tr><td>Number of Simulations</td><td>{inputs.n_scenarios:,}</td></tr>
            </table>
        </div>

        {generate_phase4_html_sections(phase4_data, inputs, primary_color, accent_color) if phase4_data else ""}

        {f'''
        <div class="section">
            <div class="disclaimer">
                <strong>Disclaimer:</strong> {branding.get('disclaimer')}
            </div>
        </div>
        ''' if branding and branding.get('disclaimer') else ''}

        <div class="footer">
            <p>{firm_name}</p>
            {f"<p>{branding.get('advisor_email')}</p>" if branding and branding.get('advisor_email') else ""}
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
    </div>

    <script>
        vegaEmbed('#fan-chart', {fan_chart_json}, {{"actions": false}});
        vegaEmbed('#depletion-chart', {depletion_chart_json}, {{"actions": false}});
    </script>
</body>
</html>
"""
    
    return html_content


def generate_phase4_html_sections(phase4_data, inputs, primary_color, accent_color):
    """Generate HTML sections for Phase 4 analytics."""
    sections = []
    
    # Historical Scenarios
    if phase4_data.get('historical'):
        hist_data = phase4_data['historical']
        last_month = inputs.years_to_model * 12
        hist_ending = hist_data['data']['stats'][hist_data['data']['stats']['Month'] == last_month].iloc[0]
        
        sections.append(f"""
        <div class="section">
            <h2>Historical Stress Scenario</h2>
            <h3>{hist_data['scenario']}</h3>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Median Ending Portfolio</td><td>${hist_ending['Median']:,.0f}</td></tr>
                <tr><td>10th Percentile</td><td>${hist_ending['P10']:,.0f}</td></tr>
                <tr><td>90th Percentile</td><td>${hist_ending['P90']:,.0f}</td></tr>
            </table>
        </div>
        """)
    
    # Rebalancing Analysis
    if phase4_data.get('rebalancing'):
        rebal_data = phase4_data['rebalancing']
        rows = ""
        for strat_name, result in rebal_data.items():
            last_month = inputs.years_to_model * 12
            ending = result['stats'][result['stats']['Month'] == last_month].iloc[0]
            rows += f"""
            <tr>
                <td>{strat_name}</td>
                <td>${ending['Median']:,.0f}</td>
                <td>${ending['P10']:,.0f}</td>
                <td>${ending['P90']:,.0f}</td>
                <td>{result['rebalance_count']:.1f}</td>
            </tr>
            """
        
        sections.append(f"""
        <div class="section">
            <h2>Rebalancing Strategy Analysis</h2>
            <table>
                <tr>
                    <th>Strategy</th>
                    <th>Median Ending</th>
                    <th>P10 Ending</th>
                    <th>P90 Ending</th>
                    <th>Avg Rebalances</th>
                </tr>
                {rows}
            </table>
        </div>
        """)
    
    # Tax Strategies
    if phase4_data.get('tax'):
        tax_data = phase4_data['tax']
        rows = ""
        for strat_name, result in tax_data.items():
            savings = result.get('tax_savings_vs_naive', 0)
            savings_str = f"${savings:,.0f}" if savings > 0 else "Baseline"
            rows += f"""
            <tr>
                <td>{strat_name}</td>
                <td>${result['total_tax']:,.0f}</td>
                <td>{result['effective_tax_rate']*100:.1f}%</td>
                <td>{savings_str}</td>
            </tr>
            """
        
        sections.append(f"""
        <div class="section">
            <h2>Tax-Efficient Withdrawal Strategies</h2>
            <table>
                <tr>
                    <th>Strategy</th>
                    <th>Total Tax</th>
                    <th>Effective Rate</th>
                    <th>Tax Savings</th>
                </tr>
                {rows}
            </table>
        </div>
        """)
    
    return "".join(sections)


# -----------------------------
# Main app
# -----------------------------

# ===========================================
# HELPER COMPONENT FUNCTIONS
# ===========================================

def risk_card(title, value, risk_level="low", description="", icon=""):
    """
    Display a risk indicator card with consistent styling.
    
    Args:
        title: Card title (e.g., "Shortfall Risk")
        value: Main value to display (e.g., "15.3%")
        risk_level: "low", "moderate", or "high" - determines color
        description: Optional description text
        icon: Optional emoji icon
    """
    # Risk color mapping
    risk_colors = {
        "low": "#10B981",     # Green
        "moderate": "#F59E0B", # Amber
        "high": "#EF4444"      # Red
    }
    
    color = risk_colors.get(risk_level, "#6B7280")
    
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid {color};
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            {f'<span style="font-size: 1.5rem;">{icon}</span>' if icon else ''}
            <span style="
                color: #1B3B5F;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                opacity: 0.7;
            ">{title}</span>
        </div>
        <div style="
            color: {color};
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin: 8px 0;
        ">{value}</div>
        {f'<div style="color: #6B7280; font-size: 0.875rem; margin-top: 8px;">{description}</div>' if description else ''}
    </div>
    """, unsafe_allow_html=True)


def metric_card(label, value, delta=None, icon=""):
    """
    Display a metric card with optional delta indicator.
    
    Args:
        label: Metric label
        value: Main value to display
        delta: Optional delta/change indicator
        icon: Optional emoji icon
    """
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(196, 160, 83, 0.2);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            {f'<span style="font-size: 1.5rem;">{icon}</span>' if icon else ''}
            <span style="
                color: #1B3B5F;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                opacity: 0.7;
            ">{label}</span>
        </div>
        <div style="
            color: #1B3B5F;
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            margin: 8px 0;
        ">{value}</div>
        {f'<div style="color: #C4A053; font-size: 1rem; font-weight: 600; margin-top: 4px;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


def success_indicator(probability, size="medium"):
    """
    Display a success probability indicator with color coding.
    
    Args:
        probability: Success probability (0-100)
        size: "small", "medium", or "large"
    """
    # Determine color based on probability
    if probability >= 85:
        color = "#10B981"  # Green
        status = "Excellent"
    elif probability >= 70:
        color = "#F59E0B"  # Amber
        status = "Good"
    elif probability >= 50:
        color = "#F97316"  # Orange
        status = "Moderate"
    else:
        color = "#EF4444"  # Red
        status = "At Risk"
    
    sizes = {
        "small": {"font": "1.5rem", "padding": "12px"},
        "medium": {"font": "2.5rem", "padding": "20px"},
        "large": {"font": "3.5rem", "padding": "32px"}
    }
    
    size_config = sizes.get(size, sizes["medium"])
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(250,250,250,0.95) 100%);
        padding: {size_config['padding']};
        border-radius: 16px;
        border: 2px solid {color};
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        text-align: center;
    ">
        <div style="
            color: {color};
            font-size: {size_config['font']};
            font-weight: 800;
            letter-spacing: -0.04em;
            margin-bottom: 8px;
        ">{probability:.1f}%</div>
        <div style="
            color: #1B3B5F;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            opacity: 0.7;
        ">Success Probability</div>
        <div style="
            color: {color};
            font-size: 1rem;
            font-weight: 600;
            margin-top: 8px;
        ">{status}</div>
    </div>
    """, unsafe_allow_html=True)


def scenario_card(name, allocation, median_ending, p10_ending, success_rate):
    """
    Display a scenario comparison card.
    
    Args:
        name: Scenario name
        allocation: Asset allocation string (e.g., "60/30/10")
        median_ending: Median ending value
        p10_ending: P10 ending value
        success_rate: Success rate percentage
    """
    # Color based on success rate
    if success_rate >= 85:
        border_color = "#10B981"
    elif success_rate >= 70:
        border_color = "#F59E0B"
    else:
        border_color = "#EF4444"
    
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.95);
        padding: 24px;
        border-radius: 12px;
        border-top: 4px solid {border_color};
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 16px;
    ">
        <div style="
            color: #1B3B5F;
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 12px;
        ">{name}</div>
        <div style="
            color: #6B7280;
            font-size: 0.875rem;
            margin-bottom: 16px;
        ">Allocation: <strong>{allocation}</strong> (Equity/FI/Cash)</div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
            <div>
                <div style="color: #6B7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Median</div>
                <div style="color: #1B3B5F; font-size: 1.25rem; font-weight: 700;">${median_ending:,.0f}</div>
            </div>
            <div>
                <div style="color: #6B7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Worst Case</div>
                <div style="color: #EF4444; font-size: 1.25rem; font-weight: 700;">${p10_ending:,.0f}</div>
            </div>
            <div>
                <div style="color: #6B7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">Success</div>
                <div style="color: {border_color}; font-size: 1.25rem; font-weight: 700;">{success_rate:.0f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def info_callout(message, type="info"):
    """
    Display an information callout box.
    
    Args:
        message: Message text
        type: "info", "success", "warning", or "error"
    """
    config = {
        "info": {"color": "#3B82F6", "bg": "#EFF6FF", "icon": "ℹ️"},
        "success": {"color": "#10B981", "bg": "#F0FDF4", "icon": "✅"},
        "warning": {"color": "#F59E0B", "bg": "#FFFBEB", "icon": "⚠️"},
        "error": {"color": "#EF4444", "bg": "#FEF2F2", "icon": "🚨"}
    }
    
    settings = config.get(type, config["info"])
    
    st.markdown(f"""
    <div style="
        background: {settings['bg']};
        border-left: 4px solid {settings['color']};
        padding: 16px 20px;
        border-radius: 8px;
        margin: 16px 0;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 1.5rem;">{settings['icon']}</span>
            <span style="color: #1B3B5F; font-size: 1rem; line-height: 1.5;">{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ===========================================
# PRESET CONFIGURATIONS
# ===========================================

PRESET_CONFIGS = {
    "Conservative": {
        "name": "Conservative",
        "description": "Low-risk portfolio suitable for retirees or risk-averse investors",
        "equity_pct": 0.30,
        "fi_pct": 0.60,
        "cash_pct": 0.10,
        "equity_ret": 0.055,
        "fi_ret": 0.025,
        "equity_vol": 0.15,
        "fi_vol": 0.05,
        "icon": "🛡️"
    },
    "Moderate": {
        "name": "Moderate (Balanced)",
        "description": "Balanced portfolio with moderate risk and growth potential",
        "equity_pct": 0.60,
        "fi_pct": 0.35,
        "cash_pct": 0.05,
        "equity_ret": 0.065,
        "fi_ret": 0.025,
        "equity_vol": 0.17,
        "fi_vol": 0.05,
        "icon": "⚖️"
    },
    "Aggressive": {
        "name": "Aggressive (Growth)",
        "description": "High-risk portfolio for long time horizons and growth-focused investors",
        "equity_pct": 0.85,
        "fi_pct": 0.10,
        "cash_pct": 0.05,
        "equity_ret": 0.075,
        "fi_ret": 0.025,
        "equity_vol": 0.19,
        "fi_vol": 0.05,
        "icon": "🚀"
    }
}


def apply_preset(preset_name):
    """Apply a preset configuration to session state."""
    if preset_name in PRESET_CONFIGS:
        preset = PRESET_CONFIGS[preset_name]
        st.session_state.preset_equity_pct = preset["equity_pct"] * 100
        st.session_state.preset_fi_pct = preset["fi_pct"] * 100
        st.session_state.preset_cash_pct = preset["cash_pct"] * 100
        st.session_state.preset_equity_ret = preset["equity_ret"] * 100
        st.session_state.preset_fi_ret = preset["fi_ret"] * 100
        st.session_state.preset_equity_vol = preset["equity_vol"] * 100
        st.session_state.preset_fi_vol = preset["fi_vol"] * 100
        st.session_state.preset_applied = preset_name
        st.success(f"✅ {preset['icon']} **{preset_name} preset** applied successfully!")


# ===========================================
# INPUT VALIDATION FRAMEWORK
# ===========================================

def validate_inputs(inputs, starting_portfolio=None):
    """
    Validate user inputs and return list of errors/warnings.
    
    Returns:
        tuple: (is_valid, errors, warnings)
        - is_valid: bool indicating if inputs are valid enough to run simulation
        - errors: list of critical error messages
        - warnings: list of warning messages
    """
    errors = []
    warnings = []
    
    # Allocation validation
    total_allocation = inputs.equity_pct + inputs.fi_pct + inputs.cash_pct
    if abs(total_allocation - 1.0) > 0.001:  # Allow small floating point errors
        errors.append(f"Portfolio allocation must sum to 100%. Current total: {total_allocation*100:.1f}%")
    
    # Individual allocation constraints
    if inputs.equity_pct < 0 or inputs.equity_pct > 1:
        errors.append(f"Equity allocation must be between 0% and 100%. Current: {inputs.equity_pct*100:.1f}%")
    if inputs.fi_pct < 0 or inputs.fi_pct > 1:
        errors.append(f"Fixed Income allocation must be between 0% and 100%. Current: {inputs.fi_pct*100:.1f}%")
    if inputs.cash_pct < 0 or inputs.cash_pct > 1:
        errors.append(f"Cash allocation must be between 0% and 100%. Current: {inputs.cash_pct*100:.1f}%")
    
    # Return constraints
    if inputs.equity_return_annual < -0.5 or inputs.equity_return_annual > 0.5:
        warnings.append(f"Equity return of {inputs.equity_return_annual*100:.1f}% seems unusual. Typical range: -10% to 20%")
    if inputs.fi_return_annual < -0.2 or inputs.fi_return_annual > 0.2:
        warnings.append(f"Fixed Income return of {inputs.fi_return_annual*100:.1f}% seems unusual. Typical range: -5% to 10%")
    if inputs.cash_return_annual < 0 or inputs.cash_return_annual > 0.1:
        warnings.append(f"Cash return of {inputs.cash_return_annual*100:.1f}% seems unusual. Typical range: 0% to 5%")
    
    # Volatility constraints
    if inputs.equity_vol_annual <= 0 or inputs.equity_vol_annual > 1:
        errors.append(f"Equity volatility must be positive and ≤100%. Current: {inputs.equity_vol_annual*100:.1f}%")
    if inputs.fi_vol_annual <= 0 or inputs.fi_vol_annual > 1:
        errors.append(f"Fixed Income volatility must be positive and ≤100%. Current: {inputs.fi_vol_annual*100:.1f}%")
    
    # Volatility warnings
    if inputs.equity_vol_annual < 0.05:
        warnings.append(f"Equity volatility of {inputs.equity_vol_annual*100:.1f}% is very low. Typical range: 15-25%")
    if inputs.equity_vol_annual > 0.40:
        warnings.append(f"Equity volatility of {inputs.equity_vol_annual*100:.1f}% is very high. Typical range: 15-25%")
    
    # Portfolio size
    if starting_portfolio and starting_portfolio <= 0:
        errors.append("Starting portfolio must be positive")
    
    # Spending validation
    if starting_portfolio and inputs.monthly_spending < 0:
        annual_spending = abs(inputs.monthly_spending) * 12
        withdrawal_rate = annual_spending / starting_portfolio
        
        if withdrawal_rate > 0.10:
            errors.append(f"Withdrawal rate of {withdrawal_rate*100:.1f}% is extremely high. Consider reducing spending.")
        elif withdrawal_rate > 0.06:
            warnings.append(f"Withdrawal rate of {withdrawal_rate*100:.1f}% is high. Historical data suggests rates >6% are risky.")
        elif withdrawal_rate > 0.045:
            warnings.append(f"Withdrawal rate of {withdrawal_rate*100:.1f}% is above the traditional 4.5% guideline.")
    
    # Age validation
    if inputs.current_age < 0 or inputs.current_age > 120:
        errors.append(f"Current age must be between 0 and 120. Current: {inputs.current_age}")
    
    if inputs.years_to_model <= 0:
        errors.append("Time horizon must be positive")
    if inputs.years_to_model > 100:
        warnings.append(f"Time horizon of {inputs.years_to_model} years is very long. Consider if this is appropriate.")
    
    # Simulation parameters
    if inputs.n_scenarios < 100:
        warnings.append(f"Only {inputs.n_scenarios} simulations. Consider using at least 1,000 for more reliable results.")
    if inputs.n_scenarios > 10000:
        warnings.append(f"{inputs.n_scenarios} simulations may be slow. Consider using 5,000 or fewer.")
    
    # Inflation
    if inputs.inflation_annual < 0 or inputs.inflation_annual > 0.20:
        warnings.append(f"Inflation rate of {inputs.inflation_annual*100:.1f}% seems unusual. Typical range: 2-4%")
    
    is_valid = len(errors) == 0
    
    return is_valid, errors, warnings


def display_validation_results(is_valid, errors, warnings):
    """Display validation results with appropriate styling."""
    if errors:
        st.error("**❌ Critical Errors - Cannot Run Simulation**")
        for error in errors:
            st.markdown(f"- {error}")
    
    if warnings:
        st.warning("**⚠️ Warnings - Review Before Running**")
        for warning in warnings:
            st.markdown(f"- {warning}")
    
    if is_valid and not warnings:
        st.success("**✅ All inputs valid - Ready to run simulation**")


# ===========================================
# SCENARIO COMPARISON OVERLAYS
# ===========================================

def create_scenario_overlay_chart(scenario_results, selected_scenarios=None):
    """
    Create an overlay chart comparing multiple scenarios on the same visualization.
    
    Args:
        scenario_results: Dict with scenario names as keys and dicts containing 'stats' DataFrames
        selected_scenarios: List of scenario names to display (None = all)
    
    Returns:
        Altair chart with overlaid scenarios
    """
    if selected_scenarios is None:
        selected_scenarios = list(scenario_results.keys())
    
    # Combine data from selected scenarios
    combined_data = []
    
    for scenario_name in selected_scenarios:
        if scenario_name not in scenario_results:
            continue
            
        stats_df = scenario_results[scenario_name]["stats"].copy()
        stats_df["Scenario"] = scenario_name
        combined_data.append(stats_df)
    
    if not combined_data:
        return None
    
    overlay_df = pd.concat(combined_data, ignore_index=True)
    overlay_df["Year"] = overlay_df["Month"] / 12
    
    # Color scheme for different scenarios
    scenario_colors = {
        "Base Case": "#1B3B5F",           # Salem Navy
        "Current Allocation": "#1B3B5F",   # Salem Navy
        "Conservative": "#10B981",         # Green
        "Moderate": "#C4A053",             # Salem Gold
        "Aggressive": "#EF4444",           # Red
        "Market Downturn": "#DC2626",      # Dark Red
        "High Inflation": "#F59E0B",       # Amber
        "Spending Shock": "#8B5CF6",       # Purple
    }
    
    # Create base chart
    base = alt.Chart(overlay_df).encode(
        x=alt.X("Year:Q", title="Years into Retirement"),
    )
    
    # P10-P90 bands for each scenario
    bands = base.mark_area(opacity=0.15).encode(
        y=alt.Y("P10:Q", title="Portfolio Value ($)", scale=alt.Scale(zero=False)),
        y2="P90:Q",
        color=alt.Color(
            "Scenario:N",
            scale=alt.Scale(
                domain=list(scenario_colors.keys()),
                range=list(scenario_colors.values())
            ),
            legend=alt.Legend(title="Scenario", orient="top")
        ),
        tooltip=[
            alt.Tooltip("Scenario:N", title="Scenario"),
            alt.Tooltip("Year:Q", title="Year", format=".1f"),
            alt.Tooltip("P10:Q", title="P10", format="$,.0f"),
            alt.Tooltip("Median:Q", title="Median", format="$,.0f"),
            alt.Tooltip("P90:Q", title="P90", format="$,.0f"),
        ]
    )
    
    # Median lines for each scenario
    median_lines = base.mark_line(strokeWidth=2.5).encode(
        y="Median:Q",
        color=alt.Color(
            "Scenario:N",
            scale=alt.Scale(
                domain=list(scenario_colors.keys()),
                range=list(scenario_colors.values())
            ),
            legend=None
        ),
        strokeDash=alt.StrokeDash(
            "Scenario:N",
            scale=alt.Scale(
                domain=list(scenario_colors.keys()),
                range=[[1, 0]] * len(scenario_colors)  # Solid lines for all
            ),
            legend=None
        )
    )
    
    # Combine layers
    chart = (bands + median_lines).properties(
        width=800,
        height=450,
        title="Scenario Comparison: Portfolio Projections"
    ).interactive()
    
    return chart


def create_scenario_comparison_table(scenario_results, years_to_model):
    """
    Create a comparison table showing key metrics across scenarios.
    
    Args:
        scenario_results: Dict with scenario names as keys and dicts containing 'stats' and 'metrics'
        years_to_model: Number of years in the simulation
    
    Returns:
        pandas DataFrame with comparison metrics
    """
    comparison_data = []
    last_month = years_to_model * 12
    
    for scenario_name, data in scenario_results.items():
        stats_df = data["stats"]
        ending_row = stats_df[stats_df["Month"] == last_month].iloc[0] if not stats_df[stats_df["Month"] == last_month].empty else None
        
        if ending_row is not None:
            # Calculate success probability if we have paths data
            success_prob = data.get("metrics", {}).get("success_probability", 0)
            
            comparison_data.append({
                "Scenario": scenario_name,
                "Success Probability": success_prob,
                "P10 Ending": ending_row["P10"],
                "Median Ending": ending_row["Median"],
                "P90 Ending": ending_row["P90"],
                "Allocation": data.get("allocation", "N/A")
            })
    
    return pd.DataFrame(comparison_data)


# ===========================================
# TAB RENDERING FUNCTIONS
# ===========================================

def render_overview_tab():
    """Overview Tab: Dashboard showing key metrics, risk indicators, and quick actions."""
    st.markdown("### 📊 Portfolio Health Dashboard")
    st.caption("Institutional-grade overview of your financial plan")
    
    # Check if simulation has been run
    simulation_run = st.session_state.get('simulation_run', False)
    
    if not simulation_run:
        # ===== PHASE 3: ADVISOR WORKFLOW - Onboarding Guide =====
        st.info("👋 Welcome! Run a Monte Carlo simulation in the **Portfolio Analysis** tab to see your personalized dashboard.")
        
        st.markdown("---")
        st.markdown("#### 🚀 Quick Start Guide")
        st.caption("Follow these steps to create an institutional-grade financial plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Step 1: Client & Assumptions**
            - Enter client details and demographics
            - Apply an institutional scenario template
            - Configure portfolio allocations
            - Review validation warnings
            
            **Step 2: Portfolio Analysis**
            - Run Monte Carlo simulation (10,000 paths)
            - Review success probability and outcomes
            - Analyze distribution of ending values
            """)
        
        with col2:
            st.markdown("""
            **Step 3: Scenario Analysis**
            - Run stress test scenarios
            - Compare allocation strategies
            - View scenario overlays
            - Assess downside risk
            
            **Step 4: Reports & Export**
            - Generate PDF reports with branding
            - Export interactive HTML
            - Download Excel data tables
            """)
        
        st.markdown("---")
        st.markdown("#### 💡 Institutional Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            **🎯 Scenario Templates**
            - Base Case
            - Conservative
            - Market Stress
            - Longevity Risk
            - Inflation Shock
            - Recession Path
            - Favorable Markets
            """)
        
        with col2:
            st.info("""
            **✅ Validation System**
            - Return assumptions
            - Volatility checks
            - Allocation assessment
            - Spending sustainability
            - Real return analysis
            """)
        
        with col3:
            st.info("""
            **📊 Advanced Analytics**
            - Required capital analysis
            - Glidepath assessment
            - Success probability gauges
            - Distribution histograms
            - Scenario differentials
            """)
        
        return
    
    # Get simulation data
    metrics = st.session_state.get('metrics')
    stats_df = st.session_state.get('stats_df')
    paths_df = st.session_state.get('paths_df')
    inputs = st.session_state.get('inputs')
    client_info = st.session_state.get('client_info')
    
    if not metrics or stats_df is None:
        st.warning("No simulation data available. Please run a simulation first.")
        return
    
    # ===== PHASE 3: ADVISOR WORKFLOW - Executive Summary =====
    # Client Header
    if client_info and client_info.client_name:
        st.markdown(f"#### Client: {client_info.client_name}")
        if client_info.client_notes:
            st.caption(client_info.client_notes)
        st.markdown("---")
    
    # Success Probability - Large Display with Institutional Gauge
    success_prob = metrics.get('success_probability', 0)
    
    st.markdown("### 🎯 Plan Success Probability")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        gauge = create_success_gauge(success_prob)
        st.altair_chart(gauge, use_container_width=True)
    
    # Risk Cards - 4 Key Metrics
    st.markdown("---")
    st.markdown("### Key Risk Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        shortfall_risk = 100 - success_prob
        risk_color = "🔴" if shortfall_risk > 30 else "🟡" if shortfall_risk > 15 else "🟢"
        st.metric(
            "Shortfall Risk",
            f"{shortfall_risk:.0f}%",
            delta=f"{risk_color} {'High' if shortfall_risk > 30 else 'Moderate' if shortfall_risk > 15 else 'Low'} Risk"
        )
    
    with col2:
        p10_value = metrics.get('ending_p10', 0)
        st.metric(
            "Worst Case (P10)",
            f"${p10_value:,.0f}",
            delta=f"10th percentile outcome"
        )
    
    with col3:
        p90_value = metrics.get('ending_p90', 0)
        st.metric(
            "Best Case (P90)",
            f"${p90_value:,.0f}",
            delta=f"90th percentile outcome"
        )
    
    with col4:
        median_vs_start = ((metrics['ending_median'] / inputs.starting_portfolio) - 1) * 100
        st.metric(
            "Expected Growth",
            f"{median_vs_start:+.0f}%",
            delta=f"${metrics['ending_median']:,.0f}"
        )
    
    # Recent Analysis Summary
    st.markdown("---")
    st.markdown("### Analysis Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Portfolio Configuration")
        st.markdown(f"- **Starting Value**: ${inputs.starting_portfolio:,.0f}")
        st.markdown(f"- **Allocation**: {inputs.equity_pct*100:.0f}% Equity / {inputs.fi_pct*100:.0f}% FI / {inputs.cash_pct*100:.0f}% Cash")
        st.markdown(f"- **Monthly Spending**: ${inputs.monthly_spending:,.0f}")
        withdrawal_rate = (inputs.monthly_spending * 12 / inputs.starting_portfolio) * 100
        st.markdown(f"- **Initial Withdrawal Rate**: {withdrawal_rate:.2f}%")
    
    with col2:
        st.markdown("#### Simulation Parameters")
        st.markdown(f"- **Time Horizon**: {inputs.years_to_model} years")
        st.markdown(f"- **Current Age**: {inputs.current_age}")
        st.markdown(f"- **Simulations**: {inputs.n_scenarios:,} paths")
        st.markdown(f"- **Inflation**: {inputs.inflation_annual:.2%}")


def render_client_tab():
    """Client & Assumptions Tab: All input parameters with organized collapsible sections."""
    st.markdown("### Client Information & Portfolio Assumptions")
    st.caption("Configure client details and simulation parameters. Click sections to expand/collapse.")
    
    # ===== PHASE 2: SCENARIO INTELLIGENCE - Institutional Scenario Templates =====
    st.markdown("---")
    st.markdown("#### 🎯 Institutional Scenario Templates")
    st.caption("Apply pre-configured scenarios based on institutional best practices")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        scenario_options = list(INSTITUTIONAL_SCENARIOS.keys())
        selected_template = st.selectbox(
            "Select Scenario Template",
            options=scenario_options,
            format_func=lambda x: f"{INSTITUTIONAL_SCENARIOS[x].icon} {INSTITUTIONAL_SCENARIOS[x].name}",
            key="scenario_template_selector"
        )
    
    with col2:
        if selected_template:
            template = INSTITUTIONAL_SCENARIOS[selected_template]
            st.info(f"📝 {template.description}")
    
    with col3:
        if st.button("Apply Template", type="primary", use_container_width=True):
            template = INSTITUTIONAL_SCENARIOS[selected_template]
            # Store template values in session state for application
            st.session_state.template_equity_return = template.equity_return
            st.session_state.template_fi_return = template.fi_return
            st.session_state.template_cash_return = template.cash_return
            st.session_state.template_equity_vol = template.equity_vol
            st.session_state.template_fi_vol = template.fi_vol
            st.session_state.template_cash_vol = template.cash_vol
            st.session_state.template_inflation = template.inflation
            st.session_state.template_applied = template.name
            st.success(f"✅ Applied {template.name} scenario")
            st.rerun()
    
    # Preset Configurations Section
    st.markdown("---")
    st.markdown("#### 🎯 Quick Start: Preset Configurations")
    st.caption("Apply a preset configuration to quickly set up portfolio assumptions")
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        if st.button("🛡️ Conservative", use_container_width=True, help="30% Equity / 60% FI / 10% Cash"):
            apply_preset("Conservative")
    
    with col2:
        if st.button("⚖️ Moderate", use_container_width=True, help="60% Equity / 35% FI / 5% Cash"):
            apply_preset("Moderate")
    
    with col3:
        if st.button("🚀 Aggressive", use_container_width=True, help="85% Equity / 10% FI / 5% Cash"):
            apply_preset("Aggressive")
    
    with col4:
        if st.session_state.get('template_applied'):
            st.success(f"✓ {st.session_state.get('template_applied')}")
        elif st.session_state.get('preset_applied'):
            st.info(f"✓ {st.session_state.get('preset_applied')}")
    
    st.markdown("---")
    
    # Client Information Section
    with st.expander("👤 Client Information", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            client_name = st.text_input(
                "Client Name",
                value="",
                key="tab_client_name",
                placeholder="John & Jane Doe"
            )
        
        with col2:
            advisor_name = st.text_input(
                "Advisor Name",
                value="",
                key="tab_advisor_name",
                placeholder="Advisor Name"
            )
        
        with col3:
            report_date = st.date_input(
                "Report Date",
                value=date.today(),
                key="tab_report_date"
            )
        
        client_notes = st.text_area(
            "Client Notes (optional)",
            value="",
            key="tab_client_notes",
            placeholder="Additional notes about the client or scenario..."
        )
    
    client_info = ClientInfo(
        client_name=client_name,
        report_date=report_date,
        advisor_name=advisor_name,
        client_notes=client_notes if 'tab_client_notes' in st.session_state else ""
    )
    
    # Store client_info early
    st.session_state.client_info = client_info
    
    # Portfolio & Time Horizon Section
    with st.expander("📊 Portfolio & Time Horizon", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            current_age = st.number_input(
                "Current Age",
                min_value=0,
                max_value=120,
                value=48,
                step=1,
                key="tab_current_age",
            )

        with col2:
            horizon_age = st.number_input(
                "Plan Horizon Age",
                min_value=current_age,
                max_value=120,
                value=78,
                step=1,
                key="tab_horizon_age",
            )

        with col3:
            starting_portfolio = _dollar_input(
                "Starting Portfolio Value",
                default_value=4_500_000.0,
                key="tab_starting_portfolio",
            )

        years_to_model = horizon_age - current_age
        
        st.info(f"📅 Planning Horizon: **{years_to_model} years** (Age {current_age} to {horizon_age})")
    
    # Call the rest of main_page_inputs but capture the other sections
    # For now, let's just call it and reorganize the output
    _, inputs, stress_scenarios, financial_goals = main_page_inputs()
    
    # Store in session state
    st.session_state.current_inputs = inputs
    st.session_state.current_stress_scenarios = stress_scenarios
    st.session_state.current_financial_goals = financial_goals
    
    # ===== PHASE 3: ADVISOR WORKFLOW - Required Capital Calculator =====
    st.markdown("---")
    st.markdown("### 💰 Required Retirement Capital Analysis")
    st.caption("Multiple methodologies for assessing retirement capital needs")
    
    annual_spending = abs(inputs.monthly_spending) * 12
    capital_analysis = calculate_required_capital(annual_spending)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Simple (4% Rule)",
            f"${capital_analysis['simple_estimate']:,.0f}",
            help="Traditional 4% withdrawal rate"
        )
    
    with col2:
        st.metric(
            "Conservative (+25%)",
            f"${capital_analysis['conservative_estimate']:,.0f}",
            help="25% safety margin"
        )
    
    with col3:
        st.metric(
            "Dynamic Range",
            f"${capital_analysis['dynamic_range_low']:,.0f}",
            delta=f"to ${capital_analysis['dynamic_range_high']:,.0f}",
            help="4-5% withdrawal range"
        )
    
    with col4:
        current_vs_recommended = ((inputs.starting_portfolio / capital_analysis['recommended']) - 1) * 100
        delta_color = "normal" if current_vs_recommended >= 0 else "inverse"
        st.metric(
            "Recommended",
            f"${capital_analysis['recommended']:,.0f}",
            delta=f"{current_vs_recommended:+.0f}%",
            delta_color=delta_color,
            help="Recommended capital requirement"
        )
    
    # ===== PHASE 3: ADVISOR WORKFLOW - Glidepath Assessment =====
    glidepath_assessment = assess_glidepath(inputs.equity_pct, current_age, years_to_model)
    
    st.markdown("---")
    st.markdown("### 📊 Asset Allocation Assessment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(
            f"**Current Allocation**: {inputs.equity_pct*100:.0f}% Equity / {inputs.fi_pct*100:.0f}% Fixed Income / {inputs.cash_pct*100:.0f}% Cash\\n\\n"
            f"**Assessment**: {glidepath_assessment['position']}\\n\\n"
            f"**Age-Based Guidelines**:\\n"
            f"- Standard (100-age): {glidepath_assessment['100_minus_age']*100:.0f}% equity\\n"
            f"- Moderate (110-age): {glidepath_assessment['110_minus_age']*100:.0f}% equity\\n"
            f"- Aggressive (120-age): {glidepath_assessment['120_minus_age']*100:.0f}% equity"
        )
    
    with col2:
        # Position indicator
        position = glidepath_assessment['position']
        if position in ["Very Aggressive", "Aggressive"]:
            st.warning(f"⚠️ {position}")
        elif position in ["Very Conservative", "Conservative"]:
            st.info(f"🛡️ {position}")
        else:
            st.success(f"✅ {position}")
    
    # ===== PHASE 2: SCENARIO INTELLIGENCE - Assumption Validation =====
    st.markdown("---")
    st.markdown("### ✅ Assumption Validation & Risk Assessment")
    st.caption("Comprehensive validation of all assumptions against institutional standards")
    
    # Run comprehensive validation
    validation_warnings = AssumptionValidator.validate_all(
        inputs.equity_return_annual,
        inputs.fi_return_annual,
        inputs.cash_return_annual,
        inputs.equity_vol_annual,
        inputs.fi_vol_annual,
        inputs.cash_vol_annual,
        inputs.inflation_annual,
        inputs.equity_pct,
        inputs.fi_pct,
        inputs.cash_pct,
        inputs.monthly_spending,
        inputs.starting_portfolio,
        inputs.years_to_model
    )
    
    # Display warnings by category
    total_warnings = sum(len(w) for w in validation_warnings.values())
    
    if total_warnings == 0:
        st.success("✅ All assumptions are within reasonable ranges based on institutional standards")
    else:
        st.warning(f"⚠️ {total_warnings} validation warning(s) detected - please review below")
        
        for category, warning_list in validation_warnings.items():
            if warning_list:
                with st.expander(f"⚠️ {category.replace('_', ' ').title()} ({len(warning_list)})", expanded=True):
                    for warning in warning_list:
                        st.warning(warning)
    
    # Validate inputs
    st.markdown("---")
    st.markdown("### 🔍 Input Validation")
    
    is_valid, errors, warnings_old = validate_inputs(inputs, starting_portfolio)
    st.session_state.inputs_valid = is_valid
    
    display_validation_results(is_valid, errors, warnings_old)
    
    # Show quick summary
    st.markdown("---")
    st.markdown("### 📋 Configuration Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        portfolio_return, portfolio_vol = compute_portfolio_return_and_vol(inputs)
        st.metric("Expected Return", f"{portfolio_return:.2%}", help="Annual expected portfolio return")
    
    with col2:
        st.metric("Portfolio Volatility", f"{portfolio_vol:.2%}", help="Annual standard deviation")
    
    with col3:
        withdrawal_rate = (inputs.monthly_spending * 12 / inputs.starting_portfolio) * 100
        risk_color = "🔴" if withdrawal_rate > 5 else "🟡" if withdrawal_rate > 4 else "🟢"
        st.metric("Withdrawal Rate", f"{withdrawal_rate:.2f}%", delta=risk_color)
    
    with col4:
        sharpe = (portfolio_return - inputs.cash_return_annual) / portfolio_vol if portfolio_vol > 0 else 0
        st.metric("Sharpe Ratio", f"{sharpe:.2f}", help="Risk-adjusted return measure")


def render_portfolio_tab():
    """Portfolio Analysis Tab: Run simulations and view detailed results."""
    st.markdown("### Monte Carlo Simulation & Results")
    
    # Get current inputs from session state or use defaults
    inputs = st.session_state.get('current_inputs')
    financial_goals = st.session_state.get('current_financial_goals', [])
    inputs_valid = st.session_state.get('inputs_valid', False)
    
    if not inputs:
        st.warning("⚠️ Please configure assumptions in the **Client & Assumptions** tab first.")
        return
    
    # Run Simulation Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        button_disabled = not inputs_valid
        button_help = "Configure valid inputs in Client & Assumptions tab first" if button_disabled else "Run Monte Carlo simulation with current inputs"
        
        if st.button(
            "Run Monte Carlo Simulation", 
            type="primary", 
            key="run_simulation", 
            use_container_width=True,
            disabled=button_disabled,
            help=button_help
        ):
            with st.spinner("Running simulation..."):
                # Generate cache key for performance
                cache_key = generate_monte_carlo_cache_key(inputs)
                paths_df, stats_df, metrics = run_monte_carlo_cached(cache_key, inputs)
                # Store results in session state
                st.session_state.paths_df = paths_df
                st.session_state.stats_df = stats_df
                st.session_state.metrics = metrics
                st.session_state.inputs = inputs
                st.session_state.financial_goals = financial_goals
                st.session_state.simulation_run = True
                st.success("✅ Simulation completed successfully!")
                st.rerun()
    
    # Show validation reminder if inputs invalid
    if not inputs_valid:
        st.error("❌ **Cannot run simulation**: Please fix validation errors in the **Client & Assumptions** tab.")
    
    # Get data from session state if simulation has been run
    paths_df = st.session_state.get('paths_df')
    stats_df = st.session_state.get('stats_df')
    metrics = st.session_state.get('metrics')
    simulation_run = st.session_state.get('simulation_run', False)
    
    if not simulation_run:
        st.info("Click the button above to run your first simulation.")
        return
    
    # Display Results
    st.markdown("---")
    st.markdown("### Key Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Median Ending Portfolio", f"${metrics['ending_median']:,.0f}")
    with col2:
        st.metric("P10 (Worst Case)", f"${metrics['ending_p10']:,.0f}")
    with col3:
        st.metric("P90 (Best Case)", f"${metrics['ending_p90']:,.0f}")
    
    # Success Gauge
    success_prob = metrics.get('success_probability', 0)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        gauge = create_success_gauge(success_prob)
        st.altair_chart(gauge, use_container_width=True)
    
    # Executive Dashboard
    st.markdown("---")
    st.markdown("### Executive Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        shortfall_risk = 100 - success_prob
        risk_color = "🔴" if shortfall_risk > 30 else "🟡" if shortfall_risk > 15 else "🟢"
        st.metric(
            "Shortfall Risk",
            f"{shortfall_risk:.0f}%",
            delta=f"{risk_color} {'High' if shortfall_risk > 30 else 'Moderate' if shortfall_risk > 15 else 'Low'} Risk"
        )
    
    with col2:
        st.metric(
            "Worst Case (P10)",
            f"${metrics['ending_p10']:,.0f}",
            delta=f"10th percentile"
        )
    
    with col3:
        st.metric(
            "Best Case (P90)",
            f"${metrics['ending_p90']:,.0f}",
            delta=f"90th percentile"
        )
    
    with col4:
        median_vs_start = ((metrics['ending_median'] / inputs.starting_portfolio) - 1) * 100
        st.metric(
            "Expected Growth",
            f"{median_vs_start:+.0f}%",
            delta=f"${metrics['ending_median']:,.0f}"
        )
    
    # Financial Goals Analysis
    if financial_goals:
        st.markdown("---")
        st.subheader("Financial Goal Analysis")
        goal_results = calculate_goal_probabilities(paths_df, financial_goals, inputs.current_age)
        
        if not goal_results.empty:
            st.caption("Probability of achieving each financial goal based on Monte Carlo simulation")
            
            # Visual goal confidence chart
            goal_chart = create_goal_confidence_chart(goal_results)
            if goal_chart:
                st.altair_chart(goal_chart, use_container_width=True)
            
            # Display as metrics
            cols = st.columns(min(len(goal_results), 3))
            for idx, (_, row) in enumerate(goal_results.iterrows()):
                with cols[idx % 3]:
                    st.metric(
                        row["Goal"],
                        f"{row['Probability of Success']:.1f}%",
                        delta=f"${row['Target Amount']:,.0f} by age {int(row['Target Age'])}"
                    )
            
            # Display detailed table
            st.dataframe(
                goal_results.style.format({
                    "Target Amount": "${:,.0f}",
                    "Target Age": "{:.0f}",
                    "Probability of Success": "{:.1f}%"
                }),
                use_container_width=True
            )
            
            # Store goal results for later use
            st.session_state.goal_results = goal_results
    
    # Visualization Charts
    st.markdown("---")
    st.subheader("📊 Institutional-Grade Projections")
    
    # ===== PHASE 1: INSTITUTIONAL CHARTS - Enhanced Fan Chart =====
    st.markdown("##### Portfolio Value Projections with Confidence Intervals")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        show_annotations = st.checkbox("Show Annotations", value=True, key="fan_annotations")
        highlight_median = st.checkbox("Highlight Median", value=True, key="fan_median")
    
    with col1:
        # Use institutional fan chart instead of legacy chart
        institutional_chart = create_institutional_fan_chart(
            stats_df, 
            title="Portfolio Value Projections (Institutional)",
            show_annotations=show_annotations,
            highlight_median=highlight_median
        )
        st.altair_chart(institutional_chart, use_container_width=True)
    
    # ===== PHASE 1: INSTITUTIONAL CHARTS - Distribution Histogram =====
    st.markdown("---")
    st.markdown("##### Distribution of Ending Portfolio Values")
    
    # Get ending values from paths
    ending_values = paths_df.iloc[-1].values
    distribution_hist = create_distribution_histogram(
        ending_values,
        title="Final Portfolio Value Distribution"
    )
    st.altair_chart(distribution_hist, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Portfolio Depletion Risk Over Time")
    st.caption(
        "This chart shows the probability that your portfolio will be depleted (reach $0) at each point in time. "
        "Lower percentages indicate lower risk."
    )
    depletion_chart = depletion_probability_chart(paths_df, "Base Case: Probability of Portfolio Depletion")
    st.altair_chart(depletion_chart, use_container_width=True)
    
    # ===== AI-POWERED INSIGHTS SECTION =====
    st.markdown("---")
    st.subheader("🤖 AI-Powered Analysis & Insights")
    
    with st.expander("**View AI Analysis**", expanded=False):
        # Check if AI analysis already exists for this scenario
        if 'ai_analysis' not in st.session_state or st.button("Generate AI Analysis", key="gen_ai_analysis"):
            with st.spinner("Analyzing scenario with AI..."):
                # Run AI analysis
                ai_engine = st.session_state.ai_engine
                
                # Prepare inputs for AI
                ai_inputs = {
                    'starting_portfolio': inputs.starting_portfolio,
                    'current_age': inputs.current_age,
                    'retirement_age': inputs.retirement_age,
                    'life_expectancy': inputs.life_expectancy,
                    'monthly_spending': inputs.monthly_spending,
                    'equity_pct': inputs.equity_pct,
                    'equity_return': inputs.equity_return_annual,
                    'fi_return': inputs.fi_return_annual,
                    'inflation': inputs.inflation_annual,
                    'equity_vol': inputs.equity_vol_annual
                }
                
                # Run analysis
                analysis = ai_engine.analyze_scenario(
                    inputs=ai_inputs,
                    metrics=metrics,
                    stats_df=stats_df,
                    paths_df=paths_df,
                    scenario_id="base_case"
                )
                
                # Store in session state
                st.session_state.ai_analysis = analysis
                
                # Log to audit trail
                audit_system = st.session_state.audit_system
                audit_system.create_record(
                    user_id="advisor",
                    client_id=st.session_state.get('client_id'),
                    scenario_type="base",
                    inputs=ai_inputs,
                    outputs={'metrics': metrics},
                    ai_analysis=analysis.to_dict() if hasattr(analysis, 'to_dict') else None
                )
        
        analysis = st.session_state.get('ai_analysis')
        
        if analysis:
            # Display short summary prominently
            st.markdown("#### Executive Summary")
            st.info(analysis.short_summary)
            
            # Key Drivers
            st.markdown("#### Key Success Drivers")
            for driver in analysis.key_drivers[:3]:  # Top 3
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{driver.title}**")
                        st.caption(driver.summary)
                    with col2:
                        confidence_color = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(driver.confidence_level, "⚪")
                        st.metric("Confidence", f"{confidence_color} {driver.confidence_level.title()}")
                    
                    with st.expander("View Details"):
                        st.markdown(driver.detailed_explanation)
                    
                    st.markdown("---")
            
            # Risk Factors
            st.markdown("#### Key Risk Factors")
            for risk in analysis.risk_factors[:3]:  # Top 3
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{risk.title}**")
                        st.caption(risk.summary)
                    with col2:
                        confidence_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk.confidence_level, "⚪")
                        st.metric("Severity", f"{confidence_color} {risk.confidence_level.title()}")
                    
                    with st.expander("View Details"):
                        st.markdown(risk.detailed_explanation)
                    
                    st.markdown("---")
            
            # Sensitivity Analysis
            st.markdown("#### Parameter Sensitivity Analysis")
            st.caption("Impact of changing each parameter on success probability")
            
            sensitivity = analysis.sensitivity_analysis
            sens_data = []
            for param, data in sensitivity.items():
                sens_data.append({
                    'Parameter': param.replace('_', ' ').title(),
                    'Importance': data['importance'],
                    'Impact': f"{data.get('impact_pct', 0):.1f}%"
                })
            
            sens_df = pd.DataFrame(sens_data)
            sens_df = sens_df.sort_values('Importance', ascending=False)
            
            # Create sensitivity chart
            sens_chart = alt.Chart(sens_df).mark_bar().encode(
                x=alt.X('Importance:Q', title='Importance Score'),
                y=alt.Y('Parameter:N', sort='-x', title=''),
                color=alt.Color('Importance:Q', scale=alt.Scale(scheme='goldorange'), legend=None),
                tooltip=['Parameter', 'Importance', 'Impact']
            ).properties(height=300)
            
            st.altair_chart(sens_chart, use_container_width=True)
            
            # Recommendations
            st.markdown("#### AI Recommendations")
            for idx, rec in enumerate(analysis.recommendations, 1):
                st.markdown(f"{idx}. {rec}")
            
            # Full narrative viewer
            with st.expander("📄 View Full Detailed Analysis"):
                st.markdown(analysis.long_form_narrative)
            
            # Compliance disclosure
            st.caption("⚠️ This AI-generated analysis is for informational purposes only and should not be considered investment advice. "
                      "Results are based on assumptions and historical data. Past performance does not guarantee future results.")



def render_scenarios_tab():
    """Scenario Analysis Tab: Stress tests, allocation comparison, and sensitivity analysis."""
    st.markdown("### Scenario Analysis & Stress Testing")
    
    # Check if base simulation has been run
    inputs = st.session_state.get('inputs')
    paths_df = st.session_state.get('paths_df')
    stats_df = st.session_state.get('stats_df')
    simulation_run = st.session_state.get('simulation_run', False)
    
    if not simulation_run:
        st.warning("⚠️ Please run a simulation in the **Portfolio Analysis** tab first.")
        return
    
    # ===== AI-POWERED NATURAL LANGUAGE STRESS TEST BUILDER =====
    st.markdown("### 🤖 AI-Powered Stress Test Builder")
    st.caption("Describe a stress scenario in plain English and let AI build the test")
    
    with st.expander("**Natural Language Stress Test Builder**", expanded=False):
        st.markdown("Describe a market scenario in natural language and the AI will translate it into parameter overrides.")
        
        # Example templates
        st.markdown("#### Example Scenarios:")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📉 Severe Recession", key="nlp_recession"):
                st.session_state.nlp_stress_input = "severe recession with -30% equity returns and 35% volatility"
            if st.button("📊 Stagflation", key="nlp_stagflation"):
                st.session_state.nlp_stress_input = "stagflation with 6% inflation and flat equities for 5 years"
        
        with col2:
            if st.button("💥 Market Crash", key="nlp_crash"):
                st.session_state.nlp_stress_input = "sudden market crash with -40% equity decline and extreme volatility"
            if st.button("📈 Rising Rates", key="nlp_rates"):
                st.session_state.nlp_stress_input = "rising interest rates with 1% bond returns and increased equity volatility"
        
        # Natural language input
        nlp_input = st.text_area(
            "Describe your stress scenario:",
            value=st.session_state.get('nlp_stress_input', ''),
            height=100,
            placeholder="Example: prolonged inflation at 6% with flat equity markets and rising rates",
            key="nlp_stress_description"
        )
        
        if st.button("🔍 Build Stress Test from Description", type="primary"):
            if nlp_input:
                with st.spinner("Parsing stress scenario..."):
                    stress_builder = st.session_state.stress_builder
                    stress_scenario = stress_builder.parse_stress_description(nlp_input)
                    
                    # Display parsed scenario
                    st.success(f"✅ Created stress scenario: **{stress_scenario.name}**")
                    
                    st.markdown("**Scenario Details:**")
                    st.info(f"**Description:** {stress_scenario.description}\n\n"
                           f"**Rationale:** {stress_scenario.rationale}\n\n"
                           f"**Severity:** {stress_scenario.severity.title()}")
                    
                    st.markdown("**Parameter Overrides:**")
                    overrides_df = pd.DataFrame([
                        {"Parameter": k.replace('_', ' ').title(), 
                         "Override Value": f"{v*100:.1f}%" if 'return' in k or 'vol' in k or 'inflation' in k else v}
                        for k, v in stress_scenario.parameter_overrides.items()
                    ])
                    st.dataframe(overrides_df, use_container_width=True)
                    
                    # Store for running
                    st.session_state.nlp_stress_scenario = stress_scenario
                    
                    # Run the stress test automatically
                    if st.button("▶️ Run This Stress Test", key="run_nlp_stress"):
                        with st.spinner(f"Running {stress_scenario.name} scenario..."):
                            # Create modified inputs
                            modified_inputs = inputs
                            for param, value in stress_scenario.parameter_overrides.items():
                                if hasattr(modified_inputs, param):
                                    setattr(modified_inputs, param, value)
                            
                            # Run simulation
                            cache_key = generate_monte_carlo_cache_key(modified_inputs)
                            paths, stats, metrics_stress = run_monte_carlo_cached(cache_key, modified_inputs)
                            
                            # Store results
                            if 'nlp_stress_results' not in st.session_state:
                                st.session_state.nlp_stress_results = {}
                            
                            st.session_state.nlp_stress_results[stress_scenario.name] = {
                                'paths': paths,
                                'stats': stats,
                                'metrics': metrics_stress,
                                'scenario': stress_scenario
                            }
                            
                            st.success(f"✅ Completed {stress_scenario.name} stress test!")
                            st.rerun()
        
        # Display NLP stress test results
        nlp_results = st.session_state.get('nlp_stress_results', {})
        if nlp_results:
            st.markdown("---")
            st.markdown("#### NLP Stress Test Results")
            
            for scenario_name, result in nlp_results.items():
                with st.expander(f"📊 {scenario_name}", expanded=True):
                    metrics_stress = result['metrics']
                    scenario_obj = result['scenario']
                    
                    # Comparison metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    base_success = st.session_state.metrics.get('success_probability', 0)
                    stress_success = metrics_stress.get('success_probability', 0)
                    
                    with col1:
                        st.metric(
                            "Success Probability",
                            f"{stress_success:.0%}",
                            delta=f"{(stress_success - base_success)*100:.1f}%",
                            delta_color="normal"
                        )
                    
                    with col2:
                        st.metric(
                            "Median Ending",
                            f"${metrics_stress.get('ending_median', 0):,.0f}",
                            delta=f"${metrics_stress.get('ending_median', 0) - st.session_state.metrics.get('ending_median', 0):,.0f}",
                            delta_color="normal"
                        )
                    
                    with col3:
                        st.metric(
                            "P10 (Worst Case)",
                            f"${metrics_stress.get('ending_p10', 0):,.0f}",
                            delta=f"${metrics_stress.get('ending_p10', 0) - st.session_state.metrics.get('ending_p10', 0):,.0f}",
                            delta_color="normal"
                        )
                    
                    with col4:
                        severity_color = {
                            'mild': '🟢',
                            'moderate': '🟡',
                            'severe': '🟠',
                            'extreme': '🔴'
                        }.get(scenario_obj.severity, '⚪')
                        st.metric(
                            "Severity",
                            f"{severity_color} {scenario_obj.severity.title()}",
                            delta="AI Assessment"
                        )
                    
                    # Charts
                    stats_stress = result['stats']
                    fan_chart = create_institutional_fan_chart(
                        stats_stress,
                        title=f"{scenario_name} Projection"
                    )
                    st.altair_chart(fan_chart, use_container_width=True)
    
    # Standard Stress Tests Section
    st.markdown("---")
    st.markdown("### Predefined Stress Test Scenarios")
    st.caption("Test your portfolio against market downturns, high inflation, and spending shocks")
    
    # Display stress test inputs
    stress_scenarios = stress_test_inputs()
    
    if st.button("Run Stress Test Simulations", type="primary", key="run_stress_tests"):
        with st.spinner("Running stress test simulations..."):
            stress_results = run_stress_tests(inputs, stress_scenarios)
            # Store in session state
            st.session_state.stress_results = stress_results
    
    # Get results from session state if available
    stress_results = st.session_state.get('stress_results', {})
    
    if stress_results:
        st.caption(
            "Each stress scenario adjusts returns / spending / inflation and runs a full Monte Carlo simulation "
            "showing the range of potential outcomes."
        )
        
        # ===== PHASE 1: INSTITUTIONAL CHARTS - Scenario Comparison Overlay =====
        st.markdown("---")
        st.markdown("##### 📊 Institutional Scenario Comparison")
        
        # Prepare data for scenario comparison chart
        scenario_data = []
        for scenario_name, data in stress_results.items():
            stats = data["stats"]
            for _, row in stats.iterrows():
                scenario_data.append({
                    "scenario": scenario_name,
                    "year": row["Month"] / 12.0,
                    "median": row["Median"],
                    "p10": row["P10"],
                    "p90": row["P90"]
                })
        
        if scenario_data:
            scenario_comparison = create_scenario_comparison_chart(
                scenario_data,
                metric="median",
                title="Scenario Comparison: Median Portfolio Values"
            )
            st.altair_chart(scenario_comparison, use_container_width=True)
        
        # Legacy charts for each scenario
        st.markdown("---")
        st.markdown("##### Individual Scenario Details")
        charts = stress_test_charts(stress_results)
        for scenario_name, fan_chart_obj, depletion_chart_obj in charts:
            st.markdown(f"#### {scenario_name}")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.altair_chart(fan_chart_obj, use_container_width=True)
            with col2:
                st.altair_chart(depletion_chart_obj, use_container_width=True)
        
        # Create ending values summary table
        last_month = inputs.years_to_model * 12
        ending_data = []
        for scenario_name, data in stress_results.items():
            ending_row = data["stats"][data["stats"]["Month"] == last_month].iloc[0]
            ending_data.append({
                "Scenario": scenario_name,
                "P10": ending_row["P10"],
                "Median": ending_row["Median"],
                "P90": ending_row["P90"],
            })
        
        endings_df = pd.DataFrame(ending_data).set_index("Scenario")
        
        st.markdown("**Ending Portfolio Values by Scenario (Percentiles)**")
        st.dataframe(
            endings_df.style.format({
                "P10": "${:,.0f}",
                "Median": "${:,.0f}",
                "P90": "${:,.0f}",
            }),
            use_container_width=True,
        )
    else:
        st.info("Define at least one stress-test scenario above and click 'Run Stress Test Simulations' to see results.")
    
    # Allocation Strategy Comparison
    st.markdown("---")
    st.subheader("Allocation Strategy Comparison")
    st.caption("Compare different portfolio allocations to see how they impact outcomes")
    
    st.markdown("##### Define Alternative Allocation Strategies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Conservative Allocation**")
        cons_eq = st.slider("Equity %", 0, 100, 40, 5, key="cons_eq")
        cons_fi = st.slider("Fixed Income %", 0, 100, 50, 5, key="cons_fi")
        cons_cash = st.slider("Cash %", 0, 100, 10, 5, key="cons_cash")
        
    with col2:
        st.markdown("**Aggressive Allocation**")
        agg_eq = st.slider("Equity %", 0, 100, 90, 5, key="agg_eq")
        agg_fi = st.slider("Fixed Income %", 0, 100, 10, 5, key="agg_fi")
        agg_cash = st.slider("Cash %", 0, 100, 0, 5, key="agg_cash")
    
    if st.button("Run Allocation Comparison"):
        with st.spinner("Running comparison simulations..."):
            # Base case (already run)
            base_results = {
                "Current Allocation": {
                    "stats": stats_df,
                    "paths": paths_df,
                    "allocation": f"{int(inputs.equity_pct*100)}/{int(inputs.fi_pct*100)}/{int(inputs.cash_pct*100)}",
                    "metrics": st.session_state.get('metrics', {})
                }
            }
            
            # Conservative allocation
            cons_inputs = ModelInputs(
                **{k: v for k, v in inputs.__dict__.items()},
            )
            cons_inputs.equity_pct = cons_eq / 100.0
            cons_inputs.fi_pct = cons_fi / 100.0
            cons_inputs.cash_pct = cons_cash / 100.0
            cons_paths, cons_stats, cons_metrics = run_monte_carlo(cons_inputs)
            base_results["Conservative"] = {
                "stats": cons_stats,
                "paths": cons_paths,
                "allocation": f"{cons_eq}/{cons_fi}/{cons_cash}",
                "metrics": cons_metrics
            }
            
            # Aggressive allocation
            agg_inputs = ModelInputs(
                **{k: v for k, v in inputs.__dict__.items()},
            )
            agg_inputs.equity_pct = agg_eq / 100.0
            agg_inputs.fi_pct = agg_fi / 100.0
            agg_inputs.cash_pct = agg_cash / 100.0
            agg_paths, agg_stats, agg_metrics = run_monte_carlo(agg_inputs)
            base_results["Aggressive"] = {
                "stats": agg_stats,
                "paths": agg_paths,
                "allocation": f"{agg_eq}/{agg_fi}/{agg_cash}",
                "metrics": agg_metrics
            }
            
            # Store in session state for overlay
            st.session_state.allocation_comparison_results = base_results
        
        # Display overlay comparison
        st.markdown("#### 📊 Scenario Overlay Comparison")
        st.caption("All three allocations displayed on the same chart for easy comparison")
        
        overlay_chart = create_scenario_overlay_chart(
            st.session_state.allocation_comparison_results,
            selected_scenarios=["Current Allocation", "Conservative", "Aggressive"]
        )
        
        if overlay_chart:
            st.altair_chart(overlay_chart, use_container_width=True)
        
        # Scenario selector for custom overlay
        st.markdown("##### Customize Scenario Selection")
        available_scenarios = list(st.session_state.allocation_comparison_results.keys())
        selected_for_overlay = st.multiselect(
            "Select scenarios to compare",
            options=available_scenarios,
            default=available_scenarios,
            key="scenario_selector"
        )
        
        if selected_for_overlay and len(selected_for_overlay) > 0:
            custom_overlay = create_scenario_overlay_chart(
                st.session_state.allocation_comparison_results,
                selected_scenarios=selected_for_overlay
            )
            if custom_overlay:
                st.altair_chart(custom_overlay, use_container_width=True)
        
        # Display comparison table
        st.markdown("#### 📈 Side-by-Side Comparison Table")
        comparison_table = create_scenario_comparison_table(
            st.session_state.allocation_comparison_results,
            inputs.years_to_model
        )
        
        st.dataframe(
            comparison_table.style.format({
                "Success Probability": "{:.1f}%",
                "P10 Ending": "${:,.0f}",
                "Median Ending": "${:,.0f}",
                "P90 Ending": "${:,.0f}"
            }),
            use_container_width=True
        )
        
        # Display individual charts
        st.markdown("---")
        st.markdown("#### Individual Scenario Details")
        
        for name, data in st.session_state.allocation_comparison_results.items():
            with st.expander(f"📊 {name} ({data['allocation']} Equity/FI/Cash)", expanded=False):
                col1, col2 = st.columns([2, 1])
                with col1:
                    chart = fan_chart(data["stats"], title=f"{name} - Portfolio Projection")
                    st.altair_chart(chart, use_container_width=True)
                with col2:
                    depl_chart = depletion_probability_chart(data["paths"], title=f"{name} - Depletion Risk")
                    st.altair_chart(depl_chart, use_container_width=True)
    
    # Check if we have stored allocation comparison results to display
    elif 'allocation_comparison_results' in st.session_state:
        st.markdown("#### 📊 Previous Scenario Overlay Comparison")
        
        overlay_chart = create_scenario_overlay_chart(
            st.session_state.allocation_comparison_results,
            selected_scenarios=list(st.session_state.allocation_comparison_results.keys())
        )
        
        if overlay_chart:
            st.altair_chart(overlay_chart, use_container_width=True)
        
        # Display comparison table
        comparison_table = create_scenario_comparison_table(
            st.session_state.allocation_comparison_results,
            inputs.years_to_model
        )
        
        st.dataframe(
            comparison_table.style.format({
                "Success Probability": "{:.1f}%",
                "P10 Ending": "${:,.0f}",
                "Median Ending": "${:,.0f}",
                "P90 Ending": "${:,.0f}"
            }),
            use_container_width=True
        )
    
    # Advanced Analytics Section
    st.markdown("---")
    st.subheader("🔬 Advanced Analytics")
    
    with st.expander("📊 Asset Correlation Analysis", expanded=False):
        st.caption("Understand how different asset classes move together and impact portfolio risk")
        
        col1, col2 = st.columns(2)
        with col1:
            eq_fi_corr = st.slider(
                "Equity-Fixed Income Correlation",
                -1.0, 1.0, 0.0, 0.1,
                key="eq_fi_corr",
                help="Positive = move together, Negative = move opposite, 0 = independent"
            )
        with col2:
            fi_cash_corr = st.slider(
                "Fixed Income-Cash Correlation",
                -1.0, 1.0, 0.3, 0.1,
                key="fi_cash_corr",
                help="Typically positive as both are defensive assets"
            )
        
        # Create and display correlation matrix
        corr_data = pd.DataFrame({
            'Asset': ['Equity', 'Fixed Income', 'Cash'],
            'Equity': [1.0, eq_fi_corr, 0.0],
            'Fixed Income': [eq_fi_corr, 1.0, fi_cash_corr],
            'Cash': [0.0, fi_cash_corr, 1.0]
        })
        
        st.markdown("**Correlation Matrix**")
        corr_chart = create_correlation_matrix_chart(corr_data)
        st.altair_chart(corr_chart, use_container_width=True)
        
        st.info("💡 **Impact**: Higher correlations reduce diversification benefits. Negative correlations provide better downside protection.")
    
    with st.expander("📉 Historical Stress Scenarios", expanded=False):
        st.caption("Test your portfolio against major historical market events")
        
        scenario = st.radio(
            "Select Historical Scenario",
            ["2008 Financial Crisis", "COVID-19 Crash (2020)", "Dot-com Bubble (2000-2002)", "1970s Stagflation"],
            key="historical_scenario"
        )
        
        if st.button("Run Historical Scenario", key="run_historical"):
            with st.spinner(f"Running {scenario} simulation..."):
                # Map scenario names to function parameters
                scenario_map = {
                    "2008 Financial Crisis": "2008_crisis",
                    "COVID-19 Crash (2020)": "covid_2020",
                    "Dot-com Bubble (2000-2002)": "dotcom_2000",
                    "1970s Stagflation": "stagflation_1970s"
                }
                
                historical_results = run_historical_stress_scenario(
                    inputs, 
                    scenario_map[scenario]
                )
                
                st.session_state.historical_results = {
                    "scenario": scenario,
                    "data": historical_results
                }
        
        # Display historical results
        if 'historical_results' in st.session_state:
            hist_data = st.session_state.historical_results
            st.markdown(f"**{hist_data['scenario']} Results**")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                hist_chart = fan_chart(
                    hist_data['data']['stats'],
                    title=f"{hist_data['scenario']} - Portfolio Projection"
                )
                st.altair_chart(hist_chart, use_container_width=True)
            
            with col2:
                hist_depl = depletion_probability_chart(
                    hist_data['data']['paths'],
                    title=f"{hist_data['scenario']} - Depletion Risk"
                )
                st.altair_chart(hist_depl, use_container_width=True)
            
            # Compare with base case
            last_month = inputs.years_to_model * 12
            hist_ending = hist_data['data']['stats'][hist_data['data']['stats']['Month'] == last_month].iloc[0]
            base_ending = stats_df[stats_df['Month'] == last_month].iloc[0]
            
            comparison_df = pd.DataFrame({
                'Scenario': ['Base Case', hist_data['scenario']],
                'Median Ending': [base_ending['Median'], hist_ending['Median']],
                'P10 Ending': [base_ending['P10'], hist_ending['P10']],
                'P90 Ending': [base_ending['P90'], hist_ending['P90']]
            })
            
            st.markdown("**Comparison with Base Case**")
            st.dataframe(
                comparison_df.style.format({
                    'Median Ending': '${:,.0f}',
                    'P10 Ending': '${:,.0f}',
                    'P90 Ending': '${:,.0f}'
                }),
                use_container_width=True
            )
    
    with st.expander("🔄 Dynamic Rebalancing Analysis", expanded=False):
        st.caption("Compare different portfolio rebalancing strategies")
        
        strategies_to_test = st.multiselect(
            "Select rebalancing strategies to compare",
            ["Annual", "Quarterly", "5% Threshold", "10% Threshold", "No Rebalancing"],
            default=["Annual", "5% Threshold", "No Rebalancing"],
            key="rebalance_strategies"
        )
        
        if st.button("Analyze Rebalancing Strategies", key="run_rebalance"):
            with st.spinner("Running rebalancing analysis..."):
                # Map display names to function parameters
                strategy_map = {
                    "Annual": "annual",
                    "Quarterly": "quarterly",
                    "5% Threshold": "threshold_5",
                    "10% Threshold": "threshold_10",
                    "No Rebalancing": "none"
                }
                
                rebalance_results = {}
                for strat in strategies_to_test:
                    result = analyze_rebalancing_strategy(inputs, strategy_map[strat])
                    rebalance_results[strat] = result
                
                st.session_state.rebalance_results = rebalance_results
        
        # Display rebalancing results
        if 'rebalance_results' in st.session_state:
            rebal_data = st.session_state.rebalance_results
            
            st.markdown("**Strategy Performance Comparison**")
            
            # Create comparison table
            last_month = inputs.years_to_model * 12
            comparison_rows = []
            
            for strat_name, result in rebal_data.items():
                ending = result['stats'][result['stats']['Month'] == last_month].iloc[0]
                comparison_rows.append({
                    'Strategy': strat_name,
                    'Median Ending': ending['Median'],
                    'P10 Ending': ending['P10'],
                    'P90 Ending': ending['P90'],
                    'Avg Rebalances': result['rebalance_count']
                })
            
            comparison_df = pd.DataFrame(comparison_rows)
            
            st.dataframe(
                comparison_df.style.format({
                    'Median Ending': '${:,.0f}',
                    'P10 Ending': '${:,.0f}',
                    'P90 Ending': '${:,.0f}',
                    'Avg Rebalances': '{:.1f}'
                }),
                use_container_width=True
            )
            
            # Display charts for each strategy
            st.markdown("**Portfolio Projections by Strategy**")
            
            for strat_name, result in rebal_data.items():
                with st.expander(f"📈 {strat_name} Strategy", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        chart = fan_chart(result['stats'], title=f"{strat_name} - Portfolio Projection")
                        st.altair_chart(chart, use_container_width=True)
                    with col2:
                        depl_chart = depletion_probability_chart(result['paths'], title=f"{strat_name} - Depletion Risk")
                        st.altair_chart(depl_chart, use_container_width=True)
                    
                    st.caption(f"Average rebalances per simulation: {result['rebalance_count']:.1f}")
            
            st.info("💡 **Trading Costs**: More frequent rebalancing may improve risk-adjusted returns but increases transaction costs. Consider your specific cost structure.")
    
    with st.expander("💰 Tax-Efficient Withdrawal Strategies", expanded=False):
        st.caption("Optimize withdrawal sequencing across different account types to minimize taxes")
        
        st.markdown("""
        **Account Type Assumptions:**
        - **Taxable**: 35% of portfolio (15% long-term capital gains tax)
        - **Traditional IRA**: 50% of portfolio (22% ordinary income tax)
        - **Roth IRA**: 15% of portfolio (tax-free withdrawals)
        """)
        
        if st.button("Analyze Tax Strategies", key="run_tax_analysis"):
            with st.spinner("Analyzing tax-efficient withdrawal strategies..."):
                tax_results = analyze_tax_efficient_withdrawals(inputs)
                st.session_state.tax_results = tax_results
        
        # Display tax analysis results
        if 'tax_results' in st.session_state:
            tax_data = st.session_state.tax_results
            
            st.markdown("**Strategy Comparison**")
            
            # Create comparison table
            comparison_rows = []
            for strategy_name, result in tax_data.items():
                row = {
                    'Strategy': strategy_name,
                    'Total Withdrawals': result['total_withdrawals'],
                    'Total Tax': result['total_tax'],
                    'After-Tax Spending': result['after_tax_spending'],
                    'Effective Tax Rate': result['effective_tax_rate'] * 100
                }
                
                if 'tax_savings_vs_naive' in result:
                    row['Tax Savings'] = result['tax_savings_vs_naive']
                    row['Savings %'] = result['savings_percentage']
                
                comparison_rows.append(row)
            
            comparison_df = pd.DataFrame(comparison_rows)
            
            st.dataframe(
                comparison_df.style.format({
                    'Total Withdrawals': '${:,.0f}',
                    'Total Tax': '${:,.0f}',
                    'After-Tax Spending': '${:,.0f}',
                    'Effective Tax Rate': '{:.1f}%',
                    'Tax Savings': '${:,.0f}',
                    'Savings %': '{:.1f}%'
                }),
                use_container_width=True
            )
            
            # Show withdrawal details for each strategy
            st.markdown("---")
            st.markdown("**Withdrawal Details by Strategy**")
            
            for strategy_name, result in tax_data.items():
                if strategy_name == 'Naive Proportional':
                    continue
                    
                with st.expander(f"💡 {strategy_name}", expanded=False):
                    if 'taxable_used' in result:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Taxable Withdrawals", f"${result['taxable_used']:,.0f}")
                        
                        if 'traditional_used' in result:
                            with col2:
                                st.metric("Traditional IRA", f"${result['traditional_used']:,.0f}")
                        
                        if 'roth_used' in result:
                            with col3:
                                st.metric("Roth IRA", f"${result['roth_used']:,.0f}")
                        
                        if 'rmd_amount' in result:
                            st.info(f"📋 **RMD Requirement**: ${result['rmd_amount']:,.0f} must be withdrawn from Traditional IRA (starting at age 72)")
                    
                    if 'tax_savings_vs_naive' in result:
                        st.success(f"💰 **Tax Savings**: ${result['tax_savings_vs_naive']:,.0f} ({result['savings_percentage']:.1f}%) compared to proportional withdrawals")
            
            st.markdown("---")
            st.info("""
            **💡 Key Insights:**
            - **Tax-Efficient Sequencing** withdraws from taxable accounts first (lower cap gains rate), then Traditional IRA, then Roth
            - **RMD-Aware Strategy** ensures Required Minimum Distributions are taken after age 72, avoiding penalties
            - Proper sequencing can save thousands in taxes over retirement
            - Consider Roth conversions in low-income years to optimize long-term tax burden
            """)
    
    # Sensitivity Analysis
    st.markdown("---")
    st.subheader("Sensitivity Analysis")
    st.caption("See how changes in key variables impact your portfolio outcomes")
    
    st.markdown("This analysis shows how ±20% changes in key variables affect your portfolio:")
    st.markdown("- **Portfolio Return**: Impact of market performance")
    st.markdown("- **Monthly Spending**: Impact of lifestyle changes")
    st.markdown("- **Starting Portfolio**: Impact of initial wealth")
    
    if st.button("Run Sensitivity Analysis"):
        with st.spinner("Running sensitivity analysis..."):
            sensitivity_df = sensitivity_analysis(inputs)
        
        st.markdown("#### Sensitivity Analysis Results")
        
        # Create tabs for different metrics
        tab1, tab2, tab3 = st.tabs(["Median Ending Value", "10th Percentile", "Success Probability"])
        
        with tab1:
            chart1 = sensitivity_chart(sensitivity_df, "Median Ending")
            st.altair_chart(chart1, use_container_width=True)
            st.caption("Shows how median ending portfolio value changes with each variable")
        
        with tab2:
            chart2 = sensitivity_chart(sensitivity_df, "P10 Ending")
            st.altair_chart(chart2, use_container_width=True)
            st.caption("Shows how 10th percentile (worst case) changes - lower values indicate higher risk")
        
        with tab3:
            # Create success probability chart
            # (Additional chart implementation here if needed)
            st.caption("Shows how probability of success changes with each variable")


# ===========================================
# EXCEL EXPORT FUNCTIONALITY
# ===========================================

def export_to_excel(client_info, inputs, metrics, stats_df, paths_df, goal_results=None, comparison_data=None):
    """
    Export comprehensive analysis to Excel with multiple formatted sheets.
    
    Returns:
        bytes: Excel file as bytes for download
    """
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#1B3B5F',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'font_color': '#1B3B5F',
        'align': 'left'
    })
    
    subtitle_format = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'font_color': '#C4A053',
        'align': 'left'
    })
    
    number_format = workbook.add_format({'num_format': '#,##0'})
    currency_format = workbook.add_format({'num_format': '$#,##0'})
    percent_format = workbook.add_format({'num_format': '0.0%'})
    date_format = workbook.add_format({'num_format': 'mm/dd/yyyy'})
    
    # Success color format based on probability
    success_high = workbook.add_format({
        'num_format': '0.0%',
        'bg_color': '#10B981',
        'font_color': 'white',
        'bold': True
    })
    
    success_medium = workbook.add_format({
        'num_format': '0.0%',
        'bg_color': '#F59E0B',
        'font_color': 'white',
        'bold': True
    })
    
    success_low = workbook.add_format({
        'num_format': '0.0%',
        'bg_color': '#EF4444',
        'font_color': 'white',
        'bold': True
    })
    
    # Sheet 1: Executive Summary
    summary_sheet = workbook.add_worksheet('Executive Summary')
    summary_sheet.set_column('A:A', 30)
    summary_sheet.set_column('B:B', 20)
    
    row = 0
    summary_sheet.write(row, 0, 'PORTFOLIO MONTE CARLO ANALYSIS', title_format)
    row += 1
    summary_sheet.write(row, 0, f'Generated: {datetime.now().strftime("%B %d, %Y %I:%M %p")}')
    row += 2
    
    # Client Information
    summary_sheet.write(row, 0, 'CLIENT INFORMATION', subtitle_format)
    row += 1
    if client_info:
        if client_info.client_name:
            summary_sheet.write(row, 0, 'Client Name:')
            summary_sheet.write(row, 1, client_info.client_name)
            row += 1
        if client_info.advisor_name:
            summary_sheet.write(row, 0, 'Advisor:')
            summary_sheet.write(row, 1, client_info.advisor_name)
            row += 1
        summary_sheet.write(row, 0, 'Report Date:')
        summary_sheet.write(row, 1, client_info.report_date, date_format)
        row += 1
    
    row += 1
    
    # Key Metrics
    summary_sheet.write(row, 0, 'KEY RESULTS', subtitle_format)
    row += 1
    
    summary_sheet.write(row, 0, 'Success Probability:', header_format)
    success_prob = metrics.get('success_probability', 0) / 100
    if success_prob >= 0.80:
        summary_sheet.write(row, 1, success_prob, success_high)
    elif success_prob >= 0.60:
        summary_sheet.write(row, 1, success_prob, success_medium)
    else:
        summary_sheet.write(row, 1, success_prob, success_low)
    row += 1
    
    summary_sheet.write(row, 0, 'Starting Portfolio:', header_format)
    summary_sheet.write(row, 1, inputs.starting_portfolio, currency_format)
    row += 1
    
    summary_sheet.write(row, 0, 'Median Ending Value:', header_format)
    summary_sheet.write(row, 1, metrics.get('ending_median', 0), currency_format)
    row += 1
    
    summary_sheet.write(row, 0, 'P10 (Worst Case):', header_format)
    summary_sheet.write(row, 1, metrics.get('ending_p10', 0), currency_format)
    row += 1
    
    summary_sheet.write(row, 0, 'P90 (Best Case):', header_format)
    summary_sheet.write(row, 1, metrics.get('ending_p90', 0), currency_format)
    row += 1
    
    row += 1
    
    # Portfolio Configuration
    summary_sheet.write(row, 0, 'PORTFOLIO CONFIGURATION', subtitle_format)
    row += 1
    
    summary_sheet.write(row, 0, 'Time Horizon:')
    summary_sheet.write(row, 1, f"{inputs.years_to_model} years")
    row += 1
    
    summary_sheet.write(row, 0, 'Current Age:')
    summary_sheet.write(row, 1, inputs.current_age)
    row += 1
    
    summary_sheet.write(row, 0, 'Monthly Spending:')
    summary_sheet.write(row, 1, abs(inputs.monthly_spending), currency_format)
    row += 1
    
    summary_sheet.write(row, 0, 'Asset Allocation:')
    summary_sheet.write(row, 1, f"{inputs.equity_pct*100:.0f}% / {inputs.fi_pct*100:.0f}% / {inputs.cash_pct*100:.0f}%")
    row += 1
    
    summary_sheet.write(row, 0, 'Simulations:')
    summary_sheet.write(row, 1, inputs.n_scenarios, number_format)
    row += 1
    
    # Sheet 2: Statistics
    stats_sheet = workbook.add_worksheet('Statistics')
    
    # Write headers
    for col_num, col_name in enumerate(stats_df.columns):
        stats_sheet.write(0, col_num, col_name, header_format)
    
    # Write data
    for row_num, row_data in enumerate(stats_df.values, start=1):
        for col_num, value in enumerate(row_data):
            if col_num == 0:  # Month column
                stats_sheet.write(row_num, col_num, value, number_format)
            else:  # Value columns
                stats_sheet.write(row_num, col_num, value, currency_format)
    
    # Auto-fit columns
    for col_num in range(len(stats_df.columns)):
        stats_sheet.set_column(col_num, col_num, 12)
    
    # Sheet 3: Simulation Paths (limited to prevent file size issues)
    paths_sheet = workbook.add_worksheet('Simulation Paths')
    
    # Limit to first 100 scenarios for performance
    paths_sample = paths_df.iloc[:, :min(100, paths_df.shape[1])]
    
    # Write headers
    for col_num, col_name in enumerate(paths_sample.columns):
        paths_sheet.write(0, col_num, col_name, header_format)
    
    # Write data
    for row_num, row_data in enumerate(paths_sample.values, start=1):
        for col_num, value in enumerate(row_data):
            paths_sheet.write(row_num, col_num, value, currency_format)
    
    # Auto-fit columns
    for col_num in range(len(paths_sample.columns)):
        paths_sheet.set_column(col_num, col_num, 12)
    
    # Sheet 4: Financial Goals (if available)
    if goal_results is not None and not goal_results.empty:
        goals_sheet = workbook.add_worksheet('Financial Goals')
        
        # Write headers
        for col_num, col_name in enumerate(goal_results.columns):
            goals_sheet.write(0, col_num, col_name, header_format)
        
        # Write data
        for row_num, row_data in enumerate(goal_results.values, start=1):
            for col_num, value in enumerate(row_data):
                if 'Probability' in goal_results.columns[col_num]:
                    goals_sheet.write(row_num, col_num, value/100, percent_format)
                elif 'Amount' in goal_results.columns[col_num]:
                    goals_sheet.write(row_num, col_num, value, currency_format)
                elif 'Age' in goal_results.columns[col_num]:
                    goals_sheet.write(row_num, col_num, value, number_format)
                else:
                    goals_sheet.write(row_num, col_num, value)
        
        # Auto-fit columns
        for col_num in range(len(goal_results.columns)):
            goals_sheet.set_column(col_num, col_num, 18)
    
    # Sheet 5: Scenario Comparison (if available)
    if comparison_data is not None and not comparison_data.empty:
        comp_sheet = workbook.add_worksheet('Scenario Comparison')
        
        # Write headers
        for col_num, col_name in enumerate(comparison_data.columns):
            comp_sheet.write(0, col_num, col_name, header_format)
        
        # Write data
        for row_num, row_data in enumerate(comparison_data.values, start=1):
            for col_num, value in enumerate(row_data):
                if 'Probability' in comparison_data.columns[col_num]:
                    comp_sheet.write(row_num, col_num, value/100, percent_format)
                elif 'Ending' in comparison_data.columns[col_num] or 'Value' in comparison_data.columns[col_num]:
                    comp_sheet.write(row_num, col_num, value, currency_format)
                else:
                    comp_sheet.write(row_num, col_num, value)
        
        # Auto-fit columns
        for col_num in range(len(comparison_data.columns)):
            comp_sheet.set_column(col_num, col_num, 18)
    
    workbook.close()
    output.seek(0)
    return output.getvalue()


def create_batch_export(client_info, inputs, metrics, stats_df, paths_df, goal_results=None, comparison_data=None):
    """
    Create a ZIP file containing PDF, Excel, and JSON exports.
    
    Returns:
        bytes: ZIP file as bytes for download
    """
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add PDF report
        try:
            pdf_bytes = generate_pdf_report(
                client_info=client_info,
                inputs=inputs,
                stats_df=stats_df,
                metrics=metrics,
                paths_df=paths_df,
                stress_results=None,
                goal_results=goal_results
            )
            zip_file.writestr('Portfolio_Report.pdf', pdf_bytes)
        except Exception as e:
            print(f"PDF generation error: {e}")
        
        # Add Excel workbook
        try:
            excel_bytes = export_to_excel(
                client_info=client_info,
                inputs=inputs,
                metrics=metrics,
                stats_df=stats_df,
                paths_df=paths_df,
                goal_results=goal_results,
                comparison_data=comparison_data
            )
            zip_file.writestr('Portfolio_Analysis.xlsx', excel_bytes)
        except Exception as e:
            print(f"Excel generation error: {e}")
        
        # Add CSV files
        try:
            zip_file.writestr('statistics.csv', stats_df.to_csv(index=False))
            paths_sample = paths_df.iloc[:, :min(50, paths_df.shape[1])]
            zip_file.writestr('simulation_paths_sample.csv', paths_sample.to_csv(index=False))
            
            if goal_results is not None and not goal_results.empty:
                zip_file.writestr('financial_goals.csv', goal_results.to_csv(index=False))
        except Exception as e:
            print(f"CSV generation error: {e}")
        
        # Add JSON summary
        try:
            summary_json = {
                'client_name': client_info.client_name if client_info else 'Unknown',
                'report_date': client_info.report_date.isoformat() if client_info else datetime.now().isoformat(),
                'generated_at': datetime.now().isoformat(),
                'metrics': {
                    'success_probability': metrics.get('success_probability', 0),
                    'starting_portfolio': inputs.starting_portfolio,
                    'ending_median': metrics.get('ending_median', 0),
                    'ending_p10': metrics.get('ending_p10', 0),
                    'ending_p90': metrics.get('ending_p90', 0),
                },
                'configuration': {
                    'time_horizon': inputs.years_to_model,
                    'current_age': inputs.current_age,
                    'monthly_spending': inputs.monthly_spending,
                    'equity_pct': inputs.equity_pct,
                    'fi_pct': inputs.fi_pct,
                    'cash_pct': inputs.cash_pct,
                    'simulations': inputs.n_scenarios
                }
            }
            
            import json
            zip_file.writestr('summary.json', json.dumps(summary_json, indent=2))
        except Exception as e:
            print(f"JSON generation error: {e}")
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


# ===========================================
# PHASE 4: ADVANCED ANALYTICS
# ===========================================

def create_correlation_matrix_chart(equity_corr=0.0, fi_corr=0.0):
    """
    Create a visual correlation matrix showing asset relationships.
    
    Args:
        equity_corr: Correlation between equity and fixed income
        fi_corr: Correlation between fixed income and cash
    
    Returns:
        Altair chart
    """
    # Create correlation matrix data
    data = pd.DataFrame({
        'Asset 1': ['Equity', 'Equity', 'Fixed Income', 'Fixed Income', 'Equity', 'Cash'],
        'Asset 2': ['Equity', 'Fixed Income', 'Fixed Income', 'Cash', 'Cash', 'Cash'],
        'Correlation': [1.0, equity_corr, 1.0, fi_corr, 0.0, 1.0]
    })
    
    chart = alt.Chart(data).mark_rect().encode(
        x=alt.X('Asset 2:N', title=''),
        y=alt.Y('Asset 1:N', title=''),
        color=alt.Color('Correlation:Q',
                       scale=alt.Scale(scheme='redyellowgreen', domain=[-1, 1]),
                       legend=alt.Legend(title='Correlation')),
        tooltip=[
            alt.Tooltip('Asset 1:N'),
            alt.Tooltip('Asset 2:N'),
            alt.Tooltip('Correlation:Q', format='.2f')
        ]
    ).properties(
        width=300,
        height=300,
        title='Asset Correlation Matrix'
    )
    
    # Add text labels
    text = chart.mark_text(baseline='middle', fontSize=14, fontWeight='bold').encode(
        text=alt.Text('Correlation:Q', format='.2f'),
        color=alt.condition(
            alt.datum.Correlation > 0.5,
            alt.value('white'),
            alt.value('black')
        )
    )
    
    return (chart + text)


def run_historical_stress_scenario(inputs, scenario_name):
    """
    Run simulation with historical crisis parameters.
    
    Returns:
        tuple: (paths_df, stats_df, metrics)
    """
    stressed_inputs = ModelInputs(**{k: v for k, v in inputs.__dict__.items()})
    
    if scenario_name == "2008 Financial Crisis":
        # -37% equity, -5% bonds in year 1, slow recovery
        stressed_inputs.equity_return_annual = -0.15
        stressed_inputs.equity_vol_annual = 0.35
        stressed_inputs.fi_return_annual = 0.02
        
    elif scenario_name == "COVID-19 Crash":
        # -34% equity Q1, rapid recovery
        stressed_inputs.equity_return_annual = 0.00
        stressed_inputs.equity_vol_annual = 0.45
        stressed_inputs.fi_return_annual = 0.03
        
    elif scenario_name == "Dot-com Bubble":
        # -49% equity over 2.5 years
        stressed_inputs.equity_return_annual = -0.10
        stressed_inputs.equity_vol_annual = 0.30
        stressed_inputs.fi_return_annual = 0.05
        
    elif scenario_name == "1970s Stagflation":
        # High inflation, poor stock returns
        stressed_inputs.equity_return_annual = 0.02
        stressed_inputs.fi_return_annual = 0.01
        stressed_inputs.inflation_annual = 0.08
        stressed_inputs.equity_vol_annual = 0.22
        
    return run_monte_carlo(stressed_inputs)


def analyze_rebalancing_strategy(inputs, strategy='annual'):
    """
    Simulate portfolio with rebalancing strategy.
    
    Args:
        inputs: ModelInputs
        strategy: 'annual', 'quarterly', 'threshold_5', 'threshold_10', 'none'
    
    Returns:
        tuple: (paths_df, stats_df, metrics, rebalance_count)
    """
    months = inputs.years_to_model * 12
    np.random.seed(42)
    
    # Target allocation
    target_eq = inputs.equity_pct
    target_fi = inputs.fi_pct
    target_cash = inputs.cash_pct
    
    values = np.zeros((months + 1, inputs.n_scenarios), dtype=float)
    rebalance_counts = np.zeros(inputs.n_scenarios)
    
    for j in range(inputs.n_scenarios):
        val = inputs.starting_portfolio
        eq_val = val * target_eq
        fi_val = val * target_fi
        cash_val = val * target_cash
        
        values[0, j] = val
        
        for month_index in range(1, months + 1):
            # Monthly returns
            monthly_infl = (1 + inputs.inflation_annual) ** (1/12) - 1
            eq_ret = inputs.equity_return_annual / 12 + np.random.normal(0, inputs.equity_vol_annual / np.sqrt(12))
            fi_ret = inputs.fi_return_annual / 12 + np.random.normal(0, inputs.fi_vol_annual / np.sqrt(12))
            cash_ret = inputs.cash_return_annual / 12
            
            # Apply returns
            eq_val *= (1 + eq_ret)
            fi_val *= (1 + fi_ret)
            cash_val *= (1 + cash_ret)
            
            # Cash flows
            spending = inputs.monthly_spending * ((1 + monthly_infl) ** (month_index - 1))
            
            # Withdraw proportionally
            total_val = eq_val + fi_val + cash_val
            if total_val > 0:
                eq_val += spending * (eq_val / total_val)
                fi_val += spending * (fi_val / total_val)
                cash_val += spending * (cash_val / total_val)
            
            # Rebalancing logic
            should_rebalance = False
            
            if strategy == 'annual' and month_index % 12 == 0:
                should_rebalance = True
            elif strategy == 'quarterly' and month_index % 3 == 0:
                should_rebalance = True
            elif strategy in ['threshold_5', 'threshold_10']:
                threshold = 0.05 if strategy == 'threshold_5' else 0.10
                total_val = eq_val + fi_val + cash_val
                if total_val > 0:
                    current_eq_pct = eq_val / total_val
                    if abs(current_eq_pct - target_eq) > threshold:
                        should_rebalance = True
            
            if should_rebalance:
                total_val = eq_val + fi_val + cash_val
                eq_val = total_val * target_eq
                fi_val = total_val * target_fi
                cash_val = total_val * target_cash
                rebalance_counts[j] += 1
            
            values[month_index, j] = max(0, eq_val + fi_val + cash_val)
    
    # Create DataFrame
    columns = [f"Scenario_{i+1}" for i in range(inputs.n_scenarios)]
    paths_df = pd.DataFrame(values, columns=columns)
    
    # Calculate statistics
    stats_list = []
    for month_idx in range(0, months + 1):
        row_vals = values[month_idx, :]
        stats_list.append({
            "Month": month_idx,
            "P10": np.percentile(row_vals, 10),
            "P25": np.percentile(row_vals, 25),
            "Median": np.percentile(row_vals, 50),
            "P75": np.percentile(row_vals, 75),
            "P90": np.percentile(row_vals, 90),
        })
    
    stats_df = pd.DataFrame(stats_list)
    
    # Calculate metrics
    final_values = values[months, :]
    success_count = np.sum(final_values > 0)
    success_probability = (success_count / inputs.n_scenarios) * 100
    
    metrics = {
        "success_probability": success_probability,
        "ending_median": np.median(final_values),
        "ending_p10": np.percentile(final_values, 10),
        "ending_p90": np.percentile(final_values, 90),
        "avg_rebalances": np.mean(rebalance_counts)
    }
    
    return paths_df, stats_df, metrics, np.mean(rebalance_counts)


def analyze_tax_efficient_withdrawals(inputs):
    """
    Analyze tax-efficient withdrawal strategies across different account types.
    
    Compares:
    - Naive: Proportional withdrawals from all accounts
    - Tax-Efficient: Taxable → Traditional IRA → Roth IRA
    - RMD-Aware: Tax-efficient with Required Minimum Distributions
    
    Args:
        inputs: ModelInputs with account breakdown
    
    Returns:
        dict: Results for each strategy with tax impact
    """
    # Account balances (assume split based on typical retiree portfolios)
    taxable_pct = 0.35
    traditional_ira_pct = 0.50
    roth_ira_pct = 0.15
    
    taxable_balance = inputs.starting_portfolio * taxable_pct
    traditional_balance = inputs.starting_portfolio * traditional_ira_pct
    roth_balance = inputs.starting_portfolio * roth_ira_pct
    
    # Tax rates (simplified)
    ordinary_income_rate = 0.22  # 22% federal bracket
    capital_gains_rate = 0.15    # Long-term capital gains
    
    # RMD factors (simplified - age 72-80)
    rmd_factors = {
        72: 27.4, 73: 26.5, 74: 25.5, 75: 24.6, 76: 23.7,
        77: 22.9, 78: 22.0, 79: 21.1, 80: 20.2
    }
    
    results = {}
    
    # Strategy 1: Naive (proportional withdrawals)
    naive_tax = 0
    monthly_spending = inputs.monthly_spending * (1 + inputs.inflation_annual) ** (inputs.years_to_model / 2)
    annual_spending = monthly_spending * 12 * inputs.years_to_model
    
    # Proportional withdrawals incur mixed taxation
    naive_taxable = annual_spending * taxable_pct
    naive_trad = annual_spending * traditional_ira_pct
    naive_roth = annual_spending * roth_ira_pct
    
    naive_tax = (naive_taxable * capital_gains_rate + 
                 naive_trad * ordinary_income_rate)
    
    results['Naive Proportional'] = {
        'total_withdrawals': annual_spending,
        'total_tax': naive_tax,
        'after_tax_spending': annual_spending - naive_tax,
        'effective_tax_rate': naive_tax / annual_spending
    }
    
    # Strategy 2: Tax-Efficient Sequencing
    remaining_need = annual_spending
    efficient_tax = 0
    
    # First: Taxable accounts (lower cap gains rate)
    from_taxable = min(remaining_need, taxable_balance)
    efficient_tax += from_taxable * capital_gains_rate
    remaining_need -= from_taxable
    
    # Second: Traditional IRA (ordinary income)
    from_trad = min(remaining_need, traditional_balance)
    efficient_tax += from_trad * ordinary_income_rate
    remaining_need -= from_trad
    
    # Third: Roth IRA (tax-free)
    from_roth = min(remaining_need, roth_balance)
    # No tax on Roth withdrawals
    
    results['Tax-Efficient Sequencing'] = {
        'total_withdrawals': annual_spending,
        'total_tax': efficient_tax,
        'after_tax_spending': annual_spending - efficient_tax,
        'effective_tax_rate': efficient_tax / annual_spending,
        'taxable_used': from_taxable,
        'traditional_used': from_trad,
        'roth_used': from_roth
    }
    
    # Strategy 3: RMD-Aware
    current_age = inputs.client_age
    rmd_tax = 0
    rmd_total = 0
    
    # Calculate average RMD over retirement
    for year in range(inputs.years_to_model):
        age = current_age + year
        if age >= 72 and age in rmd_factors:
            annual_rmd = traditional_balance / rmd_factors[age]
            rmd_total += annual_rmd
            rmd_tax += annual_rmd * ordinary_income_rate
            traditional_balance -= annual_rmd
    
    # Fill remaining needs from taxable then Roth
    remaining_after_rmd = annual_spending - rmd_total
    from_taxable_rmd = min(remaining_after_rmd, taxable_balance)
    rmd_tax += from_taxable_rmd * capital_gains_rate
    
    from_roth_rmd = remaining_after_rmd - from_taxable_rmd
    
    results['RMD-Aware Strategy'] = {
        'total_withdrawals': annual_spending,
        'total_tax': rmd_tax,
        'after_tax_spending': annual_spending - rmd_tax,
        'effective_tax_rate': rmd_tax / annual_spending,
        'rmd_amount': rmd_total,
        'taxable_used': from_taxable_rmd,
        'roth_used': from_roth_rmd
    }
    
    # Calculate savings vs naive
    for strategy_name, data in results.items():
        if strategy_name != 'Naive Proportional':
            data['tax_savings_vs_naive'] = results['Naive Proportional']['total_tax'] - data['total_tax']
            data['savings_percentage'] = (data['tax_savings_vs_naive'] / results['Naive Proportional']['total_tax']) * 100
    
    return results


# ===========================================
# AI RESEARCH TAB
# ===========================================

def render_ai_research_tab():
    """AI Research Tab: Natural language Q&A for advisors."""
    st.markdown("### 🤖 AI Research Assistant")
    st.caption("Ask questions about retirement planning, portfolio analysis, and financial planning best practices")
    
    # Get AI research assistant
    ai_research = st.session_state.get('ai_research')
    
    if not ai_research:
        st.error("AI Research Assistant not initialized. Please refresh the page.")
        return
    
    # Get current simulation context if available
    inputs = st.session_state.get('inputs')
    metrics = st.session_state.get('metrics')
    simulation_run = st.session_state.get('simulation_run', False)
    
    # Display context info
    if simulation_run and inputs:
        with st.expander("📊 Current Simulation Context", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Portfolio", f"${inputs.starting_portfolio:,.0f}")
                st.metric("Age", f"{inputs.current_age}")
            with col2:
                st.metric("Equity %", f"{inputs.equity_pct*100:.0f}%")
                st.metric("Monthly Spending", f"${abs(inputs.monthly_spending):,.0f}")
            with col3:
                if metrics:
                    st.metric("Success Probability", f"{metrics.get('success_probability', 0):.0%}")
                    st.metric("Median Ending", f"${metrics.get('ending_median', 0):,.0f}")
    
    # Example queries
    st.markdown("#### Example Questions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Portfolio & Withdrawal:**")
        st.markdown("- What is a safe withdrawal rate?")
        st.markdown("- How should I adjust spending in a downturn?")
        st.markdown("- What withdrawal rate research exists?")
    
    with col2:
        st.markdown("**Allocation & Strategy:**")
        st.markdown("- What is a good asset allocation for age 65?")
        st.markdown("- How do I reduce sequence of returns risk?")
        st.markdown("- What were historical equity returns?")
    
    # Initialize chat history if not exists
    if 'ai_chat_history' not in st.session_state:
        st.session_state.ai_chat_history = []
    
    # Query input
    st.markdown("---")
    st.markdown("#### Ask a Question")
    
    query = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="Example: What is a safe withdrawal rate for a 30-year retirement?",
        key="ai_query_input"
    )
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        ask_button = st.button("🔍 Ask AI", type="primary", use_container_width=True)
    
    if ask_button and query:
        with st.spinner("Researching your question..."):
            # Build context from current simulation
            context = {}
            if simulation_run and inputs:
                context = {
                    'starting_portfolio': inputs.starting_portfolio,
                    'current_age': inputs.current_age,
                    'retirement_age': inputs.retirement_age,
                    'monthly_spending': inputs.monthly_spending,
                    'equity_pct': inputs.equity_pct,
                    'success_probability': metrics.get('success_probability', 0) if metrics else 0
                }
            
            # Get answer from AI
            answer = ai_research.answer_query(query, context=context)
            
            # Add to chat history
            st.session_state.ai_chat_history.append({
                'query': query,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            })
    
    # Display chat history
    if st.session_state.ai_chat_history:
        st.markdown("---")
        st.markdown("#### Research History")
        
        # Reverse to show most recent first
        for idx, chat in enumerate(reversed(st.session_state.ai_chat_history)):
            with st.expander(f"Q: {chat['query'][:100]}...", expanded=(idx == 0)):
                st.markdown("**Question:**")
                st.info(chat['query'])
                st.markdown("**Answer:**")
                st.markdown(chat['answer'])
                st.caption(f"Asked at: {chat['timestamp']}")
        
        # Clear history button
        if st.button("🗑️ Clear Research History"):
            st.session_state.ai_chat_history = []
            st.rerun()
    
    # Knowledge base reference
    st.markdown("---")
    st.markdown("#### Knowledge Base Topics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Withdrawal Rates**")
        st.caption("• 4% Rule (Bengen 1994)")
        st.caption("• Trinity Study findings")
        st.caption("• Dynamic withdrawal strategies")
    
    with col2:
        st.markdown("**📈 Asset Allocation**")
        st.caption("• Age-based rules")
        st.caption("• Risk tolerance assessment")
        st.caption("• Glidepath strategies")
    
    with col3:
        st.markdown("**📉 Market History**")
        st.caption("• Historical returns (1926-2023)")
        st.caption("• Market crises & recoveries")
        st.caption("• Inflation regimes")
    
    # Compliance notice
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** This AI Research Assistant provides educational information based on historical data "
              "and research. Responses are not personalized investment advice. Always consider individual client "
              "circumstances and consult with qualified professionals before making investment decisions.")


# ===========================================
# REPORTS TAB
# ===========================================

def render_reports_tab():
    """Reports & Export Tab: Generate PDFs and export analysis data."""
    st.markdown("### Reports & Export")
    st.caption("Generate professional reports and export analysis data")
    
    # Check if simulation has been run
    simulation_run = st.session_state.get('simulation_run', False)
    
    if not simulation_run:
        st.warning("⚠️ Please run a simulation in the **Portfolio Analysis** tab first.")
        return
    
    # Get data from session state
    client_info = st.session_state.get('client_info')
    inputs = st.session_state.get('inputs')
    paths_df = st.session_state.get('paths_df')
    stats_df = st.session_state.get('stats_df')
    metrics = st.session_state.get('metrics')
    financial_goals = st.session_state.get('financial_goals', [])
    goal_results = st.session_state.get('goal_results')
    
    # Branding Customization
    st.markdown("### 🎨 Report Branding & Customization")
    
    with st.expander("⚙️ Customize Report Appearance", expanded=False):
        st.caption("Personalize reports with your firm's branding")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Firm Information**")
            firm_name = st.text_input("Firm Name", value="Salem Investment Counselors", key="firm_name")
            advisor_name = st.text_input("Advisor Name", value=client_info.advisor_name if client_info and client_info.advisor_name else "", key="report_advisor_name")
            advisor_phone = st.text_input("Phone", value="", key="advisor_phone", placeholder="(555) 123-4567")
            advisor_email = st.text_input("Email", value="", key="advisor_email", placeholder="advisor@firm.com")
        
        with col2:
            st.markdown("**Branding Colors**")
            primary_color = st.color_picker("Primary Color", value="#1B3B5F", key="primary_color_picker")
            accent_color = st.color_picker("Accent Color", value="#C4A053", key="accent_color_picker")
            
            st.markdown("**Logo Upload** (Optional)")
            logo_file = st.file_uploader("Upload firm logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'], key="logo_upload")
            
            if logo_file:
                st.image(logo_file, width=150, caption="Logo Preview")
        
        st.markdown("**Custom Disclaimer**")
        custom_disclaimer = st.text_area(
            "Report Disclaimer",
            value="This analysis is for illustrative purposes only and does not guarantee future results. Past performance does not predict future returns. Please consult with a financial advisor before making investment decisions.",
            height=100,
            key="custom_disclaimer"
        )
        
        # Store branding in session state
        st.session_state.branding = {
            'firm_name': firm_name,
            'advisor_name': advisor_name,
            'advisor_phone': advisor_phone,
            'advisor_email': advisor_email,
            'primary_color': primary_color,
            'accent_color': accent_color,
            'logo': logo_file,
            'disclaimer': custom_disclaimer
        }
        
        st.info("💡 **Tip**: Branding settings will be applied to all generated reports during this session.")
    
    st.markdown("---")
    
    # ===== AUDIT TRAIL VIEWER =====
    st.markdown("### 📋 Audit Trail & Compliance Log")
    
    with st.expander("**View Audit History**", expanded=False):
        st.caption("Timestamped record of all simulations and analyses for compliance")
        
        audit_system = st.session_state.get('audit_system')
        
        if audit_system:
            # Export audit log
            try:
                # Get date range filters
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    start_date = st.date_input(
                        "Start Date",
                        value=datetime.now() - pd.Timedelta(days=30),
                        key="audit_start"
                    )
                
                with col2:
                    end_date = st.date_input(
                        "End Date",
                        value=datetime.now(),
                        key="audit_end"
                    )
                
                with col3:
                    client_filter = st.text_input(
                        "Client ID Filter",
                        value="",
                        placeholder="Optional",
                        key="audit_client_filter"
                    )
                
                # Export button
                if st.button("📊 Generate Audit Log", key="export_audit"):
                    with st.spinner("Generating audit log..."):
                        audit_df = audit_system.export_audit_log(
                            start_date=pd.to_datetime(start_date) if start_date else None,
                            end_date=pd.to_datetime(end_date) if end_date else None,
                            client_id=client_filter if client_filter else None
                        )
                        
                        if not audit_df.empty:
                            st.success(f"✅ Found {len(audit_df)} audit records")
                            
                            # Display summary metrics
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Records", len(audit_df))
                            
                            with col2:
                                unique_clients = audit_df['client_id'].nunique()
                                st.metric("Unique Clients", unique_clients)
                            
                            with col3:
                                flagged = audit_df[audit_df['compliance_flags'] != ''].shape[0]
                                st.metric("Flagged Records", flagged)
                            
                            # Display audit log table
                            st.markdown("**Audit Records:**")
                            display_df = audit_df.copy()
                            display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                            
                            st.dataframe(
                                display_df[['timestamp', 'record_id', 'scenario_type', 
                                           'success_probability', 'starting_portfolio', 'compliance_flags']].style.format({
                                    'success_probability': '{:.0%}',
                                    'starting_portfolio': '${:,.0f}'
                                }),
                                use_container_width=True
                            )
                            
                            # Export audit log as CSV
                            csv = display_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Audit Log (CSV)",
                                data=csv,
                                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                key="download_audit_csv"
                            )
                            
                            # Compliance flags summary
                            if flagged > 0:
                                st.markdown("---")
                                st.markdown("**Compliance Flags:**")
                                st.warning(f"⚠️ {flagged} record(s) have compliance flags")
                                
                                flagged_df = display_df[display_df['compliance_flags'] != '']
                                st.dataframe(
                                    flagged_df[['timestamp', 'record_id', 'compliance_flags']],
                                    use_container_width=True
                                )
                        else:
                            st.info("No audit records found for the selected date range.")
                
                # Cleanup old records
                st.markdown("---")
                st.markdown("**Data Retention Management**")
                st.caption(f"Current retention policy: {audit_system.retention_days} days (~7 years)")
                
                if st.button("🗑️ Cleanup Old Records", key="cleanup_audit"):
                    with st.spinner("Cleaning up old records..."):
                        deleted = audit_system.cleanup_old_records()
                        if deleted > 0:
                            st.success(f"✅ Deleted {deleted} record(s) older than retention period")
                        else:
                            st.info("No records to delete within retention policy")
            
            except Exception as e:
                st.error(f"Error loading audit log: {str(e)}")
        else:
            st.warning("Audit system not initialized")
    
    st.markdown("---")
    
    # PDF Report Generation
    st.markdown("### 📄 Generate Comprehensive PDF Report")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Report Sections**")
        col_a, col_b = st.columns(2)
        with col_a:
            include_executive = st.checkbox("Executive Summary", value=True, key="pdf_executive")
            include_assumptions = st.checkbox("Portfolio Assumptions", value=True, key="pdf_assumptions")
            include_analysis = st.checkbox("Portfolio Analysis", value=True, key="pdf_analysis")
        with col_b:
            include_goals = st.checkbox("Financial Goals", value=True if financial_goals else False, key="pdf_goals")
            include_stress = st.checkbox("Stress Tests", value=False, key="pdf_stress")
            include_phase4 = st.checkbox("🔬 Advanced Analytics (Phase 4)", value=True, key="pdf_phase4")
    
    with col2:
        st.markdown("**Report Metadata**")
        st.caption(f"Client: {client_info.client_name if client_info and client_info.client_name else 'Not specified'}")
        st.caption(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        st.caption(f"Simulations: {inputs.n_scenarios:,} paths")
    
    # Show Phase 4 analytics options if selected
    if include_phase4:
        st.markdown("**Phase 4 Analytics to Include**")
        col_c, col_d = st.columns(2)
        with col_c:
            include_historical = st.checkbox(
                "Historical Scenarios", 
                value='historical_results' in st.session_state,
                disabled='historical_results' not in st.session_state,
                key="pdf_historical"
            )
            include_rebalancing = st.checkbox(
                "Rebalancing Analysis",
                value='rebalance_results' in st.session_state,
                disabled='rebalance_results' not in st.session_state,
                key="pdf_rebalancing"
            )
        with col_d:
            include_tax = st.checkbox(
                "Tax Strategies",
                value='tax_results' in st.session_state,
                disabled='tax_results' not in st.session_state,
                key="pdf_tax"
            )
            include_correlation = st.checkbox(
                "Correlation Analysis",
                value=True,
                key="pdf_correlation"
            )
        
        if not any(['historical_results' in st.session_state, 'rebalance_results' in st.session_state, 'tax_results' in st.session_state]):
            st.info("💡 Run analyses in the **Scenarios** tab to include them in the PDF report.")
    
    if st.button("📥 Generate Enhanced PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating comprehensive PDF report..."):
            try:
                # Prepare selected sections
                selected_sections = []
                if include_executive: selected_sections.append('executive_summary')
                if include_assumptions: selected_sections.append('assumptions')
                if include_analysis: selected_sections.append('analysis')
                if include_goals and goal_results is not None: selected_sections.append('goals')
                if include_stress: selected_sections.append('stress')
                
                # Prepare Phase 4 data
                phase4_data = None
                if include_phase4:
                    phase4_data = {
                        'historical': st.session_state.get('historical_results') if include_historical else None,
                        'rebalancing': st.session_state.get('rebalance_results') if include_rebalancing else None,
                        'tax': st.session_state.get('tax_results') if include_tax else None,
                        'correlation': include_correlation
                    }
                
                # Get branding
                branding = st.session_state.get('branding', {})
                
                # Generate the PDF
                pdf_bytes = generate_enhanced_pdf_report(
                    client_info=client_info,
                    inputs=inputs,
                    stats_df=stats_df,
                    metrics=metrics,
                    paths_df=paths_df,
                    goal_results=goal_results if include_goals else None,
                    selected_sections=selected_sections,
                    phase4_data=phase4_data,
                    branding=branding
                )
                
                # Offer download
                st.success("✅ Enhanced PDF report generated successfully!")
                
                filename = f"Portfolio_Report_{client_info.client_name.replace(' ', '_') if client_info and client_info.client_name else 'Client'}_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                st.download_button(
                    label="💾 Download PDF Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.exception(e)
    
    # Data Export Section
    st.markdown("---")
    st.markdown("### 📊 Export Data")
    
    # Excel Export (Main Feature)
    st.markdown("#### 📗 Comprehensive Excel Export")
    st.caption("Export all analysis data to a multi-sheet Excel workbook with professional formatting")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        excel_options = st.multiselect(
            "Select data to include:",
            options=["Statistics", "Simulation Paths", "Financial Goals", "Scenario Comparison"],
            default=["Statistics", "Simulation Paths"],
            key="excel_export_options"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("📥 Generate Excel", type="primary", use_container_width=True):
            with st.spinner("Creating Excel workbook..."):
                try:
                    # Prepare optional data
                    goals_for_excel = goal_results if "Financial Goals" in excel_options and goal_results is not None else None
                    comparison_for_excel = None
                    
                    if "Scenario Comparison" in excel_options:
                        comparison_for_excel = st.session_state.get('allocation_comparison_results')
                        if comparison_for_excel:
                            # Convert comparison dict to DataFrame
                            comparison_for_excel = create_scenario_comparison_table(
                                comparison_for_excel,
                                inputs.years_to_model
                            )
                    
                    # Generate Excel
                    excel_bytes = export_to_excel(
                        client_info=client_info,
                        inputs=inputs,
                        metrics=metrics,
                        stats_df=stats_df,
                        paths_df=paths_df if "Simulation Paths" in excel_options else pd.DataFrame(),
                        goal_results=goals_for_excel,
                        comparison_data=comparison_for_excel
                    )
                    
                    st.success("✅ Excel workbook generated successfully!")
                    
                    filename = f"Portfolio_Analysis_{client_info.client_name.replace(' ', '_') if client_info and client_info.client_name else 'Client'}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                    
                    st.download_button(
                        label="💾 Download Excel Workbook",
                        data=excel_bytes,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Error generating Excel: {str(e)}")
                    st.error("Please ensure all required data is available and try again.")
    
    st.markdown("---")
    
    # CSV Export (Quick Export)
    st.markdown("#### 📄 Quick CSV Export")
    st.caption("Download individual datasets as CSV files")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Statistics CSV", use_container_width=True):
            csv = stats_df.to_csv(index=False)
            st.download_button(
                label="💾 Save Statistics CSV",
                data=csv,
                file_name=f"statistics_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("📈 Download Paths CSV", use_container_width=True):
            # Sample paths for reasonable file size
            paths_sample = paths_df.iloc[:, :min(50, paths_df.shape[1])]
            csv = paths_sample.to_csv(index=False)
            st.download_button(
                label="💾 Save Paths CSV",
                data=csv,
                file_name=f"simulation_paths_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col3:
        if goal_results is not None and not goal_results.empty:
            if st.button("🎯 Download Goals CSV", use_container_width=True):
                csv = goal_results.to_csv(index=False)
                st.download_button(
                    label="💾 Save Goals CSV",
                    data=csv,
                    file_name=f"financial_goals_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.button("🎯 Goals CSV (N/A)", use_container_width=True, disabled=True)
    
    st.markdown("---")
    
    # Interactive HTML Export
    st.markdown("#### 🌐 Interactive HTML Report")
    st.caption("Generate a standalone HTML file with interactive charts (no Streamlit required)")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 **Best for sharing**: Recipients can open the HTML file in any web browser and interact with the charts without installing anything.")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🌐 Generate HTML Report", type="secondary", use_container_width=True):
            with st.spinner("Creating interactive HTML report..."):
                try:
                    # Get branding
                    branding = st.session_state.get('branding', {})
                    
                    # Prepare Phase 4 data
                    phase4_data = {
                        'historical': st.session_state.get('historical_results'),
                        'rebalancing': st.session_state.get('rebalance_results'),
                        'tax': st.session_state.get('tax_results')
                    }
                    
                    # Generate HTML
                    html_content = generate_interactive_html_report(
                        client_info=client_info,
                        inputs=inputs,
                        stats_df=stats_df,
                        metrics=metrics,
                        paths_df=paths_df,
                        goal_results=goal_results,
                        phase4_data=phase4_data,
                        branding=branding
                    )
                    
                    st.success("✅ Interactive HTML report generated!")
                    
                    filename = f"Portfolio_Report_Interactive_{client_info.client_name.replace(' ', '_') if client_info and client_info.client_name else 'Client'}_{datetime.now().strftime('%Y%m%d')}.html"
                    
                    st.download_button(
                        label="💾 Download HTML Report",
                        data=html_content,
                        file_name=filename,
                        mime="text/html",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"Error generating HTML: {str(e)}")
                    st.exception(e)
    
    st.markdown("---")
    
    # Batch Export
    st.markdown("#### 📦 Complete Analysis Package")
    st.caption("Download everything in one ZIP file: PDF report, Excel workbook, CSV files, and JSON summary")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 **Recommended for archiving**: This package includes all analysis outputs in multiple formats for maximum compatibility and long-term storage.")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📦 Download Complete Package", type="primary", use_container_width=True):
            with st.spinner("Creating complete analysis package..."):
                try:
                    # Prepare optional data
                    goals_for_batch = goal_results if goal_results is not None else None
                    comparison_for_batch = None
                    
                    allocation_results = st.session_state.get('allocation_comparison_results')
                    if allocation_results:
                        comparison_for_batch = create_scenario_comparison_table(
                            allocation_results,
                            inputs.years_to_model
                        )
                    
                    # Generate batch export
                    zip_bytes = create_batch_export(
                        client_info=client_info,
                        inputs=inputs,
                        metrics=metrics,
                        stats_df=stats_df,
                        paths_df=paths_df,
                        goal_results=goals_for_batch,
                        comparison_data=comparison_for_batch
                    )
                    
                    st.success("✅ Complete package created successfully!")
                    
                    filename = f"Portfolio_Analysis_Complete_{client_info.client_name.replace(' ', '_') if client_info and client_info.client_name else 'Client'}_{datetime.now().strftime('%Y%m%d')}.zip"
                    
                    st.download_button(
                        label="💾 Download ZIP Package",
                        data=zip_bytes,
                        file_name=filename,
                        mime="application/zip",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    with st.expander("📋 Package Contents"):
                        st.markdown("""
                        **Included files:**
                        - `Portfolio_Report.pdf` - Professional PDF report
                        - `Portfolio_Analysis.xlsx` - Multi-sheet Excel workbook
                        - `statistics.csv` - Portfolio statistics by month
                        - `simulation_paths_sample.csv` - Sample simulation paths
                        - `financial_goals.csv` - Goal analysis (if applicable)
                        - `summary.json` - Machine-readable summary
                        """)
                        
                except Exception as e:
                    st.error(f"Error creating package: {str(e)}")
                    st.error("Please ensure all required data is available and try again.")


# ===========================================
# MAIN APPLICATION
# ===========================================

def main():
    """Main application entry point with health checks and observability."""
    # Initialize observability - generate correlation ID for request tracking
    correlation_id = new_correlation_id()
    structured_logger.info("Application request started", {"correlation_id": correlation_id})
    
    # Check application readiness
    health_status = health_checker.check_readiness()
    if not health_status["ready"]:
        st.error("⚠️ Application is not ready. Please check system health.")
        structured_logger.error("Application not ready", health_status)
        return
    
    # Track request metrics
    metrics.increment("request_count")
    
    # Initialize input validator and rate limiter
    validator = InputValidator()
    
    st.set_page_config(
        page_title="Portfolio Scenario Analysis",
        layout="wide",
    )
    
    # Apply Salem Investment Counselors styling
    apply_salem_styling()
    
    # Initialize AI systems (once per session)
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = AIAnalysisEngine()
    if 'ai_research' not in st.session_state:
        st.session_state.ai_research = AIResearchAssistant(st.session_state.ai_engine)
    if 'stress_builder' not in st.session_state:
        st.session_state.stress_builder = StressTestBuilder()
    if 'audit_system' not in st.session_state:
        st.session_state.audit_system = AuditTrailSystem()

    # Display Salem logo and title
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        st.image("Salem logo.jpg", width=280)
    with col_title:
        st.title("Portfolio Scenario Analysis")
    
    st.markdown("---")
    
    # Tab Navigation
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview",
        "👤 Client & Assumptions",
        "📈 Portfolio Analysis",
        "🎯 Scenario Analysis",
        "🤖 AI Research",
        "📄 Reports & Export"
    ])
    
    with tab1:
        render_overview_tab()
    
    with tab2:
        render_client_tab()
    
    with tab3:
        render_portfolio_tab()
    
    with tab4:
        render_scenarios_tab()
    
    with tab5:
        render_ai_research_tab()
    
    with tab6:
        render_reports_tab()


if __name__ == "__main__":
    main()

