# plotting.py

import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
import pandas as pd

DARK_TEMPLATE = {
    # ... (template gelap tetap sama) ...
}

# --- BARU: Grafik untuk Analisis Volume & Frekuensi ---
def create_volume_frequency_scatter(df):
    """Membuat scatter plot untuk menganalisis Volume vs Frekuensi."""
    if df.empty or 'frequency' not in df.columns:
        return go.Figure()

    fig = px.scatter(
        df,
        x='Volume',
        y='frequency',
        color='Final Signal',
        size='Strength_Score',
        hover_name='Stock Code',
        log_x=True,
        log_y=True,
        color_discrete_sequence=px.colors.qualitative.Set1,
        labels={'Volume': 'Volume (Log)', 'frequency': 'Frekuensi (Log)'}
    )
    fig.update_layout(
        title='Analisis Volume vs Frekuensi Transaksi',
        height=600,
        **DARK_TEMPLATE["layout"]
    )
    return fig

# --- BARU: Grafik untuk Analisis Mingguan (WbW) Sektor ---
def create_wbw_sektor_chart(df, metric_choice='Rata-rata Harga'):
    """Membuat line chart pergerakan mingguan untuk sektor."""
    if df.empty or 'week' not in df.columns:
        return go.Figure()

    # Agregasi data per minggu dan per sektor
    wvw_sektor = df.groupby(['week', 'Sector']).agg(
        total_volume=('Volume', 'sum'),
        total_frequency=('frequency', 'sum'),
        avg_close=('Close', 'mean')
    ).reset_index().sort_values('week')

    metric_map = {
        'Rata-rata Harga': ('avg_close', 'Rata-rata Harga Penutupan'),
        'Total Volume': ('total_volume', 'Total Volume'),
        'Total Frekuensi': ('total_frequency', 'Total Frekuensi')
    }
    y_val, y_title = metric_map[metric_choice]

    fig = px.line(
        wvw_sektor,
        x='week',
        y=y_val,
        color='Sector',
        markers=True,
        labels={'week': 'Minggu', y_val: y_title}
    )
    fig.update_layout(
        title=f'Pergerakan Mingguan (WbW) per Sektor - {y_title}',
        height=500,
        **DARK_TEMPLATE["layout"]
    )
    return fig

# --- BARU: Grafik untuk Analisis Mingguan (WbW) Saham ---
def create_wbw_saham_chart(df, stock_code):
    """Membuat combo chart pergerakan mingguan untuk satu saham."""
    df_saham = df[df['Stock Code'] == stock_code].copy()
    if df_saham.empty or 'week' not in df.columns:
        return go.Figure()

    wvw_saham = df_saham.groupby('week').agg(
        total_volume=('Volume', 'sum'),
        total_frequency=('frequency', 'sum'),
        avg_close=('Close', 'mean')
    ).reset_index().sort_values('week')
    
    fig = go.Figure()
    # Garis untuk harga
    fig.add_trace(go.Scatter(
        x=wvw_saham['week'], y=wvw_saham['avg_close'],
        name='Rata-rata Harga', mode='lines+markers',
        line=dict(color='#00ff8c')
    ))
    # Bar untuk volume dan frekuensi
    fig.add_trace(go.Bar(
        x=wvw_saham['week'], y=wvw_saham['total_volume'],
        name='Total Volume', yaxis='y2',
        marker_color='#636efa', opacity=0.7
    ))
    fig.add_trace(go.Bar(
        x=wvw_saham['week'], y=wvw_saham['total_frequency'],
        name='Total Frekuensi', yaxis='y3',
        marker_color='#ff7f0e', opacity=0.7
    ))

    fig.update_layout(
        title=f'Analisis Mingguan (WbW) untuk {stock_code}',
        xaxis=dict(title='Minggu'),
        yaxis=dict(title='Rata-rata Harga (Rp)', color='#00ff8c'),
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False, color='#636efa'),
        yaxis3=dict(title='Frekuensi', overlaying='y', side='right', position=0.9, showgrid=False, color='#ff7f0e', anchor='free'),
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode='group',
        **DARK_TEMPLATE["layout"]
    )
    return fig

# ... (fungsi plotting yang sudah ada tetap sama) ...
# create_heatmap_sektor, create_big_player_scatter, create_historical_chart