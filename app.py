import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils import load_data_from_gcs, process_data

# Konfigurasi halaman
st.set_page_config(
    page_title="Big Player Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================== PERBAIKAN CSS ========================
st.markdown("""
<style>
    /* Global */
    .stApp {
        background-color: #0e1117;
        color: #f0f0f0 !important;
    }
    
    /* Semua teks */
    body, p, h1, h2, h3, h4, h5, h6, div, span {
        color: #f0f0f0 !important;
    }
    
    /* Header */
    .header-section {
        border-bottom: 2px solid #2a2f4f;
        padding-bottom: 10px;
        margin-bottom: 20px;
        color: #ffffff;
    }
    
    /* Kartu Saham */
    .stock-card {
        background-color: #1e2130;
        color: #ffffff;
        border: 1px solid #2a2f4f;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        transition: transform 0.2s;
    }
    .stock-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    
    /* Tabel */
    .stDataFrame th {
        background-color: #2a2f4f !important;
        color: white !important;
    }
    .stDataFrame td {
        background-color: #1e2130 !important;
        color: #f0f0f0 !important;
    }
    
    /* Input & Dropdown */
    .stSelectbox, .stMultiSelect, .stDateInput, .stNumberInput {
        background-color: #1e2130;
        color: white;
        border-color: #4a4f69;
    }
    .st-bd {
        background-color: #1e2130 !important;
    }
    .st-at {
        background-color: #2a2f4f !important;
    }
    
    /* Tombol */
    .stButton>button {
        background-color: #4a4f69;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #5a5f79;
    }
    
    /* Metric */
    .stMetric {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #2a2f4f;
    }
    
    /* Plotly Chart */
    .js-plotly-plot .plotly, .main-svg {
        background-color: transparent !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #0e1117;
        border-right: 1px solid #2a2f4f;
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        color: white !important;
    }
    
    /* Footer */
    .footer {
        color: #a0a0a0;
        font-size: 0.9em;
        text-align: center;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #2a2f4f;
    }
</style>
""", unsafe_allow_html=True)

# Judul Dashboard
st.title("📈 Big Player & Bandarmologi Analysis")
st.markdown("""
    <div class="header-section">
        Dashboard ini menampilkan <strong>Top 25 Stock Picks</strong> berdasarkan analisis pergerakan big player (akumulasi/distribusi) dan sinyal bandarmologi.
    </div>
""", unsafe_allow_html=True)

# Parameter GCS
BUCKET_NAME = "stock-csvku"
FILE_NAME = "hasil_gabungan.csv"

# Load data
@st.cache_data(ttl=3600, show_spinner="Memuat data saham terbaru...") 
def load_data():
    # ... [kode load data tetap sama] ...

# UI Loading
# ... [kode loading tetap sama] ...

# ======================== PERBAIKAN VISUALISASI ========================

# Top 25 Stock Picks
st.header("🔥 Top 25 Stock Picks")
if not df_filtered.empty:
    df_top25 = df_filtered.sort_values('Strength_Score', ascending=False).head(25)

    # Tampilkan dalam grid
    cols = st.columns(5)
    for idx, (_, row) in enumerate(df_top25.iterrows()):
        with cols[idx % 5]:
            signal_color = "#00ff8c" if "Akumulasi" in str(row['Final Signal']) else "#ff4d4d"
            foreign_color = "#00ff8c" if row['Foreign Flow'] == 'Inflow' else "#ff4d4d"
            
            card = f"""
            <div class="stock-card">
                <h4 style="color:white">{row['Stock Code']}</h4>
                <p style="margin:5px 0;font-size:0.9em;color:#d0d0d0">{row['Company Name']}</p>
                <div style="display:flex;justify-content:space-between">
                    <span style="color:#a0a0a0"><strong>Sektor:</strong> {row['Sector']}</span>
                    <span style="color:{signal_color}"><strong>{row['Final Signal']}</strong></span>
                </div>
                <div style="margin-top:10px;background:#2a2f4f;border-radius:5px;padding:5px;text-align:center">
                    <strong style="color:#c0c0c0">Strength Score:</strong> 
                    <span style="font-size:1.2em;color:{signal_color}">{row['Strength_Score']:.1f}</span>
                </div>
                <div style="margin-top:10px;display:flex;justify-content:space-between">
                    <div>
                        <div style="color:#a0a0a0">Volume</div>
                        <div><strong style="color:white">{row['Volume']/1e6:.1f}M</strong></div>
                    </div>
                    <div>
                        <div style="color:#a0a0a0">Foreign</div>
                        <div style="color:{foreign_color}">
                            <strong>{row['Foreign Flow']}</strong>
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(card, unsafe_allow_html=True)
else:
    st.warning("Tidak ada data setelah filter tanggal dan sektor")

# Visualisasi 1: Heatmap Bandarmologi
st.header("📊 Heatmap Bandarmologi")
if not df_filtered.empty:
    heatmap_data = df_filtered.pivot_table(
        index='Sector',
        columns='Final Signal',
        values='Strength_Score',
        aggfunc='mean',
        fill_value=0
    )

    if not heatmap_data.empty:
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Sinyal", y="Sektor", color="Strength Score"),
            color_continuous_scale='RdYlGn',
            aspect="auto"
        )
        
        # PERBAIKAN: Tema dark untuk plotly
        fig_heatmap.update_layout(
            title='Rata-rata Strength Score per Sektor dan Sinyal',
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(tickfont=dict(color='white')),
            yaxis=dict(tickfont=dict(color='white')),
            coloraxis_colorbar=dict(
                title_font=dict(color='white'),
                tickfont=dict(color='white')
            )
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("Tidak ada data untuk menampilkan heatmap.")
else:
    st.warning("Tidak ada data untuk heatmap")

# Visualisasi lainnya (Big Player Movement, Sektor Rotation) 
# ... [Tambahkan update_layout serupa untuk semua plotly] ...

# Footer
st.markdown("---")
st.markdown("""
    <div class="footer">
        <strong>Big Player Stock Analysis</strong> | Data diperbarui setiap hari bursa<br>
        © 2024 Bandarmologi Analytics Team | [Beri Masukan](mailto:feedback@bandarmologi.com)
    </div>
""", unsafe_allow_html=True)
