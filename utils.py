def load_data_from_gcs(bucket_name, file_name):
    """Load data dari Google Cloud Storage"""
    from google.cloud import storage
    import io
    import traceback

    try:
        # Cek apakah secret ada
        if 'gcp_service_account' not in st.secrets:
            st.error("Secret 'gcp_service_account' tidak ditemukan")
            return pd.DataFrame()
        
        # Ambil credentials sebagai dictionary langsung
        credentials_info = dict(st.secrets["gcp_service_account"])

        # Buat client dari credentials
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
