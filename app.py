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

# CSS Custom
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stock-card {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #1e2130;
        transition: transform 0.2s;
    }
    .stock-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    .positive {
        color: #00ff8c;
    }
    .negative {
        color: #ff4d4d;
    }
    .header-section {
        border-bottom: 2px solid #2a2f4f;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .st-bd {
        background-color: #161a28 !important;
    }
    .st-at {
        background-color: #2a2f4f !important;
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
@st.cache_data(ttl=3600)  # Cache data selama 1 jam
def load_data():
    df = load_data_from_gcs(BUCKET_NAME, FILE_NAME)
    if df.empty:
        return df
    df['Last Trading Date'] = pd.to_datetime(df['Last Trading Date'])
    return process_data(df)

with st.spinner('Memuat data saham terbaru...'):
    df = load_data()
    if df.empty:
        st.error("Data kosong atau gagal dimuat. Periksa koneksi atau konfigurasi.")
        st.stop()
    latest_date = df['Last Trading Date'].max()
    st.success(f"Data berhasil dimuat! Terakhir diperbarui: {latest_date.strftime('%d %B %Y')}")

# Filter tanggal
st.sidebar.header("Filter Dashboard")
date_options = sorted(df['Last Trading Date'].unique(), reverse=True)
selected_date = st.sidebar.selectbox(
    "Pilih Tanggal", 
    options=date_options,
    index=0,
    format_func=lambda x: x.strftime('%d %b %Y')
)

# Filter sektor
all_sectors = sorted(df['Sector'].unique())
selected_sectors = st.sidebar.multiselect(
    "Filter Sektor",
    options=all_sectors,
    default=all_sectors
)

# Filter data
df_filtered = df[
    (df['Last Trading Date'] == selected_date) & 
    (df['Sector'].isin(selected_sectors))
]

# Top 25 Stock Picks
st.header("🔥 Top 25 Stock Picks")
df_top25 = df_filtered.sort_values('Strength_Score', ascending=False).head(25)

# Tampilkan dalam grid
cols = st.columns(5)
for idx, (_, row) in enumerate(df_top25.iterrows()):
    with cols[idx % 5]:
        signal_color = "#00ff8c" if "Akumulasi" in row['Final Signal'] else "#ff4d4d"
        card = f"""
        <div class="stock-card">
            <h4>{row['Stock Code']}</h4>
            <p style="margin:5px 0;font-size:0.9em">{row['Company Name']}</p>
            <div style="display:flex;justify-content:space-between">
                <span><strong>Sektor:</strong> {row['Sector']}</span>
                <span style="color:{signal_color}"><strong>{row['Final Signal']}</strong></span>
            </div>
            <div style="margin-top:10px;background:#2a2f4f;border-radius:5px;padding:5px;text-align:center">
                <strong>Strength Score:</strong> 
                <span style="font-size:1.2em;color:{signal_color}">{row['Strength_Score']:.1f}</span>
            </div>
            <div style="margin-top:10px;display:flex;justify-content:space-between">
                <div>
                    <div>Volume</div>
                    <div><strong>{row['Volume']/1e6:.1f}M</strong></div>
                </div>
                <div>
                    <div>Foreign</div>
                    <div style="color:{'#00ff8c' if row['Foreign Flow'] == 'Inflow' else '#ff4d4d'}">
                        <strong>{row['Foreign Flow']}</strong>
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(card, unsafe_allow_html=True)

# Visualisasi 1: Heatmap Bandarmologi
st.header("📊 Heatmap Bandarmologi")
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
    fig_heatmap.update_layout(
        title='Rata-rata Strength Score per Sektor dan Sinyal',
        height=500
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
else:
    st.info("Tidak ada data untuk menampilkan heatmap.")

# Visualisasi 2: Big Player Movement
st.header("🚨 Big Player Movement Tracker")
df_signals = df_filtered[df_filtered['Big_Player_Pattern'] != "Normal"]

if not df_signals.empty:
    fig_signals = px.scatter(
        df_signals,
        x='Bid/Offer Imbalance',
        y='Volume_Spike_Ratio',
        color='Big_Player_Pattern',
        size='Strength_Score',
        hover_name='Stock Code',
        log_y=True,
        color_discrete_map={
            "Big Player Accumulation": "#00ff8c",
            "Bandar Accumulation": "#00cc66",
            "Big Player Distribution": "#ff4d4d",
            "Bandar Distribution": "#cc0000"
        }
    )
    fig_signals.update_layout(
        title='Pola Pergerakan Big Player',
        xaxis_title="Bid/Offer Imbalance",
        yaxis_title="Volume Spike Ratio (vs 30d avg)",
        height=600
    )
    st.plotly_chart(fig_signals, use_container_width=True)
else:
    st.info("Tidak ada sinyal big player kuat hari ini")

# Visualisasi 3: Sektor Rotation Analysis
st.header("🔄 Sektor Rotation Analysis")
if not df_filtered.empty:
    sector_trend = df_filtered.groupby('Sector').agg({
        'Strength_Score': 'mean',
        'Volume': 'sum'
    }).reset_index().sort_values('Strength_Score', ascending=False)

    fig_sector = go.Figure()
    fig_sector.add_trace(go.Bar(
        x=sector_trend['Sector'],
        y=sector_trend['Strength_Score'],
        name='Strength Score',
        marker_color='#636efa'
    ))
    fig_sector.add_trace(go.Scatter(
        x=sector_trend['Sector'],
        y=sector_trend['Volume'] / sector_trend['Volume'].max() * 100,
        name='Volume (%)',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#ff7f0e', width=3)
    ))
    fig_sector.update_layout(
        title='Kekuatan dan Volume per Sektor',
        yaxis=dict(title='Strength Score'),
        yaxis2=dict(
            title='Volume (%)',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        height=500
    )
    st.plotly_chart(fig_sector, use_container_width=True)
else:
    st.info("Tidak ada data sektor untuk ditampilkan.")

# Detail Saham Terpilih
st.header("🔍 Detail Saham")
if not df_top25.empty:
    selected_stock = st.selectbox(
        "Pilih Saham untuk Analisa Detail",
        options=df_top25['Stock Code'].unique()
    )

    if selected_stock:
        stock_data = df_top25[df_top25['Stock Code'] == selected_stock].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Kode Saham", stock_data['Stock Code'])
            st.metric("Perusahaan", stock_data['Company Name'])
            st.metric("Sektor", stock_data['Sector'])
        
        with col2:
            signal_color = "#00ff8c" if "Akumulasi" in stock_data['Final Signal'] else "#ff4d4d"
            st.metric("Sinyal Akhir", stock_data['Final Signal'], delta=None, 
                     delta_color="normal", help="Sinyal berdasarkan VWAP dan volume")
            st.metric("Strength Score", f"{stock_data['Strength_Score']:.1f}", 
                     delta=f"Rank {list(df_top25['Stock Code']).index(selected_stock)+1} dari 25")
            st.metric("Pola Big Player", stock_data['Big_Player_Pattern'])
        
        with col3:
            st.metric("Harga Penutupan", f"Rp {stock_data['Close']:,.0f}")
            st.metric("Volume", f"{stock_data['Volume']/1e6:.2f} juta")
            st.metric("Aliran Asing", stock_data['Foreign Flow'], 
                     delta=f"Buy: {stock_data['Foreign Buy']/1e6:.1f}M / Sell: {stock_data['Foreign Sell']/1e6:.1f}M")
        
        # Grafik historis 7 hari
        st.subheader("Perkembangan 7 Hari Terakhir")
        hist_data = df[
            (df['Stock Code'] == selected_stock) & 
            (df['Last Trading Date'] >= selected_date - timedelta(days=7))
        ].sort_values('Last Trading Date')
        
        if not hist_data.empty:
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Scatter(
                x=hist_data['Last Trading Date'],
                y=hist_data['Close'],
                mode='lines+markers',
                name='Harga Penutupan',
                line=dict(color='#00ff8c', width=3)
            ))
            fig_hist.add_trace(go.Bar(
                x=hist_data['Last Trading Date'],
                y=hist_data['Volume'],
                name='Volume',
                yaxis='y2',
                marker_color='#636efa'
            ))
            fig_hist.update_layout(
                title='Harga dan Volume Historis',
                yaxis=dict(title='Harga Penutupan'),
                yaxis2=dict(
                    title='Volume',
                    overlaying='y',
                    side='right'
                ),
                height=400
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Tidak ada data historis untuk saham ini")
else:
    st.info("Tidak ada data untuk menampilkan detail saham.")

# Footer
st.markdown("---")
st.markdown("""
    **Big Player Stock Analysis** | Data diperbarui setiap hari bursa  
    © 2024 Bandarmologi Analytics Team | [Beri Masukan](mailto:feedback@bandarmologi.com)
""")
