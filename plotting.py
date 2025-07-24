# plotting.py

import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
import pandas as pd

# ... (semua fungsi yang sudah ada dari create_heatmap_sektor sampai create_wbw_saham_chart tetap sama, tidak perlu diubah) ...
# ...
# ...

# --- TAMBAHKAN FUNGSI BARU DI BAWAH INI ---
def create_wbw_foreign_flow_chart(df, stock_code):
    """Membuat bar chart pergerakan foreign flow mingguan untuk satu saham."""
    df_saham = df[df['Stock Code'] == stock_code].copy()
    if df_saham.empty or 'Foreign Buy' not in df.columns or 'Foreign Sell' not in df.columns:
        return go.Figure()

    # Agregasi data foreign flow per minggu
    wvw_foreign = df_saham.groupby('week').agg(
        total_buy=('Foreign Buy', 'sum'),
        total_sell=('Foreign Sell', 'sum')
    ).reset_index().sort_values('week')
    
    # Hitung Net Flow
    wvw_foreign['net_flow'] = wvw_foreign['total_buy'] - wvw_foreign['total_sell']

    fig = go.Figure()
    
    # Bar untuk Foreign Buy & Sell
    fig.add_trace(go.Bar(
        x=wvw_foreign['week'], y=wvw_foreign['total_buy'],
        name='Foreign Buy', marker_color='springgreen'
    ))
    fig.add_trace(go.Bar(
        x=wvw_foreign['week'], y=wvw_foreign['total_sell'],
        name='Foreign Sell', marker_color='tomato'
    ))

    # Garis untuk Net Flow
    fig.add_trace(go.Scatter(
        x=wvw_foreign['week'], y=wvw_foreign['net_flow'],
        name='Net Flow', line=dict(color='deepskyblue', width=3),
        yaxis='y2' # Menggunakan sumbu y kedua
    ))

    fig.update_layout(
        title=f'Analisis Foreign Flow Mingguan untuk {stock_code}',
        barmode='group', # Mengelompokkan bar Buy dan Sell
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(title='Minggu'),
        yaxis=dict(title='Total Buy/Sell (Rp)', gridcolor="#444"),
        yaxis2=dict(
            title='Net Flow (Rp)', 
            overlaying='y', 
            side='right', 
            showgrid=False, 
            titlefont=dict(color='deepskyblue'),
            tickfont=dict(color='deepskyblue')
        )
    )
    return fig
