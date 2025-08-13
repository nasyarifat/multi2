import streamlit as st

# Judul utama
st.title("Kalkulator Akuaponik")

# Buat tab
tab1, tab2 = st.tabs(["Estimasi Panen", "Forecasting Produksi Ikan"])

# ================= TAB 1 - ESTIMASI PANEN =================
# ================= TAB 1 - ESTIMASI PANEN =================
with tab1:
    import pandas as pd

    st.header("Estimasi Panen")

    tingkat = 3
    lubang_per_tingkat = 5
    max_sayuran_per_lubang = 10
    volume_per_drum = 200  # liter

    total_lubang = tingkat * lubang_per_tingkat
    max_sayuran_total = total_lubang * max_sayuran_per_lubang
    total_volume_liter = total_lubang * volume_per_drum

    st.markdown(f"**Konfigurasi default:** {tingkat} tingkat × {lubang_per_tingkat} lubang per tingkat = {total_lubang} lubang")
    st.markdown(f"Volume total drum: {total_volume_liter} liter (3 m³)")

    # Input user
    jumlah_bibit = st.number_input("Jumlah Bibit Ikan (ekor)", min_value=1, step=1)
    bobot_awal = st.number_input("Bobot Awal per Ekor (gram)", min_value=0.0, step=0.1, value=5.0)
    bobot_akhir = st.number_input("Bobot Akhir per Ekor (gram)", min_value=0.0, step=0.1, value=500.0)
    jumlah_sayuran = st.number_input(f"Jumlah Sayuran Total (maksimal {max_sayuran_total})", min_value=1, max_value=max_sayuran_total, step=1, value=int(max_sayuran_total * 0.8))
    lama_pemeliharaan = st.number_input("Lama Pemeliharaan (hari)", min_value=1, step=1, value=60)

    harga_bibit = st.number_input("Harga Bibit per Ekor (Rp)", min_value=0, step=100, value=1500)
    harga_sayuran = st.number_input("Harga Sayuran per Tanaman (Rp)", min_value=0, step=100, value=2000)

    if st.button("Hitung Estimasi"):
        # Hitung hasil panen
        total_berat_kg = jumlah_bibit * bobot_akhir / 1000  # kg

        # Estimasi pakan (misal 1.5 kali bobot akhir per ekor)
        total_pakan_kg = jumlah_bibit * bobot_akhir * 1.5 / 1000  # kg

        # Modal awal
        modal_bibit = jumlah_bibit * harga_bibit
        modal_sayuran = jumlah_sayuran * harga_sayuran
        modal_total = modal_bibit + modal_sayuran

        # Efektivitas
        hasil_per_liter = total_berat_kg / total_volume_liter  # kg per liter
        sayuran_efficiency = jumlah_sayuran / max_sayuran_total  # 0-1

        # Tampilkan hasil
        st.success(f"Estimasi Total Bobot Panen: {total_berat_kg:.2f} kg")
        st.info(f"Estimasi Total Pakan Dibutuhkan: {total_pakan_kg:.2f} kg")
        st.write(f"Lama Pemeliharaan: {lama_pemeliharaan} hari")
        st.write(f"Estimasi Modal Awal: Rp {modal_total:,} (Bibit: Rp {modal_bibit:,}, Sayuran: Rp {modal_sayuran:,})")
        st.write(f"Efektivitas Sistem:")
        st.write(f"- Hasil Panen per Liter Air: {hasil_per_liter:.4f} kg/liter")
        st.write(f"- Efektivitas Penanaman Sayuran: {sayuran_efficiency*100:.2f}% dari kapasitas maksimal")

        if hasil_per_liter < 0.05:
            st.warning("📉 Hasil panen per liter air rendah. Evaluasi kepadatan bibit atau kualitas pakan.")
        else:
            st.success("📈 Hasil panen per liter air cukup baik.")

        if sayuran_efficiency < 0.7:
            st.info("⚠️ Kapasitas sayuran belum maksimal, bisa ditingkatkan untuk efisiensi nutrisi.")
        else:
            st.success("Sayuran ditanam mendekati kapasitas maksimal.")



