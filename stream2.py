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
        
file_id = '14a4HmKACWics1ObPevlF0BXG1gVFShn_'
dest_path = f'downloaded_file.zip'
download_file_from_google_drive(file_id, dest_path)

if 'df_item' not in locals():
    with zipfile.ZipFile(f'downloaded_file.zip', 'r') as z:
        df_item = []
        df_paket = []
        for file_name in z.namelist():
          # Memeriksa apakah file tersebut berformat CSV
          if file_name.startswith('df_item'):
              with z.open(file_name) as f:
                  df_item.append(pd.read_csv(f))
          elif file_name.startswith('df_paket'):
              # Membaca file CSV ke dalam DataFrame
              with z.open(file_name) as f:
                  df_paket.append(pd.read_csv(f))
      
        # Menggabungkan semua DataFrame menjadi satu
        df_item = pd.concat(df_item, ignore_index=True)
        df_paket = pd.concat(df_paket, ignore_index=True)
        
st.title('Dashboard - Promix (WEBSMART)')

days_in_month = {
    'January': 31,
    'February': 28,  # untuk tahun non-kabisat
    'March': 31,
    'April': 30,
    'May': 31,
    'June': 30,
    'July': 31,
    'August': 31,
    'September': 30,
    'October': 31,
    'November': 30,
    'December': 31
}



df_cab = pd.read_csv('daftar_gudang.csv')


df_item['Tanggal'] = pd.to_datetime(df_item['BULAN'], format='%B %Y')
df_item['BULAN'] = pd.Categorical(df_item['BULAN'], categories=df_item.sort_values('Tanggal')['BULAN'].unique(), ordered=True)


def format_number(x):
    if x==0:
        return ''
    if isinstance(x, (int, float)):
        return "{:,.0f}".format(x)
    return x
    
pivot1 = df_item.groupby(['BULAN','Nama Cabang'])[['Kuantitas']].sum().reset_index().pivot(index=['Nama Cabang'], columns=['BULAN'], values='Kuantitas').reset_index()
total = pd.DataFrame((pivot1.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot1.columns)-1),columns=pivot1.columns[1:])
total['Nama Cabang']='TOTAL'+(pivot1['Nama Cabang'].str.len().max()+25)*' '
st.dataframe(pd.concat([pivot1,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)
st.dataframe(pd.concat([pivot1,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)
for month in total.columns.drop(['Nama Cabang']):
    total[month]=total[month][0] / days_in_month[month[:-5]]
total['Nama Cabang']='AVG DAILY'+(pivot1['Nama Cabang'].str.len().max()+22)*' '
st.dataframe(pd.concat([pivot1,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)

st.markdown('### ')
cabang = st.selectbox("CABANG:", ['ALL']+df_item['Nama Cabang'].unique().tolist(), index=0)

pivot2 = df_item[(df_item['Nama Cabang'].isin(df_item['Nama Cabang'].unique() if cabang=='ALL' else [cabang]))].groupby(['BULAN','NAMA BARANG'])[['Kuantitas']].sum().reset_index().pivot(index='NAMA BARANG', columns='BULAN', values='Kuantitas').reset_index().fillna(0)
total = pd.DataFrame((pivot2.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot2.columns)-1),columns=pivot2.columns[1:])
total['NAMA BARANG']='TOTAL'+(pivot2['NAMA BARANG'].str.len().max()+25)*' '
st.dataframe(pd.concat([pivot2,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2.columns[1:]), use_container_width=True, hide_index=True)
st.dataframe(pd.concat([pivot2,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2.columns[1:]), use_container_width=True, hide_index=True)
for month in total.columns.drop(['NAMA BARANG']):
    total[month]=total[month][0] / days_in_month[month[:-5]]
total['NAMA BARANG']='AVG DAILY'+(pivot2['NAMA BARANG'].str.len().max()+22)*' '
st.dataframe(pd.concat([pivot2,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2.columns[1:]), use_container_width=True, hide_index=True)

st.markdown('### ')
pivot3 = df_paket[(df_paket['Nama Cabang'].isin(df_item['Nama Cabang'].unique() if cabang=='ALL' else [cabang]))].groupby(['BULAN','NAMA BARANG'])[['Kuantitas']].sum().reset_index().pivot(index='NAMA BARANG', columns='BULAN', values='Kuantitas').reset_index().fillna(0)
total = pd.DataFrame((pivot3.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot3.columns)-1),columns=pivot3.columns[1:])
total['NAMA BARANG']='TOTAL'+(pivot3['NAMA BARANG'].str.len().max()+25)*' '
st.dataframe(pd.concat([pivot3,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot3.columns[1:]), use_container_width=True, hide_index=True)
st.dataframe(pd.concat([pivot3,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot3.columns[1:]), use_container_width=True, hide_index=True)
for month in total.columns.drop(['NAMA BARANG']):
    total[month]=total[month][0] / days_in_month[month[:-5]]
total['NAMA BARANG']='AVG DAILY'+(pivot3['NAMA BARANG'].str.len().max()+22)*' '
st.dataframe(pd.concat([pivot3,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot3.columns[1:]), use_container_width=True, hide_index=True)
