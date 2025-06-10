import pandas as pd
import numpy as np
import streamlit as st

# Fungsi z-score manual
def zscore(s):
    mean_val = s.mean()
    std_val = s.std()
    if std_val == 0:
        return pd.Series(0, index=s.index)
    return (s - mean_val) / std_val

def calculate_strength_score(df):
    """Menghitung strength score tanpa scipy"""
    # Normalisasi fitur
    df['vol_norm'] = np.log1p(df['Volume'])
    df['imb_norm'] = df['Bid/Offer Imbalance'].clip(-1, 1)
    df['foreign_ratio'] = df['Foreign Buy'] / (df['Foreign Sell'] + 1e-6)
    
    # Hitung z-score manual
    df['vol_z'] = zscore(df['vol_norm'])
    df['imb_z'] = zscore(df['imb_norm'])
    df['foreign_z'] = zscore(np.log1p(df['foreign_ratio']))
    
    # Strength score formula
    df['Strength_Score'] = (
        (df['imb_z'] * 0.4) +
        (df['vol_z'] * 0.3) +
        (df['foreign_z'] * 0.2) +
        (np.where(df['Final Signal'] == 'Strong Akumulasi', 1.5, 0)) +
        (np.where(df['Final Signal'] == 'Akumulasi', 0.5, 0)) -
        (np.where(df['Final Signal'].str.contains('Distribusi'), 1.0, 0))
    )
    
    # Scale to 0-100
    min_score = df['Strength_Score'].min()
    max_score = df['Strength_Score'].max()
    range_score = max_score - min_score + 1e-6
    
    df['Strength_Score'] = ((df['Strength_Score'] - min_score) / range_score) * 100
    return df

def detect_volume_spike(df):
    """Deteksi volume spike vs rata-rata 30 hari"""
    df['30d_avg_volume'] = df.groupby('Stock Code')['Volume'].transform(
        lambda x: x.rolling(30, min_periods=1).mean()
    )
    df['Volume_Spike_Ratio'] = df['Volume'] / (df['30d_avg_volume'] + 1e-6)
    df['Volume_Spike'] = df['Volume_Spike_Ratio'] > 3
    return df

def big_player_pattern(row):
    """Klasifikasi pola big player"""
    if row['Volume_Spike'] and row['Foreign Flow'] == 'Inflow' and row['Bid/Offer Imbalance'] > 0.3:
        return "Big Player Accumulation"
    elif row['Volume_Spike'] and row['Foreign Flow'] == 'Outflow' and row['Bid/Offer Imbalance'] < -0.3:
        return "Big Player Distribution"
    elif row['Volume_Spike'] and row['Bid/Offer Imbalance'] > 0.4:
        return "Bandar Accumulation"
    elif row['Volume_Spike'] and row['Bid/Offer Imbalance'] < -0.4:
        return "Bandar Distribution"
    return "Normal"

def load_data_from_gcs(bucket_name, file_name):
    """Load data dari Google Cloud Storage"""
    from google.cloud import storage
    import io
    
    try:
        # Menggunakan service account dari Streamlit secrets
        client = storage.Client.from_service_account_info(st.secrets["gcp_service_account"])
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        data = blob.download_as_bytes()
        return pd.read_csv(io.BytesIO(data))
    except Exception as e:
        st.error(f"Error loading data from GCS: {str(e)}")
        return pd.DataFrame()

def process_data(df):
    """Preprocessing utama"""
    if not df.empty:
        df = calculate_strength_score(df)
        df = detect_volume_spike(df)
        df['Big_Player_Pattern'] = df.apply(big_player_pattern, axis=1)
    return df
