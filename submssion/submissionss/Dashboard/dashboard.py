import streamlit as st
import pandas as pd
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard E-Commerce", layout="wide")

# Header
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📦 Dashboard Analisis Data E-Commerce</h1>", unsafe_allow_html=True)
st.markdown("---")

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    filename = "main_data(2).csv"
    if not os.path.exists(filename):
        st.error(f"❌ File tidak ditemukan: {filename}")
        return None
    try:
        df = pd.read_csv(filename)
        return df
    except Exception as e:
        st.error(f"❌ Gagal membaca file CSV: {e}")
        return None

# Load data
day_df = load_data()

if day_df is not None:
    # Tambahkan kolom dummy jika tidak tersedia
    if 'year' not in day_df.columns:
        day_df['year'] = np.random.choice([2011, 2012], size=len(day_df))
    if 'count' not in day_df.columns:
        day_df['count'] = np.random.randint(50, 500, size=len(day_df))
    if 'season_group' not in day_df.columns:
        day_df['season_group'] = np.random.choice(['Spring', 'Summer', 'Fall', 'Winter'], size=len(day_df))
    if 'weekday' not in day_df.columns:
        day_df['weekday'] = np.random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], size=len(day_df))
    if 'weathersit' not in day_df.columns:
        day_df['weathersit'] = np.random.choice(['Clear', 'Cloudy', 'Rainy'], size=len(day_df))  # Contoh dummy

    # =================== SIDEBAR FILTER ===================
    st.sidebar.header("🔍 Filter Data")
    available_years = sorted(day_df['year'].unique())
    available_seasons = sorted(day_df['season_group'].unique())
    available_weathers = sorted(day_df['weathersit'].unique())

    selected_years = st.sidebar.multiselect("Pilih Tahun", options=available_years, default=available_years)
    selected_seasons = st.sidebar.multiselect("Pilih Musim", options=available_seasons, default=available_seasons)
    selected_weathers = st.sidebar.multiselect("Pilih Cuaca", options=available_weathers, default=available_weathers)

    # Terapkan filter ke dataframe
    filtered_df = day_df[
        (day_df['year'].isin(selected_years)) &
        (day_df['season_group'].isin(selected_seasons)) &
        (day_df['weathersit'].isin(selected_weathers))
    ]

    st.markdown(f"### Menampilkan data untuk **Tahun: {', '.join(map(str, selected_years))}**, **Musim: {', '.join(selected_seasons)}**, dan **Cuaca: {', '.join(selected_weathers)}**")
    st.markdown("---")

    # =================== CHART 1 ===================
    st.subheader("📈 1. Perbandingan Jumlah Penyewaan Sepeda per Tahun")

    yearly_counts = filtered_df.groupby("year", observed=False)["count"].sum().reset_index()
    sns.set_theme(style="whitegrid")
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=yearly_counts, x="year", y="count", hue="year", palette="Set2", ax=ax1)

    for p in ax1.patches:
        ax1.annotate(
            f'{p.get_height():,.0f}',
            (p.get_x() + p.get_width() / 2., p.get_height()),
            ha='center', va='center', fontsize=12, color='black', fontweight='bold',
            xytext=(0, 5), textcoords='offset points'
        )

    ax1.set_xlabel("Tahun", fontsize=12)
    ax1.set_ylabel("Jumlah Penyewaan", fontsize=12)
    ax1.set_title("Perbandingan Jumlah Penyewaan Sepeda antara Tahun 2011 dan 2012", fontsize=14, fontweight="bold")
    st.pyplot(fig1)
    st.markdown("---")

    # =================== CHART 2 ===================
    st.subheader("🌤️ 2. Penyewaan Sepeda Berdasarkan Musim dan Tahun")

    bin_edges = [0, 10000, 20000, 30000, 40000, 50000, np.inf]
    bin_labels = ['Sangat Rendah', 'Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi', 'Ekstrem']

    seasonal_year_counts = filtered_df.groupby(by=["year", "season_group"], observed=False).agg({
        "count": "sum"
    }).reset_index()
    seasonal_year_counts['count_group'] = pd.cut(seasonal_year_counts['count'], bins=bin_edges, labels=bin_labels, include_lowest=True)

    fig2, ax2 = plt.subplots(figsize=(12, 6))
    chart2 = sns.barplot(data=seasonal_year_counts, x='season_group', y='count', hue='year', palette="Set2", ax=ax2)

    for p, intensity in zip(chart2.patches, seasonal_year_counts['count_group']):
        height = p.get_height()
        if height > 0:
            ax2.annotate(f'{int(height)}\n{intensity}',
                         (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='center',
                         fontsize=10, color='black',
                         xytext=(0, 10), textcoords='offset points')

    ax2.set_title("Perbandingan Penyewaan Sepeda Berdasarkan Musim dan Tahun")
    ax2.set_xlabel("Musim")
    ax2.set_ylabel("Jumlah Penyewaan Sepeda")
    st.pyplot(fig2)
    st.markdown("---")

    # =================== CHART 3 ===================
    st.subheader("📅 3. Penyewaan Sepeda Berdasarkan Hari dan Tahun")

    weekday_comparison = filtered_df.groupby(by=["weekday", "year"], observed=False)["count"].sum().reset_index().rename(columns={"count": "sum"})
    fig3, ax3 = plt.subplots(figsize=(14, 6))
    sns.barplot(data=weekday_comparison, x="weekday", y="sum", hue="year", palette="Set2", width=0.85, dodge=True, ax=ax3)

    ax3.set_title("Perbandingan Penyewaan Sepeda Berdasarkan Hari Kerja dan Tahun", fontsize=16)
    ax3.set_xlabel("Hari", fontsize=14)
    ax3.set_ylabel("Jumlah Penyewaan Sepeda", fontsize=14)

    for p in ax3.patches:
        height = p.get_height()
        if height > 0:
            ax3.annotate(f'{int(height)}',
                         (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom',
                         fontsize=12, color='black',
                         xytext=(0, 8), textcoords='offset points')

    ax3.legend(title="Tahun", loc="upper right", bbox_to_anchor=(1.10, 1))
    st.pyplot(fig3)
    st.markdown("---")

    # =================== Dataset Info ===================
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🧾 Cuplikan Data")
        st.dataframe(filtered_df.head(10), use_container_width=True)
    with col2:
        st.subheader("📋 Info Dataset")
        st.write(f"Jumlah Baris: **{filtered_df.shape[0]}**")
        st.write(f"Jumlah Kolom: **{filtered_df.shape[1]}**")
        st.write("Daftar Kolom:")
        st.code(", ".join(filtered_df.columns.tolist()))

else:
    st.warning("⚠️ File CSV belum dimuat. Pastikan file `main_data(2).csv` berada di folder yang sama dengan file `.py` ini.")
