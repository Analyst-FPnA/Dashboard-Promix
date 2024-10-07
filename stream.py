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
          if file_name.endswith('nota.csv'):
              with z.open(file_name) as f:
                  df_cancelnota = pd.read_csv(f)
          elif file_name.endswith('.csv'):
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

df_cancelnota['Month'] = pd.Categorical(df_cancelnota['Month'], categories=[x for x in list_bulan if x in df_cancelnota['Month'].unique()], ordered=True)
df_cancelnota['Cabang'] = df_cancelnota['Nama Pelanggan'].str.extract(r'\(([^()]*)\)[^()]*$')[0].values
df_cancelnota = df_cancelnota.merge(df_cab[['Cabang','Nama Cabang']],how='left')

df_2205['Month'] = pd.Categorical(df_2205['Month'], categories=[x for x in list_bulan if x in df_2205['Month'].unique()], ordered=True)
df_2205['Cabang'] = df_2205['Nama Pelanggan'].str.extract(r'\(([^()]*)\)[^()]*$')[0].values
df_2205 = df_2205.merge(df_cab[['Cabang','Nama Cabang']],how='left')

df_2205_can = df_2205[df_2205['Nota Status']      ==  'Cancel Nota']
df_2205 = df_2205[df_2205['Nota Status']      !=  'Cancel Nota']

kategori = st.selectbox("KATEGORI:", ['ALL','BEVERAGES','DIMSUM','MIE'], index=0)

def format_number(x):
    if x==0:
        return ''
    if isinstance(x, (int, float)):
        return "{:,.0f}".format(x)
    return x
    

pivot1 = df_2205[df_2205['Master Kategori'].isin((df_2205['Master Kategori'].unique() if kategori=='ALL' else [kategori]))].groupby(['Nama Cabang','Month'])[['Kuantitas']].sum().reset_index().pivot(index='Nama Cabang',columns='Month',values='Kuantitas').reset_index()
total = pd.DataFrame((pivot1.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot1.columns)-1),columns=pivot1.columns[1:])
total['Nama Cabang']='TOTAL'+(pivot1['Nama Cabang'].str.len().max()+25)*' '

st.dataframe(pd.concat([pivot1,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)
st.dataframe(pd.concat([pivot1,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)

st.markdown('### ')
cabang = st.selectbox("CABANG:", ['ALL']+df_2205['Nama Cabang'].unique().tolist(), index=0)

pivot2 = df_2205[(df_2205['Master Kategori'].isin((df_2205['Master Kategori'].unique() if kategori=='ALL' else [kategori]))) & (df_2205['Nama Cabang'].isin(df_2205['Nama Cabang'].unique() if cabang=='ALL' else [cabang]))].groupby(['Nama Barang','Month'])[['Kuantitas']].sum().reset_index().pivot(index='Nama Barang',columns='Month',values='Kuantitas').reset_index()
total = pd.DataFrame((pivot2.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot2.columns)-1),columns=pivot2.columns[1:])
total['Nama Barang']='TOTAL'+(pivot2['Nama Barang'].str.len().max()+12)*' '
st.dataframe(pd.concat([pivot2,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2.columns[1:]), use_container_width=True, hide_index=True)
st.dataframe(pd.concat([pivot2,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2.columns[1:]), use_container_width=True, hide_index=True)



st.markdown('### ')
st.markdown('## Cancel Nota')
kategori_cn = st.selectbox("TOTAL CANCELNOTA:", ['ITEM','NOMOR','NOM'], index=0)
if kategori_cn=='ITEM':
    pivot1_can = df_2205_can[df_2205_can['Master Kategori'].isin((df_2205_can['Master Kategori'].unique() if kategori=='ALL' else [kategori]))].groupby(['Nama Cabang','Month'])[['Kuantitas']].sum().reset_index().pivot(index='Nama Cabang',columns='Month',values='Kuantitas').reset_index()
elif kategori_cn=='NOMOR':
    pivot1_can = df_cancelnota.pivot(index='Nama Cabang',columns='Month',values='Nomor #').reset_index().fillna(0)
elif kategori_cn=='NOM':
    pivot1_can = df_cancelnota.pivot(index='Nama Cabang',columns='Month',values='Total Harga').reset_index.fillna(0)
total = pd.DataFrame((pivot1_can.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot1_can.columns)-1),columns=pivot1_can.columns[1:])    
total['Nama Cabang']='TOTAL'+(pivot1_can['Nama Cabang'].str.len().max()+25)*' '
st.dataframe(pd.concat([pivot1_can,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1_can.columns[1:]), use_container_width=True, hide_index=True)
st.dataframe(pd.concat([pivot1_can,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1_can.columns[1:]), use_container_width=True, hide_index=True)

st.markdown('### ')
pivot2_can = df_2205_can[(df_2205_can['Master Kategori'].isin((df_2205_can['Master Kategori'].unique() if kategori=='ALL' else [kategori]))) & (df_2205_can['Nama Cabang'].isin(df_2205_can['Nama Cabang'].unique() if cabang=='ALL' else [cabang]))].groupby(['Nama Barang','Month'])[['Kuantitas']].sum().reset_index().pivot(index='Nama Barang',columns='Month',values='Kuantitas').reset_index()
total = pd.DataFrame((pivot2_can.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot2_can.columns)-1),columns=pivot2_can.columns[1:])
total['Nama Barang']='TOTAL'+(pivot2_can['Nama Barang'].str.len().max()+12)*' '
st.dataframe(pd.concat([pivot2_can,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2_can.columns[1:]), use_container_width=True, hide_index=True)
st.dataframe(pd.concat([pivot2_can,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2_can.columns[1:]), use_container_width=True, hide_index=True)
