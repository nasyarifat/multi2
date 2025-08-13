import streamlit as st
import pandas as pd
from statsmodels.tsa.holtwinters import Holt, ExponentialSmoothing
import calendar
from datetime import datetime
import altair as alt

# Mapping bulan Inggris ke Indonesia
bulan_mapping = {
    "January": "Januari", "February": "Februari", "March": "Maret",
    "April": "April", "May": "Mei", "June": "Juni",
    "July": "Juli", "August": "Agustus", "September": "September",
    "October": "Oktober", "November": "November", "December": "Desember"
}
# Reverse mapping untuk parsing datetime
reverse_mapping = {v: k for k, v in bulan_mapping.items()}

# ==================== APP ====================
st.title("Kalkulator Akuaponik")

tab1, tab2 = st.tabs(["Estimasi Panen", "Forecasting Produksi Ikan"])

# ==================== TAB 1 ====================
with tab1:
    st.header("Estimasi Panen")

    # Konfigurasi default
    tingkat = 3  # jumlah pipa
    lubang_per_tingkat = 5  # lubang per pipa
    volume_per_drum = 200  # liter (default alat)

    # Hitungan kapasitas
    total_lubang = tingkat * lubang_per_tingkat  # total lubang tanam
    max_sayuran_total = total_lubang             # 1 lubang = 1 tanaman
    total_volume_liter = volume_per_drum         # volume air tidak berubah

    st.markdown(f"Konfigurasi default: {tingkat} pipa × {lubang_per_tingkat} lubang = {total_lubang} lubang")
    st.markdown(f"Volume drum: {total_volume_liter} liter")

    # Input pengguna
    jumlah_bibit = st.number_input("Jumlah Bibit Ikan (ekor)", min_value=1, step=1)
    bobot_awal = st.number_input("Bobot Awal per Ekor (gram)", min_value=0.0, step=0.1, value=5.0)
    bobot_akhir = st.number_input("Bobot Akhir per Ekor (gram)", min_value=0.0, step=0.1, value=500.0)
    jumlah_sayuran = st.number_input(
        f"Jumlah Sayuran Total (maksimal {max_sayuran_total})",
        min_value=1, max_value=max_sayuran_total, step=1,
        value=int(max_sayuran_total * 0.8)
    )
    lama_pemeliharaan = st.number_input("Lama Pemeliharaan (hari)", min_value=1, step=1, value=60)

    harga_bibit = st.number_input("Harga Bibit per Ekor (Rp)", min_value=0, step=100, value=1500)
    harga_sayuran = st.number_input("Harga Sayuran per Tanaman (Rp)", min_value=0, step=100, value=2000)

    if st.button("Hitung Estimasi"):
        # Perhitungan produksi ikan
        total_berat_kg = jumlah_bibit * bobot_akhir / 1000
        total_pakan_kg = jumlah_bibit * bobot_akhir * 1.5 / 1000

        # Modal
        modal_bibit = jumlah_bibit * harga_bibit
        modal_sayuran = jumlah_sayuran * harga_sayuran
        modal_total = modal_bibit + modal_sayuran

        # Efektivitas
        hasil_per_liter = total_berat_kg / total_volume_liter
        sayuran_efficiency = jumlah_sayuran / max_sayuran_total

        # Output hasil
        st.success(f"Estimasi Total Bobot Panen: {total_berat_kg:.2f} kg")
        st.info(f"Estimasi Total Pakan Dibutuhkan: {total_pakan_kg:.2f} kg")
        st.write(f"Lama Pemeliharaan: {lama_pemeliharaan} hari")
        st.write(f"Estimasi Modal Awal: Rp {modal_total:,} "
                 f"(Bibit: Rp {modal_bibit:,}, Sayuran: Rp {modal_sayuran:,})")

        # Efektivitas sistem
        st.write("Efektivitas Sistem:")
        st.write(f"- Hasil Panen per Liter Air: {hasil_per_liter:.4f} kg/liter")
        st.write(f"- Efektivitas Penanaman Sayuran: {sayuran_efficiency*100:.2f}% dari kapasitas maksimal")

        if hasil_per_liter < 0.05:
            st.warning("📉 Hasil panen per liter air rendah.")
        else:
            st.success("📈 Hasil panen per liter air cukup baik.")

        if sayuran_efficiency < 0.7:
            st.info("⚠ Kapasitas sayuran belum maksimal.")
        else:
            st.success("Sayuran mendekati kapasitas maksimal.")

