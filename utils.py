import pandas as pd
import numpy as np
import streamlit as st
import json
import traceback
from google.cloud import storage
import io

# Fungsi z-score manual
def zscore(s):
    try:
        if s.empty or len(s) < 2:
            return pd.Series(0, index=s.index)
        mean_val = s.mean()
        std_val = s.std()
        if std_val == 0 or pd.isna(std_val):
            return pd.Series(0, index=s.index)
        return (s - mean_val) / std_val
    except Exception as e:
        st.error(f"Error in zscore: {str(e)}")
        return pd.Series(0, index=s.index)

def calculate_strength_score(df):
    """Menghitung strength score tanpa scipy"""
    try:
        # Normalisasi fitur
        df['vol_norm'] = np.log1p(df['Volume'])
        df['imb_norm'] = df['Bid/Offer Imbalance'].clip(-1, 1)
        df['foreign_ratio'] = df['Foreign Buy'] / (df['Foreign Sell'].replace(0, 1e-6) + 1e-6)
        
        # Hitung z-score manual
        df['vol_z'] = zscore(df['vol_norm'])
        df['imb_z'] = zscore(df['imb_norm'])
        df['foreign_z'] = zscore(np.log1p(df['foreign_ratio']))
        
        # Strength score formula
        conditions = [
            df['Final Signal'] == 'Strong Akumulasi',
            df['Final Signal'] == 'Akumulasi',
            df['Final Signal'].str.contains('Distribusi', na=False)
        ]
        choices = [1.5, 0.5, -1.0]
        signal_score = np.select(conditions, choices, default=0)
        
        df['Strength_Score'] = (
            (df['imb_z'] * 0.4) +
            (df['vol_z'] * 0.3) +
            (df['foreign_z'] * 0.2) +
            signal_score
        )
        
        # Scale to 0-100
        min_score = df['Strength_Score'].min()
        max_score = df['Strength_Score'].max()
        range_score = max_score - min_score + 1e-6
        
        df['Strength_Score'] = ((df['Strength_Score'] - min_score) / range_score) * 100
        return df
    except Exception as e:
        st.error(f"Error in calculate_strength_score: {str(e)}")
        return df

def detect_volume_spike(df):
    """Deteksi volume spike vs rata-rata 30 hari"""
    try:
        df['30d_avg_volume'] = df.groupby('Stock Code')['Volume'].transform(
            lambda x: x.rolling(30, min_periods=1).mean()
        )
        df['Volume_Spike_Ratio'] = df['Volume'] / (df['30d_avg_volume'] + 1e-6)
        df['Volume_Spike'] = df['Volume_Spike_Ratio'] > 3
        return df
    except Exception as e:
        st.error(f"Error in detect_volume_spike: {str(e)}")
        return df

def big_player_pattern(row):
    """Klasifikasi pola big player"""
    try:
        if row['Volume_Spike'] and row['Foreign Flow'] == 'Inflow' and row['Bid/Offer Imbalance'] > 0.3:
            return "Big Player Accumulation"
        elif row['Volume_Spike'] and row['Foreign Flow'] == 'Outflow' and row['Bid/Offer Imbalance'] < -0.3:
            return "Big Player Distribution"
        elif row['Volume_Spike'] and row['Bid/Offer Imbalance'] > 0.4:
            return "Bandar Accumulation"
        elif row['Volume_Spike'] and row['Bid/Offer Imbalance'] < -0.4:
            return "Bandar Distribution"
        return "Normal"
    except:
        return "Normal"

def load_data_from_gcs(bucket_name, file_name):
    """Load data dari Google Cloud Storage"""
    try:
        # Cek apakah secret ada
        if 'gcp_credentials_json' not in st.secrets:
            st.error("Secret 'gcp_credentials_json' tidak ditemukan di st.secrets")
            st.write("Available secrets:", list(st.secrets.keys()))
            return pd.DataFrame()
            
        # Ambil credentials
        credentials_json = st.secrets["gcp_credentials_json"]
        
        # Konversi ke dictionary jika perlu
        if isinstance(credentials_json, str):
            credentials_info = json.loads(credentials_json)
        else:
            credentials_info = dict(credentials_json)
        
        # Buat client
        client = storage.Client.from_service_account_info(credentials_info)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        # Cek apakah file ada
        if not blob.exists():
            st.error(f"File {file_name} tidak ditemukan di bucket {bucket_name}")
            return pd.DataFrame()
            
        # Download file
        data = blob.download_as_bytes()
        return pd.read_csv(io.BytesIO(data))
        
    except Exception as e:
        error_msg = f"GCS Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        st.error(error_msg)
        return pd.DataFrame()

def process_data(df):
    """Preprocessing utama"""
    try:
        if not df.empty:
            df = calculate_strength_score(df)
            df = detect_volume_spike(df)
            df['Big_Player_Pattern'] = df.apply(big_player_pattern, axis=1)
        return df
    except Exception as e:
        st.error(f"Error in process_data: {str(e)}")
        return df
