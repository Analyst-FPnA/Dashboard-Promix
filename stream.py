import streamlit as st
import requests
import zipfile
import io
import pandas as pd
import os
import gdown
import tempfile
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.graph_objs as go
import streamlit as st

def download_file_from_google_drive(file_id, dest_path):
    if not os.path.exists(dest_path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, dest_path, quiet=False)
        
file_id = '1EDWQJXuYu34WZNcZOx1WXqxOEwq_QKug'
dest_path = f'downloaded_file.zip'
download_file_from_google_drive(file_id, dest_path)

if 'df_2205' not in locals():
    with zipfile.ZipFile(f'downloaded_file.zip', 'r') as z:
        df_list = []
        for file_name in z.namelist():
          # Memeriksa apakah file tersebut berformat CSV
          if file_name.endswith('.csv'):
              # Membaca file CSV ke dalam DataFrame
              with z.open(file_name) as f:
                  df = pd.read_csv(f)
                  df_list.append(df)
      
        # Menggabungkan semua DataFrame menjadi satu
        df_2205 = pd.concat(df_list, ignore_index=True)

st.dataframe(df_2205)
