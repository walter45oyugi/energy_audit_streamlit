import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import os
import base64

# Page configuration
st.set_page_config(
    page_title="Energy Audit Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white;
    }
    [data-testid="stSidebar"] .css-1d391kg {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
    }
    [data-testid="stSidebar"] .css-1d391kg .css-1d391kg {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
    }
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        border-left: 4px solid #1a237e;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .insight-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left: 4px solid #9c27b0;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .sidebar-logo {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    .sidebar-logo img {
        max-width: 250px;
        height: auto;
        border-radius: 10px;
    }
    .sidebar-title {
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .sidebar-nav {
        color: white;
    }
    .sidebar-nav .stSelectbox {
        color: white;
    }
    .sidebar-nav .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.1);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def get_logo_base64():
    """Get the logo as base64 for embedding"""
    try:
        logo_path = Path("Strathmore-University-Logo.png")
        if logo_path.exists():
            with open(logo_path, "rb") as f:
                data = f.read()
                return base64.b64encode(data).decode()
        return None
    except:
        return None

@st.cache_data
def load_station_data(station):
    """Load data for a specific station with caching"""
    try:
        if station == 'mvule':
            file_path = Path('MVULE corrected time.xlsx')
        else:  # clinic
            file_path = Path('Clinic corrected time.xlsx')
        
        if file_path.exists():
            df = pd.read_excel(file_path)
            
            # Try different possible time column names
            time_columns = [
                'Stop(E. Africa Standard Time)',
                'Start/Stop(E. Africa Standard Time)',
                'Time',
                'DateTime',
                'Timestamp'
            ]
            
            time_col = None
            for col in time_columns:
                if col in df.columns:
                    time_col = col
                    break
            
            if time_col:
                df[time_col] = pd.to_datetime(df[time_col])
                df = df.set_index(time_col)
                return df
            else:
                st.error(f"Time column not found in {station} data. Available columns: {list(df.columns)}")
                return None
        else:
            st.error(f"File not found: {file_path}")
            return None
    except Exception as e:
        st.error(f"Error loading data for {station}: {e}")
        return None

def calculate_daily_averages(df):
    """Calculate daily averages for KPI metrics"""
    if df is None or df.empty:
        return {}
    
    try:
        # Calculate KPIs directly from the data (not daily averages)
        kpis = {
            'avg_power': df.get('PowerP_Total_avg', pd.Series()).mean(),
            'avg_pf': df.get('PfFwdRev_Total_avg', pd.Series()).mean(),
            'avg_voltage': df.get('Vrms_AN_avg', pd.Series()).mean(),
            'avg_current': df.get('Irms_A_avg', pd.Series()).mean(),
            'avg_frequency': df.get('Frequency_avg', pd.Series()).mean(),
            'avg_vthd': df.get('Vthd_AN_avg', pd.Series()).mean(),
            'avg_ithd': df.get('Ithd_A_avg', pd.Series()).mean(),
            'data_points': len(df),
        }
        
        # Convert power from W to kW
        if 'avg_power' in kpis and not pd.isna(kpis['avg_power']):
            kpis['avg_power'] = kpis['avg_power'] / 1000
        
        return kpis
    except Exception as e:
        st.error(f"Error calculating averages: {e}")
        return {}