# ================= TAB 2 - FORECASTING PRODUKSI IKAN =================
with tab2:
    import streamlit as st
    import pandas as pd
    from statsmodels.tsa.holtwinters import Holt, ExponentialSmoothing
    import calendar
    from datetime import datetime
    import altair as alt
    import locale
    
    try:
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
    except:
        st.warning("Locale 'id_ID.UTF-8' tidak tersedia di sistem. Bulan akan tetap dalam bahasa Inggris.")
    
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame(columns=["Periode", "Produksi (kg)"])
    
    st.title("🐟 Forecasting Produksi Ikan Akuaponik")
    
    bulan_list = list(calendar.month_name)[1:]
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
                        new_row = pd.DataFrame({"Periode": [periode_str], "Produksi (kg)": [produksi]})
                        st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                        st.success(f"Data untuk periode '{periode_str}' berhasil ditambahkan.")
            except ValueError:
                st.error("Masukkan angka valid untuk produksi.")
    
    if not st.session_state.data.empty:
        st.subheader("📊 Data Historis Produksi")
        st.dataframe(st.session_state.data, use_container_width=True)
        
        forecast_steps_str = st.text_input("Berapa bulan ke depan ingin di-forecast?", placeholder="Misal: 3")
        harga_jual_str = st.text_input("Masukkan harga jual ikan per kg (Rp)", placeholder="Misal: 20000")
        
        if st.button("🔮 Hitung Forecasting"):
            try:
                forecast_steps = int(forecast_steps_str)
                if not (1 <= forecast_steps <= 24):
                    st.error("Jumlah bulan forecast harus 1-24.")
                    forecast_steps = None
            except ValueError:
                st.error("Masukkan angka bulat untuk bulan forecast.")
                forecast_steps = None
            
            try:
                harga_jual = float(harga_jual_str)
                if harga_jual < 0:
                    st.error("Harga jual harus positif.")
                    harga_jual = None
            except ValueError:
                st.error("Masukkan angka valid untuk harga jual.")
                harga_jual = None
            
            if forecast_steps and harga_jual is not None:
                df = st.session_state.data.copy()
                df['Periode'] = pd.to_datetime(df['Periode'], format='%B %Y')
                df = df.sort_values('Periode')
                
                series = pd.Series(df['Produksi (kg)'].values, index=df['Periode'])
                if len(series) < 12:
                    model = Holt(series).fit(optimized=True)
                else:
                    model = ExponentialSmoothing(series, trend='add', seasonal='add', seasonal_periods=12).fit()
                    
                forecast_result = model.forecast(forecast_steps)
                
                st.session_state.update({
                    'forecast_result': forecast_result,
                    'df': df,
                    'forecast_steps': forecast_steps,
                    'harga_jual': harga_jual
                })
    
    st.divider()
    
    if 'forecast_result' in st.session_state:
        forecast_result = st.session_state['forecast_result']
        df = st.session_state['df']
        harga_jual = st.session_state['harga_jual']
        
        forecast_df = forecast_result.rename("Produksi (kg)").to_frame()
        forecast_df.index = forecast_df.index.strftime("%b %Y")
        st.subheader("📅 Hasil Forecasting")
        st.table(forecast_df.style.format("{:.2f}"))
        
        hist_df = df.copy()
        hist_df["Tipe"] = "Historis"
        
        forecast_plot_df = forecast_result.rename("Produksi (kg)").to_frame().reset_index()
        forecast_plot_df.columns = ["Periode", "Produksi (kg)"]
        forecast_plot_df["Tipe"] = "Forecast"
        
        combined_df = pd.concat([hist_df, forecast_plot_df], ignore_index=True)
        combined_df["Periode"] = pd.to_datetime(combined_df["Periode"])
        combined_df = combined_df.sort_values("Periode")
        
        color_scale = alt.Scale(domain=["Historis", "Forecast"], range=["steelblue", "orange"])
        
        line = alt.Chart(combined_df).mark_line().encode(
            x=alt.X("Periode:T", axis=alt.Axis(format="%b %Y", tickCount="month"), title="Periode"),
            y=alt.Y("Produksi (kg):Q"),
            color=alt.Color("Tipe:N", scale=color_scale, title="Jenis Data"),
            strokeDash=alt.condition(alt.datum.Tipe == "Forecast", alt.value([5, 5]), alt.value([0]))
        )
        
        points = alt.Chart(combined_df).mark_point(size=60).encode(
            x=alt.X("Periode:T", axis=alt.Axis(format="%b %Y")),
            y="Produksi (kg):Q",
            color=alt.Color("Tipe:N", scale=color_scale, legend=None),
            shape=alt.Shape("Tipe:N", legend=None)
        )
        
        st.altair_chart((line + points).properties(height=350), use_container_width=True)
        
        kebutuhan_pakan = forecast_result.iloc[0] * 1.5
        st.subheader("🍽️ Estimasi Kebutuhan Pakan (Bulan Pertama Forecast)")
        st.write(f"{kebutuhan_pakan:.2f} kg")
        
        estimasi_pendapatan = forecast_result.iloc[0] * harga_jual
        st.subheader("💰 Estimasi Pendapatan (Bulan Pertama Forecast)")
        st.write(f"Rp {estimasi_pendapatan:,.0f}")
        
        produksi_bulan_pertama = forecast_result.iloc[0]
        if produksi_bulan_pertama < 10:
            st.info("📉 Produksi rendah. Optimalkan pemeliharaan atau pakan.")
        elif produksi_bulan_pertama > 50:
            st.success("📈 Produksi tinggi. Siapkan pakan & strategi pemasaran.")
        else:
            st.write("🔄 Produksi stabil. Lanjutkan pemeliharaan.")
        if estimasi_pendapatan < 200000:
            st.warning("⚠️ Pendapatan rendah. Periksa harga jual & biaya produksi.")
        else:
            st.write("✅ Pendapatan baik. Pertahankan strategi.")
    else:
        st.info("Silakan input data terlebih dahulu untuk melihat hasil forecast.")
