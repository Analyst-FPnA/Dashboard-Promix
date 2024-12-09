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
        df_mie = []
        for file_name in z.namelist():
          # Memeriksa apakah file tersebut berformat CSV
            if file_name.startswith('df_sales'):
        # Menggabungkan semua DataFrame menjadi satu
        df_mie = pd.concat(df_sales, ignore_index=True)
        
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

df_days = pd.DataFrame([days_in_month]).T.reset_index().rename(columns={'index':'BULAN',0:'days'})
df_days['BULAN'] = df_days['BULAN']+' 2023'
df_days2 = df_days.copy()
df_days2['BULAN'] = df_days2['BULAN'].str.replace('2023','2024')
df_days = pd.concat([df_days,df_days2]) 
df_days.loc[df_days[df_days['BULAN']=='February 2024'].index,'days'] = 29

df_mie['Tanggal'] = pd.to_datetime(df_mie['Tanggal'])
df_mie['BULAN'] = pd.Categorical(df_mie['BULAN'], categories=df_mie.sort_values('Tanggal')['BULAN'].unique(), ordered=True)

pivot1=df_mie.pivot(index='Nama Cabang', columns='BULAN', values='Kuantitas').reset_index()
st.dataframe(pivot1)
total = pd.DataFrame((pivot1.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot1.columns)-1),columns=pivot1.columns[1:])
total['Nama Cabang'] ='TOTAL'
st.dataframe(total.loc[:,[total.columns[-1]]+total.columns[:-1].to_list()])
for month in total.columns.drop(['Nama Cabang']):
        total[month]=total[month][0] / days_in_month[month[:-5]]
total['Nama Cabang']='AVG DAILY'+(pivot1['Nama Cabang'].str.len().max()+22)*' '
st.dataframe(total.loc[:,[total.columns[-1]]+total.columns[:-1].to_list()])
