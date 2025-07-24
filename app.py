import streamlit as st
import pandas as pd
from datetime import datetime

from utils import load_data_from_gcs, process_data
from ui_components import display_stock_card, display_main_metrics
from plotting import (
    create_heatmap_sektor, create_big_player_scatter, create_historical_chart,
    create_volume_frequency_scatter, create_wbw_sektor_chart, create_wbw_saham_chart,
    create_wbw_foreign_flow_chart
)

st.set_page_config(
    page_title="Big Player Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""<style>
.stApp { background-color: #0e1117; color: #f0f0f0; }
.stock-card { background-color: #1e2130; border: 1px solid #2a2f4f; border-radius: 10px; padding: 15px; margin: 10px 5px; transition: transform 0.2s; height: 230px; display: flex; flex-direction: column; justify-content: space-between; }
.stock-card:hover { transform: translateY(-5px); }
.stMetric { background-color: #1e2130; border-radius: 10px; padding: 10px; border: 1px solid #2a2f4f; }
</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner="Memuat data saham terbaru...")
def load_and_process_data(bucket_name, file_name):
    try:
        df = load_data_from_gcs(bucket_name, file_name)
        return process_data(df) if not df.empty else pd.DataFrame()
    except Exception as e:
        st.error(f"Error saat memuat data: {e}")
        return pd.DataFrame()

st.title("📈 Big Player & Bandarmologi Analysis")
st.markdown("Dasbor interaktif untuk melacak pergerakan Big Player, sinyal Bandarmologi, dan analisis mingguan.")

BUCKET_NAME = "stock-csvku"
FILE_NAME = "hasil_gabungan.csv"
df_full = load_and_process_data(BUCKET_NAME, FILE_NAME)

if df_full.empty:
    st.error("Data tidak tersedia. Silakan cek konfigurasi atau sumber data.")
    st.stop()

st.sidebar.header("Filter Global")
date_options = sorted(df_full['Last Trading Date'].unique(), reverse=True)
selected_date = st.sidebar.selectbox("Pilih Tanggal Analisis", options=date_options, format_func=lambda x: pd.to_datetime(x).strftime('%d %b %Y'))
all_sectors = sorted(df_full['Sector'].unique())
selected_sectors = st.sidebar.multiselect("Filter Sektor", options=all_sectors, default=all_sectors)

df_filtered = df_full[(df_full['Last Trading Date'] == selected_date) & (df_full['Sector'].isin(selected_sectors))].copy()
st.sidebar.info(f"Data harian ditemukan: {len(df_filtered)} baris")
if df_filtered.empty:
    st.sidebar.error("Tidak ada data untuk filter ini. Coba ganti tanggal/sektor.")

tab_titles = ["📊 Ringkasan Pasar", "🔥 Top 25 Pilihan", "🔍 Analisis & Perbandingan", "⚡ Vol & Freq Analysis", "📅 Analisis Mingguan (WbW)"]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_titles)

with tab1:
    if not df_filtered.empty:
        display_main_metrics(df_filtered)
        st.markdown("---")
        st.subheader("Visualisasi Pasar")
        st.plotly_chart(create_heatmap_sektor(df_filtered), use_container_width=True)
        st.plotly_chart(create_big_player_scatter(df_filtered), use_container_width=True)
    else:
        st.warning("Pilih tanggal atau sektor yang valid di sidebar untuk menampilkan data.")

with tab2:
    if not df_filtered.empty:
        df_top25 = df_filtered.sort_values('Strength_Score', ascending=False).head(25)
        st.subheader(f"Top 25 Saham Pilihan pada {pd.to_datetime(selected_date).strftime('%d %B %Y')}")
        for i in range(0, len(df_top25), 5):
            cols = st.columns(5)
            for col, (idx, row) in zip(cols, df_top25.iloc[i:i+5].iterrows()):
                display_stock_card(row, col)
    else:
        st.warning("Pilih tanggal atau sektor yang valid di sidebar untuk menampilkan data.")

with tab3: # Analisis & Perbandingan
    if not df_filtered.empty:
        st.subheader("Analisis Saham Individual (Harian)")
        all_stocks_list = sorted(df_filtered['Stock Code'].unique())
        search_stock = st.selectbox("Cari saham untuk dianalisis:", options=all_stocks_list, key="search_daily")
        if search_stock:
            st.plotly_chart(create_historical_chart(df_full, search_stock, selected_date), use_container_width=True)
        st.markdown("---")
        st.subheader("Bandingkan Saham (Harian)")
        stocks_to_compare = st.multiselect("Pilih 2 hingga 4 saham untuk dibandingkan:", options=all_stocks_list, max_selections=4)
        if stocks_to_compare:
            cols = st.columns(len(stocks_to_compare))
            for i, stock_code in enumerate(stocks_to_compare):
                data_to_display = df_filtered[df_filtered['Stock Code'] == stock_code]
                if not data_to_display.empty:
                    data = data_to_display.iloc[0]
                    with cols[i]:
                        st.markdown(f"<h5>{data['Stock Code']}</h5>", unsafe_allow_html=True)
                        st.metric("Strength Score", f"{data['Strength_Score']:.1f}")
                        # --- PERUBAHAN DI SINI: Menampilkan Buy & Sell, bukan Net Flow ---
                        st.metric("Foreign Buy", f"Rp {data['Foreign Buy']/1e9:.2f} M")
                        st.metric("Foreign Sell", f"Rp {data['Foreign Sell']/1e9:.2f} M")

    else:
        st.warning("Pilih tanggal atau sektor yang valid di sidebar untuk menampilkan data.")

with tab4:
    st.header("Analisis Volume dan Frekuensi (Harian)")
    if not df_filtered.empty:
        st.plotly_chart(create_volume_frequency_scatter(df_filtered), use_container_width=True)
    else:
        st.warning("Pilih tanggal atau sektor yang valid di sidebar untuk menampilkan data.")

with tab5:
    st.header("Analisis Pergerakan Mingguan (Week-by-Week)")
    st.subheader("Performa Sektor per Minggu")
    metric_choice = st.radio("Pilih metrik:", options=['Rata-rata Harga', 'Total Volume', 'Total Frekuensi'], horizontal=True)
    st.plotly_chart(create_wbw_sektor_chart(df_full, metric_choice), use_container_width=True)
    st.markdown("---")
    st.subheader("Detail Saham per Minggu")
    stock_choice_wvw = st.selectbox("Pilih saham:", options=sorted(df_full['Stock Code'].unique()))
    if stock_choice_wvw:
        st.plotly_chart(create_wbw_saham_chart(df_full, stock_choice_wvw), use_container_width=True)
        st.plotly_chart(create_wbw_foreign_flow_chart(df_full, stock_choice_wvw), use_container_width=True)
