import pandas as pd
import numpy as np
import io
from google.cloud import storage

def process_data(df):
    """
    Fungsi untuk memproses data mentah.
    Menambahkan kolom-kolom analisis yang dibutuhkan oleh dashboard.
    """
    df['Last Trading Date'] = pd.to_datetime(df['Last Trading Date'])
    df['week'] = df['Last Trading Date'].dt.strftime('%Y-%U')

    if 'Strength_Score' not in df.columns:
        df['Strength_Score'] = np.random.uniform(50, 100, size=len(df))
    if 'Foreign Flow' not in df.columns:
        df['Foreign Flow'] = np.where(df['Foreign Buy'] > df['Foreign Sell'], 'Inflow', 'Outflow')
    if 'Big_Player_Pattern' not in df.columns:
        patterns = ["Big Player Accumulation", "Bandar Accumulation", "Normal", "Big Player Distribution", "Bandar Distribution"]
        df['Big_Player_Pattern'] = np.random.choice(patterns, size=len(df), p=[0.2, 0.2, 0.2, 0.2, 0.2])
    if 'Volume_Spike_Ratio' not in df.columns:
        df['Volume_Spike_Ratio'] = np.random.uniform(0.5, 5.0, size=len(df))
    if 'Bid/Offer Imbalance' not in df.columns:
        df['Bid/Offer Imbalance'] = np.random.uniform(0.5, 2.0, size=len(df))
    if 'Close' not in df.columns:
        df['Close'] = np.random.randint(100, 10000, size=len(df))
    if 'frequency' not in df.columns:
        df['frequency'] = np.random.randint(500, 20000, size=len(df))
    if 'Final Signal' not in df.columns:
        signals = ["Strong Akumulasi", "Akumulasi", "Netral", "Distribusi", "Strong Distribusi"]
        df['Final Signal'] = np.random.choice(signals, size=len(df))
    return df

def load_data_from_local(file_name="hasil_gabungan.csv"):
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        dates = pd.to_datetime(pd.date_range(end=pd.Timestamp.now(), periods=30, freq='B'))
        stocks = ['BBCA', 'TLKM', 'BBRI', 'ASII', 'GOTO', 'BMRI', 'UNVR', 'ICBP', 'ADRO', 'ANTM']
        sectors = {'BBCA': 'Financials', 'TLKM': 'Technology', 'BBRI': 'Financials', 'ASII': 'Industrials', 'GOTO': 'Technology', 'BMRI': 'Financials', 'UNVR': 'Consumer Staples', 'ICBP': 'Consumer Staples', 'ADRO': 'Energy', 'ANTM': 'Basic Materials'}
        data = []
        for date in dates:
            for stock in stocks:
                data.append({'Last Trading Date': date, 'Stock Code': stock, 'Company Name': f'PT {stock} Tbk.', 'Sector': sectors[stock], 'Volume': np.random.randint(1e6, 1e8), 'Foreign Buy': np.random.randint(1e9, 5e10), 'Foreign Sell': np.random.randint(1e9, 5e10)})
        df = pd.DataFrame(data)
    return df

def load_data_from_gcs(bucket_name, file_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        data = blob.download_as_bytes()
        df = pd.read_csv(io.BytesIO(data))
        return df
    except Exception as e:
        print(f"Gagal terhubung ke GCS: {e}. Menggunakan data lokal sebagai fallback.")
        return load_data_from_local()