# ==================== TAB 2 ====================
with tab2:
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame(columns=["Periode", "Produksi (kg)"])

    st.header("🐟 Forecasting Produksi Ikan Akuaponik")

    bulan_list = list(bulan_mapping.values())
    tahun_list = list(range(datetime.now().year, datetime.now().year + 6))

    with st.form("input_form"):
        bulan = st.selectbox("Pilih Bulan", bulan_list)
        tahun = st.selectbox("Pilih Tahun", tahun_list)
        produksi_str = st.text_input("Hasil Produksi Lele (kg)", placeholder="Misal: 10.5")
        submitted = st.form_submit_button("Tambah Data")

        if submitted:
            try:
                produksi = float(produksi_str)
                if produksi < 0:
                    st.error("Produksi tidak boleh negatif.")
                else:
                    periode_str = f"{bulan} {tahun}"
                    if periode_str in st.session_state.data["Periode"].values:
                        st.error(f"Periode '{periode_str}' sudah ada.")
                    else:
                        st.session_state.data = pd.concat([
                            st.session_state.data,
                            pd.DataFrame({"Periode": [periode_str], "Produksi (kg)": [produksi]})
                        ], ignore_index=True)
                        st.success(f"Data '{periode_str}' berhasil ditambahkan.")
            except ValueError:
                st.error("Masukkan angka valid.")

    if not st.session_state.data.empty:
        st.subheader("📊 Data Historis Produksi")
        st.dataframe(st.session_state.data, use_container_width=True)

        forecast_steps_str = st.text_input("Berapa bulan ke depan ingin di-forecast?", placeholder="Misal: 3")
        harga_jual_str = st.text_input("Masukkan harga jual ikan per kg (Rp)", placeholder="Misal: 20000")

        if st.button("🔮 Hitung Forecasting"):
            try:
                forecast_steps = int(forecast_steps_str)
                if not (1 <= forecast_steps <= 24):
                    st.error("Forecast 1-24 bulan.")
                    forecast_steps = None
            except ValueError:
                st.error("Masukkan angka bulat.")
                forecast_steps = None

            try:
                harga_jual = float(harga_jual_str)
                if harga_jual < 0:
                    st.error("Harga harus positif.")
                    harga_jual = None
            except ValueError:
                st.error("Masukkan angka valid.")
                harga_jual = None

            if forecast_steps and harga_jual is not None:
                df = st.session_state.data.copy()
                # Parsing bulan Indonesia ke Inggris
                df["Periode"] = df["Periode"].apply(lambda x: x.replace(x.split()[0], reverse_mapping[x.split()[0]]))
                df['Periode'] = pd.to_datetime(df['Periode'], format='%B %Y')
                df = df.sort_values('Periode')

                series = pd.Series(df['Produksi (kg)'].values, index=df['Periode'])
                if len(series) < 12:
                    model = Holt(series).fit(optimized=True)
                else:
                    model = ExponentialSmoothing(series, trend='add', seasonal='add', seasonal_periods=12).fit()

                forecast_result = model.forecast(forecast_steps)

                # Simpan state
                st.session_state.update({
                    'forecast_result': forecast_result,
                    'df': df,
                    'forecast_steps': forecast_steps,
                    'harga_jual': harga_jual
                })

    if 'forecast_result' in st.session_state:
        forecast_result = st.session_state['forecast_result']
        df = st.session_state['df']
        harga_jual = st.session_state['harga_jual']

        # Tabel forecast
        forecast_df = forecast_result.rename("Produksi (kg)").to_frame()
        forecast_df.index = forecast_df.index.strftime("%b %Y")
        st.subheader("📅 Hasil Forecasting")
        st.table(forecast_df.style.format("{:.2f}"))

        # Plot
        hist_df = df.copy()
        hist_df["Tipe"] = "Historis"

        forecast_plot_df = forecast_result.rename("Produksi (kg)").to_frame().reset_index()
        forecast_plot_df.columns = ["Periode", "Produksi (kg)"]
        forecast_plot_df["Tipe"] = "Forecast"

        combined_df = pd.concat([hist_df, forecast_plot_df], ignore_index=True)
        combined_df["Periode"] = pd.to_datetime(combined_df["Periode"])
        combined_df = combined_df.sort_values("Periode")

        color_scale = alt.Scale(domain=["Historis", "Forecast"], range=["steelblue", "orange"])

        chart = alt.Chart(combined_df).mark_line().encode(
            x=alt.X("Periode:T", axis=alt.Axis(format="%b %Y"), title="Periode"),
            y=alt.Y("Produksi (kg):Q"),
            color=alt.Color("Tipe:N", scale=color_scale, title="Jenis Data"),
            strokeDash=alt.condition(alt.datum.Tipe == "Forecast", alt.value([5, 5]), alt.value([0]))
        ) + alt.Chart(combined_df).mark_point(size=60).encode(
            x="Periode:T",
            y="Produksi (kg):Q",
            color=alt.Color("Tipe:N", scale=color_scale, legend=None),
            shape=alt.Shape("Tipe:N", legend=None)
        )

        st.altair_chart(chart.properties(height=350), use_container_width=True)

        # Hitung kebutuhan pakan & pendapatan
        kebutuhan_pakan = forecast_result.iloc[0] * 1.5
        st.subheader("🍽️ Estimasi Kebutuhan Pakan (Bulan Pertama Forecast)")
        st.write(f"{kebutuhan_pakan:.2f} kg")

        estimasi_pendapatan = forecast_result.iloc[0] * harga_jual
        st.subheader("💰 Estimasi Pendapatan (Bulan Pertama Forecast)")
        st.write(f"Rp {estimasi_pendapatan:,.0f}")

     
