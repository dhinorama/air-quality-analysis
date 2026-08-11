import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# KONFIGURASI DASHBOARD
# ============================================================

st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Air Quality Analysis Dashboard")
st.markdown(
    "Dashboard analisis kualitas udara berdasarkan "
    "Air Quality Dataset periode 2013–2017."
)


# ============================================================
# MEMBACA DATA
# ============================================================

df = pd.read_csv("main_data.csv")


# ============================================================
# SIDEBAR FILTER
# ============================================================

st.sidebar.header("🔎 Filter Data")

tahun_pilihan = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(df["year"].unique()),
    default=sorted(df["year"].unique())
)

stasiun_pilihan = st.sidebar.multiselect(
    "Pilih Stasiun",
    options=sorted(df["station"].unique()),
    default=sorted(df["station"].unique())
)


# Filter data berdasarkan pilihan pengguna
filtered_df = df[
    (df["year"].isin(tahun_pilihan)) &
    (df["station"].isin(stasiun_pilihan))
]


# ============================================================
# RINGKASAN DATA
# ============================================================

st.header("📊 Ringkasan Data")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Jumlah Data",
        f"{len(filtered_df):,}"
    )

with col2:
    st.metric(
        "Rata-rata PM2.5",
        f"{filtered_df['PM2.5'].mean():.2f}"
    )

with col3:
    st.metric(
        "Rata-rata CO",
        f"{filtered_df['CO'].mean():.2f}"
    )

with col4:
    st.metric(
        "Jumlah Stasiun",
        filtered_df["station"].nunique()
    )


# ============================================================
# PERTANYAAN BISNIS 1
# ============================================================

st.header("📈 Pertanyaan Bisnis 1")

st.markdown(
    """
    **Bagaimana perubahan rata-rata konsentrasi PM2.5 dan CO
    berdasarkan tahun selama periode 2013–2017, dan tahun mana
    yang memiliki tingkat polusi tertinggi?**
    """
)


# Menghitung rata-rata PM2.5 dan CO berdasarkan tahun
q1 = (
    filtered_df
    .groupby("year")[["PM2.5", "CO"]]
    .mean()
    .reset_index()
)


# Mengubah format data agar dapat digunakan untuk grafik
q1_melt = q1.melt(
    id_vars="year",
    value_vars=["PM2.5", "CO"],
    var_name="Polutan",
    value_name="Rata-rata"
)


# Membuat grafik
fig1 = px.line(
    q1_melt,
    x="year",
    y="Rata-rata",
    color="Polutan",
    markers=True,
    title="Perubahan Rata-rata PM2.5 dan CO Berdasarkan Tahun"
)

fig1.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Rata-rata Konsentrasi"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# Menentukan tahun dengan PM2.5 tertinggi
tahun_pm25 = q1.loc[
    q1["PM2.5"].idxmax(),
    "year"
]

nilai_pm25 = q1["PM2.5"].max()


# Menentukan tahun dengan CO tertinggi
tahun_co = q1.loc[
    q1["CO"].idxmax(),
    "year"
]

nilai_co = q1["CO"].max()


col1, col2 = st.columns(2)

with col1:
    st.info(
        f"PM2.5 tertinggi: **{int(tahun_pm25)}** "
        f"({nilai_pm25:.2f})"
    )

with col2:
    st.info(
        f"CO tertinggi: **{int(tahun_co)}** "
        f"({nilai_co:.2f})"
    )


# ============================================================
# PERTANYAAN BISNIS 2
# ============================================================

st.header("📍 Pertanyaan Bisnis 2")

st.markdown(
    """
    **Stasiun pemantauan mana yang memiliki rata-rata konsentrasi
    PM2.5 tertinggi selama periode 2013–2017, dan bagaimana
    kondisi cuaca berkaitan dengan konsentrasi PM2.5?**
    """
)


# Rata-rata PM2.5 berdasarkan stasiun
q2 = (
    filtered_df
    .groupby("station")["PM2.5"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)


# Membuat grafik
fig2 = px.bar(
    q2,
    x="station",
    y="PM2.5",
    title="Rata-rata Konsentrasi PM2.5 Berdasarkan Stasiun",
    labels={
        "station": "Stasiun",
        "PM2.5": "Rata-rata PM2.5"
    }
)

fig2.update_layout(
    xaxis_tickangle=-45
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# Menentukan stasiun dengan PM2.5 tertinggi
stasiun_tertinggi = q2.iloc[0]["station"]
nilai_stasiun_tertinggi = q2.iloc[0]["PM2.5"]


st.info(
    f"Stasiun dengan rata-rata PM2.5 tertinggi: "
    f"**{stasiun_tertinggi}** "
    f"({nilai_stasiun_tertinggi:.2f})"
)


# ============================================================
# KORELASI PM2.5 DENGAN FAKTOR CUACA
# ============================================================

st.subheader("🌦️ Hubungan PM2.5 dengan Faktor Cuaca")


faktor_cuaca = [
    "TEMP",
    "PRES",
    "DEWP",
    "RAIN",
    "WSPM"
]


korelasi = (
    filtered_df[
        ["PM2.5"] + faktor_cuaca
    ]
    .corr()["PM2.5"]
    .drop("PM2.5")
    .sort_values()
    .reset_index()
)

korelasi.columns = [
    "Faktor Cuaca",
    "Korelasi"
]


# Grafik korelasi
fig3 = px.bar(
    korelasi,
    x="Faktor Cuaca",
    y="Korelasi",
    title="Korelasi PM2.5 dengan Faktor Cuaca"
)

fig3.add_hline(y=0)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# Faktor dengan hubungan paling kuat
korelasi["Nilai Absolut"] = korelasi["Korelasi"].abs()

faktor_terkuat = korelasi.loc[
    korelasi["Nilai Absolut"].idxmax(),
    "Faktor Cuaca"
]

nilai_korelasi = korelasi.loc[
    korelasi["Nilai Absolut"].idxmax(),
    "Korelasi"
]


st.info(
    f"Faktor cuaca dengan hubungan paling kuat terhadap PM2.5: "
    f"**{faktor_terkuat}** "
    f"(korelasi = {nilai_korelasi:.2f})"
)


# ============================================================
# KESIMPULAN DAN REKOMENDASI
# ============================================================

st.header("📝 Kesimpulan & Rekomendasi")


st.markdown(
    f"""
    ### Kesimpulan

    - Tahun dengan rata-rata PM2.5 tertinggi pada data yang
      dipilih adalah **{int(tahun_pm25)}**, dengan nilai
      rata-rata **{nilai_pm25:.2f}**.

    - Stasiun dengan rata-rata PM2.5 tertinggi adalah
      **{stasiun_tertinggi}**, dengan nilai rata-rata
      **{nilai_stasiun_tertinggi:.2f}**.

    - Faktor cuaca yang memiliki hubungan paling kuat dengan
      PM2.5 adalah **{faktor_terkuat}**, dengan nilai korelasi
      **{nilai_korelasi:.2f}**.

    ### Rekomendasi

    - Meningkatkan pemantauan kualitas udara pada stasiun dengan
      konsentrasi PM2.5 yang tinggi.

    - Memperhatikan kondisi cuaca yang memiliki hubungan kuat
      dengan PM2.5 dalam proses pemantauan kualitas udara.

    - Melakukan pemantauan lebih intensif pada periode ketika
      konsentrasi polutan menunjukkan peningkatan.
    """
)


st.caption(
    "Air Quality Analysis Dashboard | 2013–2017"
)