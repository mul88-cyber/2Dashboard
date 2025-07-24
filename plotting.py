import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

DARK_TEMPLATE = {
    "layout": {
        "plot_bgcolor": "rgba(0,0,0,0)",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "white"},
        "xaxis": {"gridcolor": "#444", "tickfont": {"color": "white"}},
        "yaxis": {"gridcolor": "#444", "tickfont": {"color": "white"}},
        "legend": {"font": {"color": "white"}},
        "title": {"font": {"color": "white"}},
        "coloraxis": {
            "colorbar": {
                "title_font": {"color": "white"},
                "tickfont": {"color": "white"}
            }
        }
    }
}

def create_heatmap_sektor(df):
    """Membuat grafik heatmap kekuatan sinyal per sektor."""
    if df.empty:
        return go.Figure()

    heatmap_data = df.pivot_table(
        index='Sector', columns='Final Signal', values='Strength_Score', 
        aggfunc='mean', fill_value=0
    )
    if heatmap_data.empty:
        return go.Figure()
        
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Sinyal Bandarmologi", y="Sektor", color="Avg. Strength"),
        color_continuous_scale='RdYlGn',
        aspect="auto"
    )
    fig.update_layout(
        title='Heatmap Kekuatan Sinyal Rata-rata per Sektor',
        height=500,
        **DARK_TEMPLATE["layout"]
    )
    return fig

def create_big_player_scatter(df):
    """Membuat scatter plot untuk melacak pergerakan big player."""
    df_signals = df[df['Big_Player_Pattern'] != "Normal"].copy()
    if df_signals.empty:
        return go.Figure()

    fig = px.scatter(
        df_signals,
        x='Bid/Offer Imbalance',
        y='Volume_Spike_Ratio',
        color='Big_Player_Pattern',
        size='Strength_Score',
        hover_name='Stock Code',
        log_y=True,
        color_discrete_map={
            "Big Player Accumulation": "#00ff8c", "Bandar Accumulation": "#00cc66",
            "Big Player Distribution": "#ff4d4d", "Bandar Distribution": "#cc0000"
        }
    )
    fig.update_layout(
        title='Peta Pergerakan Big Player & Bandar',
        xaxis_title="Bid/Offer Imbalance",
        yaxis_title="Volume Spike Ratio (vs Rata-rata)",
        height=600,
        **DARK_TEMPLATE["layout"]
    )
    return fig
    
def create_historical_chart(df_full, stock_code, current_date):
    """Membuat grafik historis harga dan volume untuk saham terpilih."""
    hist_data = df_full[
        (df_full['Stock Code'] == stock_code) & 
        (df_full['Last Trading Date'] >= pd.to_datetime(current_date) - timedelta(days=90))
    ].sort_values('Last Trading Date')

    if hist_data.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist_data['Last Trading Date'], y=hist_data['Close'], name='Harga Penutupan', line=dict(color='#00ff8c')))
    fig.add_trace(go.Bar(x=hist_data['Last Trading Date'], y=hist_data['Volume'], name='Volume', yaxis='y2', marker_color='#636efa', opacity=0.6))
    fig.update_layout(
        title=f'Perkembangan Harga & Volume {stock_code} (90 Hari)',
        yaxis=dict(title='Harga Penutupan (Rp)'),
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
        height=400,
        **DARK_TEMPLATE["layout"]
    )
    return fig

def create_volume_frequency_scatter(df):
    """Membuat scatter plot untuk menganalisis Volume vs Frekuensi."""
    if df.empty or 'frequency' not in df.columns:
        return go.Figure()

    fig = px.scatter(
        df, x='Volume', y='frequency', color='Final Signal', size='Strength_Score',
        hover_name='Stock Code', log_x=True, log_y=True,
        color_discrete_sequence=px.colors.qualitative.Set1,
        labels={'Volume': 'Volume (Log)', 'frequency': 'Frekuensi (Log)'}
    )
    fig.update_layout(title='Analisis Volume vs Frekuensi Transaksi', height=600, **DARK_TEMPLATE["layout"])
    return fig

def create_wbw_sektor_chart(df, metric_choice='Rata-rata Harga'):
    """Membuat line chart pergerakan mingguan untuk sektor."""
    if df.empty or 'week' not in df.columns:
        return go.Figure()

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

    fig = px.line(wvw_sektor, x='week', y=y_val, color='Sector', markers=True, labels={'week': 'Minggu', y_val: y_title})
    fig.update_layout(title=f'Pergerakan Mingguan (WbW) per Sektor - {y_title}', height=500, **DARK_TEMPLATE["layout"])
    return fig

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
    fig.add_trace(go.Scatter(x=wvw_saham['week'], y=wvw_saham['avg_close'], name='Harga Rata-rata', line=dict(color='#00ff8c')))
    fig.add_trace(go.Bar(x=wvw_saham['week'], y=wvw_saham['total_volume'], name='Total Volume', yaxis='y2', marker_color='#636efa'))
    fig.add_trace(go.Bar(x=wvw_saham['week'], y=wvw_saham['total_frequency'], name='Total Frekuensi', yaxis='y3', marker_color='#ff7f0e'))

    fig.update_layout(
        title=f'Analisis Mingguan (WbW) untuk {stock_code}',
        xaxis=dict(title='Minggu'),
        yaxis=dict(title='Harga Rata-rata (Rp)', color='#00ff8c'),
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False, color='#636efa'),
        yaxis3=dict(title='Frekuensi', overlaying='y', side='right', position=0.9, showgrid=False, color='#ff7f0e', anchor='free'),
        height=500, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **DARK_TEMPLATE["layout"]
    )
    return fig
