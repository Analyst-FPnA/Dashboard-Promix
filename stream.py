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

st.set_page_config(layout="wide")
def download_file_from_github(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved to {save_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")


def list_files_in_directory(dir_path):
    # Fungsi untuk mencetak semua isi dari suatu direktori
    for root, dirs, files in os.walk(dir_path):
        st.write(f'Direktori: {root}')
        for file_name in files:
            st.write(f'  - {file_name}')

# URL file model .pkl di GitHub (gunakan URL raw dari file .pkl di GitHub)
url = 'https://raw.githubusercontent.com/Analyst-FPnA/Dashboard-Promix/main/daftar_gudang.csv'

# Path untuk menyimpan file yang diunduh
save_path = 'daftar_gudang.csv'

# Unduh file dari GitHub
download_file_from_github(url, save_path)

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

st.title('Dashboard - Promix')

list_bulan = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']

df_cab = pd.read_csv('daftar_gudang.csv')
df_2205['Month'] = pd.Categorical(df_2205['Month'], categories=[x for x in list_bulan if x in df_2205['Month'].unique()], ordered=True)
df_2205['Cabang'] = df_2205['Nama Pelanggan'].str.extract(r'\(([^()]*)\)[^()]*$')[0].values
df_2205 = df_2205.merge(df_cab[['Cabang','Nama Cabang']],how='left')

kategori = st.selectbox("KATEGORI:", ['ALL','BEVERAGES','DIMSUM','MIE'], index=0)

def format_number(x):
    if x==0:
        return ''
    if isinstance(x, (int, float)):
        return "{:,.0f}".format(x)
    return x

pivot1 = df_2205[df_2205['Master Kategori'].isin((df_2205['Master Kategori'].unique() if kategori=='ALL' else [kategori]))].groupby(['Nama Cabang','Month'])[['Kuantitas']].sum().reset_index().pivot(index='Nama Cabang',columns='Month',values='Kuantitas').reset_index()
st.dataframe(pivot1.style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)

st.markdown('### ')
cabang = st.selectbox("CABANG:", ['ALL']+df_2205['Nama Cabang'].unique().tolist(), index=0)

pivot2 = df_2205[(df_2205['Master Kategori'].isin((df_2205['Master Kategori'].unique() if kategori=='ALL' else [kategori]))) & (df_2205['Nama Cabang'].isin(df_2205['Nama Cabang'].unique() if cabang=='ALL' else [cabang]))].groupby(['Nama Barang','Month'])[['Kuantitas']].sum().reset_index().pivot(index='Nama Barang',columns='Month',values='Kuantitas').reset_index()
st.dataframe(pivot2.style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2.columns[1:]), use_container_width=True, hide_index=True)
