# app.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import fungsi dari file lain
from utils import load_data_from_gcs, process_data
from ui_components import display_stock_card, display_main_metrics
from plotting import (
    create_heatmap_sektor, create_big_player_scatter, create_historical_chart,
    create_volume_frequency_scatter, create_wbw_sektor_chart, create_wbw_saham_chart # --- Diperbarui ---
)

# --- KONFIGURASI HALAMAN & CSS ---
# ... (bagian ini tetap sama) ...

# --- FUNGSI LOAD DATA DENGAN CACHE ---
@st.cache_data(ttl=3600, show_spinner="Memuat data saham terbaru...")
def load_and_process_data(bucket_name, file_name):
    """Memuat dan memproses data, dengan caching."""
    try:
        df = load_data_from_gcs(bucket_name, file_name)
        if df.empty: return pd.DataFrame()
        return process_data(df)
    except Exception as e:
        st.error(f"Error saat memuat data: {e}")
        return pd.DataFrame()

# --- MAIN APP ---

# Judul Utama
st.title("📈 Big Player & Bandarmologi Analysis")
st.markdown("Dasbor interaktif untuk melacak pergerakan Big Player, sinyal Bandarmologi, dan analisis mingguan.")

# Load Data
BUCKET_NAME = "stock-csvku"
FILE_NAME = "hasil_gabungan.csv"
df_full = load_and_process_data(BUCKET_NAME, FILE_NAME)

if df_full.empty:
    st.error("Data tidak tersedia. Silakan cek konfigurasi atau sumber data.")
    st.stop()

# --- SIDEBAR FILTERS ---
# ... (sidebar tetap sama, tapi kita akan pakai df_full untuk analisis WbW) ...

# Filter data harian berdasarkan input sidebar
selected_date = pd.to_datetime(st.session_state.get('selected_date', df_full['Last Trading Date'].max()))
df_filtered = df_full[
    (df_full['Last Trading Date'] == selected_date) &
    (df_full['Sector'].isin(st.session_state.get('selected_sectors', df_full['Sector'].unique())))
].copy()

# --- TABS LAYOUT (Diperbarui) ---
tab_titles = [
    "📊 Ringkasan Pasar", 
    "🔥 Top 25 Pilihan", 
    "🔍 Analisis & Perbandingan",
    "⚡ Vol & Freq Analysis", # --- BARU ---
    "📅 Analisis Mingguan (WbW)" # --- BARU ---
]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_titles)

# ... (Tab 1, 2, 3 tetap sama) ...

# --- BARU: TAB 4: VOLUME & FREKUENSI ANALYSIS ---
with tab4:
    st.header("Analisis Volume dan Frekuensi")
    st.info("Gunakan grafik ini untuk melihat karakteristik saham berdasarkan aktivitas transaksinya pada tanggal terpilih.")
    with st.expander("Bagaimana cara membacanya?"):
        st.write("""
        - **Kanan Atas (Volume Tinggi, Frekuensi Tinggi)**: Saham sangat likuid dan aktif, sering diminati oleh ritel dan institusi.
        - **Kanan Bawah (Volume Tinggi, Frekuensi Rendah)**: Aksi borongan/jualan besar dalam sedikit transaksi. Potensi pergerakan oleh *big player*.
        - **Kiri Atas (Volume Rendah, Frekuensi Tinggi)**: Banyak transaksi kecil-kecil (*scalping*), biasanya saham kurang likuid.
        - **Kiri Bawah (Volume Rendah, Frekuensi Rendah)**: Saham tidak likuid / sepi peminat.
        """)

    if df_filtered.empty:
        st.warning("Tidak ada data untuk tanggal dan sektor yang dipilih.")
    else:
        fig_vf_scatter = create_volume_frequency_scatter(df_filtered)
        st.plotly_chart(fig_vf_scatter, use_container_width=True)

# --- BARU: TAB 5: ANALISIS MINGGUAN (WbW) ---
with tab5:
    st.header("Analisis Pergerakan Mingguan (Week-by-Week)")
    
    st.subheader("Performa Sektor per Minggu")
    metric_choice = st.radio(
        "Pilih metrik untuk ditampilkan:",
        options=['Rata-rata Harga', 'Total Volume', 'Total Frekuensi'],
        horizontal=True,
        key='wvw_metric'
    )
    fig_wvw_sektor = create_wbw_sektor_chart(df_full, metric_choice)
    st.plotly_chart(fig_wvw_sektor, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Detail Saham per Minggu")
    all_stocks_list = sorted(df_full['Stock Code'].unique())
    stock_choice_wvw = st.selectbox(
        "Pilih saham untuk melihat tren mingguan:",
        options=all_stocks_list,
        key='wvw_stock_choice'
    )
    if stock_choice_wvw:
        fig_wvw_saham = create_wbw_saham_chart(df_full, stock_choice_wvw)
        st.plotly_chart(fig_wvw_saham, use_container_width=True)

# --- FOOTER ---
# ... (footer tetap sama) ...
