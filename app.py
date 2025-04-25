import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time

# Setup halaman
st.set_page_config(
    page_title="Dashboard Pusat Gadai Indonesia", 
    page_icon="💰", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Kustom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .metric-title {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E3A8A;
        margin: 0;
    }
    .metric-delta {
        font-size: 0.8rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #1E3A8A;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
    .small-text {
        font-size: 0.8rem;
        color: #666;
    }
    .footer {
        margin-top: 80px;
        text-align: center;
        color: #666;
        font-size: 0.8rem;
    }
    /* Logo styling */
    .logo-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .logo-text {
        margin-left: 10px;
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    /* Competitor toggles */
    .competitor-toggle {
        display: flex;
        overflow-x: auto;
        padding: 5px 0;
    }
    .competitor-button {
        flex: 0 0 auto;
        padding: 8px 16px;
        margin-right: 8px;
        background-color: #f1f1f1;
        border-radius: 20px;
        font-size: 14px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .competitor-button.active {
        background-color: #1E3A8A;
        color: white;
    }
    .competitor-button:hover {
        background-color: #ddd;
    }
    .competitor-button.active:hover {
        background-color: #152a62;
    }
</style>
""", unsafe_allow_html=True)

# Data dummy
def generate_dummy_data():
    # Provinsi-provinsi di Indonesia
    provinces = [
        "Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi", "Sumatera Selatan", 
        "Bengkulu", "Lampung", "Kepulauan Bangka Belitung", "Kepulauan Riau", "DKI Jakarta", 
        "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Banten", "Bali", 
        "Nusa Tenggara Barat", "Nusa Tenggara Timur", "Kalimantan Barat", "Kalimantan Tengah", 
        "Kalimantan Selatan", "Kalimantan Timur", "Kalimantan Utara", "Sulawesi Utara", 
        "Sulawesi Tengah", "Sulawesi Selatan", "Sulawesi Tenggara", "Gorontalo", 
        "Sulawesi Barat", "Maluku", "Maluku Utara", "Papua Barat", "Papua"
    ]
    
    # Koordinat provinsi (perkiraan)
    coordinates = {
        "Aceh": [4.6951, 96.7494],
        "Sumatera Utara": [2.1154, 99.5451],
        "Sumatera Barat": [-0.7393, 100.8008],
        "Riau": [0.2933, 101.7068],
        "Jambi": [-1.6101, 103.6131],
        "Sumatera Selatan": [-3.3194, 104.9144],
        "Bengkulu": [-3.5778, 102.3464],
        "Lampung": [-4.5586, 105.4068],
        "Kepulauan Bangka Belitung": [-2.7411, 106.4406],
        "Kepulauan Riau": [3.9456, 108.1428],
        "DKI Jakarta": [-6.2088, 106.8456],
        "Jawa Barat": [-7.0909, 107.6689],
        "Jawa Tengah": [-7.1510, 110.1403],
        "DI Yogyakarta": [-7.7956, 110.3695],
        "Jawa Timur": [-7.5360, 112.2384],
        "Banten": [-6.4058, 106.0640],
        "Bali": [-8.3405, 115.0920],
        "Nusa Tenggara Barat": [-8.6529, 117.3616],
        "Nusa Tenggara Timur": [-8.6573, 121.0794],
        "Kalimantan Barat": [0.2787, 111.4753],
        "Kalimantan Tengah": [-1.6813, 113.3823],
        "Kalimantan Selatan": [-3.0926, 115.2838],
        "Kalimantan Timur": [0.5387, 116.4194],
        "Kalimantan Utara": [3.0731, 116.0414],
        "Sulawesi Utara": [0.6246, 123.9750],
        "Sulawesi Tengah": [-1.4301, 121.4456],
        "Sulawesi Selatan": [-3.6687, 119.9740],
        "Sulawesi Tenggara": [-4.1449, 122.1746],
        "Gorontalo": [0.6999, 122.4467],
        "Sulawesi Barat": [-2.8441, 119.2321],
        "Maluku": [-3.2385, 130.1453],
        "Maluku Utara": [1.5709, 127.8088],
        "Papua Barat": [-1.3361, 133.1747],
        "Papua": [-4.2699, 138.0804]
    }
    
    # Kategori barang gadai
    item_categories = ["Emas", "Elektronik", "Kendaraan", "Perhiasan", "Lainnya"]
    
    # Outlet data
    outlets = []
    
    # Distribusi outlet di provinsi (weighted)
    province_weights = {
        "DKI Jakarta": 15, "Jawa Barat": 12, "Jawa Timur": 10, "Jawa Tengah": 9,
        "Sumatera Utara": 7, "Banten": 6, "Sumatera Selatan": 5, "Bali": 5,
        "Sulawesi Selatan": 4, "Kalimantan Timur": 4
    }
    
    # Default weight untuk provinsi lain
    default_weight = 2
    
    # Buat outlet untuk setiap provinsi
    outlet_id = 1
    for province in provinces:
        # Jumlah outlet di provinsi ini
        num_outlets = province_weights.get(province, default_weight) * 5 + random.randint(-3, 5)
        
        # Base value untuk provinsi
        province_base_customer = random.randint(1000, 5000)
        province_base_loan = random.randint(500_000_000, 3_000_000_000)
        
        for _ in range(num_outlets):
            # Koordinat outlet - tambahkan offset kecil dari koordinat provinsi
            lat_offset = random.uniform(-0.3, 0.3)
            lon_offset = random.uniform(-0.3, 0.3)
            lat = coordinates[province][0] + lat_offset
            lon = coordinates[province][1] + lon_offset
            
            # Metrik outlet
            customer_count = province_base_customer + random.randint(-500, 1000)
            loan_value = province_base_loan + random.randint(-200_000_000, 500_000_000)
            growth_rate = random.uniform(-5, 25)
            redemption_rate = random.uniform(60, 98)
            
            # Komposisi kategori barang gadai
            category_distribution = {}
            remaining = 100
            for cat in item_categories[:-1]:
                if cat == "Emas":
                    category_distribution[cat] = random.randint(20, 60)
                else:
                    category_distribution[cat] = random.randint(5, 20)
                remaining -= category_distribution[cat]
            category_distribution[item_categories[-1]] = remaining
            
            # Tambahkan ke daftar outlet
            outlets.append({
                "outlet_id": outlet_id,
                "outlet_name": f"PGI {province} {outlet_id % 10 + 1}",
                "province": province,
                "latitude": lat,
                "longitude": lon,
                "customer_count": customer_count,
                "loan_value": loan_value,
                "growth_rate": growth_rate,
                "redemption_rate": redemption_rate,
                "category_distribution": category_distribution,
                "risk_score": random.uniform(1, 5)
            })
            outlet_id += 1
    
    # Data provinsi
    province_data = []
    
    for province in provinces:
        # Outlet di provinsi ini
        province_outlets = [o for o in outlets if o["province"] == province]
        
        # Kalkulasi data agregat untuk provinsi
        total_customers = sum(o["customer_count"] for o in province_outlets)
        total_loan_value = sum(o["loan_value"] for o in province_outlets)
        avg_growth = np.mean([o["growth_rate"] for o in province_outlets]) if province_outlets else 0
        redemption_rate = np.mean([o["redemption_rate"] for o in province_outlets]) if province_outlets else 0
        
        # Tambahkan ke daftar provinsi
        province_data.append({
            "province": province,
            "num_outlets": len(province_outlets),
            "total_customers": total_customers,
            "total_loan_value": total_loan_value,
            "avg_growth_rate": avg_growth,
            "redemption_rate": redemption_rate,
            "latitude": coordinates[province][0],
            "longitude": coordinates[province][1]
        })
    
    # Data historis nasabah (18 bulan terakhir)
    historical_data = []
    
    start_date = datetime.now() - timedelta(days=18*30)
    customers_base = 300000
    cumulative_growth = 1.0
    
    for i in range(18):
        month_date = start_date + timedelta(days=30*i)
        # Seasonal effects (higher in Dec-Jan, lower in mid-year)
        month_factor = 1.0 + 0.2 * np.sin(np.pi * (i % 12) / 6)
        # Small random factor
        random_factor = random.uniform(0.97, 1.03)
        # Steady growth plus seasonal and random factors
        cumulative_growth *= 1.015 * month_factor * random_factor
        
        customers = int(customers_base * cumulative_growth)
        loans = int(customers * random.uniform(3.5, 5.2) * 1_000_000)
        redemptions = int(loans * random.uniform(0.65, 0.85))
        
        historical_data.append({
            "month": month_date.strftime("%Y-%m"),
            "year": month_date.year, 
            "month_name": month_date.strftime("%b"),
            "customers": customers,
            "loan_value": loans,
            "redemption_value": redemptions,
            "new_customers": int(customers * random.uniform(0.05, 0.12)),
            "emas_percentage": random.uniform(45, 65),
            "elektronik_percentage": random.uniform(10, 25),
            "kendaraan_percentage": random.uniform(10, 20),
            "perhiasan_percentage": random.uniform(5, 15),
            "lainnya_percentage": random.uniform(3, 8)
        })
    
    # Data kompetitor
    competitors = [
        {"name": "Pegadaian", "outlets": 625, "market_share": 56.8},
        {"name": "Bank BRI", "outlets": 235, "market_share": 16.2},
        {"name": "Bank Syariah", "outlets": 97, "market_share": 8.5},
        {"name": "Fintech", "outlets": 122, "market_share": 10.7},
        {"name": "Lainnya", "outlets": 82, "market_share": 7.8}
    ]
    
    # Data skenario simulasi
    scenarios = [
        {
            "name": "Baseline", 
            "growth_rate": 15.2,
            "redemption_rate": 84.3,
            "profit_margin": 12.8,
            "risk_score": 2.3
        },
        {
            "name": "Ekspansi Outlet", 
            "growth_rate": 24.5,
            "redemption_rate": 81.7,
            "profit_margin": 11.5,
            "risk_score": 3.1
        },
        {
            "name": "Penurunan Bunga", 
            "growth_rate": 19.8,
            "redemption_rate": 88.2,
            "profit_margin": 10.2,
            "risk_score": 2.6
        },
        {
            "name": "Fokus Digital", 
            "growth_rate": 21.3,
            "redemption_rate": 86.5,
            "profit_margin": 13.9,
            "risk_score": 1.9
        }
    ]
    
    return {
        "outlets": pd.DataFrame(outlets),
        "provinces": pd.DataFrame(province_data),
        "historical": pd.DataFrame(historical_data),
        "competitors": pd.DataFrame(competitors),
        "scenarios": pd.DataFrame(scenarios)
    }

# Generate dummy data
data = generate_dummy_data()

# Sidebar
with st.sidebar:
    st.image("https://file.dev2-emas.pgindonesia.com/LOGO_PROGRAM/logo.png", width=150)
    st.subheader("Dashboard Filters")
    
    # Date range filter
    st.write("**Periode Waktu**")
    date_range = st.selectbox(
        "Pilih rentang waktu:",
        ["YTD 2024", "FY 2023", "Q1 2024", "Q4 2023", "Q3 2023", "Last 12 months", "Last 6 months", "Last 3 months"],
        index=0
    )
    
    # Region filter
    st.write("**Wilayah**")
    region_options = ["Semua Wilayah", "Jawa", "Sumatera", "Kalimantan", "Sulawesi", "Bali & Nusra", "Maluku & Papua"]
    selected_region = st.selectbox("Pilih wilayah:", region_options, index=0)
    
    # Provinsi filter - show only if region is selected
    if selected_region != "Semua Wilayah":
        provinces_by_region = {
            "Jawa": ["DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Banten"],
            "Sumatera": ["Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi", "Sumatera Selatan", 
                         "Bengkulu", "Lampung", "Kepulauan Bangka Belitung", "Kepulauan Riau"],
            "Kalimantan": ["Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan", 
                           "Kalimantan Timur", "Kalimantan Utara"],
            "Sulawesi": ["Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan", 
                         "Sulawesi Tenggara", "Gorontalo", "Sulawesi Barat"],
            "Bali & Nusra": ["Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"],
            "Maluku & Papua": ["Maluku", "Maluku Utara", "Papua Barat", "Papua"]
        }
        selected_provinces = st.multiselect(
            "Pilih provinsi:",
            provinces_by_region[selected_region],
            default=provinces_by_region[selected_region]
        )
    
    # Product category filter
    st.write("**Kategori Produk**")
    product_categories = ["Semua Kategori", "Emas", "Elektronik", "Kendaraan", "Perhiasan", "Lainnya"]
    selected_categories = st.multiselect(
        "Pilih kategori produk:",
        product_categories[1:],  # Skip "Semua Kategori"
        default=product_categories[1:]  # Default select all specific categories
    )
    
    if not selected_categories:
        selected_categories = product_categories[1:]  # If none selected, use all
    
    # Customer segment filter
    st.write("**Segmen Nasabah**")
    customer_segments = ["Semua Segmen", "Regular", "Premium", "Loyal", "New", "Dormant"]
    selected_segment = st.radio("Pilih segmen nasabah:", customer_segments, index=0)
    
    # Advanced filters (collapsible)
    with st.expander("Filter Lanjutan"):
        # LTV Range
        st.write("**Loan to Value (LTV)**")
        ltv_range = st.slider("Range LTV (%)", 30, 95, (50, 90))
        
        # Loan Status
        st.write("**Status Pinjaman**")
        loan_statuses = ["Aktif", "Jatuh Tempo", "Sudah Dilunasi", "Dilelang"]
        selected_statuses = st.multiselect(
            "Pilih status:",
            loan_statuses,
            default=loan_statuses
        )
        
        # Risk Score
        st.write("**Risk Score**")
        risk_range = st.slider("Risk Score", 1.0, 5.0, (1.0, 3.5))
    
    # Reset filters button
    if st.button("Reset Semua Filter"):
        st.experimental_rerun()

# Main content
# Judul di tengah
st.markdown('<h1 style="text-align: center; color: #1E3A8A; font-size: 2.5rem; margin-bottom: 20px;">Dashboard Pusat Gadai Indonesia</h1>', unsafe_allow_html=True)

# Logo di tengah panjang dibawah judul
_, logo_col, _ = st.columns([1, 2, 1])
with logo_col:
    st.image("https://file.dev2-emas.pgindonesia.com/LOGO_PROGRAM/logo.png", width=400)

# Subtitle dibawah logo
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-top: 10px;">Analisis Pertumbuhan dan Kinerja Bisnis Gadai</p>', unsafe_allow_html=True)

# Loading spinner for effect (simulating data loading)
with st.spinner("Memuat data terbaru..."):
    time.sleep(0.5)

# Top-level metrics
st.markdown('<div class="section-header">Metrik Bisnis Utama</div>', unsafe_allow_html=True)

# Get the latest month data for metrics
latest_month = data["historical"].iloc[-1]
prev_month = data["historical"].iloc[-2]

# Calculate changes from previous month
customer_change = ((latest_month["customers"] / prev_month["customers"]) - 1) * 100
loan_change = ((latest_month["loan_value"] / prev_month["loan_value"]) - 1) * 100
redemption_change = ((latest_month["redemption_value"] / prev_month["redemption_value"]) - 1) * 100
new_customer_change = ((latest_month["new_customers"] / prev_month["new_customers"]) - 1) * 100

# Format currency values
format_currency = lambda x: f"Rp{x/1e9:.2f}T" if x >= 1e12 else f"Rp{x/1e6:.2f}M"

# Create 4 metric columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">Total Nasabah Aktif</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{latest_month["customers"]:,.0f}</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="metric-delta" style="color:{'green' if customer_change >= 0 else 'red'}">
            {customer_change:+.1f}% dari bulan lalu
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">Nilai Gadai Outstanding</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{format_currency(latest_month["loan_value"])}</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="metric-delta" style="color:{'green' if loan_change >= 0 else 'red'}">
            {loan_change:+.1f}% dari bulan lalu
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">Tingkat Penebusan</div>', unsafe_allow_html=True)
    redemption_percentage = (latest_month["redemption_value"] / latest_month["loan_value"]) * 100
    st.markdown(f'<div class="metric-value">{redemption_percentage:.1f}%</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="metric-delta" style="color:{'green' if redemption_change >= 0 else 'red'}">
            {redemption_change:+.1f}% dari bulan lalu
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">Nasabah Baru</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-value">{latest_month["new_customers"]:,.0f}</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="metric-delta" style="color:{'green' if new_customer_change >= 0 else 'red'}">
            {new_customer_change:+.1f}% dari bulan lalu
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Geographical Analysis
st.markdown('<div class="section-header">Analisis Geografis Bisnis Gadai</div>', unsafe_allow_html=True)

map_col1, map_col2 = st.columns([2, 1])

with map_col1:
    # Create base map
    m = folium.Map(location=[-2.5, 118], zoom_start=5, control_scale=True)

    # Add outlet markers to map
    for idx, outlet in data["outlets"].iterrows():
        # Format popup content
        popup_content = f"""
        <strong>{outlet['outlet_name']}</strong><br>
        Nasabah: {outlet['customer_count']:,.0f}<br>
        Nilai Gadai: {format_currency(outlet['loan_value'])}<br>
        Pertumbuhan: {outlet['growth_rate']:.1f}%<br>
        Tingkat Penebusan: {outlet['redemption_rate']:.1f}%
        """
        
        # Color based on growth rate
        if outlet['growth_rate'] > 15:
            color = 'green'
        elif outlet['growth_rate'] > 5:
            color = 'blue'
        elif outlet['growth_rate'] > 0:
            color = 'orange'
        else:
            color = 'red'
        
        # Size based on loan value (scaled)
        radius = min(float(outlet['loan_value']) / 2e8, 15)
        if radius < 5:
            radius = 5
        
        folium.CircleMarker(
            location=[outlet['latitude'], outlet['longitude']],
            radius=radius,
            popup=folium.Popup(popup_content, max_width=300),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            tooltip=outlet['outlet_name']
        ).add_to(m)
    
    # Add province level data visualization
    for idx, province in data["provinces"].iterrows():
        # Create a circle marker at province center
        folium.CircleMarker(
            location=[province['latitude'], province['longitude']],
            radius=0,  # No visible circle
            tooltip=f"{province['province']}: {province['total_customers']:,.0f} nasabah, {format_currency(province['total_loan_value'])}"
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Display the map
    st.subheader("Peta Distribusi Nasabah dan Outlet")
    folium_static(m, width=800, height=500)

with map_col2:
    # Top provinces by customer count
    st.subheader("Wilayah Dengan Nasabah Terbanyak")
    
    top_provinces = data["provinces"].sort_values("total_customers", ascending=False).head(10)
    
    # Create a horizontal bar chart
    fig = px.bar(
        top_provinces,
        y="province",
        x="total_customers",
        orientation='h',
        labels={"province": "Provinsi", "total_customers": "Jumlah Nasabah"},
        color="avg_growth_rate",
        color_continuous_scale="RdYlGn",
        range_color=[-5, 25],
        title=""
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Jumlah Nasabah",
        yaxis_title="",
        margin=dict(l=0, r=0, t=30, b=0),
        coloraxis_colorbar=dict(title="Growth Rate (%)")
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Trend Analysis
st.markdown('<div class="section-header">Analisis Tren & Performa Bisnis</div>', unsafe_allow_html=True)

trend_col1, trend_col2 = st.columns(2)

with trend_col1:
    # Customer and Loan Value trends
    st.subheader("Tren Pertumbuhan Nasabah & Nilai Gadai")
    
    # Prepare trend data
    trend_data = data["historical"].copy()
    
    # Create a combined trend chart with dual y-axis
    fig = go.Figure()
    
    # Customer trend line (left y-axis)
    fig.add_trace(go.Scatter(
        x=trend_data["month"],
        y=trend_data["customers"],
        name="Jumlah Nasabah",
        line=dict(color='royalblue', width=2)
    ))
    
    # Loan value trend line (right y-axis)
    fig.add_trace(go.Scatter(
        x=trend_data["month"],
        y=trend_data["loan_value"],
        name="Nilai Gadai (Rp)",
        line=dict(color='firebrick', width=2),
        yaxis="y2"
    ))
    
    # Add reference for COVID-19 start in Indonesia (March 2020)
    covid_start = "2020-03"
    if covid_start in trend_data["month"].values:
        covid_index = trend_data[trend_data["month"] == covid_start].index[0]
        fig.add_vline(
            x=covid_index, 
            line_dash="dash", 
            line_color="gray",
            annotation_text="COVID-19",
            annotation_position="top right"
        )
    
    # Layout with dual y-axis
    fig.update_layout(
        yaxis=dict(title="Jumlah Nasabah"),
        yaxis2=dict(title="Nilai Gadai (Rp)", overlaying="y", side="right"),
        legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1),
        height=400,
        margin=dict(l=20, r=50, t=20, b=20),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

with trend_col2:
    # Product category distribution over time
    st.subheader("Distribusi Kategori Barang Gadai")
    
    # Prepare category trend data
    cat_data = data["historical"].copy()
    
    # Stack data for area chart
    fig = go.Figure()
    
    # Add each category as a stacked area
    fig.add_trace(go.Scatter(
        x=cat_data["month"], 
        y=cat_data["emas_percentage"],
        name="Emas",
        mode='lines',
        stackgroup='one',
        line=dict(width=0.5, color='gold')
    ))
    
    fig.add_trace(go.Scatter(
        x=cat_data["month"], 
        y=cat_data["elektronik_percentage"],
        name="Elektronik",
        mode='lines',
        stackgroup='one',
        line=dict(width=0.5, color='darkblue')
    ))
    
    fig.add_trace(go.Scatter(
        x=cat_data["month"], 
        y=cat_data["kendaraan_percentage"],
        name="Kendaraan",
        mode='lines',
        stackgroup='one',
        line=dict(width=0.5, color='darkgreen')
    ))
    
    fig.add_trace(go.Scatter(
        x=cat_data["month"], 
        y=cat_data["perhiasan_percentage"],
        name="Perhiasan",
        mode='lines',
        stackgroup='one',
        line=dict(width=0.5, color='purple')
    ))
    
    fig.add_trace(go.Scatter(
        x=cat_data["month"], 
        y=cat_data["lainnya_percentage"],
        name="Lainnya",
        mode='lines',
        stackgroup='one',
        line=dict(width=0.5, color='gray')
    ))
    
    fig.update_layout(
        yaxis=dict(
            title="Persentase (%)",
            range=[0, 100],
            tickfont=dict(size=10)
        ),
        xaxis=dict(
            tickfont=dict(size=10)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Customer Insights
st.markdown('<div class="section-header">Wawasan Nasabah</div>', unsafe_allow_html=True)

customer_col1, customer_col2, customer_col3 = st.columns([1.5, 1, 1.5])

with customer_col1:
    # Customer Segmentation
    st.subheader("Segmentasi Nasabah")
    
    # Dummy customer segmentation data
    segment_data = pd.DataFrame({
        "Segment": ["Regular", "Premium", "Loyal", "New", "Dormant"],
        "Count": [4300, 2100, 1750, 1200, 650]
    })
    
    # Calculate percentages
    total = segment_data["Count"].sum()
    segment_data["Percentage"] = segment_data["Count"] / total * 100
    
    # Sort by count
    segment_data = segment_data.sort_values("Count", ascending=False)
    
    # Create a horizontal bar chart
    fig = px.bar(
        segment_data,
        y="Segment",
        x="Count",
        orientation='h',
        text=segment_data["Percentage"].apply(lambda x: f"{x:.1f}%"),
        color="Count",
        color_continuous_scale="Blues",
        labels={"Count": "Jumlah Nasabah", "Segment": ""}
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

with customer_col2:
    # Average Loan Value by Category
    st.subheader("Nilai Gadai Rata-rata")
    
    # Dummy data for average loan values by category
    avg_loan_data = pd.DataFrame({
        "Category": ["Kendaraan", "Elektronik", "Emas", "Perhiasan", "Lainnya"],
        "Value": [8500000, 2800000, 3500000, 4200000, 1500000]
    })
    
    # Create a bar chart
    fig = px.bar(
        avg_loan_data,
        x="Category",
        y="Value",
        color="Category",
        labels={"Value": "Nilai (Rp)", "Category": ""}
    )
    
    fig.update_layout(
        height=300,
        yaxis=dict(title="Nilai Gadai Rata-rata"),
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    
    # Format y-axis to currency
    fig.update_yaxes(tickprefix="Rp", tickformat=",")
    
    st.plotly_chart(fig, use_container_width=True)

with customer_col3:
    # Customer Retention
    st.subheader("Tingkat Retensi Nasabah")
    
    # Dummy customer retention data over months
    retention_data = pd.DataFrame({
        "Month": data["historical"]["month_name"],
        "Retention_Rate": [
            82, 81, 83, 85, 84, 79, 78, 76, 75, 77, 79, 82, 84, 85, 86, 87, 88, 89
        ]
    })
    
    # Create line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=retention_data["Month"], 
        y=retention_data["Retention_Rate"],
        mode='lines+markers',
        name='Retention Rate',
        line=dict(color='royalblue', width=2)
    ))
    
    # Add target line
    fig.add_trace(go.Scatter(
        x=retention_data["Month"],
        y=[85] * len(retention_data),
        mode='lines',
        name='Target',
        line=dict(dash='dash', color='red', width=1)
    ))
    
    fig.update_layout(
        height=300,
        yaxis=dict(
            title="Retention Rate (%)",
            range=[70, 95]
        ),
        xaxis=dict(
            tickangle=45,
            tickmode='array',
            tickvals=list(retention_data["Month"])[::3],  # Show every 3rd month
            ticktext=list(retention_data["Month"])[::3]
        ),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Risk Analysis
st.markdown('<div class="section-header">Analisis Risiko</div>', unsafe_allow_html=True)

risk_col1, risk_col2 = st.columns(2)

with risk_col1:
    # NPL (Non-Performing Loan) by Province
    st.subheader("NPL per Provinsi")
    
    # Generate random NPL rates for provinces
    np.random.seed(42)  # For reproducibility
    npl_data = data["provinces"].copy()
    npl_data["npl_rate"] = np.random.uniform(1.5, 8.2, len(npl_data))
    
    # Sort and keep top 15 provinces with highest NPL
    npl_data = npl_data.sort_values("npl_rate", ascending=False).head(15)
    
    # Create a horizontal bar chart
    fig = px.bar(
        npl_data,
        y="province",
        x="npl_rate",
        orientation='h',
        labels={"province": "Provinsi", "npl_rate": "NPL Rate (%)"},
        color="npl_rate",
        color_continuous_scale="RdYlGn_r",
        range_color=[1.5, 8.2]
    )
    
    # Add a reference line for the average NPL
    avg_npl = npl_data["npl_rate"].mean()
    fig.add_vline(
        x=avg_npl, 
        line_dash="dash", 
        line_color="black",
        annotation_text=f"Avg: {avg_npl:.1f}%",
        annotation_position="top right"
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(title=""),
        xaxis=dict(title="NPL Rate (%)"),
        coloraxis_colorbar=dict(title="NPL Rate (%)")
    )
    
    st.plotly_chart(fig, use_container_width=True)

with risk_col2:
    # Risk Score Distribution
    st.subheader("Distribusi Risk Score Outlet")
    
    # Risk scores from outlets data
    risk_scores = data["outlets"]["risk_score"]
    
    # Create histogram
    fig = px.histogram(
        risk_scores, 
        nbins=20,
        labels={"value": "Risk Score", "count": "Jumlah Outlet"},
        color_discrete_sequence=["royalblue"]
    )
    
    # Add a reference line for the average risk score
    avg_risk = risk_scores.mean()
    fig.add_vline(
        x=avg_risk, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Avg: {avg_risk:.2f}",
        annotation_position="top right"
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title="Risk Score (1-5)"),
        yaxis=dict(title="Jumlah Outlet"),
        bargap=0.1
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Business Simulation
st.markdown('<div class="section-header">Simulasi Bisnis</div>', unsafe_allow_html=True)

# Business scenario simulation data
scenario_data = data["scenarios"]

# Create a radar chart for comparing scenarios
categories = ['growth_rate', 'redemption_rate', 'profit_margin', 'risk_score']
category_labels = {
    'growth_rate': 'Pertumbuhan (%)',
    'redemption_rate': 'Tingkat Penebusan (%)',
    'profit_margin': 'Margin Keuntungan (%)',
    'risk_score': 'Risk Score (1-5)'
}

# Set up the simulation
sim_col1, sim_col2 = st.columns([2, 3])

with sim_col1:
    st.subheader("Pemilihan Skenario")
    
    selected_scenario = st.radio(
        "Pilih skenario bisnis:",
        scenario_data["name"].tolist()
    )
    
    # Get the selected scenario data
    selected_scenario_data = scenario_data[scenario_data["name"] == selected_scenario].iloc[0]
    
    # Display scenario metrics
    st.markdown("**Detail Skenario:**")
    
    metrics_col1, metrics_col2 = st.columns(2)
    
    with metrics_col1:
        st.metric("Pertumbuhan", f"{selected_scenario_data['growth_rate']}%")
        st.metric("Tingkat Penebusan", f"{selected_scenario_data['redemption_rate']}%")
    
    with metrics_col2:
        st.metric("Margin Keuntungan", f"{selected_scenario_data['profit_margin']}%")
        st.metric("Risk Score", f"{selected_scenario_data['risk_score']:.1f}/5")
    
    # Add scenario description
    descriptions = {
        "Baseline": "Melanjutkan operasi dengan model bisnis saat ini tanpa perubahan signifikan.",
        "Ekspansi Outlet": "Menambah jumlah outlet baru di wilayah potensial untuk memperluas jangkauan.",
        "Penurunan Bunga": "Menurunkan tingkat bunga untuk meningkatkan daya saing dan pangsa pasar.",
        "Fokus Digital": "Berinvestasi pada platform digital untuk mempercepat proses dan menjangkau nasabah online."
    }
    
    st.markdown(f"**Deskripsi:**")
    st.markdown(descriptions.get(selected_scenario, ""))
    
    # Add a what-if analysis for interest rate
    st.markdown("### What-If Analysis")
    
    interest_rate = st.slider(
        "Tingkat Bunga (%)",
        min_value=0.5,
        max_value=3.0,
        value=1.5,
        step=0.1
    )
    
    # Calculate impact based on interest rate
    baseline_interest = 1.5  # Assume baseline is 1.5%
    growth_delta = (baseline_interest - interest_rate) * 5  # Each 0.1% change affects growth by 0.5%
    redemption_delta = (baseline_interest - interest_rate) * 2  # Each 0.1% change affects redemption by 0.2%
    margin_delta = (interest_rate - baseline_interest) * 4  # Each 0.1% change affects margin by 0.4%
    
    adjusted_growth = selected_scenario_data['growth_rate'] + growth_delta
    adjusted_redemption = selected_scenario_data['redemption_rate'] + redemption_delta
    adjusted_margin = selected_scenario_data['profit_margin'] + margin_delta
    
    st.markdown("**Dampak Perubahan Bunga:**")
    impact_col1, impact_col2 = st.columns(2)
    
    with impact_col1:
        st.metric(
            "Pertumbuhan", 
            f"{adjusted_growth:.1f}%",
            f"{growth_delta:+.1f}%"
        )
        st.metric(
            "Tingkat Penebusan",
            f"{adjusted_redemption:.1f}%",
            f"{redemption_delta:+.1f}%"
        )
    
    with impact_col2:
        st.metric(
            "Margin Keuntungan",
            f"{adjusted_margin:.1f}%",
            f"{margin_delta:+.1f}%"
        )
        
        # Calculate a combined score
        baseline_score = (selected_scenario_data['growth_rate'] + 
                          selected_scenario_data['redemption_rate'] * 0.5 + 
                          selected_scenario_data['profit_margin'] * 2) / 3
        
        adjusted_score = (adjusted_growth + 
                         adjusted_redemption * 0.5 + 
                         adjusted_margin * 2) / 3
        
        st.metric(
            "Business Performance Score",
            f"{adjusted_score:.1f}",
            f"{adjusted_score - baseline_score:+.1f}"
        )

with sim_col2:
    # Create a radar chart comparing all scenarios
    st.subheader("Perbandingan Skenario")
    
    # Prepare data for radar chart
    fig = go.Figure()
    
    for i, scenario in scenario_data.iterrows():
        # Scale all values to 0-100 for radar chart
        values = []
        for cat in categories:
            if cat == 'risk_score':
                # Invert risk score (lower is better)
                val = (6 - scenario[cat]) * 20  # Scale to 0-100
            elif cat == 'redemption_rate':
                # Scale to 0-100
                val = scenario[cat]
            else:
                # Scale to 0-100 with maximum expected value of 25
                val = min(scenario[cat] * 4, 100)
            values.append(val)
        
        # Add one more value to close the loop
        values.append(values[0])
        cats = [category_labels[c] for c in categories]
        cats.append(cats[0])
        
        # Add trace for this scenario
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=cats,
            fill='toself',
            name=scenario['name'],
            line_color='darkblue' if scenario['name'] == selected_scenario else None
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Footer with update information
st.markdown('<div class="footer">Dashboard Pusat Gadai Indonesia | Terakhir diperbarui: April 26, 2025 | Data hanya untuk tujuan demonstrasi</div>', unsafe_allow_html=True)

# Ekspansi Outlet Analysis
st.markdown('<div class="section-header">Analisis Ekspansi Outlet</div>', unsafe_allow_html=True)
st.subheader("Simulasi Potensi Outlet Baru")

# Create two columns for the expansion analysis
exp_col1, exp_col2 = st.columns([1, 2])

with exp_col1:
    st.markdown("### Input Parameter Lokasi")
    
    # Input for region
    region_options = sorted(["DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", 
                       "Banten", "Sumatera Utara", "Sumatera Barat", "Riau", "Sumatera Selatan",
                       "Kalimantan Timur", "Sulawesi Selatan", "Bali"])
    selected_expansion_area = st.selectbox("Pilih Daerah/Kota:", region_options)
    
    # Key socio-economic variables
    st.markdown("#### Data Demografis & Ekonomi")
    penduduk = st.number_input("Jumlah Penduduk (ribu)", min_value=0, max_value=5000, value=250, step=10)
    kemiskinan = st.slider("Tingkat Kemiskinan (%)", min_value=0.0, max_value=30.0, value=9.5, step=0.1)
    umk = st.number_input("UMK (Rp)", min_value=1000000, max_value=6000000, value=3500000, step=100000, format="%d")
    
    # Infrastructure variables
    st.markdown("#### Infrastruktur")
    lebar_jalan = st.slider("Lebar Jalan (m)", min_value=2, max_value=50, value=12)
    lebar = st.slider("Lebar Bangunan (m)", min_value=2, max_value=30, value=6)
    
    # Nearby facilities
    st.markdown("#### Fasilitas Sekitar")
    kompetitor = st.number_input("Jumlah Kompetitor", min_value=0, max_value=20, value=3)
    ada_pgi = st.checkbox("Sudah Ada Outlet PGI di Sekitar", value=False)
    
    col_a, col_b = st.columns(2)
    with col_a:
        pasar = st.number_input("Pasar", min_value=0, max_value=10, value=1)
        toko_elektronik = st.number_input("Toko Elektronik", min_value=0, max_value=50, value=15)
        toko_handphone = st.number_input("Toko Handphone", min_value=0, max_value=50, value=20)
    
    with col_b:
        minimarket = st.number_input("Minimarket", min_value=0, max_value=50, value=12)
        restaurant = st.number_input("Restaurant", min_value=0, max_value=50, value=18)
        pom_bensin = st.number_input("SPBU", min_value=0, max_value=10, value=2)
    
    fasilitas_kesehatan = st.number_input("Fasilitas Kesehatan", min_value=0, max_value=20, value=5)
    universitas = st.number_input("Universitas/Sekolah", min_value=0, max_value=10, value=2)
    
    # Target omset
    omset_target = st.number_input("Target Omset Bulanan (Juta Rp)", min_value=50, max_value=2000, value=350, step=10)
    
    # Generate analysis button
    generate_analysis = st.button("Analisis Potensi Lokasi", type="primary")

# Kolom untuk hasil analisis
with exp_col2:
    # If button is clicked, generate analysis
    if generate_analysis:
        st.markdown("### Hasil Analisis Potensi Lokasi")
        
        # Create a score based on the inputs (simplified model)
        demographic_score = min(penduduk / 50, 10) - min(kemiskinan / 3, 10) + min(umk / 500000, 10)
        infrastructure_score = min(lebar_jalan / 5, 10) + min(lebar / 3, 10)
        
        facility_score = (
            min(pasar * 2, 10) + 
            min(toko_elektronik / 5, 10) + 
            min(toko_handphone / 5, 10) + 
            min(minimarket / 5, 10) + 
            min(restaurant / 5, 10) + 
            min(pom_bensin * 2, 10) + 
            min(fasilitas_kesehatan * 1.5, 10) + 
            min(universitas * 3, 10)
        ) / 8
        
        # Competition has negative impact
        competition_score = 10 - min(kompetitor * 2, 10)
        if ada_pgi:
            competition_score -= 5
        
        # Calculate final score with weighting
        final_score = (
            demographic_score * 0.35 + 
            infrastructure_score * 0.15 + 
            facility_score * 0.30 + 
            competition_score * 0.20
        )
        
        # Scale to 0-100
        final_score = min(max(final_score * 10, 0), 100)
        
        # Display score with gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = final_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Skor Potensi Lokasi"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 50], 'color': "orange"},
                    {'range': [50, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Recommendation based on score
        st.markdown("#### Rekomendasi")
        if final_score >= 80:
            recommendation = "Sangat Potensial"
            desc = "Lokasi sangat strategis dengan potensi bisnis tinggi. Direkomendasikan untuk menjadi prioritas utama ekspansi."
            action = "Lanjutkan ke tahap negosiasi sewa/pembelian dan persiapan pembukaan outlet."
        elif final_score >= 65:
            recommendation = "Potensial"
            desc = "Lokasi memiliki potensi yang baik. Perlu pertimbangan lebih lanjut mengenai beberapa aspek."
            action = "Lakukan survey lapangan lebih detail dan analisis kompetitor."
        elif final_score >= 50:
            recommendation = "Cukup Potensial"
            desc = "Lokasi memiliki beberapa indikator positif namun juga beberapa tantangan."
            action = "Pertimbangkan faktor khusus seperti demografi atau infrastruktur tambahan."
        elif final_score >= 30:
            recommendation = "Kurang Potensial"
            desc = "Lokasi kurang strategis dengan beberapa hambatan signifikan."
            action = "Tidak direkomendasikan kecuali ada faktor khusus yang belum tercakup dalam analisis."
        else:
            recommendation = "Tidak Potensial"
            desc = "Lokasi tidak memenuhi kriteria minimum untuk pembukaan outlet baru."
            action = "Cari alternatif lokasi lain di area sekitar atau kota lain."
        
        st.markdown(f"**Status**: {recommendation}")
        st.markdown(f"**Deskripsi**: {desc}")
        st.markdown(f"**Tindakan yang Disarankan**: {action}")
        
        # Financial projections
        st.markdown("#### Proyeksi Keuangan")
        
        # Calculate projected performance based on score and target
        performance_factor = final_score / 100 * random.uniform(0.8, 1.2)  # Add some randomness
        projected_omset = omset_target * performance_factor
        
        # Costs assumptions
        sewa_bulanan = 15 + random.uniform(-3, 5)  # Juta Rupiah
        operasional = projected_omset * 0.15  # 15% of omset for operational costs
        gaji_karyawan = 12 + random.uniform(-1, 2)  # Juta Rupiah
        
        # Profit calculation
        profit = projected_omset - operasional - sewa_bulanan - gaji_karyawan
        profit_margin = (profit / projected_omset) * 100 if projected_omset > 0 else 0
        
        # Breakeven calculation (simplified)
        monthly_costs = sewa_bulanan + gaji_karyawan
        variable_cost_rate = 0.15  # Assume 15% variable costs
        contribution_margin_rate = 1 - variable_cost_rate
        breakeven_omset = monthly_costs / contribution_margin_rate
        
        # ROI calculation (simplified)
        initial_investment = 150 + random.uniform(-20, 30)  # Juta Rupiah
        monthly_profit = profit
        roi_months = initial_investment / monthly_profit if monthly_profit > 0 else float('inf')
        
        # Create financial metrics table
        financial_data = {
            "Metrik": ["Proyeksi Omset Bulanan", "Biaya Sewa", "Biaya Operasional", "Gaji Karyawan", 
                      "Profit Bulanan", "Margin Keuntungan", "Breakeven Point", "Modal Awal", "ROI (Bulan)"],
            "Nilai": [
                f"Rp {projected_omset:.1f} juta",
                f"Rp {sewa_bulanan:.1f} juta",
                f"Rp {operasional:.1f} juta",
                f"Rp {gaji_karyawan:.1f} juta",
                f"Rp {profit:.1f} juta",
                f"{profit_margin:.1f}%",
                f"Rp {breakeven_omset:.1f} juta",
                f"Rp {initial_investment:.1f} juta",
                f"{roi_months:.1f} bulan"
            ]
        }
        
        # Apply color to profit-related metrics
        financial_df = pd.DataFrame(financial_data)
        
        # Display the table
        st.table(financial_df)
        
        # Add a note about assumptions
        st.markdown("""
        <div class="small-text">
        <strong>Catatan Asumsi:</strong><br>
        - Proyeksi berdasarkan data historis outlet dengan karakteristik serupa<br>
        - Biaya operasional termasuk utilitas, keamanan, dan perlengkapan kantor<br>
        - Modal awal mencakup renovasi, perizinan, dan peralatan<br>
        - ROI dihitung berdasarkan profit bulanan konsisten
        </div>
        """, unsafe_allow_html=True)
        
        # Risk factors specific to location
        st.markdown("#### Faktor Risiko Spesifik Lokasi")
        
        # Calculate risk factors based on inputs
        risks = []
        
        if kemiskinan > 20:
            risks.append("Tingkat kemiskinan tinggi (risiko daya beli rendah)")
        
        if kompetitor > 5:
            risks.append("Tingkat kompetisi tinggi")
            
        if ada_pgi:
            risks.append("Potensi kanibalisasi dengan outlet PGI lainnya")
            
        if lebar_jalan < 8:
            risks.append("Akses jalan terbatas")
            
        if penduduk < 150:
            risks.append("Kepadatan populasi rendah")
            
        if pasar + minimarket + restaurant < 10:
            risks.append("Fasilitas komersial sekitar terbatas")
            
        # Add some random risks based on selected area
        area_specific_risks = {
            "DKI Jakarta": ["Biaya sewa tinggi", "Kepadatan lalu lintas", "Persaingan tinggi"],
            "Jawa Barat": ["Variasi ekonomi antar wilayah", "Tantangan distribusi"],
            "Bali": ["Fluktuasi musiman (pariwisata)", "Sensitivitas terhadap isu keamanan global"],
            "Sumatera Utara": ["Tantangan logistik", "Variasi budaya signifikan"]
        }
        
        if selected_expansion_area in area_specific_risks:
            specific_risk = random.choice(area_specific_risks[selected_expansion_area])
            risks.append(specific_risk)
        
        # If no risks identified, add positive note
        if not risks:
            st.markdown("✅ Tidak ada faktor risiko signifikan teridentifikasi")
        else:
            for risk in risks:
                st.markdown(f"⚠️ {risk}")
            
        # Potential mitigation
        if risks:
            st.markdown("#### Mitigasi Potensial")
            mitigations = {
                "Tingkat kemiskinan tinggi": "Fokus pada produk gadai dengan nilai terjangkau, program edukasi keuangan",
                "Tingkat kompetisi tinggi": "Diferensiasi layanan, program loyalitas, peningkatan kualitas pelayanan",
                "Potensi kanibalisasi": "Spesialisasi produk atau segmen, koordinasi strategi pemasaran",
                "Akses jalan terbatas": "Peningkatan visibilitas, signage yang jelas, layanan pickup",
                "Kepadatan populasi rendah": "Ekspansi coverage area, layanan mobile/pickup, marketing yang lebih luas",
                "Fasilitas komersial sekitar terbatas": "Kemitraan dengan bisnis sekitar, program cross-promotion",
                "Biaya sewa tinggi": "Negosiasi kontrak jangka panjang, optimasi penggunaan ruang",
                "Kepadatan lalu lintas": "Jam operasional yang diperpanjang, layanan online/booking",
                "Persaingan tinggi": "Diferensiasi layanan, program insentif khusus",
                "Variasi ekonomi antar wilayah": "Penyesuaian produk berdasarkan demografi lokal",
                "Tantangan distribusi": "Kemitraan logistik lokal, optimasi rantai pasokan",
                "Fluktuasi musiman (pariwisata)": "Diversifikasi produk, program promosi counter-seasonal",
                "Tantangan logistik": "Kerja sama dengan penyedia logistik lokal, stok cadangan strategis",
                "Variasi budaya signifikan": "Penyesuaian pendekatan marketing, rekrutmen staf lokal"
            }
            
            for risk in risks:
                if risk in mitigations:
                    st.markdown(f"**{risk}**: {mitigations[risk]}")
    else:
        # Show placeholder when analysis hasn't been generated
        st.markdown("""
        ### Analisis Potensi Lokasi
        
        Gunakan panel di sebelah kiri untuk memasukkan data lokasi yang ingin dianalisis sebagai kandidat outlet baru.
        
        Sistem akan memberikan:
        - Skor kelayakan lokasi
        - Rekomendasi pembukaan outlet
        - Proyeksi finansial
        - Analisis risiko khusus lokasi
        
        Masukkan data yang diperlukan dan klik "Analisis Potensi Lokasi" untuk melihat hasil.
        """)

# Competitor Analysis
st.markdown('<div class="section-header">Analisis Kompetitor</div>', unsafe_allow_html=True)

# Competitor radio buttons with custom styling
st.markdown('''
<div class="competitor-toggle">
    <div class="competitor-button active">Pusat Gadai Indonesia</div>
    <div class="competitor-button">Pegadaian (625)</div>
    <div class="competitor-button">Bank BRI (235)</div>
    <div class="competitor-button">Bank Syariah (97)</div>
    <div class="competitor-button">Fintech (122)</div>
    <div class="competitor-button">Lainnya (82)</div>
</div>
''', unsafe_allow_html=True)

comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    # Market share pie chart
    market_share_data = data["competitors"].copy()
    # Add our company
    our_company = pd.DataFrame([{
        "name": "Pusat Gadai Indonesia", 
        "outlets": len(data["outlets"]),
        "market_share": 100 - market_share_data["market_share"].sum()
    }])
    market_share_data = pd.concat([our_company, market_share_data])
    
    fig = px.pie(
        market_share_data, 
        values='market_share', 
        names='name',
        title="Market Share Industri Gadai (%)",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

with comp_col2:
    # Competitor outlet comparison
    outlets_data = market_share_data.copy()
    
    fig = px.bar(
        outlets_data,
        x="name",
        y="outlets",
        title="Perbandingan Jumlah Outlet",
        color="name",
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Jumlah Outlet",
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
