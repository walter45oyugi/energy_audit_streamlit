# Energy Audit Dashboard

A comprehensive Streamlit dashboard for analyzing energy audit data from Mvule and Clinic stations. The dashboard provides detailed insights into power quality, voltage analysis, current analysis, harmonics, and power factor metrics.

## Features

- **Interactive Charts**: Plotly-based interactive visualizations
- **Comprehensive Analysis**: Detailed insights with specific values and recommendations
- **Derived Metrics**: Calculated power factor, voltage/current imbalances, harmonic losses
- **Professional Insights**: Notebook-style analysis with actionable recommendations
- **Multi-Station Support**: Analysis for both Mvule and Clinic stations

## Data Sources

- `MVULE corrected time.xlsx` - Mvule station data
- `Clinic corrected time.xlsx` - Clinic station data
- `Strathmore-University-Logo.png` - Dashboard logo

## Local Development

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd energy_audit_streamlit

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run energy_audit_streamlit_app.py
```

The dashboard will be available at `http://localhost:8501`

## Deployment Options

### 1. Streamlit Cloud (Recommended - Free)

**Steps:**
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Select your repository
5. Set the main file path: `energy_audit_streamlit_app.py`
6. Deploy!

**Advantages:**
- ✅ Free hosting
- ✅ Automatic deployments from GitHub
- ✅ Built specifically for Streamlit
- ✅ Easy to set up

### 2. Render (Free Tier)

**Steps:**
1. Create account at [render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Use the `render.yaml` configuration
5. Deploy!

**Configuration:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `streamlit run energy_audit_streamlit_app.py --server.port $PORT --server.address 0.0.0.0`

### 3. Railway (Free Tier)

**Steps:**
1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect the `railway.json` configuration
4. Deploy!

### 4. Heroku (Paid)

**Steps:**
1. Create Heroku account
2. Install Heroku CLI
3. Use the provided `Procfile`
4. Deploy using Heroku CLI or GitHub integration

## Dashboard Sections

### Overview
- Combined KPI metrics for both stations
- Power consumption comparison
- System health indicators

### Station-Specific Analysis
Each station (Mvule/Clinic) has detailed analysis tabs:

#### Power Quality
- **Frequency Analysis**: Grid stability monitoring
- **Voltage THD**: Harmonic distortion assessment

#### Voltage Analysis
- **Line-to-Neutral Voltage**: Phase voltage monitoring
- **Line-to-Line Voltage**: Phase-to-phase voltage analysis
- **Voltage Imbalance**: Phase balance assessment

#### Current Analysis
- **Current Distribution**: Phase current monitoring
- **Current THD**: Harmonic distortion in current
- **Current Imbalance**: Phase current balance

#### Harmonics Analysis
- **Voltage THD**: Power quality harmonics
- **Current THD**: Load characteristic harmonics

#### Power Factor Analysis
- **Power Factor**: Calculated system power factor
- **Active Power**: Real power consumption analysis

## Derived Metrics

The dashboard calculates the following derived metrics (same as your notebooks):

```python
df['Avg_Voltage_LN'] = df[['Vrms_AN_avg', 'Vrms_BN_avg', 'Vrms_CN_avg']].mean(axis=1)
df['Voltage_Imbalance'] = (df[['Vrms_AN_avg', 'Vrms_BN_avg', 'Vrms_CN_avg']].std(axis=1) / df['Avg_Voltage_LN']) * 100
df['Current_Imbalance'] = (df[['Irms_A_avg', 'Irms_B_avg', 'Irms_C_avg']].std(axis=1) / df[['Irms_A_avg', 'Irms_B_avg', 'Irms_C_avg']].mean(axis=1)) * 100
df['System_PF'] = df['PowerP_Total_avg'] / df['PowerS_Total_avg']
df['Harmonic_Loss'] = df['PowerS_Total_avg'] - df['PowerP_Total_avg']
```

## Insights & Recommendations

Each chart includes:
- **Key Findings**: Specific numerical values (min, max, average)
- **Analysis**: Conditional assessment based on industry standards
- **Recommendations**: Actionable steps for improvement

## Technical Details

- **Framework**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas
- **File Format**: Excel (.xlsx)
- **Logo Integration**: Base64 encoding for deployment

## File Structure

```
energy_audit_streamlit/
├── energy_audit_streamlit_app.py    # Main dashboard application
├── requirements.txt                  # Python dependencies
├── .streamlit/config.toml           # Streamlit configuration
├── render.yaml                      # Render deployment config
├── railway.json                     # Railway deployment config
├── Procfile                         # Heroku deployment config
├── README.md                        # This file
├── MVULE corrected time.xlsx        # Mvule station data
├── Clinic corrected time.xlsx       # Clinic station data
├── Strathmore-University-Logo.png   # Dashboard logo
├── Mvule Energy (1).ipynb          # Original analysis notebook
└── clinic energy.ipynb              # Original analysis notebook
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is for educational and research purposes. 