def create_frequency_chart(df, station):
    """Create frequency analysis chart"""
    if df is None or df.empty or 'Frequency_avg' not in df.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Frequency_avg'],
        mode='lines',
        name='Frequency (Hz)',
        line=dict(color='blue', width=2)
    ))
    
    # Add reference lines for acceptable frequency range
    fig.add_hline(y=50.5, line_dash="dash", line_color="red", 
                  annotation_text="Upper Limit (50.5 Hz)")
    fig.add_hline(y=49.5, line_dash="dash", line_color="red", 
                  annotation_text="Lower Limit (49.5 Hz)")
    
    fig.update_layout(
        title=f'{station.title()} Station - Frequency Analysis',
        xaxis_title='Time',
        yaxis_title='Frequency (Hz)',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_voltage_thd_chart(df, station):
    """Create voltage THD analysis chart"""
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Add voltage THD data
    vthd_cols = [col for col in df.columns if 'Vthd' in col and 'avg' in col]
    colors = ['red', 'green', 'blue']
    for i, col in enumerate(vthd_cols):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=f'{col.replace("_avg", "")} (%)',
            line=dict(color=colors[i], width=2)
        ))
    
    # Add reference line for acceptable THD
    fig.add_hline(y=5, line_dash="dash", line_color="orange", 
                  annotation_text="Acceptable Limit (5%)")
    
    fig.update_layout(
        title=f'{station.title()} Station - Voltage THD Analysis',
        xaxis_title='Time',
        yaxis_title='Voltage THD (%)',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_voltage_analysis_chart(df, station):
    """Create voltage analysis chart"""
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Add line-to-neutral voltage data
    vln_cols = [col for col in df.columns if 'Vrms_AN_avg' in col or 'Vrms_BN_avg' in col or 'Vrms_CN_avg' in col]
    colors = ['red', 'green', 'blue']
    for i, col in enumerate(vln_cols):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col.replace('_avg', ''),
            line=dict(color=colors[i], width=2)
        ))
    
    # Add reference lines for acceptable voltage range
    fig.add_hline(y=253, line_dash="dash", line_color="red", 
                  annotation_text="Upper Limit (253V)")
    fig.add_hline(y=207, line_dash="dash", line_color="red", 
                  annotation_text="Lower Limit (207V)")
    
    fig.update_layout(
        title=f'{station.title()} Station - Line-to-Neutral Voltage Analysis',
        xaxis_title='Time',
        yaxis_title='Voltage (V)',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_line_to_line_voltage_chart(df, station):
    """Create line-to-line voltage analysis chart"""
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Add line-to-line voltage data
    vll_cols = [col for col in df.columns if 'Vrms_AB_avg' in col or 'Vrms_BC_avg' in col or 'Vrms_CA_avg' in col]
    colors = ['purple', 'orange', 'brown']
    for i, col in enumerate(vll_cols):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col.replace('_avg', ''),
            line=dict(color=colors[i], width=2)
        ))
    
    # Add reference lines for acceptable voltage range
    fig.add_hline(y=440, line_dash="dash", line_color="red", 
                  annotation_text="Upper Limit (440V)")
    fig.add_hline(y=360, line_dash="dash", line_color="red", 
                  annotation_text="Lower Limit (360V)")
    
    fig.update_layout(
        title=f'{station.title()} Station - Line-to-Line Voltage Analysis',
        xaxis_title='Time',
        yaxis_title='Voltage (V)',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_current_analysis_chart(df, station):
    """Create current analysis chart"""
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Add current data
    current_cols = [col for col in df.columns if 'Irms_A_avg' in col or 'Irms_B_avg' in col or 'Irms_C_avg' in col]
    colors = ['red', 'green', 'blue']
    for i, col in enumerate(current_cols):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col.replace('_avg', ''),
            line=dict(color=colors[i], width=2)
        ))
    
    fig.update_layout(
        title=f'{station.title()} Station - Current Analysis',
        xaxis_title='Time',
        yaxis_title='Current (A)',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_current_thd_chart(df, station):
    """Create current THD analysis chart"""
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Add current THD data
    ithd_cols = [col for col in df.columns if 'Ithd' in col and 'avg' in col]
    colors = ['purple', 'orange', 'brown']
    for i, col in enumerate(ithd_cols):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=f'{col.replace("_avg", "")} (%)',
            line=dict(color=colors[i], width=2)
        ))
    
    # Add reference line for acceptable THD
    fig.add_hline(y=8, line_dash="dash", line_color="orange", 
                  annotation_text="Acceptable Limit (8%)")
    
    fig.update_layout(
        title=f'{station.title()} Station - Current THD Analysis',
        xaxis_title='Time',
        yaxis_title='Current THD (%)',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_power_factor_chart(df, station):
    """Create power factor analysis chart"""
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Add power factor data
    pf_cols = [col for col in df.columns if 'PfFwdRev' in col and 'avg' in col]
    for col in pf_cols:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col.replace('_avg', ''),
            line=dict(color='blue', width=2)
        ))
    
    # Add reference line for acceptable power factor
    fig.add_hline(y=0.9, line_dash="dash", line_color="orange", 
                  annotation_text="Recommended (0.9)")
    
    fig.update_layout(
        title=f'{station.title()} Station - Power Factor Analysis',
        xaxis_title='Time',
        yaxis_title='Power Factor',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_active_power_chart(df, station):
    """Create active power analysis chart"""
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Add power data (convert to kW)
    power_cols = [col for col in df.columns if 'PowerP_' in col and 'avg' in col]
    colors = ['red', 'green', 'blue', 'purple']
    for i, col in enumerate(power_cols):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col] / 1000,  # Convert to kW
            mode='lines',
            name=f'{col.replace("_avg", "")} (kW)',
            line=dict(color=colors[i], width=2)
        ))
    
    fig.update_layout(
        title=f'{station.title()} Station - Active Power Analysis',
        xaxis_title='Time',
        yaxis_title='Power (kW)',
        height=400,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

# Main app
def main():
    # Sidebar with logo
    with st.sidebar:
        # Logo at the top of sidebar
        logo_base64 = get_logo_base64()
        if logo_base64:
            st.markdown(f"""
            <div class="sidebar-logo">
                <img src="data:image/png;base64,{logo_base64}" alt="Strathmore University Logo">
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-title">Energy Audit Dashboard</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
        page = st.selectbox(
            "Choose a page",
            ["Overview", "Mvule Station", "Clinic Station"]
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1><i class="fas fa-tachometer-alt"></i> Energy Audit Dashboard</h1>
        <p>Comprehensive analysis of power consumption and quality metrics for both stations</p>
    </div>
    """, unsafe_allow_html=True)
    
    if page == "Overview":
        show_overview()
    elif page == "Mvule Station":
        show_station_analysis("mvule", "Mvule")
    elif page == "Clinic Station":
        show_station_analysis("clinic", "Clinic")

def show_overview():
    """Show the main overview page"""
    st.markdown("## Overview Dashboard")
    
    # Load data
    mvule_data = load_station_data('mvule')
    clinic_data = load_station_data('clinic')
    
    # Calculate KPIs
    mvule_kpis = calculate_daily_averages(mvule_data)
    clinic_kpis = calculate_daily_averages(clinic_data)
    
    # KPI Cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Mvule Station")
        if mvule_kpis:
            st.metric("Average Power", f"{mvule_kpis.get('avg_power', 0):.1f} kW")
            st.metric("Average Power Factor", f"{mvule_kpis.get('avg_pf', 0):.2f}")
            st.metric("Average Voltage", f"{mvule_kpis.get('avg_voltage', 0):.0f} V")
        else:
            st.warning("No data available for Mvule Station")
    
    with col2:
        st.markdown("### Clinic Station")
        if clinic_kpis:
            st.metric("Average Power", f"{clinic_kpis.get('avg_power', 0):.1f} kW")
            st.metric("Average Power Factor", f"{clinic_kpis.get('avg_pf', 0):.2f}")
            st.metric("Average Voltage", f"{clinic_kpis.get('avg_voltage', 0):.0f} V")
        else:
            st.warning("No data available for Clinic Station")
    
    # Key Findings
    st.markdown("## Key Findings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
            <h6>⚡ Power Factor Issues</h6>
            <p>Both stations show power factor values below the recommended 0.9, indicating significant reactive power consumption.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="insight-box">
            <h6>📊 Harmonic Distortion</h6>
            <p>Current THD frequently exceeds acceptable limits, particularly during low-load periods when solar generation dominates.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-box">
            <h6>⚖️ Load Imbalance</h6>
            <p>Current and voltage imbalances detected across phases, with some phases showing significantly higher loads.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="insight-box">
            <h6>☀️ Solar Integration</h6>
            <p>Grid-tied solar system shows power quality challenges during transitions between solar and grid power sources.</p>
        </div>
        """, unsafe_allow_html=True)

def show_station_analysis(station, station_name):
    """Show detailed analysis for a specific station"""
    st.markdown(f"## {station_name} Station Analysis")
    
    # Load data
    df = load_station_data(station)
    kpis = calculate_daily_averages(df)
    
    if df is None or df.empty:
        st.error(f"No data available for {station_name} Station")
        return
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average Power", f"{kpis.get('avg_power', 0):.1f} kW")
    
    with col2:
        st.metric("Average Power Factor", f"{kpis.get('avg_pf', 0):.2f}")
    
    with col3:
        st.metric("Average Voltage", f"{kpis.get('avg_voltage', 0):.0f} V")
    
    with col4:
        st.metric("Average Current", f"{kpis.get('avg_current', 0):.1f} A")
    
    # Analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Power Quality", "Voltage", "Current", "Harmonics", "Power Factor"
    ])
    
    with tab1:
        st.markdown("### Power Quality Analysis")
        
        # Frequency Analysis
        st.markdown("#### Frequency Analysis")
        freq_fig = create_frequency_chart(df, station)
        if freq_fig:
            st.plotly_chart(freq_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>📊 Frequency Insights</h6>
                <p>Frequency variations are monitored to ensure grid stability. Values should remain within 49.5-50.5 Hz range.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Voltage THD Analysis
        st.markdown("#### Voltage THD Analysis")
        vthd_fig = create_voltage_thd_chart(df, station)
        if vthd_fig:
            st.plotly_chart(vthd_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>⚡ Voltage THD Insights</h6>
                <p>Voltage THD should remain below 5% to ensure power quality. Higher values indicate harmonic distortion.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Voltage Analysis")
        
        # Line-to-Neutral Voltage
        st.markdown("#### Line-to-Neutral Voltage Analysis")
        vln_fig = create_voltage_analysis_chart(df, station)
        if vln_fig:
            st.plotly_chart(vln_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>⚡ Line-to-Neutral Voltage Insights</h6>
                <p>Voltage should remain within 207-253V range. Variations indicate load changes or grid issues.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Line-to-Line Voltage
        st.markdown("#### Line-to-Line Voltage Analysis")
        vll_fig = create_line_to_line_voltage_chart(df, station)
        if vll_fig:
            st.plotly_chart(vll_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>⚡ Line-to-Line Voltage Insights</h6>
                <p>Line-to-line voltage should remain within 360-440V range. Imbalances indicate phase loading issues.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### Current Analysis")
        
        # Current Analysis
        st.markdown("#### Current Distribution")
        current_fig = create_current_analysis_chart(df, station)
        if current_fig:
            st.plotly_chart(current_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>⚖️ Current Distribution Insights</h6>
                <p>Current should be balanced across phases. Imbalances indicate uneven load distribution.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Current THD Analysis
        st.markdown("#### Current THD Analysis")
        ithd_fig = create_current_thd_chart(df, station)
        if ithd_fig:
            st.plotly_chart(ithd_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>📊 Current THD Insights</h6>
                <p>Current THD should remain below 8%. Higher values indicate harmonic distortion from non-linear loads.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### Harmonics Analysis")
        
        # Voltage THD
        st.markdown("#### Voltage THD Analysis")
        vthd_fig = create_voltage_thd_chart(df, station)
        if vthd_fig:
            st.plotly_chart(vthd_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>⚡ Voltage Harmonics Insights</h6>
                <p>Voltage THD indicates power quality. Values above 5% require harmonic filtering.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Current THD
        st.markdown("#### Current THD Analysis")
        ithd_fig = create_current_thd_chart(df, station)
        if ithd_fig:
            st.plotly_chart(ithd_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>📊 Current Harmonics Insights</h6>
                <p>Current THD indicates load characteristics. High values suggest non-linear loads or harmonic resonance.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### Power Factor Analysis")
        
        # Power Factor
        st.markdown("#### Power Factor Analysis")
        pf_fig = create_power_factor_chart(df, station)
        if pf_fig:
            st.plotly_chart(pf_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>📉 Power Factor Insights</h6>
                <p>Power factor should be close to 1.0. Low values indicate reactive power consumption.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Active Power
        st.markdown("#### Active Power Analysis")
        power_fig = create_active_power_chart(df, station)
        if power_fig:
            st.plotly_chart(power_fig, use_container_width=True)
            st.markdown("""
            <div class="insight-box">
                <h6>⚡ Active Power Insights</h6>
                <p>Active power shows real energy consumption. Patterns indicate load profiles and efficiency.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 