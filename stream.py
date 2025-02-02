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



def download_file_from_google_drive(file_id, dest_path):
    if not os.path.exists(dest_path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, dest_path, quiet=False)
        
download_file_from_google_drive('1EDWQJXuYu34WZNcZOx1WXqxOEwq_QKug', 'downloaded_file.zip')
download_file_from_google_drive('1e25qJ5HQiz0I_v77NGsKM3uTxUuOgBEW', 'daftar_gudang.csv')

if 'df_2205' not in locals():
    with zipfile.ZipFile(f'downloaded_file.zip', 'r') as z:
        df_2205 = []
        df_cancelnota = []
        df_paket = []
        for file_name in z.namelist():
          # Memeriksa apakah file tersebut berformat CSV
          if file_name.startswith('Cancel'):
              with z.open(file_name) as f:
                  df_cancelnota.append(pd.read_csv(f))
          elif file_name.startswith('Promix'):
              # Membaca file CSV ke dalam DataFrame
              with z.open(file_name) as f:
                  df_2205.append(pd.read_csv(f))
          elif file_name.startswith('Paket'):
              # Membaca file CSV ke dalam DataFrame
              with z.open(file_name) as f:
                  df_paket.append(pd.read_csv(f))
      
        # Menggabungkan semua DataFrame menjadi satu
        df_2205 = pd.concat(df_2205, ignore_index=True)
        df_cancelnota = pd.concat(df_cancelnota, ignore_index=True)
        df_paket = pd.concat(df_paket, ignore_index=True)
        
st.title('Dashboard - Promix')

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

list_bulan = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']

df_cab = pd.read_csv('daftar_gudang.csv')

df_cancelnota['Month'] = pd.Categorical(df_cancelnota['Month'], categories=[x for x in list_bulan if x in df_cancelnota['Month'].unique()], ordered=True)
df_cancelnota = df_cancelnota.merge(df_cab[['Cabang','Nama Cabang']],how='left')

df_2205['Month'] = pd.Categorical(df_2205['Month'], categories=[x for x in list_bulan if x in df_2205['Month'].unique()], ordered=True)
df_2205 = df_2205.merge(df_cab[['Cabang','Nama Cabang']],how='left')
df_2205['Nota Status'] = df_2205['Nota Status'].fillna('')
df_2205['Status'] = df_2205['Status'].replace({'ONLINE/OFFLINE':'TAKE AWAY'})
col = st.columns(2)
with col[0]:
    sales = st.selectbox("SALES/CANCEL NOTA:", ['SALES','CANCEL NOTA'], index=0)
    total = st.selectbox("TOTAL:", ['KUANTITAS'] if sales == 'SALES' else ['KUANTITAS','NOMOR','HARGA'], index=0)
with col[1]:
    kategori = st.selectbox("KATEGORI:", ['ALL','BEVERAGES','DIMSUM','MIE'] if total=='KUANTITAS' else ['ALL'], index=0)
    status = st.selectbox("STATUS:", ['ALL','DINE IN','TAKE AWAY'] if total=='KUANTITAS' else ['ALL'], index=0)

def format_number(x):
    if x==0:
        return ''
    if isinstance(x, (int, float)):
        return "{:,.0f}".format(x)
    return x
    
if (total=='KUANTITAS'):
    pivot1 = df_2205[(df_2205['Nota Status'] == ('Cancel Nota' if sales=='CANCEL NOTA' else '')) & (df_2205['Master Kategori'].isin((df_2205['Master Kategori'].unique() if kategori=='ALL' else [kategori]))) &
                (df_2205['Status'].isin((df_2205['Status'].unique() if status=='ALL' else [status])))].groupby(['Nama Cabang','Month'])[['Kuantitas']].sum().reset_index().pivot(index='Nama Cabang',columns='Month',values='Kuantitas').reset_index().fillna(0)
    total = pd.DataFrame((pivot1.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot1.columns)-1),columns=pivot1.columns[1:])
    total['Nama Cabang']='TOTAL'+(pivot1['Nama Cabang'].str.len().max()+25)*' '
    st.dataframe(pd.concat([pivot1,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)
    st.dataframe(pd.concat([pivot1,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)
    for month in total.columns.drop(['Nama Cabang']):
        total[month]=total[month][0] / days_in_month[month]
    total['Nama Cabang']='AVG DAILY'+(pivot1['Nama Cabang'].str.len().max()+22)*' '
    st.dataframe(pd.concat([pivot1,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)
else:
    pivot1 = df_cancelnota.groupby(['Nama Cabang','Month'])[['Nomor #' if total=='NOMOR' else 'Total Harga']].sum().reset_index().pivot(index='Nama Cabang',columns='Month',values='Nomor #' if total=='NOMOR' else 'Total Harga').reset_index().fillna(0)
    total = pd.DataFrame((pivot1.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot1.columns)-1),columns=pivot1.columns[1:])
    total['Nama Cabang']='TOTAL'+(pivot1['Nama Cabang'].str.len().max()+25)*' '
    st.dataframe(pd.concat([pivot1,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)
    st.dataframe(pd.concat([pivot1,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)
    for month in total.columns.drop(['Nama Cabang']):
        total[month]=total[month][0] / days_in_month[month]
    total['Nama Cabang']='AVG DAILY'+(pivot1['Nama Cabang'].str.len().max()+20)*' '
    st.dataframe(pd.concat([pivot1,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)

st.markdown('### ')
cabang = st.selectbox("CABANG:", ['ALL']+df_2205['Nama Cabang'].unique().tolist(), index=0)
    
pivot2 = df_2205[(df_2205['Nota Status'] == ('Cancel Nota' if sales=='CANCEL NOTA' else '')) & (df_2205['Master Kategori'].isin((df_2205['Master Kategori'].unique() if kategori=='ALL' else [kategori]))) &
                (df_2205['Status'].isin((df_2205['Status'].unique() if status=='ALL' else [status]))) & (df_2205['Nama Cabang'].isin(df_2205['Nama Cabang'].unique() if cabang=='ALL' else [cabang]))].groupby(['Nama Barang','Month'])[['Kuantitas']].sum().reset_index().pivot(index='Nama Barang',columns='Month',values='Kuantitas').reset_index()
total = pd.DataFrame((pivot2.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot2.columns)-1),columns=pivot2.columns[1:])
total['Nama Barang']='TOTAL'+(pivot2['Nama Barang'].str.len().max()+12)*' '
st.dataframe(pd.concat([pivot2,total])[:-1].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2.columns[1:]), use_container_width=True, hide_index=True)
st.dataframe(pd.concat([pivot2,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot2.columns[1:]), use_container_width=True, hide_index=True)
for month in total.columns.drop(['Nama Barang']):
    total[month]=total[month][0] / days_in_month[month]
total['Nama Barang']='AVG DAILY'+(pivot2['Nama Barang'].str.len().max()+8)*' '
st.dataframe(pd.concat([pivot2,total])[-1:].style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)


st.markdown('### ')
st.markdown('### Sales - Paket ')
total2 = st.selectbox("TOTAL:", ['KUANTITAS','HARGA'], index=0)
df_paket['Month'] = pd.Categorical(df_paket['Month'], categories=[x for x in list_bulan if x in df_paket['Month'].unique()], ordered=True)
df_paket = df_paket.pivot(index='Nama Barang',columns='Month',values='Kuantitas' if total2=='KUANTITAS' else 'Total Harga').reset_index()
st.dataframe(df_paket.style.format(lambda x: '' if x==0 else format_number(x)).background_gradient(cmap='Reds', axis=1, subset=pivot1.columns[1:]), use_container_width=True, hide_index=True)

