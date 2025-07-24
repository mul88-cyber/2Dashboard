# app.py

import streamlit as st
import pandas as pd
from datetime import datetime

from utils import load_data_from_gcs, process_data
from ui_components import display_stock_card, display_main_metrics
from plotting import (
    create_heatmap_sektor, create_big_player_scatter, create_historical_chart,
    create_volume_frequency_scatter, create_wbw_sektor_chart, create_wbw_saham_chart,
    create_wbw_foreign_flow_chart # <-- Tambahkan import fungsi baru
)

# ... (kode dari st.set_page_config sampai df_filtered tetap sama) ...
# ...
# ...

# --- Layout dengan Tabs ---
tab_titles = ["📊 Ringkasan Pasar", "🔥 Top 25 Pilihan", "🔍 Analisis & Perbandingan", "⚡ Vol & Freq Analysis", "📅 Analisis Mingguan (WbW)"]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_titles)

# ... (Tab 1 dan Tab 2 tidak berubah) ...

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
                        st.metric("Final Signal", data['Final Signal'])
                        
                        # --- TAMBAHAN METRIK NET FOREIGN FLOW DI SINI ---
                        net_flow = data['Foreign Buy'] - data['Foreign Sell']
                        st.metric("Net Foreign Flow", f"Rp {net_flow/1e9:.2f} M", delta="Inflow" if net_flow > 0 else "Outflow")
                        # ---------------------------------------------
    else:
        st.warning("Pilih tanggal atau sektor yang valid di sidebar untuk menampilkan data.")

# ... (Tab 4 tidak berubah) ...

with tab5: # Analisis Mingguan (WbW)
    st.header("Analisis Pergerakan Mingguan (Week-by-Week)")
    
    st.subheader("Performa Sektor per Minggu")
    metric_choice = st.radio("Pilih metrik:", options=['Rata-rata Harga', 'Total Volume', 'Total Frekuensi'], horizontal=True)
    st.plotly_chart(create_wbw_sektor_chart(df_full, metric_choice), use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Detail Saham per Minggu")
    stock_choice_wvw = st.selectbox("Pilih saham:", options=sorted(df_full['Stock Code'].unique()))
    if stock_choice_wvw:
        # Grafik Harga, Volume, Frekuensi
        st.plotly_chart(create_wbw_saham_chart(df_full, stock_choice_wvw), use_container_width=True)
        
        # --- TAMBAHAN GRAFIK FOREIGN FLOW DI SINI ---
        st.plotly_chart(create_wbw_foreign_flow_chart(df_full, stock_choice_wvw), use_container_width=True)
        # -------------------------------------------

# ... (Footer tidak berubah) ...
