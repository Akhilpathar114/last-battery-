import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
from datetime import datetime, timedelta
import numpy as np
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Battery Cell Monitoring Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for better styling and animations
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .health-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .health-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.6s ease;
    }
    
    .health-card:hover::before {
        animation: shine 0.6s ease-in-out;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .health-excellent {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        animation: pulse-green 2s infinite;
    }
    
    .health-good {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .health-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        animation: pulse-orange 2s infinite;
    }
    
    .health-critical {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        animation: pulse-red 1s infinite;
    }
    
    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 8px 25px rgba(17, 153, 142, 0.3); }
        50% { box-shadow: 0 8px 35px rgba(17, 153, 142, 0.6); }
    }
    
    @keyframes pulse-orange {
        0%, 100% { box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3); }
        50% { box-shadow: 0 8px 35px rgba(240, 147, 251, 0.6); }
    }
    
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 8px 25px rgba(255, 65, 108, 0.4); }
        50% { box-shadow: 0 8px 35px rgba(255, 65, 108, 0.8); }
    }
    
    .status-excellent {
        color: #00ff88;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    .status-good {
        color: #28a745;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(40, 167, 69, 0.5);
    }
    
    .status-warning {
        color: #ff6b35;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 107, 53, 0.5);
        animation: blink 1.5s infinite;
    }
    
    .status-critical {
        color: #ff3838;
        font-weight: bold;
        text-shadow: 0 0 15px rgba(255, 56, 56, 0.8);
        animation: blink 0.8s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.6; }
    }
    
    .battery-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
        display: block;
    }
    
    .health-percentage {
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .cell-name {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 5px;
        opacity: 0.9;
    }
    
    .overview-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        margin: 10px 0;
    }
    
    .overview-number {
        font-size: 2rem;
        font-weight: bold;
        display: block;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .overview-label {
        font-size: 0.9rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .parameter-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    
    .export-button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .export-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
    }
    
    .process-status {
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .status-running {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        animation: pulse-green 2s infinite;
    }
    
    .status-stopped {
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        color: white;
    }
    
    .status-completed {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = []
if 'is_monitoring' not in st.session_state:
    st.session_state.is_monitoring = False
if 'process_start_time' not in st.session_state:
    st.session_state.process_start_time = None
if 'process_parameters' not in st.session_state:
    st.session_state.process_parameters = {}
if 'total_test_duration' not in st.session_state:
    st.session_state.total_test_duration = 0
if 'elapsed_time' not in st.session_state:
    st.session_state.elapsed_time = 0

# Cell type configurations with enhanced colors
CELL_CONFIGS = {
    "LFP": {
        "nominal_voltage": 3.2,
        "min_voltage": 2.8,
        "max_voltage": 3.6,
        "color": "#00ff88",
        "gradient": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
        "capacity_range": (2.5, 3.5),
        "temp_range": (-20, 60)
    },
    "NMC": {
        "nominal_voltage": 3.6,
        "min_voltage": 3.2,
        "max_voltage": 4.0,
        "color": "#ff6b6b",
        "gradient": "linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%)",
        "capacity_range": (2.8, 3.2),
        "temp_range": (-10, 50)
    },
    "LTO": {
        "nominal_voltage": 2.4,
        "min_voltage": 1.5,
        "max_voltage": 2.8,
        "color": "#ffa726",
        "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "capacity_range": (1.8, 2.8),
        "temp_range": (-30, 55)
    },
    "LiCoO2": {
        "nominal_voltage": 3.7,
        "min_voltage": 3.0,
        "max_voltage": 4.2,
        "color": "#ab47bc",
        "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "capacity_range": (2.0, 3.0),
        "temp_range": (0, 45)
    }
}

def get_battery_icon(health):
    """Return battery icon based on health percentage"""
    if health >= 90:
        return "🔋"  # Full battery
    elif health >= 75:
        return "🔋"  # Good battery
    elif health >= 50:
        return "🪫"  # Medium battery
    elif health >= 25:
        return "🪫"  # Low battery
    else:
        return "🪫"  # Critical battery

def get_health_class(health):
    """Return CSS class based on health percentage"""
    if health >= 90:
        return "health-excellent"
    elif health >= 75:
        return "health-good"
    elif health >= 50:
        return "health-warning"
    else:
        return "health-critical"

def get_status_class(status):
    """Return CSS class based on status"""
    if status == "Excellent":
        return "status-excellent"
    elif status == "Good":
        return "status-good"
    elif status == "Warning":
        return "status-warning"
    else:
        return "status-critical"

def generate_cell_data(cell_type, cell_id, current_time, process_params=None):
    """Generate realistic battery cell data with enhanced status based on process parameters"""
    config = CELL_CONFIGS[cell_type]
    
    # Apply process parameters if available
    if process_params:
        # Simulate effects of process parameters
        voltage_offset = 0
        temp_offset = 0
        
        # Charging/Discharging rate effects
        if process_params.get('charge_rate', 0) > 2:
            voltage_offset += random.uniform(0.02, 0.05)
            temp_offset += random.uniform(2, 5)
        elif process_params.get('discharge_rate', 0) > 2:
            voltage_offset -= random.uniform(0.02, 0.05)
            temp_offset += random.uniform(1, 3)
            
        # Temperature control effects
        target_temp = process_params.get('target_temperature', 25)
        temp_variation = random.uniform(-2, 2)
        temperature = target_temp + temp_variation + temp_offset
        
        # Voltage with process effects
        base_voltage = config["nominal_voltage"] + voltage_offset
        voltage_variation = random.uniform(-0.05, 0.05)
        voltage = round(base_voltage + voltage_variation, 3)
    else:
        # Default behavior
        base_voltage = config["nominal_voltage"]
        voltage_variation = random.uniform(-0.1, 0.1)
        voltage = round(base_voltage + voltage_variation, 3)
        
        base_temp = 25
        temp_variation = random.uniform(-2, 8)
        temperature = round(base_temp + temp_variation, 1)
    
    # Simulate current based on process parameters
    if process_params:
        charge_rate = process_params.get('charge_rate', 0)
        discharge_rate = process_params.get('discharge_rate', 0)
        
        if charge_rate > 0:
            current = round(random.uniform(charge_rate * 0.8, charge_rate * 1.2), 2)
        elif discharge_rate > 0:
            current = round(random.uniform(-discharge_rate * 1.2, -discharge_rate * 0.8), 2)
        else:
            current = round(random.uniform(-5.0, 5.0), 2)
    else:
        current = round(random.uniform(-5.0, 5.0), 2)
    
    # Calculate power and capacity
    power = round(voltage * abs(current), 2)
    capacity = round(random.uniform(*config["capacity_range"]), 2)
    
    # Enhanced health calculation with process parameter effects
    voltage_health = 100 * (1 - abs(voltage - config["nominal_voltage"]) / config["nominal_voltage"])
    temp_health = 100 * max(0, 1 - max(0, temperature - 35) / 20)
    
    # Process stress factor
    stress_factor = 1.0
    if process_params:
        if abs(current) > 3:
            stress_factor *= 0.98
        if temperature > 40:
            stress_factor *= 0.95
    
    overall_health = round((voltage_health + temp_health) / 2 * stress_factor, 1)
    
    # Enhanced status determination
    if voltage < config["min_voltage"] or voltage > config["max_voltage"] or temperature > 50:
        status = "Critical"
    elif temperature > 45 or overall_health < 75:
        status = "Warning"
    elif overall_health >= 90:
        status = "Excellent"
    else:
        status = "Good"
    
    return {
        "cell_id": cell_id,
        "cell_type": cell_type,
        "voltage": voltage,
        "current": current,
        "temperature": temperature,
        "power": power,
        "capacity": capacity,
        "health": overall_health,
        "status": status,
        "timestamp": current_time,
        "min_voltage": config["min_voltage"],
        "max_voltage": config["max_voltage"],
        "stress_factor": stress_factor
    }

def export_to_csv(data, filename_prefix="battery_data"):
    """Export data to CSV format"""
    if not data:
        return None
    
    # Create DataFrame from current data
    df = pd.DataFrame(data.values())
    
    # Add timestamp formatting
    df['formatted_timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Reorder columns for better readability
    columns_order = [
        'formatted_timestamp', 'cell_id', 'cell_type', 'voltage', 'current', 
        'temperature', 'power', 'capacity', 'health', 'status', 
        'min_voltage', 'max_voltage', 'stress_factor'
    ]
    df = df[columns_order]
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    return df, filename

def export_historical_to_csv(historical_data, filename_prefix="battery_historical"):
    """Export historical data to CSV format"""
    if not historical_data:
        return None, None
    
    # Flatten historical data
    flattened_data = []
    for record in historical_data:
        for cell_id, cell_data in record["data"].items():
            row = cell_data.copy()
            row['record_timestamp'] = record["timestamp"]
            flattened_data.append(row)
    
    df = pd.DataFrame(flattened_data)
    
    # Format timestamps
    df['formatted_timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['formatted_record_timestamp'] = df['record_timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    return df, filename

# Main Dashboard
st.markdown('<h1 class="main-header">🔋 Battery Cell Monitoring Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Bench and group information
    bench_name = st.text_input("Bench Name", value="Bench-001", key="bench_name")
    group_num = st.number_input("Group Number", min_value=1, max_value=100, value=1, key="group_num")
    
    st.divider()
    
    # Process Parameters Section
    st.subheader("🔧 Process Parameters")
    with st.expander("⚙️ Test Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            test_duration = st.number_input(
                "Test Duration (hours)", 
                min_value=0.1, 
                max_value=168.0, 
                value=2.0, 
                step=0.1,
                help="Total duration for the battery test"
            )
            
            charge_rate = st.number_input(
                "Charge Rate (A)", 
                min_value=0.0, 
                max_value=10.0, 
                value=1.0, 
                step=0.1,
                help="Charging current in Amperes"
            )
            
            target_temperature = st.number_input(
                "Target Temperature (°C)", 
                min_value=-40, 
                max_value=80, 
                value=25, 
                step=1,
                help="Target operating temperature"
            )
        
        with col2:
            discharge_rate = st.number_input(
                "Discharge Rate (A)", 
                min_value=0.0, 
                max_value=10.0, 
                value=1.0, 
                step=0.1,
                help="Discharging current in Amperes"
            )
            
            sampling_interval = st.number_input(
                "Sampling Interval (seconds)", 
                min_value=1, 
                max_value=60, 
                value=5, 
                step=1,
                help="Data collection frequency"
            )
            
            safety_voltage_limit = st.number_input(
                "Safety Voltage Limit (V)", 
                min_value=2.0, 
                max_value=5.0, 
                value=4.2, 
                step=0.1,
                help="Maximum safe voltage threshold"
            )
    
    # Store process parameters
    st.session_state.process_parameters = {
        'test_duration': test_duration,
        'charge_rate': charge_rate,
        'discharge_rate': discharge_rate,
        'target_temperature': target_temperature,
        'sampling_interval': sampling_interval,
        'safety_voltage_limit': safety_voltage_limit
    }
    st.session_state.total_test_duration = test_duration
    
    st.divider()
    
    # Cell configuration
    st.subheader("🔋 Cell Configuration")
    num_cells = st.slider("Number of Cells", min_value=1, max_value=16, value=8)
    
    cell_types = []
    for i in range(num_cells):
        cell_type = st.selectbox(
            f"Cell {i+1} Type",
            options=list(CELL_CONFIGS.keys()),
            key=f"cell_type_{i}",
            help=f"Select battery chemistry for Cell {i+1}"
        )
        cell_types.append(cell_type)
    
    st.divider()
    
    # Control panel
    st.subheader("🎛️ Control Panel")
    
    if st.button("🚀 Initialize Test", type="primary", use_container_width=True):
        current_time = datetime.now()
        st.session_state.cells_data = {}
        st.session_state.historical_data = []
        st.session_state.process_start_time = current_time
        st.session_state.elapsed_time = 0
        
        for i, cell_type in enumerate(cell_types):
            cell_id = f"Cell_{i+1}_{cell_type}"
            st.session_state.cells_data[cell_id] = generate_cell_data(
                cell_type, cell_id, current_time, st.session_state.process_parameters
            )
        st.success("🎉 Test initialized successfully!")
    
    # Process status display
    if st.session_state.process_start_time:
        current_time = datetime.now()
        elapsed = (current_time - st.session_state.process_start_time).total_seconds() / 3600
        st.session_state.elapsed_time = elapsed
        
        progress = min(elapsed / st.session_state.total_test_duration, 1.0)
        remaining_time = max(st.session_state.total_test_duration - elapsed, 0)
        
        if st.session_state.is_monitoring:
            if progress >= 1.0:
                st.markdown("""
                <div class="process-status status-completed">
                    ✅ Test Completed
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="process-status status-running">
                    🔄 Test In Progress
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="process-status status-stopped">
                ⏸️ Test Paused
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(progress)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("⏱️ Elapsed", f"{elapsed:.1f}h")
        with col2:
            st.metric("⏳ Remaining", f"{remaining_time:.1f}h")
    
    # Monitoring controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.is_monitoring = True
            if not st.session_state.process_start_time:
                st.session_state.process_start_time = datetime.now()
            st.success("Monitoring started!")
    
    with col2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.is_monitoring = False
            st.info("Monitoring paused!")
    
    # Reset button
    if st.button("🔄 Reset Test", use_container_width=True, type="secondary"):
        st.session_state.is_monitoring = False
        st.session_state.process_start_time = None
        st.session_state.elapsed_time = 0
        st.session_state.cells_data = {}
        st.session_state.historical_data = []
        st.info("Test reset successfully!")
    
    st.divider()
    
    # Export Section
    st.subheader("💾 Data Export")
    
    # Current data export
    if st.session_state.cells_data:
        if st.button("📊 Export Current Data", use_container_width=True):
            df, filename = export_to_csv(st.session_state.cells_data, f"{bench_name}_Group{group_num}_current")
            if df is not None:
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="⬇️ Download Current Data CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
                st.success(f"📁 Current data ready for download!")
    
    # Historical data export
    if st.session_state.historical_data:
        if st.button("📈 Export Historical Data", use_container_width=True):
            df, filename = export_historical_to_csv(st.session_state.historical_data, f"{bench_name}_Group{group_num}_historical")
            if df is not None:
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="⬇️ Download Historical Data CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
                st.success(f"📁 Historical data ready for download!")
        
        # Data summary
        st.info(f"📊 Records: {len(st.session_state.historical_data)}")
    
    # Auto-refresh control
    st.divider()
    auto_refresh = st.checkbox("🔄 Auto Refresh", value=True)
    refresh_interval = st.selectbox(
        "Refresh Interval",
        options=[1, 3, 5, 10, 30],
        index=2,
        format_func=lambda x: f"{x}s"
    )
    
    if auto_refresh and st.session_state.is_monitoring:
        time.sleep(refresh_interval)
        st.rerun()

# Main content area
if st.session_state.cells_data:
    
    # Update data if monitoring
    if st.session_state.is_monitoring:
        current_time = datetime.now()
        
        # Check if test duration exceeded
        if st.session_state.process_start_time:
            elapsed_hours = (current_time - st.session_state.process_start_time).total_seconds() / 3600
            if elapsed_hours >= st.session_state.total_test_duration:
                st.session_state.is_monitoring = False
                st.balloons()
                st.success("🎉 Test completed successfully!")
        
        # Update cell data with process parameters
        for cell_id in st.session_state.cells_data.keys():
            cell_type = st.session_state.cells_data[cell_id]["cell_type"]
            st.session_state.cells_data[cell_id] = generate_cell_data(
                cell_type, cell_id, current_time, st.session_state.process_parameters
            )
        
        # Store historical data
        st.session_state.historical_data.append({
            "timestamp": current_time,
            "data": st.session_state.cells_data.copy(),
            "process_params": st.session_state.process_parameters.copy()
        })
        
        # Keep only reasonable amount of historical data
        if len(st.session_state.historical_data) > 1000:
            st.session_state.historical_data = st.session_state.historical_data[-1000:]
    
    # System overview with enhanced styling
    st.header(f"📊 System Overview - {bench_name} (Group {group_num})")
    
    # Process Parameters Display
    with st.expander("🔧 Current Process Parameters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**⚡ Electrical Parameters**")
            st.write(f"Charge Rate: {st.session_state.process_parameters['charge_rate']} A")
            st.write(f"Discharge Rate: {st.session_state.process_parameters['discharge_rate']} A")
            st.write(f"Safety Limit: {st.session_state.process_parameters['safety_voltage_limit']} V")
        
        with col2:
            st.markdown("**🌡️ Environmental Parameters**")
            st.write(f"Target Temperature: {st.session_state.process_parameters['target_temperature']} °C")
            st.write(f"Test Duration: {st.session_state.process_parameters['test_duration']} hours")
        
        with col3:
            st.markdown("**📊 Data Collection**")
            st.write(f"Sampling Interval: {st.session_state.process_parameters['sampling_interval']} seconds")
            if st.session_state.process_start_time:
                st.write(f"Test Progress: {(st.session_state.elapsed_time/st.session_state.total_test_duration*100):.1f}%")
    
    # Summary metrics with enhanced cards
    total_cells = len(st.session_state.cells_data)
    excellent_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Excellent")
    good_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Good")
    warning_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Warning")
    critical_cells = sum(1 for cell in st.session_state.cells_data.values() if cell["status"] == "Critical")
    avg_health = np.mean([cell["health"] for cell in st.session_state.cells_data.values()])
    total_power = sum([cell["power"] for cell in st.session_state.cells_data.values()])
    avg_voltage = np.mean([cell["voltage"] for cell in st.session_state.cells_data.values()])
    avg_temperature = np.mean([cell["temperature"] for cell in st.session_state.cells_data.values()])
    
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        st.markdown(f"""
        <div class="overview-card">
            <span class="overview-number">{total_cells}</span>
            <span class="overview-label">Total Cells</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="overview-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <span class="overview-number">{excellent_cells}</span>
            <span class="overview-label">Excellent</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="overview-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <span class="overview-number">{good_cells}</span>
            <span class="overview-label">Good</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="overview-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <span class="overview-number">{warning_cells}</span>
            <span class="overview-label">Warning</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="overview-card" style="background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);">
            <span class="overview-number">{critical_cells}</span>
            <span class="overview-label">Critical</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="overview-card">
            <span class="overview-number">{avg_health:.1f}%</span>
            <span class="overview-label">Avg Health</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col7:
        st.markdown(f"""
        <div class="overview-card">
            <span class="overview-number">{total_power:.1f}W</span>
            <span class="overview-label">Total Power</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col8:
        st.markdown(f"""
        <div class="overview-card">
            <span class="overview-number">{avg_voltage:.2f}V</span>
            <span class="overview-label">Avg Voltage</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Safety alerts
    safety_alerts = []
    for cell_id, cell_data in st.session_state.cells_data.items():
        if cell_data["voltage"] > st.session_state.process_parameters["safety_voltage_limit"]:
            safety_alerts.append(f"⚠️ {cell_id}: Voltage ({cell_data['voltage']}V) exceeds safety limit!")
        if cell_data["temperature"] > 50:
            safety_alerts.append(f"🔥 {cell_id}: High temperature ({cell_data['temperature']}°C)!")
        if cell_data["status"] == "Critical":
            safety_alerts.append(f"🚨 {cell_id}: Critical status detected!")
    
    if safety_alerts:
        st.error("🚨 Safety Alerts:")
        for alert in safety_alerts[:5]:  # Show max 5 alerts
            st.error(alert)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Real-time Data", "🔋 Enhanced Health", "🔥 Temperature Monitor", "⚡ Historical Trends", "📊 Process Analysis"])
    
    with tab1:
        st.subheader("📊 Real-time Cell Data")
        
        # Create DataFrame for display
        df = pd.DataFrame(st.session_state.cells_data.values())
        
        # Enhanced data table with better formatting
        df_display = df[["cell_id", "cell_type", "voltage", "current", "temperature", "power", "capacity", "health", "status"]].copy()
        df_display["voltage"] = df_display["voltage"].round(3)
        df_display["current"] = df_display["current"].round(2)
        df_display["temperature"] = df_display["temperature"].round(1)
        df_display["power"] = df_display["power"].round(2)
        df_display["capacity"] = df_display["capacity"].round(2)
        df_display["health"] = df_display["health"].round(1)
        
        # Color-code the dataframe based on status
        def highlight_status(row):
            if row['status'] == 'Critical':
                return ['background-color: #ffebee'] * len(row)
            elif row['status'] == 'Warning':
                return ['background-color: #fff3e0'] * len(row)
            elif row['status'] == 'Excellent':
                return ['background-color: #e8f5e8'] * len(row)
            else:
                return [''] * len(row)
        
        styled_df = df_display.style.apply(highlight_status, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # Enhanced voltage comparison chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig_voltage = px.bar(
                df, 
                x="cell_id", 
                y="voltage", 
                color="cell_type",
                title="🔋 Cell Voltage Comparison",
                color_discrete_map={cell_type: config["color"] for cell_type, config in CELL_CONFIGS.items()}
            )
            
            # Add safety limit line
            fig_voltage.add_hline(
                y=st.session_state.process_parameters["safety_voltage_limit"], 
                line_dash="dash", 
                line_color="red",
                annotation_text="Safety Limit"
            )
            
            fig_voltage.update_traces(marker_line_width=2, marker_line_color='white')
            fig_voltage.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333',
                title_font_size=18
            )
            st.plotly_chart(fig_voltage, use_container_width=True)
        
        with col2:
            # Current vs Power scatter plot
            fig_current_power = px.scatter(
                df, 
                x="current", 
                y="power", 
                color="cell_type",
                size="health",
                title="⚡ Current vs Power Analysis",
                hover_data=["cell_id", "voltage", "temperature"],
                color_discrete_map={cell_type: config["color"] for cell_type, config in CELL_CONFIGS.items()}
            )
            fig_current_power.update_traces(marker_line_width=2, marker_line_color='white')
            fig_current_power.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333',
                title_font_size=18
            )
            st.plotly_chart(fig_current_power, use_container_width=True)
    
    with tab2:
        st.subheader("🔋 Enhanced Battery Health Indicators")
        
        # Enhanced health cards with animations and better visuals
        cols = st.columns(4)
        for i, (cell_id, cell_data) in enumerate(st.session_state.cells_data.items()):
            with cols[i % 4]:
                health_class = get_health_class(cell_data["health"])
                battery_icon = get_battery_icon(cell_data["health"])
                status_class = get_status_class(cell_data["status"])
                
                st.markdown(f"""
                <div class="health-card {health_class}">
                    <div class="battery-icon">{battery_icon}</div>
                    <div class="cell-name">{cell_id}</div>
                    <div class="health-percentage">{cell_data["health"]:.1f}%</div>
                    <div class="{status_class}" style="margin-top: 10px; font-size: 1.1rem;">
                        {cell_data["status"]}
                    </div>
                    <div style="margin-top: 8px; font-size: 0.9rem; opacity: 0.8;">
                        {cell_data["cell_type"]} • {cell_data["voltage"]}V • {cell_data["temperature"]}°C
                    </div>
                    <div style="margin-top: 5px; font-size: 0.8rem; opacity: 0.7;">
                        Stress Factor: {cell_data["stress_factor"]:.3f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Enhanced circular health indicators
        st.subheader("🎯 Health Overview Gauges")
        gauge_cols = st.columns(4)
        
        for i, (cell_id, cell_data) in enumerate(st.session_state.cells_data.items()):
            with gauge_cols[i % 4]:
                health_value = cell_data["health"]
                
                # Determine colors based on health
                if health_value >= 90:
                    gauge_color = "#00ff88"
                    bar_color = "#11998e"
                elif health_value >= 75:
                    gauge_color = "#667eea"
                    bar_color = "#764ba2"
                elif health_value >= 50:
                    gauge_color = "#f093fb"
                    bar_color = "#f5576c"
                else:
                    gauge_color = "#ff416c"
                    bar_color = "#ff4b2b"
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = health_value,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': f"🔋 {cell_id}", 'font': {'size': 14, 'color': '#333'}},
                    delta = {'reference': 100, 'increasing': {'color': gauge_color}},
                    gauge = {
                        'axis': {'range': [None, 100], 'tickcolor': '#666'},
                        'bar': {'color': bar_color, 'thickness': 0.8},
                        'bgcolor': "rgba(255,255,255,0.1)",
                        'borderwidth': 3,
                        'bordercolor': gauge_color,
                        'steps': [
                            {'range': [0, 25], 'color': "rgba(255, 65, 108, 0.2)"},
                            {'range': [25, 50], 'color': "rgba(240, 147, 251, 0.2)"},
                            {'range': [50, 75], 'color': "rgba(102, 126, 234, 0.2)"},
                            {'range': [75, 90], 'color': "rgba(17, 153, 142, 0.2)"},
                            {'range': [90, 100], 'color': "rgba(0, 255, 136, 0.3)"}
                        ],
                        'threshold': {
                            'line': {'color': gauge_color, 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig_gauge.update_layout(
                    height=280,
                    font={'color': "#333", 'size': 12},
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Enhanced health distribution
        col1, col2 = st.columns(2)
        
        with col1:
            fig_health = px.histogram(
                df, 
                x="health", 
                nbins=15, 
                title="🎯 Health Distribution Analysis",
                color="status",
                color_discrete_map={
                    "Excellent": "#00ff88", 
                    "Good": "#667eea", 
                    "Warning": "#f093fb", 
                    "Critical": "#ff416c"
                }
            )
            fig_health.update_traces(marker_line_width=2, marker_line_color='white')
            fig_health.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333',
                title_font_size=18
            )
            st.plotly_chart(fig_health, use_container_width=True)
        
        with col2:
            # Health vs Stress Factor correlation
            fig_stress = px.scatter(
                df, 
                x="stress_factor", 
                y="health", 
                color="status",
                size="temperature",
                title="📊 Health vs Stress Factor",
                hover_data=["cell_id", "voltage", "current"],
                color_discrete_map={
                    "Excellent": "#00ff88", 
                    "Good": "#667eea", 
                    "Warning": "#f093fb", 
                    "Critical": "#ff416c"
                }
            )
            fig_stress.update_traces(marker_line_width=2, marker_line_color='white')
            fig_stress.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333',
                title_font_size=18
            )
            st.plotly_chart(fig_stress, use_container_width=True)
    
    with tab3:
        st.subheader("🔥 Temperature Monitoring")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced temperature heatmap
            temp_data = df.pivot_table(values='temperature', index='cell_type', columns='cell_id', fill_value=0)
            fig_temp = px.imshow(
                temp_data, 
                title="🌡️ Temperature Heatmap",
                color_continuous_scale="plasma",
                aspect="auto"
            )
            # Add target temperature line
            fig_temp.add_hline(
                y=st.session_state.process_parameters["target_temperature"], 
                line_dash="dash", 
                line_color="white",
                annotation_text="Target Temp"
            )
            fig_temp.update_layout(
                title_font_size=18,
                font_color='#333'
            )
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            # Temperature distribution by cell type
            fig_temp_dist = px.box(
                df, 
                x="cell_type", 
                y="temperature", 
                color="cell_type",
                title="🌡️ Temperature Distribution by Cell Type",
                color_discrete_map={cell_type: config["color"] for cell_type, config in CELL_CONFIGS.items()}
            )
            fig_temp_dist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333',
                title_font_size=18
            )
            st.plotly_chart(fig_temp_dist, use_container_width=True)
        
        # Enhanced temperature vs power scatter
        fig_scatter = px.scatter(
            df, 
            x="temperature", 
            y="power", 
            color="cell_type",
            size="health",
            title="🔥 Temperature vs Power Analysis",
            hover_data=["cell_id", "voltage", "current", "status"],
            color_discrete_map={cell_type: config["color"] for cell_type, config in CELL_CONFIGS.items()}
        )
        
        # Add target temperature line
        fig_scatter.add_vline(
            x=st.session_state.process_parameters["target_temperature"], 
            line_dash="dash", 
            line_color="gray",
            annotation_text="Target Temperature"
        )
        
        fig_scatter.update_traces(marker_line_width=2, marker_line_color='white')
        fig_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#333',
            title_font_size=18
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab4:
        st.subheader("⚡ Historical Trends")
        
        if len(st.session_state.historical_data) > 1:
            # Prepare historical data
            hist_df = []
            for record in st.session_state.historical_data[-100:]:  # Last 100 records
                for cell_id, cell_data in record["data"].items():
                    hist_df.append({
                        "timestamp": record["timestamp"],
                        "cell_id": cell_id,
                        "cell_type": cell_data["cell_type"],
                        "voltage": cell_data["voltage"],
                        "current": cell_data["current"],
                        "temperature": cell_data["temperature"],
                        "health": cell_data["health"],
                        "power": cell_data["power"],
                        "status": cell_data["status"]
                    })
            
            hist_df = pd.DataFrame(hist_df)
            
            # Enhanced multi-line charts
            fig_trends = make_subplots(
                rows=2, cols=2,
                subplot_titles=("⚡ Voltage Trends", "🔄 Current Trends", "🌡️ Temperature Trends", "💚 Health Trends"),
                vertical_spacing=0.08
            )
            
            # Color palette for different cells
            colors = ['#00ff88', '#ff416c', '#f093fb', '#667eea', '#ffa726', '#ab47bc', '#26c6da', '#66bb6a']
            
            # Voltage trends
            for i, cell_id in enumerate(hist_df["cell_id"].unique()):
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(
                        x=cell_hist["timestamp"], 
                        y=cell_hist["voltage"], 
                        name=f"{cell_id}_V", 
                        line=dict(width=3, color=colors[i % len(colors)])
                    ),
                    row=1, col=1
                )
            
            # Current trends
            for i, cell_id in enumerate(hist_df["cell_id"].unique()):
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(
                        x=cell_hist["timestamp"], 
                        y=cell_hist["current"], 
                        name=f"{cell_id}_I", 
                        showlegend=False,
                        line=dict(width=3, color=colors[i % len(colors)])
                    ),
                    row=1, col=2
                )
            
            # Temperature trends
            for i, cell_id in enumerate(hist_df["cell_id"].unique()):
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(
                        x=cell_hist["timestamp"], 
                        y=cell_hist["temperature"], 
                        name=f"{cell_id}_T", 
                        showlegend=False,
                        line=dict(width=3, color=colors[i % len(colors)])
                    ),
                    row=2, col=1
                )
            
            # Health trends
            for i, cell_id in enumerate(hist_df["cell_id"].unique()):
                cell_hist = hist_df[hist_df["cell_id"] == cell_id]
                fig_trends.add_trace(
                    go.Scatter(
                        x=cell_hist["timestamp"], 
                        y=cell_hist["health"], 
                        name=f"{cell_id}_H", 
                        showlegend=False,
                        line=dict(width=3, color=colors[i % len(colors)])
                    ),
                    row=2, col=2
                )
            
            fig_trends.update_layout(
                height=600, 
                title_text="📈 Historical Data Trends",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333'
            )
            fig_trends.update_xaxes(title_text="Time")
            fig_trends.update_yaxes(title_text="Voltage (V)", row=1, col=1)
            fig_trends.update_yaxes(title_text="Current (A)", row=1, col=2)
            fig_trends.update_yaxes(title_text="Temperature (°C)", row=2, col=1)
            fig_trends.update_yaxes(title_text="Health (%)", row=2, col=2)
            
            st.plotly_chart(fig_trends, use_container_width=True)
            
            # Historical statistics
            st.subheader("📊 Historical Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📈 Max Voltage", f"{hist_df['voltage'].max():.3f}V")
                st.metric("📉 Min Voltage", f"{hist_df['voltage'].min():.3f}V")
            
            with col2:
                st.metric("⚡ Max Current", f"{hist_df['current'].max():.2f}A")
                st.metric("⚡ Min Current", f"{hist_df['current'].min():.2f}A")
            
            with col3:
                st.metric("🌡️ Max Temperature", f"{hist_df['temperature'].max():.1f}°C")
                st.metric("🌡️ Min Temperature", f"{hist_df['temperature'].min():.1f}°C")
            
            with col4:
                st.metric("💚 Max Health", f"{hist_df['health'].max():.1f}%")
                st.metric("💔 Min Health", f"{hist_df['health'].min():.1f}%")
        else:
            st.info("Start monitoring to see historical trends...")
    
    with tab5:
        st.subheader("📊 Process Analysis")
        
        if len(st.session_state.historical_data) > 1:
            # Process efficiency analysis
            hist_df = []
            for record in st.session_state.historical_data:
                for cell_id, cell_data in record["data"].items():
                    hist_df.append({
                        "timestamp": record["timestamp"],
                        "cell_id": cell_id,
                        "voltage": cell_data["voltage"],
                        "current": cell_data["current"],
                        "power": cell_data["power"],
                        "health": cell_data["health"],
                        "temperature": cell_data["temperature"],
                        "stress_factor": cell_data["stress_factor"]
                    })
            
            hist_df = pd.DataFrame(hist_df)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Process efficiency over time
                efficiency_data = hist_df.groupby('timestamp').agg({
                    'power': 'mean',
                    'health': 'mean',
                    'stress_factor': 'mean'
                }).reset_index()
                
                fig_efficiency = px.line(
                    efficiency_data, 
                    x="timestamp", 
                    y=["power", "health"], 
                    title="⚡ Process Efficiency Over Time",
                    labels={"value": "Value", "variable": "Metric"}
                )
                fig_efficiency.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#333',
                    title_font_size=18
                )
                st.plotly_chart(fig_efficiency, use_container_width=True)
            
            with col2:
                # Cell performance comparison
                performance_data = hist_df.groupby('cell_id').agg({
                    'health': ['mean', 'std'],
                    'power': 'mean',
                    'stress_factor': 'mean'
                }).round(2)
                
                performance_data.columns = ['Avg Health', 'Health Std', 'Avg Power', 'Avg Stress']
                performance_data = performance_data.reset_index()
                
                fig_performance = px.scatter(
                    performance_data, 
                    x="Avg Health", 
                    y="Avg Power", 
                    size="Health Std",
                    color="Avg Stress",
                    hover_data=["cell_id"],
                    title="🎯 Cell Performance Analysis",
                    color_continuous_scale="viridis"
                )
                fig_performance.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#333',
                    title_font_size=18
                )
                st.plotly_chart(fig_performance, use_container_width=True)
            
            # Process summary report
            st.subheader("📋 Process Summary Report")
            
            if st.session_state.process_start_time:
                total_runtime = (datetime.now() - st.session_state.process_start_time).total_seconds() / 3600
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**⏱️ Test Progress**")
                    st.write(f"Total Runtime: {total_runtime:.2f} hours")
                    st.write(f"Progress: {(total_runtime/st.session_state.total_test_duration*100):.1f}%")
                    st.write(f"Data Points: {len(st.session_state.historical_data)}")
                
                with col2:
                    st.markdown("**📊 Performance Metrics**")
                    st.write(f"Avg System Health: {hist_df['health'].mean():.1f}%")
                    st.write(f"Avg System Power: {hist_df['power'].mean():.2f}W")
                    st.write(f"Std Health Deviation: {hist_df['health'].std():.2f}%")
                
                with col3:
                    st.markdown("**🔍 Quality Indicators**")
                    stable_cells = len([cell for cell in performance_data['Health Std'] if cell < 5.0])
                    st.write(f"Stable Cells: {stable_cells}/{len(performance_data)}")
                    st.write(f"Avg Stress Factor: {hist_df['stress_factor'].mean():.3f}")
                    
                    if hist_df['health'].min() > 75:
                        st.success("✅ All cells maintaining good health")
                    elif hist_df['health'].min() > 50:
                        st.warning("⚠️ Some cells showing degradation")
                    else:
                        st.error("🚨 Critical health levels detected")
        else:
            st.info("Start the test to see process analysis...")

else:
    st.info("👈 Please configure and initialize cells using the sidebar to begin monitoring.")
    
    # Display enhanced sample configuration
    st.subheader("🔋 Available Cell Types:")
    
    config_col1, config_col2 = st.columns(2)
    
    with config_col1:
        for i, (cell_type, config) in enumerate(list(CELL_CONFIGS.items())[:2]):
            st.markdown(f"""
            **{cell_type}** (Lithium {cell_type})
            - Voltage Range: {config['min_voltage']}V - {config['max_voltage']}V
            - Nominal: {config['nominal_voltage']}V
            - Capacity: {config['capacity_range'][0]}-{config['capacity_range'][1]} Ah
    
    st.subheader("🚀 Quick Start Guide:")
    st.markdown("""
    1. **Configure Process Parameters** - Set test duration, charge/discharge rates, and temperature
    2. **Select Cell Types** - Choose battery chemistry for each cell position
    3. **Initialize Test** - Click '🚀 Initialize Test' to setup the monitoring system
    4. **Start Monitoring** - Click '▶️ Start' to begin real-time data collection
    5. **Export Data** - Use the export buttons to download CSV files for analysis
    
    **Pro Tips:**
    - Use auto-refresh for real-time monitoring
    - Export data regularly for backup
    - Monitor safety alerts closely
    - Check historical trends for performance analysis
    """)
    
    # Sample process parameters display
    st.subheader("⚙️ Sample Process Parameters:")
    sample_col1, sample_col2, sample_col3 = st.columns(3)
    
    with sample_col1:
        st.markdown("""
        **Standard Test**
        - Duration: 2 hours
        - Charge Rate:1
        - Discharge Rate:1
        - Target Temp: 25°C
        """)
    
    with sample_col2:
        st.markdown("""
        **Fast Charging Test**
        - Duration: 1 hour
        - Charge Rate: 3A
        - Discharge Rate: 2A
        - Target Temp: 30°C
        """)
    
    with sample_col3:
        st.markdown("""
        **Stress Test**
        - Duration: 4 hours
        - Charge Rate: 2A
        - Discharge Rate: 3A
        - Target Temp: 40°C
        """)

# Footer with enhanced styling
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🔋 <strong>Enhanced Battery Cell Monitoring Dashboard</strong> | Professional Real-time Monitoring System</p>
        <p style='font-size: 0.9rem; opacity: 0.8;'>
            Features: Process Parameter Control • CSV Export • Historical Analysis • Safety Monitoring • Real-time Alerts
        </p>
        <p style='font-size: 0.8rem; opacity: 0.6;'>
            Developed for Professional Battery Testing Applications
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)voltage']}V
            - Capacity: {config['capacity_range'][0]}-{config['capacity_range'][1]} Ah
            - Temperature: {config['temp_range'][0]}°C to {config['temp_range'][1]}°C
            """)
    
    with config_col2:
        for i, (cell_type, config) in enumerate(list(CELL_CONFIGS.items())[2:]):
            st.markdown(f"""
            **{cell_type}** (Lithium {cell_type})
            - Voltage Range: {config['min_voltage']}V - {config['max_voltage']}V
            - Nominal: {config['nominal_
