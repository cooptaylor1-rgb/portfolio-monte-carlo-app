import math
from dataclasses import dataclass
from typing import List, Tuple
from datetime import date
import io
import base64

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Salem Investment Counselors Color Scheme
SALEM_GOLD = "#C4A053"  # Gold/tan from logo
SALEM_NAVY = "#1B3B5F"  # Dark blue/navy
SALEM_LIGHT_GOLD = "#D4B87D"  # Lighter gold accent
SALEM_DARK_NAVY = "#0F2540"  # Darker navy


def apply_salem_styling():
    """Apply Apple-inspired premium styling with Salem Investment Counselors branding."""
    st.markdown(f"""
    <style>
        /* Import SF Pro Display font (Apple's signature font) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
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
            padding: 1rem 2rem;
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
            line-height: 1.2 !important;
            letter-spacing: -0.02em;
            margin: 0 !important;
        }}
        
        /* Metrics - Apple card style with subtle shadows */
        .stMetric {{
            background: rgba(255, 255, 255, 0.95);
            padding: 16px 16px;
            border-radius: 12px;
            border: 1px solid rgba(196, 160, 83, 0.2);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0,0,0,0.02);
            backdrop-filter: blur(20px);
            transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
        }}
        .stMetric:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 0 0 1px rgba(196, 160, 83, 0.3);
        }}
        .stMetric label {{
            color: {SALEM_NAVY} !important;
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            opacity: 0.7;
        }}
        .stMetric [data-testid="stMetricValue"] {{
            color: {SALEM_NAVY} !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.03em;
            margin: 4px 0;
        }}
        .stMetric [data-testid="stMetricDelta"] {{
            color: {SALEM_GOLD} !important;
            font-size: 1rem !important;
            font-weight: 600;
        }}
        
        /* Headers - Clean Apple typography */
        h1 {{
            color: {SALEM_NAVY} !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            font-weight: 700 !important;
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.04em;
            line-height: 1.1;
        }}
        h2 {{
            color: {SALEM_NAVY} !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            font-weight: 700 !important;
            font-size: 1.75rem !important;
            margin-top: 1.5rem !important;
            margin-bottom: 0.75rem !important;
            letter-spacing: -0.03em;
            line-height: 1.2;
            border: none;
            padding-bottom: 0;
        }}
        h3 {{
            color: {SALEM_NAVY} !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            font-weight: 600 !important;
            font-size: 1.25rem !important;
            letter-spacing: -0.02em;
            margin-top: 0.75rem !important;
            margin-bottom: 0.25rem !important;
        }}
        h4 {{
            color: {SALEM_NAVY} !important;
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            letter-spacing: -0.02em;
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem !important;
        }}
        
        /* Buttons - Apple style with smooth animations */
        .stButton>button {{
            background: linear-gradient(180deg, {SALEM_GOLD} 0%, #B89648 100%);
            color: white !important;
            font-weight: 600 !important;
            border: none !important;
            padding: 10px 24px !important;
            border-radius: 12px !important;
            font-size: 1rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
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
            transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
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
        
        /* Chart containers - Apple card style */
        [data-testid="stVegaLiteChart"] {{
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(196, 160, 83, 0.15) !important;
            border-radius: 12px !important;
            padding: 12px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0,0,0,0.02) !important;
            backdrop-filter: blur(20px);
            transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
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


def run_monte_carlo(inputs: ModelInputs, seed: int | None = None):
    """Monthly Monte Carlo model. Returns (paths_df, stats_df, metrics_dict)."""
    if seed is not None:
        np.random.seed(seed)

    months = inputs.years_to_model * 12

    # Portfolio-level parameters (annual -> monthly)
    exp_ann, vol_ann = compute_portfolio_return_and_vol(inputs)
    mu_month = (1 + exp_ann) ** (1 / 12) - 1        # geometric monthly mean
    sigma_month = vol_ann / math.sqrt(12)           # monthly vol

    monthly_inflation = (1 + inputs.inflation_annual) ** (1 / 12) - 1

    values = np.zeros((months, inputs.n_scenarios), dtype=float)

    for j in range(inputs.n_scenarios):
        val = inputs.starting_portfolio
        spending = inputs.monthly_spending

        for m in range(months):
            month_index = m + 1
            current_month_age = inputs.current_age + (month_index / 12.0)

            # Spending rule
            if inputs.spending_rule == 1:
                cf = spending
            else:
                cf = -val * (inputs.spending_pct_annual / 12.0)

            # Add income sources based on age
            if inputs.social_security_monthly > 0 and current_month_age >= inputs.ss_start_age:
                cf += inputs.social_security_monthly
            
            if inputs.pension_monthly > 0 and current_month_age >= inputs.pension_start_age:
                cf += inputs.pension_monthly
            
            # Regular income (available from start)
            if inputs.regular_income_monthly > 0:
                cf += inputs.regular_income_monthly
            
            if inputs.other_income_monthly > 0 and current_month_age >= inputs.other_income_start_age:
                cf += inputs.other_income_monthly
            
            # Add spouse Social Security if applicable
            if inputs.is_couple and inputs.spouse_ss_monthly > 0:
                spouse_current_age = inputs.spouse_age + (month_index / 12.0)
                if spouse_current_age >= inputs.spouse_ss_start_age:
                    cf += inputs.spouse_ss_monthly
            
            # Subtract healthcare costs if applicable
            if inputs.healthcare_monthly > 0 and current_month_age >= inputs.healthcare_start_age:
                # Healthcare costs inflate at their own rate
                healthcare_months = month_index - ((inputs.healthcare_start_age - inputs.current_age) * 12)
                if healthcare_months > 0:
                    monthly_hc_infl = (1 + inputs.healthcare_inflation) ** (1 / 12) - 1
                    inflated_hc = inputs.healthcare_monthly * ((1 + monthly_hc_infl) ** healthcare_months)
                    cf -= inflated_hc
                else:
                    cf -= inputs.healthcare_monthly

            # One-time cash flow
            if inputs.one_time_cf_month and month_index == inputs.one_time_cf_month:
                cf += inputs.one_time_cf

            # Apply cash flow then random return
            val = max(val + cf, 0.0)
            rnd = np.random.normal(mu_month, sigma_month)
            val = max(val * (1.0 + rnd), 0.0)

            values[m, j] = val

            # Inflate spending for next month (fixed-$ rule)
            if inputs.spending_rule == 1:
                spending *= (1 + monthly_inflation)

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

    ending_values = values[-1, :]
    min_values = values.min(axis=0)

    prob_never_depleted = np.mean(min_values > 0)
    prob_positive_at_end = np.mean(ending_values > 0)

    metrics = {
        "ending_median": float(np.median(ending_values)),
        "ending_p10": float(np.percentile(ending_values, 10)),
        "ending_p90": float(np.percentile(ending_values, 90)),
        "prob_never_depleted": float(prob_never_depleted),
        "prob_positive_at_end": float(prob_positive_at_end),
    }

    return paths_df, stats_df, metrics


def create_success_gauge(probability: float, title: str = "Plan Success Probability"):
    """Create a visual gauge for success probability."""
    # Determine color based on probability
    if probability >= 0.85:
        color = "#28a745"  # green
        status = "Excellent"
    elif probability >= 0.75:
        color = SALEM_GOLD
        status = "Good"
    elif probability >= 0.65:
        color = "#ffc107"  # yellow
        status = "Moderate"
    else:
        color = "#dc3545"  # red
        status = "At Risk"
    
    # Create gauge visualization using Altair
    gauge_data = pd.DataFrame([
        {"category": "Success", "value": probability * 100, "order": 1},
        {"category": "Risk", "value": (1 - probability) * 100, "order": 2}
    ])
    
    chart = alt.Chart(gauge_data).mark_arc(innerRadius=60, outerRadius=100).encode(
        theta=alt.Theta("value:Q", stack=True),
        color=alt.Color(
            "category:N",
            scale=alt.Scale(
                domain=["Success", "Risk"],
                range=[color, "#e9ecef"]
            ),
            legend=None
        ),
        order=alt.Order("order:Q")
    ).properties(
        width=250,
        height=250,
        title={
            "text": [title, f"{probability*100:.1f}% - {status}"],
            "fontSize": 18,
            "fontWeight": 700,
            "color": SALEM_NAVY
        }
    ).configure_view(
        strokeWidth=0
    )
    
    return chart


def fan_chart(stats_df: pd.DataFrame, title: str = "Portfolio Value – Monte Carlo Fan Chart"):
    # Add Year column for x-axis
    df = stats_df.copy()
    df["Year"] = df["Month"] / 12.0
    
    base = alt.Chart(df).encode(
        x=alt.X("Year:Q", title="Year", 
               axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
    )

    band_10_90 = base.mark_area(opacity=0.15, color=SALEM_LIGHT_GOLD).encode(
        y=alt.Y("P10:Q", title="Portfolio Value", 
               axis=alt.Axis(format="$,.0f", labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
        y2="P90:Q"
    )

    band_25_75 = base.mark_area(opacity=0.3, color=SALEM_GOLD).encode(
        y="P25:Q",
        y2="P75:Q"
    )

    median_line = base.mark_line(size=3, color=SALEM_NAVY).encode(
        y="Median:Q"
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
    )
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
    
    chart = (
        alt.Chart(df)
        .mark_area(opacity=0.6, color="#c94c4c", line={"color": SALEM_DARK_NAVY, "size": 2})
        .encode(
            x=alt.X("Year:Q", title="Year", 
                   axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
            y=alt.Y("Probability:Q", title="Probability of Depletion (%)", 
                   scale=alt.Scale(domain=[0, 100]),
                   axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
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
    
    col1, col2, col3 = st.columns(3)

    with col1:
        equity_return_annual = _percent_input(
            "Equity Return",
            default_fraction=equity_return_default,
            key=f"equity_return_{selected_preset}",
        )
    with col2:
        fi_return_annual = _percent_input(
            "Fixed Income Return",
            default_fraction=fi_return_default,
            key=f"fi_return_{selected_preset}",
        )
    with col3:
        cash_return_annual = _percent_input(
            "Cash Return",
            default_fraction=cash_return_default,
            key=f"cash_return_{selected_preset}",
        )

    # --- Volatility Assumptions ---
    st.subheader("Volatility (Annual)")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        equity_vol_annual = _percent_input(
            "Equity Volatility",
            default_fraction=equity_vol_default,
            key=f"equity_vol_{selected_preset}",
        )
    with col2:
        fi_vol_annual = _percent_input(
            "Fixed Income Volatility",
            default_fraction=fi_vol_default,
            key=f"fi_vol_{selected_preset}",
        )
    with col3:
        cash_vol_annual = _percent_input(
            "Cash Volatility",
            default_fraction=cash_vol_default,
            key=f"cash_vol_{selected_preset}",
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


# -----------------------------
# Main app
# -----------------------------

def main():
    st.set_page_config(
        page_title="Portfolio Scenario Analysis",
        layout="wide",
    )
    
    # Apply Salem Investment Counselors styling
    apply_salem_styling()

    # Display Salem logo and title
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        st.image("Salem logo.jpg", width=280)
    with col_title:
        st.title("Portfolio Scenario Analysis")

    client_info, inputs, stress_scenarios, financial_goals = main_page_inputs()
    
    # Store client_info in session state for PDF generation
    st.session_state.client_info = client_info
    
    # Display client information if provided
    if client_info.client_name:
        st.markdown(f"### Client: {client_info.client_name}")
        col1, col2 = st.columns(2)
        with col1:
            if client_info.advisor_name:
                st.markdown(f"**Advisor:** {client_info.advisor_name}")
        with col2:
            st.markdown(f"**Report Date:** {client_info.report_date.strftime('%B %d, %Y')}")
        st.markdown("---")

    exp_ann, vol_ann = compute_portfolio_return_and_vol(inputs)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Starting Portfolio", f"${inputs.starting_portfolio:,.0f}")
        st.metric("Years to Model", f"{inputs.years_to_model} years")
    with col2:
        if inputs.spending_rule == 1:
            st.metric("Monthly Spending (initial)", f"${-inputs.monthly_spending:,.0f}")
        else:
            # Calculate monthly spending based on percentage of portfolio
            monthly_pct_spending = inputs.starting_portfolio * (inputs.spending_pct_annual / 12.0)
            st.metric("Monthly Spending (initial)", f"${monthly_pct_spending:,.0f}")
        st.metric("Asset Allocation", f"{int(inputs.equity_pct*100)}/{int(inputs.fi_pct*100)}/{int(inputs.cash_pct*100)}")
    with col3:
        st.metric("Portfolio Expected Annual Return (Real)", f"{exp_ann*100:.2f}%")
        st.metric("Portfolio Annual Volatility", f"{vol_ann*100:.2f}%")

    st.markdown("---")

    if st.button("Run Monte Carlo Simulation", type="primary"):
        with st.spinner("Running simulations..."):
            paths_df, stats_df, metrics = run_monte_carlo(inputs)
            
            # Store results in session state for use by comparison and sensitivity tools
            st.session_state.paths_df = paths_df
            st.session_state.stats_df = stats_df
            st.session_state.metrics = metrics
            st.session_state.inputs = inputs
            st.session_state.stress_scenarios = stress_scenarios
            st.session_state.financial_goals = financial_goals
            st.session_state.simulation_run = True

        st.subheader("Key Monte Carlo Results")
    
    # Check if simulation has been run
    if st.session_state.get("simulation_run", False):
        # Retrieve results from session state
        paths_df = st.session_state.paths_df
        stats_df = st.session_state.stats_df
        metrics = st.session_state.metrics
        inputs = st.session_state.inputs
        stress_scenarios = st.session_state.stress_scenarios
        financial_goals = st.session_state.financial_goals

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Median Ending Portfolio", f"${metrics['ending_median']:,.0f}")
        with c2:
            st.metric("10th Percentile Ending Portfolio", f"${metrics['ending_p10']:,.0f}")
        with c3:
            st.metric("90th Percentile Ending Portfolio", f"${metrics['ending_p90']:,.0f}")

        st.metric("Probability Portfolio Never Depletes", f"{metrics['prob_never_depleted']*100:.1f}%")
        
        # --- PROMINENT SUCCESS GAUGE ---
        st.markdown("---")
        st.markdown("## Plan Success Analysis")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            gauge_chart = create_success_gauge(metrics['prob_never_depleted'], "Plan Success Probability")
            st.altair_chart(gauge_chart, use_container_width=False)
        
        # Executive Dashboard
        st.markdown("### Executive Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            shortfall_risk = 1 - metrics['prob_never_depleted']
            # Color code based on risk level
            if shortfall_risk < 0.10:
                risk_indicator = "Low Risk"
                risk_color = "normal"
            elif shortfall_risk < 0.15:
                risk_indicator = "Moderate"
                risk_color = "off"
            else:
                risk_indicator = "High Risk"
                risk_color = "inverse"
            
            st.metric(
                "Shortfall Risk",
                f"{shortfall_risk*100:.1f}%",
                delta=risk_indicator,
                delta_color=risk_color
            )
        with col2:
            p10_positive = (stats_df['P10'].iloc[-1] > 0)
            worst_case_status = "Positive" if p10_positive else "Depleted"
            st.metric(
                "Worst Case (P10)",
                f"${metrics['ending_p10']:,.0f}",
                delta=worst_case_status
            )
        with col3:
            p90_vs_start = ((metrics['ending_p90'] / inputs.starting_portfolio) - 1) * 100
            st.metric(
                "Best Case (P90)",
                f"${metrics['ending_p90']:,.0f}",
                delta=f"+{p90_vs_start:.0f}%" if p90_vs_start > 0 else f"{p90_vs_start:.0f}%"
            )
        with col4:
            median_vs_start = ((metrics['ending_median'] / inputs.starting_portfolio) - 1) * 100
            st.metric(
                "Expected Growth",
                f"{median_vs_start:+.0f}%",
                delta=f"${metrics['ending_median']:,.0f}"
            )
        
        # Display financial goals if any
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

        st.markdown("---")
        st.subheader("Fan Chart of Projected Portfolio Values")

        chart = fan_chart(stats_df)
        st.altair_chart(chart, use_container_width=True)

        st.markdown("---")
        st.subheader("Portfolio Depletion Risk Over Time")
        st.caption(
            "This chart shows the probability that your portfolio will be depleted (reach $0) at each point in time. "
            "Lower percentages indicate lower risk."
        )
        
        depletion_chart = depletion_probability_chart(paths_df, "Base Case: Probability of Portfolio Depletion")
        st.altair_chart(depletion_chart, use_container_width=True)

        # --- Stress Tests section ---
        st.markdown("---")
        st.subheader("Stress Tests (Monte Carlo Simulations)")
        
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

            charts = stress_test_charts(stress_results)
            for scenario_name, fan_chart_obj, depletion_chart_obj in charts:
                st.markdown(f"### {scenario_name}")
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
        
        # --- Scenario Comparison Tool ---
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
                        "allocation": f"{int(inputs.equity_pct*100)}/{int(inputs.fi_pct*100)}/{int(inputs.cash_pct*100)}"
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
                    "allocation": f"{cons_eq}/{cons_fi}/{cons_cash}"
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
                    "allocation": f"{agg_eq}/{agg_fi}/{agg_cash}"
                }
            
            # Display comparison charts
            st.markdown("#### Allocation Comparison Results")
            
            for name, data in base_results.items():
                st.markdown(f"##### {name} ({data['allocation']} Equity/FI/Cash)")
                col1, col2 = st.columns([2, 1])
                with col1:
                    chart = fan_chart(data["stats"], title=f"{name} - Portfolio Projection")
                    st.altair_chart(chart, use_container_width=True)
                with col2:
                    depl_chart = depletion_probability_chart(data["paths"], title=f"{name} - Depletion Risk")
                    st.altair_chart(depl_chart, use_container_width=True)
            
            # Comparison metrics table
            st.markdown("#### Comparison Metrics")
            comparison_data = []
            for name, data in base_results.items():
                last_month = inputs.years_to_model * 12
                ending_row = data["stats"][data["stats"]["Month"] == last_month].iloc[0]
                min_vals = data["paths"].min(axis=0)
                prob_never_depleted = (min_vals > 0).sum() / len(min_vals) * 100
                
                comparison_data.append({
                    "Strategy": name,
                    "Allocation": data["allocation"],
                    "Median Ending": ending_row["Median"],
                    "P10 Ending": ending_row["P10"],
                    "P90 Ending": ending_row["P90"],
                    "Never Depletes": prob_never_depleted
                })
            
            comp_df = pd.DataFrame(comparison_data)
            st.dataframe(
                comp_df.style.format({
                    "Median Ending": "${:,.0f}",
                    "P10 Ending": "${:,.0f}",
                    "P90 Ending": "${:,.0f}",
                    "Never Depletes": "{:.1f}%"
                }),
                use_container_width=True
            )
        
        # --- Sensitivity Analysis ---
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
                chart3 = (
                    alt.Chart(sensitivity_df)
                    .mark_line(point={"size": 100, "filled": True}, strokeWidth=3, color=SALEM_NAVY)
                    .encode(
                        x=alt.X("Change:N", title="Change from Base Case", sort=None,
                               axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
                        y=alt.Y("Success Prob:Q", title="Probability Portfolio Never Depletes (%)", 
                               scale=alt.Scale(domain=[0, 100]),
                               axis=alt.Axis(labelFontSize=14, titleFontSize=16, labelColor=SALEM_NAVY, titleColor=SALEM_NAVY, labelFontWeight=600)),
                        color=alt.Color("Variable:N", title="Variable", 
                                      scale=alt.Scale(range=[SALEM_NAVY, SALEM_GOLD, SALEM_LIGHT_GOLD])),
                        tooltip=["Variable", "Change", "Value", "Success Prob:Q"]
                    )
                    .properties(
                        width="container",
                        height=450,
                        title={
                            "text": "Sensitivity Analysis: Portfolio Success Probability",
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
                st.altair_chart(chart3, use_container_width=True)
                st.caption("Shows probability that portfolio never depletes throughout the planning period")
            
            # Display detailed table
            st.markdown("#### Detailed Sensitivity Results")
            st.dataframe(
                sensitivity_df.style.format({
                    "Median Ending": "${:,.0f}",
                    "P10 Ending": "${:,.0f}",
                    "Success Prob": "{:.1f}%"
                }),
                use_container_width=True
            )
            
            # Heat Map
            st.markdown("---")
            st.markdown("#### Sensitivity Heat Map")
            st.caption("Interactive visualization showing how combinations of changes affect success probability")
            
            if st.button("Generate Heat Map", key="gen_heatmap"):
                with st.spinner("Generating heat map (running 25 simulations)..."):
                    heat_map_chart = create_sensitivity_heat_map(inputs)
                    st.altair_chart(heat_map_chart, use_container_width=True)
                    st.info("**Interpretation**: Darker red = higher risk, Darker green = higher success. Each cell shows the success probability for that combination of changes.")
        
        # --- Interactive What-If Analysis ---
        st.markdown("---")
        st.subheader("Interactive What-If Analysis")
        st.caption("Adjust sliders to see real-time impact on key metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            whatif_spending_delta = st.slider(
                "Spending Change",
                min_value=-50,
                max_value=50,
                value=0,
                step=5,
                key="whatif_spending",
                help="Adjust monthly spending by this percentage"
            )
            
            whatif_return_delta = st.slider(
                "Return Change (Annual)",
                min_value=-4.0,
                max_value=4.0,
                value=0.0,
                step=0.5,
                key="whatif_return",
                help="Adjust expected returns by this percentage"
            )
            
            whatif_portfolio_delta = st.slider(
                "Starting Portfolio Change",
                min_value=-30,
                max_value=30,
                value=0,
                step=5,
                key="whatif_portfolio",
                help="Adjust starting portfolio by this percentage"
            )
        
        with col2:
            if whatif_spending_delta != 0 or whatif_return_delta != 0.0 or whatif_portfolio_delta != 0:
                with st.spinner("Calculating..."):
                    whatif_inputs = ModelInputs(**{k: v for k, v in inputs.__dict__.items()})
                    whatif_inputs.monthly_spending = inputs.monthly_spending * (1 + whatif_spending_delta / 100.0)
                    whatif_inputs.equity_return_annual = inputs.equity_return_annual + (whatif_return_delta / 100.0)
                    whatif_inputs.fi_return_annual = inputs.fi_return_annual + (whatif_return_delta / 100.0)
                    whatif_inputs.cash_return_annual = inputs.cash_return_annual + (whatif_return_delta / 100.0)
                    whatif_inputs.starting_portfolio = inputs.starting_portfolio * (1 + whatif_portfolio_delta / 100.0)
                    
                    _, _, whatif_metrics = run_monte_carlo(whatif_inputs, seed=42)
                    
                    st.markdown("**What-If Results:**")
                    st.metric(
                        "Success Probability",
                        f"{whatif_metrics['prob_never_depleted']*100:.1f}%",
                        delta=f"{(whatif_metrics['prob_never_depleted'] - metrics['prob_never_depleted'])*100:+.1f}%"
                    )
                    st.metric(
                        "Median Ending",
                        f"${whatif_metrics['ending_median']:,.0f}",
                        delta=f"${whatif_metrics['ending_median'] - metrics['ending_median']:+,.0f}"
                    )
                    st.metric(
                        "P10 Ending",
                        f"${whatif_metrics['ending_p10']:,.0f}",
                        delta=f"${whatif_metrics['ending_p10'] - metrics['ending_p10']:+,.0f}"
                    )
            else:
                st.info("👆 Adjust sliders to see how changes impact your results")
        
        # --- Proposal Mode (Comparison View) ---
        st.markdown("---")
        st.subheader("📋 Proposal Mode: Current vs Recommended")
        st.caption("Compare your current plan with proposed changes side-by-side")
        
        with st.expander("Define Recommended Scenario", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Spending Changes**")
                rec_spending = _dollar_input(
                    "Recommended Monthly Spending",
                    default_value=-inputs.monthly_spending,
                    key="rec_spending"
                )
                
                st.markdown("**Allocation Changes**")
                rec_equity = st.slider("Equity %", 0, 100, int(inputs.equity_pct * 100), 5, key="rec_eq")
                rec_fi = st.slider("Fixed Income %", 0, 100, int(inputs.fi_pct * 100), 5, key="rec_fi")
                rec_cash = st.slider("Cash %", 0, 100, int(inputs.cash_pct * 100), 5, key="rec_cash")
            
            with col2:
                st.markdown("**Why this recommendation?**")
                rec_rationale = st.text_area(
                    "Advisor Notes",
                    value="",
                    key="rec_rationale",
                    help="Explain the reasoning behind these recommendations",
                    height=200
                )
        
        if st.button("Run Comparison Analysis", key="run_proposal"):
            with st.spinner("Running comparison..."):
                # Recommended scenario
                rec_inputs = ModelInputs(**{k: v for k, v in inputs.__dict__.items()})
                rec_inputs.monthly_spending = -abs(rec_spending)
                rec_inputs.equity_pct = rec_equity / 100.0
                rec_inputs.fi_pct = rec_fi / 100.0
                rec_inputs.cash_pct = rec_cash / 100.0
                
                rec_paths, rec_stats, rec_metrics = run_monte_carlo(rec_inputs, seed=42)
                
                st.markdown("### Comparison Results")
                
                # Side-by-side metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Metric**")
                    st.markdown("Success Probability")
                    st.markdown("Median Ending")
                    st.markdown("P10 Ending")
                    st.markdown("P90 Ending")
                
                with col2:
                    st.markdown("**Current Plan**")
                    st.markdown(f"{metrics['prob_never_depleted']*100:.1f}%")
                    st.markdown(f"${metrics['ending_median']:,.0f}")
                    st.markdown(f"${metrics['ending_p10']:,.0f}")
                    st.markdown(f"${metrics['ending_p90']:,.0f}")
                
                with col3:
                    st.markdown("**Recommended Plan**")
                    success_delta = (rec_metrics['prob_never_depleted'] - metrics['prob_never_depleted']) * 100
                    st.markdown(f"{rec_metrics['prob_never_depleted']*100:.1f}% ({'+'if success_delta > 0 else ''}{success_delta:.1f}%)")
                    median_delta = rec_metrics['ending_median'] - metrics['ending_median']
                    st.markdown(f"${rec_metrics['ending_median']:,.0f} (${median_delta:+,.0f})")
                    p10_delta = rec_metrics['ending_p10'] - metrics['ending_p10']
                    st.markdown(f"${rec_metrics['ending_p10']:,.0f} (${p10_delta:+,.0f})")
                    p90_delta = rec_metrics['ending_p90'] - metrics['ending_p90']
                    st.markdown(f"${rec_metrics['ending_p90']:,.0f} (${p90_delta:+,.0f})")
                
                # Side-by-side charts
                st.markdown("### Visual Comparison")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Current Plan**")
                    current_chart = fan_chart(stats_df, "Current Plan")
                    st.altair_chart(current_chart, use_container_width=True)
                
                with col2:
                    st.markdown("**Recommended Plan**")
                    rec_chart = fan_chart(rec_stats, "Recommended Plan")
                    st.altair_chart(rec_chart, use_container_width=True)
                
                if rec_rationale:
                    st.markdown("### Advisor Recommendation")
                    st.info(rec_rationale)
        
        # --- RMD PROJECTIONS (Quick Win #1) ---
        if inputs.current_age < inputs.rmd_age and inputs.ira_pct > 0:
            st.markdown("---")
            st.subheader("Required Minimum Distribution (RMD) Projections")
            st.caption("Projected RMDs from Traditional IRA/401(k) accounts")
            
            rmd_df = calculate_rmd_projections(inputs)
            
            if not rmd_df.empty:
                rmd_chart = create_rmd_chart(rmd_df)
                st.altair_chart(rmd_chart, use_container_width=True)
                
                st.markdown("**RMD Summary Table**")
                st.dataframe(
                    rmd_df.style.format({
                        "IRA Balance": "${:,.0f}",
                        "RMD Amount": "${:,.0f}",
                        "Tax on RMD": "${:,.0f}",
                        "After-Tax RMD": "${:,.0f}"
                    }),
                    use_container_width=True
                )
                
                total_rmds = rmd_df["RMD Amount"].sum()
                total_taxes = rmd_df["Tax on RMD"].sum()
                st.info(f"**Total RMDs over planning horizon**: ${total_rmds:,.0f} (Estimated taxes: ${total_taxes:,.0f})")
        
        # --- HISTORICAL BACKTESTING (Quick Win #2) ---
        st.markdown("---")
        st.subheader("Historical Backtesting")
        st.caption("See how your plan would have performed if you retired during past market crises")
        
        historical_years = {
            "2008 Financial Crisis": 2008,
            "2000 Dot-Com Bubble": 2000,
            "1929 Great Depression": 1929,
            "2022 Bear Market": 2022
        }
        
        selected_scenarios = st.multiselect(
            "Select Historical Scenarios to Test",
            options=list(historical_years.keys()),
            default=["2008 Financial Crisis", "2000 Dot-Com Bubble"],
            key="historical_scenarios"
        )
        
        if st.button("Run Historical Backtests", key="run_historical"):
            if selected_scenarios:
                with st.spinner("Running historical simulations..."):
                    historical_results = {}
                    
                    for scenario_name in selected_scenarios:
                        start_year = historical_years[scenario_name]
                        df, metrics_hist = run_historical_backtest(inputs, start_year)
                        historical_results[scenario_name] = {
                            "df": df,
                            "metrics": metrics_hist
                        }
                    
                    # Add current Monte Carlo median for comparison
                    mc_df = pd.DataFrame({
                        "Month": stats_df["Month"],
                        "Value": stats_df["Median"]
                    })
                    historical_results["Monte Carlo (Median)"] = {
                        "df": mc_df,
                        "metrics": {"ending_value": metrics["ending_median"]}
                    }
                    
                    # Display comparison chart
                    hist_chart = create_historical_comparison_chart(historical_results)
                    st.altair_chart(hist_chart, use_container_width=True)
                    
                    # Comparison table
                    st.markdown("**Historical Scenario Comparison**")
                    comparison_data = []
                    for scenario_name, data in historical_results.items():
                        comparison_data.append({
                            "Scenario": scenario_name,
                            "Ending Value": data["metrics"].get("ending_value", 0),
                            "Min Value": data["metrics"].get("min_value", 0) if "min_value" in data["metrics"] else "-",
                            "Max Drawdown": f"{data['metrics'].get('max_drawdown', 0)*100:.1f}%" if "max_drawdown" in data["metrics"] else "-"
                        })
                    
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(
                        comparison_df.style.format({
                            "Ending Value": "${:,.0f}",
                            "Min Value": lambda x: f"${x:,.0f}" if isinstance(x, (int, float)) else x
                        }),
                        use_container_width=True
                    )
                    
                    st.warning("**Note**: Historical results use actual market returns for the selected period. Past performance does not guarantee future results.")
            else:
                st.warning("Please select at least one historical scenario to test.")
        
        # --- SOCIAL SECURITY OPTIMIZATION (Quick Win #3) ---
        if inputs.social_security_monthly > 0:
            st.markdown("---")
            st.subheader("Social Security Claiming Strategy Optimization")
            st.caption("Compare different ages to start Social Security benefits")
            
            ss_df = calculate_social_security_optimization(
                inputs.social_security_monthly,
                inputs.current_age,
                inputs.horizon_age
            )
            
            ss_chart = create_ss_optimization_chart(ss_df)
            st.altair_chart(ss_chart, use_container_width=True)
            
            st.markdown("**Claiming Strategy Comparison**")
            st.dataframe(
                ss_df.style.format({
                    "Monthly Benefit": "${:,.0f}",
                    "Lifetime Total": "${:,.0f}",
                    "vs Age 67": "${:+,.0f}"
                }),
                use_container_width=True
            )
            
            # Find optimal strategy
            optimal_row = ss_df.loc[ss_df["Lifetime Total"].idxmax()]
            st.success(f"**Optimal Strategy**: Claim at age {int(optimal_row['Claiming Age'])} for maximum lifetime benefits of ${optimal_row['Lifetime Total']:,.0f}")
            
            # Breakeven analysis
            if len(ss_df) > 1:
                st.info("**Breakeven Analysis**: Claiming later provides higher monthly benefits but fewer years of payments. Consider your health, longevity expectations, and need for current income.")
            
            # Separate by variable for clarity
            for variable in ["Portfolio Return", "Monthly Spending", "Starting Portfolio"]:
                var_data = sensitivity_df[sensitivity_df["Variable"] == variable].copy()
                var_data = var_data.sort_values("Sort")
                var_data = var_data[["Change", "Value", "Median Ending", "P10 Ending", "Success Prob"]]
                
                st.markdown(f"**{variable}**")
                st.dataframe(
                    var_data.style.format({
                        "Median Ending": "${:,.0f}",
                        "P10 Ending": "${:,.0f}",
                        "Success Prob": "{:.1f}%"
                    }).hide(axis="index"),
                    use_container_width=True
                )
        
        # --- PDF Report Generation ---
        st.markdown("---")
        st.subheader("📄 Generate PDF Report")
        st.caption("Create a comprehensive PDF report with selected sections from this analysis")
        
        with st.expander("Configure and Generate PDF Report", expanded=False):
            st.markdown("##### Select Report Sections")
            
            col1, col2 = st.columns(2)
            
            with col1:
                include_title = st.checkbox("Title Page", value=True, key="pdf_title")
                include_summary = st.checkbox("Executive Summary", value=True, key="pdf_summary")
                include_assumptions = st.checkbox("Portfolio Assumptions", value=True, key="pdf_assumptions")
            
            with col2:
                include_goals = st.checkbox("Financial Goals", value=bool(financial_goals), 
                                          disabled=not financial_goals, key="pdf_goals")
                include_stress = st.checkbox("Stress Test Results", value=bool(stress_results), 
                                            disabled=not stress_results, key="pdf_stress")
                include_disclaimer = st.checkbox("Disclaimer", value=True, key="pdf_disclaimer")
            
            st.markdown("---")
            
            if st.button("Generate PDF Report", type="primary"):
                # Collect selected sections
                selected_sections = []
                if include_title:
                    selected_sections.append('title_page')
                if include_summary:
                    selected_sections.append('executive_summary')
                if include_assumptions:
                    selected_sections.append('assumptions')
                if include_goals and financial_goals:
                    selected_sections.append('financial_goals')
                if include_stress and stress_results:
                    selected_sections.append('stress_tests')
                if include_disclaimer:
                    selected_sections.append('disclaimer')
                
                if not selected_sections:
                    st.warning("Please select at least one section to include in the report.")
                else:
                    with st.spinner("Generating PDF report..."):
                        try:
                            # Calculate goal results if needed
                            goal_results_pdf = None
                            if 'financial_goals' in selected_sections and financial_goals:
                                goal_results_pdf = calculate_goal_probabilities(paths_df, financial_goals, inputs.current_age)
                            
                            # Generate PDF
                            pdf_buffer = generate_pdf_report(
                                client_info=st.session_state.get('client_info', ClientInfo()),
                                inputs=inputs,
                                metrics=metrics,
                                stats_df=stats_df,
                                paths_df=paths_df,
                                stress_results=stress_results if 'stress_tests' in selected_sections else {},
                                financial_goals=financial_goals if 'financial_goals' in selected_sections else [],
                                goal_results=goal_results_pdf,
                                selected_sections=selected_sections
                            )
                            
                            # Create download button
                            client_name = st.session_state.get('client_info', ClientInfo()).client_name or "Client"
                            filename = f"Portfolio_Analysis_{client_name.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.pdf"
                            
                            st.success("PDF report generated successfully!")
                            st.download_button(
                                label="Download PDF Report",
                                data=pdf_buffer.getvalue(),
                                file_name=filename,
                                mime="application/pdf",
                                type="primary"
                            )
                        except Exception as e:
                            st.error(f"Error generating PDF: {str(e)}")
                            st.error("Please ensure all required data is available and try again.")
    
    # --- MEETING PRESENTATION MODE (Quick Win #5) ---
    st.markdown("---")
    meeting_mode = st.checkbox("Meeting Presentation Mode", value=False, key="meeting_mode",
                               help="Enable this for client presentations - hides input controls on page reload")
    
    if meeting_mode:
        st.info("**Presentation Mode Enabled** - Reload the page to hide input controls and show clean results for client presentations.")

    else:
        st.info("Adjust inputs in the sidebar and click **Run Monte Carlo Simulation** to see results.")


if __name__ == "__main__":
    main()
