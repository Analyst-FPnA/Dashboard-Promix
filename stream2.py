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

download_file_from_google_drive('14a4HmKACWics1ObPevlF0BXG1gVFShn_', 'downloaded_file.zip')
download_file_from_google_drive('1e25qJ5HQiz0I_v77NGsKM3uTxUuOgBEW', 'daftar_gudang.csv')

if 'df_item' not in locals():
    with zipfile.ZipFile(f'downloaded_file.zip', 'r') as z:
        df_mie = []
        for file_name in z.namelist():
          # Memeriksa apakah file tersebut berformat CSV
            if file_name.startswith('df_sales'):
                with z.open(file_name) as f:
                    df_mie.append(pd.read_csv(f))
        # Menggabungkan semua DataFrame menjadi satu
        df_mie = pd.concat(df_mie, ignore_index=True)
        
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

df_mie = df_mie.groupby(['BULAN','CABANG','Nama Cabang'])[['Kuantitas']].sum().reset_index()
df_mie['Tanggal'] = pd.to_datetime(df_mie['BULAN'], format='%B-%Y')
df_mie['BULAN'] = pd.Categorical(df_mie['BULAN'], categories=df_mie.sort_values('Tanggal')['BULAN'].unique(), ordered=True)
df_mie = df_mie[df_mie['BULAN']>='January 2024']
pivot1=df_mie.pivot(index='Nama Cabang', columns='BULAN', values='Kuantitas').reset_index()
st.dataframe(pivot1.fillna(0), use_container_width=True, hide_index=True)
total = pd.DataFrame((pivot1.iloc[:,1:].sum(axis=0).values).reshape(1,len(pivot1.columns)-1),columns=pivot1.columns[1:])
total['Nama Cabang'] ='TOTAL'
st.dataframe(total.loc[:,[total.columns[-1]]+total.columns[:-1].to_list()], use_container_width=True, hide_index=True)
df_mie3 = df_mie.merge(df_days, how='left')
#df_mie3['AVG_SALES'] = df_mie3['QTY'] / df_mie3['days'] 
df_mie3['AVG_SALES(-Cancel nota)'] = df_mie3['Kuantitas'] / df_mie3['days'] 

df_mie3['Tanggal'] = pd.to_datetime(df_mie3['BULAN'], format='%B-%Y')
df_mie3['BULAN'] = pd.Categorical(df_mie3['BULAN'], categories=df_mie3.sort_values('Tanggal')['BULAN'].unique(), ordered=True)

pivot1 = df_mie3[(df_mie3['BULAN'].str.contains('2024')) & (df_mie3['Kuantitas']>0)].pivot(index='CABANG',columns='BULAN',values='AVG_SALES(-Cancel nota)').reset_index()
total = pd.DataFrame((pivot1.iloc[:,1:].mean(axis=0).values).reshape(1,len(pivot1.columns)-1),columns=pivot1.columns[1:])
total['CABANG']='AVG DAILY'+(pivot1['CABANG'].str.len().max()+22)*' '

st.dataframe(total.loc[:,[total.columns[-1]]+total.columns[:-1].to_list()], use_container_width=True, hide_index=True)

df_mie = df_mie.merge(df_days, how='left')
df_mie['AVG_SALES(-Cancel nota)'] = df_mie['Kuantitas'] / df_mie['days'] 

df_mie2 = df_mie[df_mie['Kuantitas']!=0].groupby('BULAN')[['Nama Cabang']].nunique().rename(columns={'Nama Cabang':'Total Cabang'}).reset_index().merge(df_mie[df_mie['AVG_SALES(-Cancel nota)']>=4400].groupby(['BULAN'])[['Nama Cabang']].nunique().reset_index().rename(columns={'Nama Cabang':'Total Cabang Achieve'}), how='left'    
)
df_mie2['%'] = round((df_mie2['Total Cabang Achieve'] / df_mie2['Total Cabang']) *100,2)

df_mie2 = df_mie2[df_mie2['BULAN'].str.contains('2024')]

df_mie2['Tanggal'] = pd.to_datetime(df_mie2['BULAN'], format='%B-%Y')
df_mie2['BULAN'] = pd.Categorical(df_mie2['BULAN'], categories=df_mie2.sort_values('Tanggal')['BULAN'].unique(), ordered=True)
df_mie2 = df_mie2.sort_values('BULAN').T
df_mie2.columns = df_mie2.iloc[0,:]
st.dataframe(df_mie2.iloc[[1,2,3],:].reset_index().rename(columns={'index':'BULAN'}), use_container_width=True, hide_index=True)
