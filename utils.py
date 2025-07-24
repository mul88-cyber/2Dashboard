# utils.py

import pandas as pd
import numpy as np

def process_data(df):
    """
    Fungsi untuk memproses data mentah.
    Menambahkan kolom-kolom analisis yang dibutuhkan oleh dashboard.
    --- Diperbarui ---
    """
    # Pastikan tipe data tanggal benar
    df['Last Trading Date'] = pd.to_datetime(df['Last Trading Date'])

    # --- BARU: Tambah kolom 'week' untuk analisis mingguan ---
    # Format 'Tahun-Minggu ke' (contoh: 2024-30)
    df['week'] = df['Last Trading Date'].dt.strftime('%Y-%U')

    # --- SIMULASI KOLOM ANALISIS ---
    # Gantikan bagian ini dengan logika processing datamu yang sebenarnya
    if 'Strength_Score' not in df.columns:
        df['Strength_Score'] = np.random.uniform(50, 100, size=len(df))
    
    if 'Foreign Flow' not in df.columns:
        df['Foreign Flow'] = np.random.choice(['Inflow', 'Outflow'], size=len(df), p=[0.6, 0.4])

    if 'Big_Player_Pattern' not in df.columns:
        patterns = ["Big Player Accumulation", "Bandar Accumulation", "Normal", "Big Player Distribution", "Bandar Distribution"]
        df['Big_Player_Pattern'] = np.random.choice(patterns, size=len(df), p=[0.2, 0.2, 0.2, 0.2, 0.2])

    if 'Volume_Spike_Ratio' not in df.columns:
        df['Volume_Spike_Ratio'] = np.random.uniform(0.5, 5.0, size=len(df))
        
    if 'Close' not in df.columns:
        df['Close'] = np.random.randint(100, 10000, size=len(df))
    
    # --- BARU: Tambah kolom 'frequency' ---
    if 'frequency' not in df.columns:
        df['frequency'] = np.random.randint(500, 20000, size=len(df))
        
    if 'Final Signal' not in df.columns:
        signals = ["Strong Akumulasi", "Akumulasi", "Netral", "Distribusi", "Strong Distribusi"]
        df['Final Signal'] = np.random.choice(signals, size=len(df))
        
    return df

# ... (sisa file utils.py tetap sama) ...
def load_data_from_local(file_name="hasil_gabungan.csv"):
    """
    Fungsi placeholder untuk memuat data dari file CSV lokal.
    Gunakan ini untuk development jika tidak terhubung ke GCS.
    """
    try:
        df = pd.read_csv(file_name)
        # Pastikan kolom penting ada (minimal)
        required_cols = ['Last Trading Date', 'Foreign Buy', 'Foreign Sell', 'Volume', 'Sector', 'Stock Code', 'Company Name']
        if not all(col in df.columns for col in required_cols):
             raise FileNotFoundError("File CSV tidak memiliki kolom yang dibutuhkan.")
        return df
    except FileNotFoundError:
        print(f"File {file_name} tidak ditemukan. Membuat data dummy...")
        # Membuat data dummy jika file tidak ada
        dates = pd.to_datetime(pd.date_range(end=pd.Timestamp.now(), periods=30, freq='B')) # Data 30 hari agar ada beberapa minggu
        stocks = ['BBCA', 'TLKM', 'BBRI', 'ASII', 'GOTO', 'BMRI', 'UNVR', 'ICBP', 'ADRO', 'ANTM']
        sectors = {'BBCA': 'Financials', 'TLKM': 'Technology', 'BBRI': 'Financials', 'ASII': 'Industrials', 'GOTO': 'Technology', 'BMRI': 'Financials', 'UNVR': 'Consumer Staples', 'ICBP': 'Consumer Staples', 'ADRO': 'Energy', 'ANTM': 'Basic Materials'}
        data = []
        for date in dates:
            for stock in stocks:
                data.append({
                    'Last Trading Date': date,
                    'Stock Code': stock,
                    'Company Name': f'{stock} Tbk.',
                    'Sector': sectors[stock],
                    'Volume': np.random.randint(1e6, 1e8),
                    'Foreign Buy': np.random.randint(1e9, 5e10),
                    'Foreign Sell': np.random.randint(1e9, 5e10)
                })
        return pd.DataFrame(data)

def load_data_from_gcs(bucket_name, file_name):
    """
    Tempatkan logika untuk download file dari Google Cloud Storage di sini.
    Return pandas DataFrame.
    """
    print("Mode Development: Menggunakan data lokal/dummy sebagai pengganti GCS.")
    return load_data_from_local(file_name)
