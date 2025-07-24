import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
import pandas as pd

DARK_TEMPLATE = {"layout": {"plot_bgcolor": "rgba(0,0,0,0)", "paper_bgcolor": "rgba(0,0,0,0)", "font": {"color": "white"}, "xaxis": {"gridcolor": "#444", "tickfont": {"color": "white"}}, "yaxis": {"gridcolor": "#444", "tickfont": {"color": "white"}}, "legend": {"font": {"color": "white"}}, "coloraxis": {"colorbar": {"title_font": {"color": "white"}, "tickfont": {"color": "white"}}}}}

# --- FUNGSI LAMA YANG TIDAK BERUBAH ---
def create_heatmap_sektor(df):
    if df.empty: return go.Figure()
    heatmap_data = df.pivot_table(index='Sector', columns='Final Signal', values='Strength_Score', aggfunc='mean', fill_value=0)
    if heatmap_data.empty: return go.Figure()
    fig = px.imshow(heatmap_data, labels=dict(x="Sinyal Bandarmologi", y="Sektor", color="Avg. Strength"), color_continuous_scale='RdYlGn', aspect="auto")
    fig.update_layout(title='Heatmap Kekuatan Sinyal Rata-rata per Sektor', height=500, **DARK_TEMPLATE["layout"])
    return fig

def create_big_player_scatter(df):
    df_signals = df[df['Big_Player_Pattern'] != "Normal"].copy()
    if df_signals.empty: return go.Figure()
    fig = px.scatter(df_signals, x='Bid/Offer Imbalance', y='Volume_Spike_Ratio', color='Big_Player_Pattern', size='Strength_Score', hover_name='Stock Code', log_y=True,
                     color_discrete_map={"Big Player Accumulation": "#00ff8c", "Bandar Accumulation": "#00cc66", "Big Player Distribution": "#ff4d4d", "Bandar Distribution": "#cc0000"})
    fig.update_layout(title='Peta Pergerakan Big Player & Bandar', xaxis_title="Bid/Offer Imbalance", yaxis_title="Volume Spike Ratio (vs Rata-rata)", height=600, **DARK_TEMPLATE["layout"])
    return fig

def create_volume_frequency_scatter(df):
    if df.empty or 'frequency' not in df.columns: return go.Figure()
    fig = px.scatter(df, x='Volume', y='frequency', color='Final Signal', size='Strength_Score', hover_name='Stock Code', log_x=True, log_y=True,
                     color_discrete_sequence=px.colors.qualitative.Set1, labels={'Volume': 'Volume (Log)', 'frequency': 'Frekuensi (Log)'})
    fig.update_layout(title='Analisis Volume vs Frekuensi Transaksi', height=600, **DARK_TEMPLATE["layout"])
    return fig

def create_wbw_sektor_chart(df, metric_choice='Rata-rata Harga'):
    if df.empty or 'week' not in df.columns: return go.Figure()
    wvw_sektor = df.groupby(['week', 'Sector']).agg(total_volume=('Volume', 'sum'), total_frequency=('frequency', 'sum'), avg_close=('Close', 'mean')).reset_index().sort_values('week')
    metric_map = {'Rata-rata Harga': ('avg_close', 'Rata-rata Harga Penutupan'), 'Total Volume': ('total_volume', 'Total Volume'), 'Total Frekuensi': ('total_frequency', 'Total Frekuensi')}
    y_val, y_title = metric_map[metric_choice]
    fig = px.line(wvw_sektor, x='week', y=y_val, color='Sector', markers=True, labels={'week': 'Minggu', y_val: y_title})
    fig.update_layout(title=f'Pergerakan Mingguan (WbW) per Sektor - {y_title}', height=500, **DARK_TEMPLATE["layout"])
    return fig

# --- FUNGSI DIPERBARUI & DIGABUNG ---

def create_historical_chart(df_full, stock_code, current_date):
    """Membuat grafik historis HARIAN (Harga, Volume, dan Foreign Flow) dalam 2 subplot."""
    hist_data = df_full[(df_full['Stock Code'] == stock_code) & (df_full['Last Trading Date'] >= pd.to_datetime(current_date) - timedelta(days=90))].sort_values('Last Trading Date')
    if hist_data.empty: return go.Figure()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
    
    # Subplot 1: Harga dan Volume
    fig.add_trace(go.Scatter(x=hist_data['Last Trading Date'], y=hist_data['Close'], name='Harga Penutupan', line=dict(color='#00ff8c')), row=1, col=1)
    fig.add_trace(go.Bar(x=hist_data['Last Trading Date'], y=hist_data['Volume'], name='Volume', marker_color='#636efa', opacity=0.6), row=1, col=1)
    
    # Subplot 2: Foreign Flow
    fig.add_trace(go.Bar(x=hist_data['Last Trading Date'], y=hist_data['Foreign Buy'], name='Foreign Buy', marker_color='springgreen'), row=2, col=1)
    fig.add_trace(go.Bar(x=hist_data['Last Trading Date'], y=hist_data['Foreign Sell'], name='Foreign Sell', marker_color='tomato'), row=2, col=1)

    fig.update_layout(
        title=f'Analisis Harian Lengkap untuk {stock_code} (90 Hari)',
        height=600,
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **DARK_TEMPLATE["layout"]
    )
    fig.update_yaxes(title_text="Harga (Rp) / Volume", row=1, col=1)
    fig.update_yaxes(title_text="Foreign Flow (Rp)", row=2, col=1)
    fig.update_xaxes(showticklabels=False, row=1, col=1) # Sembunyikan label x di chart atas
    return fig

def create_wbw_combined_chart(df, stock_code):
    """Membuat grafik gabungan MINGGUAN (Harga, Volume, dan Foreign Flow) dalam 2 subplot."""
    df_saham = df[df['Stock Code'] == stock_code].copy()
    if df_saham.empty or 'week' not in df.columns: return go.Figure()

    # Agregasi semua data yang diperlukan
    wvw_data = df_saham.groupby('week').agg(
        total_volume=('Volume', 'sum'),
        avg_close=('Close', 'mean'),
        total_buy=('Foreign Buy', 'sum'),
        total_sell=('Foreign Sell', 'sum')
    ).reset_index().sort_values('week')

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])

    # Subplot 1: Harga dan Volume Mingguan
    fig.add_trace(go.Scatter(x=wvw_data['week'], y=wvw_data['avg_close'], name='Harga Rata-rata', line=dict(color='#00ff8c')), row=1, col=1)
    fig.add_trace(go.Bar(x=wvw_data['week'], y=wvw_data['total_volume'], name='Total Volume', marker_color='#636efa', opacity=0.6), row=1, col=1)
    
    # Subplot 2: Foreign Flow Mingguan
    fig.add_trace(go.Bar(x=wvw_data['week'], y=wvw_data['total_buy'], name='Foreign Buy', marker_color='springgreen'), row=2, col=1)
    fig.add_trace(go.Bar(x=wvw_data['week'], y=wvw_data['total_sell'], name='Foreign Sell', marker_color='tomato'), row=2, col=1)
    
    fig.update_layout(
        title=f'Analisis Mingguan Lengkap untuk {stock_code}',
        height=600,
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **DARK_TEMPLATE["layout"]
    )
    fig.update_yaxes(title_text="Harga (Rp) / Volume", row=1, col=1)
    fig.update_yaxes(title_text="Foreign Flow (Rp)", row=2, col=1)
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    return fig
