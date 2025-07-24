# ui_components.py

import streamlit as st

def display_stock_card(stock_row, container):
    """Menampilkan satu kartu saham di dalam container yang diberikan."""
    signal_color = "#00ff8c" if "Akumulasi" in str(stock_row['Final Signal']) else "#ff4d4d"
    foreign_color = "#00ff8c" if stock_row['Foreign Flow'] == 'Inflow' else "#ff4d4d"

    card_html = f"""
    <div class="stock-card" onclick="this.classList.toggle('flipped');">
        <h4 style="color:white; margin-bottom: 5px;">{stock_row['Stock Code']}</h4>
        <p style="margin:0;font-size:0.9em;color:#d0d0d0; min-height: 35px;">{stock_row['Company Name']}</p>
        <div style="display:flex;justify-content:space-between; margin: 8px 0;">
            <span style="color:#a0a0a0; font-size:0.85em;"><strong>Sektor:</strong> {stock_row['Sector']}</span>
            <span style="color:{signal_color}; font-size:0.9em;"><strong>{stock_row['Final Signal']}</strong></span>
        </div>
        <div style="background:#2a2f4f;border-radius:5px;padding:5px;text-align:center; margin-bottom: 8px;">
            <strong style="color:#c0c0c0">Strength:</strong> 
            <span style="font-size:1.2em;color:{signal_color}">{stock_row['Strength_Score']:.1f}</span>
        </div>
        <div style="display:flex;justify-content:space-between; font-size:0.9em;">
            <div>
                <div style="color:#a0a0a0">Volume</div>
                <div><strong style="color:white">{stock_row['Volume']/1e6:.1f}M</strong></div>
            </div>
            <div>
                <div style="color:#a0a0a0">Foreign</div>
                <div style="color:{foreign_color}"><strong>{stock_row['Foreign Flow']}</strong></div>
            </div>
        </div>
    </div>
    """
    container.markdown(card_html, unsafe_allow_html=True)

def display_main_metrics(df):
    """Menampilkan metrik utama pasar di halaman ringkasan."""
    st.subheader("Ringkasan Pasar Hari Ini")
    col1, col2, col3 = st.columns(3)

    if not df.empty:
        net_foreign_flow = (df['Foreign Buy'] - df['Foreign Sell']).sum()
        akumulasi_count = df[df['Final Signal'].str.contains("Akumulasi", case=False)].shape[0]
        distribusi_count = df[df['Final Signal'].str.contains("Distribusi", case=False)].shape[0]

        flow_delta = "Naik" if net_foreign_flow > 0 else "Turun"

        col1.metric(
            "Net Foreign Flow", 
            f"Rp {net_foreign_flow/1e9:.2f} M", 
            delta=flow_delta,
            delta_color="normal" if net_foreign_flow > 0 else "inverse"
        )
        col2.metric("Saham Sinyal Akumulasi", f"{akumulasi_count} saham")
        col3.metric("Saham Sinyal Distribusi", f"{distribusi_count} saham")
    else:
        col1.metric("Net Foreign Flow", "N/A")
        col2.metric("Saham Sinyal Akumulasi", "N/A")
        col3.metric("Saham Sinyal Distribusi", "N/A")

    with st.expander("❓ Apa arti metrik ini?"):
        st.info("""
        - **Net Foreign Flow**: Total nilai pembelian dikurangi penjualan oleh investor asing di seluruh pasar pada hari terpilih. Positif berarti *net buy*, negatif berarti *net sell*.
        - **Saham Sinyal Akumulasi**: Jumlah saham yang terdeteksi memiliki sinyal akumulasi (baik kuat maupun lemah).
        - **Saham Sinyal Distribusi**: Jumlah saham yang terdeteksi memiliki sinyal distribusi.
        """)