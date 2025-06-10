import pandas as pd
import numpy as np
from scipy import stats

def calculate_strength_score(df):
    """Menghitung strength score berdasarkan multi-faktor"""
    # Normalisasi fitur
    df['vol_norm'] = np.log1p(df['Volume'])
    df['imb_norm'] = df['Bid/Offer Imbalance'].clip(-1, 1)
    df['foreign_ratio'] = df['Foreign Buy'] / (df['Foreign Sell'] + 1e-6)
    
    # Hitung z-score untuk fitur penting
    df['vol_z'] = stats.zscore(df['vol_norm'])
    df['imb_z'] = stats.zscore(df['imb_norm'])
    df['foreign_z'] = stats.zscore(np.log1p(df['foreign_ratio']))
    
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
    df['Strength_Score'] = (df['Strength_Score'] - df['Strength_Score'].min()) / \
                          (df['Strength_Score'].max() - df['Strength_Score'].min() + 1e-6) * 100
    
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
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    data = blob.download_as_bytes()
    
    return pd.read_csv(io.BytesIO(data))

def process_data(df):
    """Preprocessing utama"""
    df = calculate_strength_score(df)
    df = detect_volume_spike(df)
    df['Big_Player_Pattern'] = df.apply(big_player_pattern, axis=1)
    return df