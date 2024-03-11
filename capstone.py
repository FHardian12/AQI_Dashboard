import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# from numerize import numerize
st.set_page_config(
    page_title = 'Dashboard '
    ,layout='wide'
)

# Definisikan nama file CSV
nama_file = 'Database_Capstone.csv'

# Membaca file CSV ke dalam sebuah DataFrame
df = pd.read_csv(nama_file)

# st.write(df)
# st.dataframe(df.describe())

df['Tanggal'] = pd.to_datetime(df['Tanggal'])

df['tgl_day'] = df['Tanggal'].dt.date

curr_day = max(df['Tanggal'].dt.date)
prev_day = curr_day - pd.Timedelta(days=1)

# Judul sidebar
st.sidebar.title("Menu")

# Pilihan menu dalam bentuk select box
selected_option = st.sidebar.selectbox(
    "Pilih Menu",
    ["Beranda", "Analisis Kualitas Udara"]
)

# Membuat dua kolom di sidebar
col1, col2 = st.sidebar.columns([0.2, 2])

# Menambahkan foto di kolom pertama
col1.image('email.jpg', width=20)

# Menambahkan teks email di kolom kedua
col2.markdown("hardianferri@gmail.com")

# Konten untuk setiap pilihan menu
if selected_option == "Beranda":
    st.write(f"<h1 style='text-align: center;'>Dashboard Harian AQI Indonesia Pada {curr_day.strftime('%d-%m-%Y')}</h1>", unsafe_allow_html=True)

    data = pd.pivot_table(
        data=df,
        index='tgl_day',
        aggfunc={
            'AQI':'mean',
            'PM2.5':'mean',
            'PM10':'mean',
            'Temp':'mean',
            'Humid' :'mean'
        }
    ).reset_index()
    # st.write(data)

    # helper function

    # def format_big_number(num):
    #     if num >= 1e6:    
    #         return f"{num / 1e6:.2f} Mio"
    #     elif num >= 1e3:
    #         return f"{num / 1e3:.2f} K"
    #     else:
    #         return f"{num:.2f}"

    mx_aqi, mx_status = st.columns(2)
    with mx_aqi:
        curr_aqi = data.loc[data['tgl_day']==curr_day, 'AQI'].values[0]
        prev_aqi = data.loc[data['tgl_day']==prev_day, 'AQI'].values[0]
        aqi_diff_pct = 100.0 * (curr_aqi - prev_aqi) / prev_aqi
        st.metric("Indeks Kualitas Udara (AQI)", value=f"{curr_aqi:.0f}", delta=f'{aqi_diff_pct:.0f}%')

    with mx_status:
        curr_aqi = data.loc[data['tgl_day']==curr_day, 'AQI'].values[0]
        if curr_aqi>= 0 and curr_aqi< 51:
            status = "GOOD"
            color = "green"
        elif curr_aqi>= 51 and curr_aqi< 101:
            status = "MODERATE"
            color = "yellow"
        elif curr_aqi>= 101 and curr_aqi< 151:
            status = "POOR"
            color = "orange"
        elif curr_aqi>= 151 and curr_aqi< 201:
            status = "UNHEALTHY"
            color = "red"
        else: 
            status = "VERY UNHEALTHY"
            color = "darkred"
    
        html_str = f"<div>Status Kualitas Udara:<br><span style='color: {color}; font-size: 30px;'><b>{status}</b></span></div>"
        st.markdown(html_str, unsafe_allow_html=True)

    mx_PM25, mx_PM10, mx_temp, mx_humid = st.columns(4)

    with mx_PM25:
        curr_pm25 = data.loc[data['tgl_day']==curr_day, 'PM2.5'].values[0]
        prev_pm25 = data.loc[data['tgl_day']==prev_day, 'PM2.5'].values[0]
        pm25_diff_pct = 100.0 * (curr_pm25 - prev_pm25) / prev_pm25
        st.metric("Tingkat PM2.5", value=f"{curr_pm25:.2f} \u03bcg/m³", delta=f'{pm25_diff_pct:.2f}%')

    with mx_PM10:
        curr_pm10 = data.loc[data['tgl_day']==curr_day, 'PM10'].values[0]
        prev_pm10 = data.loc[data['tgl_day']==prev_day, 'PM10'].values[0]
        pm10_diff_pct = 100.0 * (curr_pm10 - prev_pm10) / prev_pm10
        st.metric("Tingkat PM10", value=f"{curr_pm10:.2f} \u03bcg/m³", delta=f'{pm10_diff_pct:.2f}%')

    with mx_temp:
        curr_temp = data.loc[data['tgl_day']==curr_day, 'Temp'].values[0]
        prev_temp = data.loc[data['tgl_day']==prev_day, 'Temp'].values[0]
        temp_diff_pct = curr_temp - prev_temp
        st.metric("Suhu", value=f"{curr_temp:.0f}\u00b0C", delta=f'{temp_diff_pct:.2f}%')

    with mx_humid:
        curr_humid = data.loc[data['tgl_day']==curr_day, 'Humid'].values[0]
        prev_humid = data.loc[data['tgl_day']==prev_day, 'Humid'].values[0]
        humid_diff_pct = 100.0 * (curr_humid - prev_humid) / prev_humid
        st.metric("Kelembaban", value=f"{curr_humid:.2f}", delta=f'{humid_diff_pct:.2f}%')

    mx_kotor, mx_bersih = st.columns(2)
    with mx_kotor:
        # Filter data by maximum date
        curr_day = max(df['Tanggal'].dt.date)
        df_selected_date = df[df['tgl_day'] == curr_day]

        # Sort by AQI in descending order and get top 5 provinces
        top_5_kotor = df_selected_date.sort_values(by='AQI', ascending=False).head(5)

        # Plot top 5 provinces
        bars = alt.Chart(top_5_kotor).mark_bar(color='orange').encode(
            x=alt.X('AQI:Q', title='Tingkat AQI', axis=None),
            y=alt.Y('Provinsi:N', title='Provinsi', sort='-x')
        ).properties(
            width=400,
            height=400,
            title=f'Top 5 Provinsi Terkotor By AQI'
        )
        # Menampilkan label nilai AQI di dalam bar
        text = alt.Chart(top_5_kotor).mark_text(
            align='center',
            baseline='middle',
            dx=-20,  # Menyesuaikan posisi teks di dalam bar
            fontWeight='bold',
            color='white'  # Mengatur warna teks menjadi hitam
        ).encode(
            x=alt.X('AQI:Q', stack='zero'),
            y=alt.Y('Provinsi:N', sort='-x'),
            text=alt.Text('AQI:Q', format='.0f')  # Menampilkan nilai AQI di dalam bar dengan format dua desimal
        )

        # Menggabungkan kedua chart
        chart = bars + text

        # Menampilkan chart
        st.altair_chart(chart, use_container_width=True)

    with mx_bersih:
        # Filter data by maximum date
        curr_day = max(df['Tanggal'].dt.date)
        df_selected_date = df[df['tgl_day'] == curr_day]

        # Sort by AQI in descending order and get top 5 provinces
        top_5_bersih = df_selected_date.sort_values(by='AQI', ascending=True).head(5)

        # Plot top 5 provinces
        bars = alt.Chart(top_5_bersih).mark_bar(color='green').encode(
            x=alt.X('AQI:Q', title='Tingkat AQI', axis=None),  # Menghilangkan label sumbu x
            y=alt.Y('Provinsi:N', title='Provinsi', sort=alt.EncodingSortField(field="AQI", order='ascending'))
        ).properties(
            width=400,
            height=400,
            title=f'Top 5 Provinsi Terbersih By AQI'
        )

        # Menampilkan label nilai AQI di dalam bar
        text = alt.Chart(top_5_bersih).mark_text(
            align='center',
            baseline='middle',
            dx=-20,  # Menyesuaikan posisi teks di dalam bar
            fontWeight='bold',
            color='white'  # Mengatur warna teks menjadi hitam
        ).encode(
            x=alt.X('AQI:Q', stack='zero'),
            y=alt.Y('Provinsi:N', sort='-x'),
            text=alt.Text('AQI:Q', format='.0f')  # Menampilkan nilai AQI di dalam bar dengan format dua desimal
        )

        # Menggabungkan kedua chart
        chart = bars + text

        # Menampilkan chart
        st.altair_chart(chart, use_container_width=True)

    mx_pie, mx_prov = st.columns(2)

    with mx_pie:
        curr_day = max(df['Tanggal'].dt.date)
        df_selected_date = df[df['tgl_day'] == curr_day]
        # Hitung jumlah status
        status_count = df_selected_date['Status'].value_counts().reset_index()
        status_count.columns = ['Status', 'Count']
        # Definisikan skala warna sesuai dengan kategori status
        color_scale = alt.Scale(
            domain=['GOOD', 'MODERATE', 'POOR', 'UNHEALTHY', 'VERY UNHEALTHY'],
            range=['green', 'yellow', 'orange', 'red', 'darkred']
        )
        #Buat diagram lingkaran menggunakan Altair
        pie_chart = alt.Chart(status_count).mark_arc().encode(
            theta='Count:Q',
            color=alt.Color('Status:N', scale=color_scale),
            tooltip=['Status', 'Count']
        ).properties(
            width=600,
            height=400,
            title=f'Persentase Status Kualitas Udara Per Provinsi'
        )
        # Tampilkan chart dengan data label
        st.altair_chart(pie_chart, use_container_width=True)
    
    with mx_prov:
        curr_day = max(df['Tanggal'].dt.date)
        df_selected_date = df[df['tgl_day'] == curr_day]

        # Filter data by status
        status = st.selectbox('Pilih Status', df['Status'].unique())

        # Filter data by selected status
        df_status = df[df['Status'] == status]

        # Define color scale
        color_scale = alt.Scale(
            domain=['GOOD', 'MODERATE', 'POOR', 'UNHEALTHY', 'VERY UNHEALTHY'],
            range=['green', 'yellow', 'orange', 'red', 'darkred']
        )

        # Filter data by selected status and date
        df_filtered = df[(df['Status'] == status) & (df['tgl_day'] == curr_day)]

        if not df_filtered.empty:
            # Define color for bars and text
            bar_color = 'steelblue'
            text_color = 'white'
            # Plot bar chart
            bar_chart = alt.Chart(df_filtered).mark_bar().encode(
                x=alt.X('Provinsi:N', title='Provinsi', sort='-y'),
                color=alt.Color('Status:N', scale=color_scale),
                y=alt.Y('AQI:Q', title='AQI', axis= None),
                tooltip=['Provinsi', 'AQI']
            ).properties(
                width=600,
                height=400,
                title=f'Nilai AQI Berdasarkan Provinsi untuk Status {status}'
            )

            # Add data labels
            text = bar_chart.mark_text(
                align='center',
                baseline='middle',
                dy=-5,  # Adjust label position
                color=text_color,
                fontWeight='bold'
            ).encode(
                text='AQI:Q'
            )

            # Combine chart and data labels
            chart_with_labels = (bar_chart + text)

            # Remove gridlines
            chart_with_labels = chart_with_labels.configure_axis(grid=False)

            # Show chart
            st.altair_chart(chart_with_labels, use_container_width=True)
        else:
            st.write("Tidak ada data untuk status dan tanggal yang dipilih.")

    # Membuat teks untuk mengenai sumber data
    sumber = """
    Sumber Data: [Indonesia Indeks Kualitas Udara (AQI)](https://www.aqi.in/id/dashboard/indonesia)
    """
    st.markdown(sumber)

    # Membuat teks untuk menjelaskan mengenai status kualitas udara dengan penyesuaian warna dan menggunakan tabel HTML untuk sejajarkan titik dua
    keterangan_status = """
    <style>
    .good {color: green;}
    .moderate {color: yellow;}
    .poor {color: orange;}
    .unhealthy {color: red;}
    .very-unhealthy {color: darkred;}
    table {width: 100%;}
    td {vertical-align: top;}
    </style>

    ## Keterangan Status Kualitas Udara:

    <table>
    <tr>
        <td><span class="good">GOOD</span></td>
        <td>: Kualitas udara baik dan tidak berbahaya bagi kesehatan.</td>
    </tr>
    <tr>
        <td><span class="moderate">MODERATE</span></td>
        <td>: Kualitas udara masih dapat ditoleransi, tetapi beberapa individu mungkin mengalami efek sementara.</td>
    </tr>
    <tr>
        <td><span class="poor">POOR</span></td>
        <td>: Kualitas udara buruk dan dapat menyebabkan masalah kesehatan bagi beberapa individu yang rentan.</td>
    </tr>
    <tr>
        <td><span class="unhealthy">UNHEALTHY</span></td>
        <td>: Kualitas udara sangat buruk dan dapat mempengaruhi kesehatan secara umum.</td>
    </tr>
    <tr>
        <td><span class="very-unhealthy">VERY UNHEALTHY</span></td>
        <td>: Kualitas udara sangat buruk dan dapat menyebabkan masalah kesehatan serius pada banyak orang.</td>
    </tr>
    </table>

    Sumber: [EPA Air Quality Index (AQI)](https://www.airnow.gov/aqi/aqi-basics/)
    """

    # Menampilkan teks dalam bentuk markdown dengan parameter unsafe_allow_html=True
    st.markdown(keterangan_status, unsafe_allow_html=True)

elif selected_option == "Analisis Kualitas Udara":
    st.write("<h1 style='text-align: center;'>Indeks Kualitas Udara Indonesia: Seberapa Buruk Kah?</h1>", unsafe_allow_html=True)
    narasi_satu = """
    <p style='text-align: justify; text-indent: 50px;'>Indonesia, dengan kekayaan alamnya yang melimpah, menjadi rumah bagi lebih dari 270 juta jiwa yang tersebar di berbagai wilayah geografis yang unik. Namun, bersamaan dengan pertumbuhan ekonomi yang pesat dan urbanisasi yang meningkat, tantangan lingkungan, terutama terkait kualitas udara, semakin menjadi fokus perhatian.
    Kualitas udara yang buruk telah menjadi masalah serius di banyak kota besar Indonesia. Tingginya tingkat polusi udara, terutama disebabkan oleh emisi kendaraan bermotor, industri, pembakaran biomassa, serta faktor-faktor alami seperti erupsi vulkanik, membawa konsekuensi serius terhadap kesehatan masyarakat dan kelestarian lingkungan.
    Indeks Kualitas Udara (Air Quality Index/AQI) menjadi alat penting untuk mengukur tingkat polusi udara dan dampaknya terhadap kesehatan manusia. Dengan menggabungkan data dari berbagai parameter polusi udara seperti PM2.5, PM10, suhu, dan kelembaban, AQI memberikan gambaran yang jelas tentang tingkat risiko yang dihadapi oleh penduduk dalam menghirup udara yang tercemar.
    Namun, dalam konteks Indonesia yang luas dan beragam, tantangan dalam pengumpulan data, pemantauan, dan analisis kualitas udara menjadi kompleks. Berbagai faktor seperti infrastruktur yang terbatas, sumber daya yang terbatas, dan keragaman geografis memperumit upaya untuk mendapatkan pemahaman yang holistik tentang kondisi udara di seluruh negeri.</p>
    """
    st.markdown(narasi_satu, unsafe_allow_html=True)
    
    st.subheader('Indeks Kualitas Udara Indonesia')
    col1, col2, col3 = st.columns([1, 1, 1])
    # Menampilkan gambar bendera Indonesia dengan ukuran yang lebih kecil
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Indonesia.svg/255px-Flag_of_Indonesia.svg.png", 
            caption='INDONESIA', 
            width=100)  # Menentukan lebar gambar
    
    # Menampilkan metrik Rata-Rata AQI di kolom kedua
    with col2:
        rata_aqi = df['AQI'].mean()
        st.metric("Rata-Rata AQI", value=f"{rata_aqi:.0f}", delta=None)

    # Menampilkan status Kualitas Udara di kolom ketiga
    with col3:
        # Menentukan status berdasarkan rata-rata AQI
        if rata_aqi >= 0 and rata_aqi < 51:
            status = "GOOD"
            color = "green"
        elif rata_aqi >= 51 and rata_aqi < 101:
            status = "MODERATE"
            color = "yellow"
        elif rata_aqi >= 101 and rata_aqi < 151:
            status = "POOR"
            color = "orange"
        elif rata_aqi >= 151 and rata_aqi < 201:
            status = "UNHEALTHY"
            color = "red"
        else: 
            status = "VERY UNHEALTHY"
            color = "darkred"
    
        # Menampilkan status dengan format HTML
        html_str = f"<div style='text-align: justify;'>Status Kualitas Udara:<br><span style='color: {color}; font-size: 30px;'><b>{status}</b></span></div>"
        st.markdown(html_str, unsafe_allow_html=True)
    narasi_dua = f"""
    <p style='text-align: justify; text-indent: 50px;'>Rata-rata AQI Indonesia berada diangka {rata_aqi:.0f} yang termasuk dalam status {status} menurut standar kualitas udara.
    Ini menunjukkan bahwa kualitas udara berada dalam rentang yang dapat diterima, tetapi masih memiliki potensi untuk memengaruhi kesehatan individu yang sensitif terhadap polusi udara.
    Meskipus berstatus {status} mungkin tidak mengancam kesehatan bagi sebagian besar populasi, akan tetapi kewaspadaan tetap diperlukan. Individu yang memiliki sensitivitas terhadap polusi udara seperti penderita penyakit paru-paru atau jantung, anak-anak, dan orang tua mungkin perlu memperhatikan tingkat polusi udara ini.
    Rata-rata AQI yang berstatus {status} dapat menyebabkan efek sementara pada kesehatan bagi individu yang sensitif, seperti iritasi mata dan saluran pernapasan, serta peningkatan risiko penyakit pernapasan. Ini menyoroti pentingnya pengawasan dan tindakan pencegahan terhadap efek kesehatan yang berkaitan dengan polusi udara.
    Meskipun kualitas udara berada dalam status {status}, aktivitas luar ruangan masih dapat dilakukan dengan aman. Namun, individu dapat mempertimbangkan untuk membatasi waktu di luar ruangan atau menghindari aktivitas yang berat jika mereka merasa terganggu oleh polusi udara.</p>
    """
    st.markdown(narasi_dua, unsafe_allow_html=True)
    
    st.subheader('Trend Rata Rata AQI Indonesia')
    lca1, lca2, lca3 = st.columns([1, 2, 1])
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])

    with lca2:
        df['tgl_day'] = df['Tanggal'].dt.date
        data = pd.pivot_table(
            data=df,
            index='tgl_day',
            aggfunc={
                'AQI':'mean',
                'PM2.5':'mean',
                'PM10':'mean',
                'Temp':'mean',
                'Humid' :'mean'
            }
        ).reset_index()
        # Hitung rata-rata kualitas udara per hari
        avg_aqi_per_day = df.groupby('tgl_day')['AQI'].mean().reset_index()

        # Buat line chart menggunakan Altair dengan tanggal di sumbu-x
        line_chart = alt.Chart(avg_aqi_per_day).mark_line(color='lightblue').encode(
            x=alt.X('tgl_day:T', axis=alt.Axis(title='Tanggal', format='%d-%m-%Y', labelAngle=90)),  # Tambahkan labelAngle=0
            y=alt.Y('AQI:Q', axis=alt.Axis(title='Rata-rata AQI', grid=False)),  # Sumbu-y untuk AQI
        ).properties(
            width=800,
            height=400
        )

        # Tambahkan bullet (titik) untuk setiap titik pada line plot
        points = line_chart.mark_point(color='lightblue', size=100).encode(  # Besarkan ukuran bullet menjadi 100
            tooltip=['tgl_day', alt.Tooltip('AQI:Q', format='.2f')]  # Tambahkan format nilai AQI menjadi dua angka dibelakang koma
        )

        # Menambahkan layer teks di atas titik bullet
        text = line_chart.mark_text(
            align='center',
            baseline='bottom',
            dx=7,  # Mengatur posisi horizontal teks di atas titik
            dy=-10,  # Mengatur posisi vertikal teks di atas titik
            color='yellow',  # Mengatur warna teks menjadi biru
            fontWeight='bold'  # Mengatur teks menjadi bold
        ).encode(
            text=alt.Text('AQI:Q', format='.2f')  # Menampilkan nilai PM10 di atas titik
        )


        # Menggabungkan line chart dengan bullet pointsnya dan teks di atas titik
        chart_with_points_and_text = (line_chart + points + text)

        # Menampilkan line chart dengan bullet points dan teks di atas titik menggunakan Streamlit
        st.write(chart_with_points_and_text)
        # Optionally, you can show the raw data as well
        # if st.checkbox('Tampilkan Data',key='checkbox1'):
        #     st.write(avg_aqi_per_day)
    
    narasi_tiga = """
    <p style='text-align: justify; text-indent: 50px;'>Fluktuasi yang terjadi secara periodik dapat mengindikasikan adanya pola musiman dalam kualitas udara. Misalnya, polusi udara mungkin cenderung meningkat selama musim kemarau, musim dingin, atau ketika aktivitas pembakaran atau polusi udara lainnya meningkat.
    Perubahan cuaca seperti angin kencang, hujan, atau kelembaban udara dapat memengaruhi dispersi polutan dalam udara. Fluktuasi yang terjadi secara tiba-tiba atau tidak terduga mungkin disebabkan oleh perubahan cuaca yang ekstrem.
    Aktivitas manusia seperti industri, transportasi, dan pembakaran sampah dapat menjadi penyebab fluktuasi dalam kualitas udara. Lonjakan polusi udara mungkin terjadi selama jam-jam sibuk atau di daerah dengan aktivitas industri yang intensif.
    Perubahan dalam regulasi atau kebijakan lingkungan juga dapat memengaruhi fluktuasi kualitas udara. Misalnya, penerapan aturan yang lebih ketat terhadap emisi industri atau kendaraan dapat menghasilkan penurunan tajam dalam polusi udara.
    Lonjakan atau penurunan yang signifikan dalam rata-rata AQI dapat disebabkan oleh peristiwa khusus seperti kebakaran hutan, bencana alam, atau kecelakaan industri. Peristiwa-peristiwa ini dapat menyebabkan peningkatan polusi udara yang mendadak dan signifikan.
    Faktor-faktor perubahan struktural seperti pertumbuhan populasi, urbanisasi, atau perubahan dalam struktur ekonomi suatu daerah juga dapat mempengaruhi fluktuasi kualitas udara dalam jangka panjang. Berikut ditampilkan Trend dari faktor-faktor AQI</p>
    """
    st.markdown(narasi_tiga, unsafe_allow_html=True)

    r1, r2, r3 = st.columns([1, 2, 1])
    with r2:
        # Menghitung rata-rata PM10 per hari
        avg_pm10_per_day = df.groupby('tgl_day')['PM10'].mean().reset_index()

        # Membuat line chart menggunakan Altair dengan tanggal pada sumbu-x
        line_chart_pm10 = alt.Chart(avg_pm10_per_day).mark_line(color='lightblue').encode(
            x=alt.X('tgl_day:T', axis=alt.Axis(title='Tanggal', format='%d-%m-%Y', labelAngle=90)),  # Mengubah format tanggal dan labelAngle
            y=alt.Y('PM10:Q', axis=alt.Axis(title='Rata-rata PM10', grid=False)),  # Menghilangkan gridline pada sumbu y
        ).properties(
            width=700,
            height=400
        )

        # Menambahkan bullet points untuk setiap titik pada plot garis
        points_pm10 = line_chart_pm10.mark_point(color='lightblue', size=100).encode(
            tooltip=['tgl_day', alt.Tooltip('PM10:Q', format='.2f')],
        )

        # Menambahkan layer teks di atas titik bullet
        text_pm10 = points_pm10.mark_text(
            align='center',
            baseline='bottom',
            dx=7,  # Mengatur posisi horizontal teks di atas titik
            dy=-10,  # Mengatur posisi vertikal teks di atas titik
            color='yellow',  # Mengatur warna teks menjadi biru
            fontWeight='bold'  # Mengatur teks menjadi bold
        ).encode(
            text=alt.Text('PM10:Q', format='.2f')  # Menampilkan nilai PM10 di atas titik
        )

        # Menggabungkan line chart dengan bullet pointsnya dan teks di atas titik
        chart_with_points_and_text_pm10 = (line_chart_pm10 + points_pm10 + text_pm10)

        # Menampilkan line chart dengan bullet points dan teks di atas titik menggunakan Streamlit
        st.write(chart_with_points_and_text_pm10)
        # if st.checkbox('Tampilkan Data', key='checkbox2'):
        #     st.write(avg_pm10_per_day)

    p1, p2, p3 = st.columns([1, 2, 1])
    with p2:
        # Menghitung rata-rata suhu (Temp) per hari
        avg_temp_per_day = df.groupby('tgl_day')['Temp'].mean().reset_index()

        # Membuat line chart untuk rata-rata suhu (Temp)
        line_chart_temp = alt.Chart(avg_temp_per_day).mark_line(color='lightblue').encode(
            x=alt.X('tgl_day:T', axis=alt.Axis(title='Tanggal', format='%d-%m-%Y', labelAngle=90)),  
            y=alt.Y('Temp:Q', axis=alt.Axis(title='Rata-rata Suhu (Temp)', grid=False)), 
        ).properties(
            width=700,
            height=400
        )

        # Menambahkan bullet points untuk rata-rata suhu (Temp)
        points_temp = line_chart_temp.mark_point(color='lightblue', size=100).encode(
            tooltip=['tgl_day', alt.Tooltip('Temp:Q', format='.2f')],
        )

        # Menambahkan layer teks di atas bullet untuk rata-rata suhu (Temp)
        text_temp = points_temp.mark_text(
            align='center',
            baseline='bottom',
            dx=7,
            dy=-10,
            color='yellow',  # Mengatur warna teks menjadi biru
            fontWeight='bold'  # Mengatur teks menjadi bold
        ).encode(
            text=alt.Text('Temp:Q', format='.2f')
        )

        # Menggabungkan line chart dengan bullet points dan teks di atas bullet
        chart_with_points_and_text_temp = (line_chart_temp + points_temp + text_temp)

        # Menampilkan grafik menggunakan Streamlit
        st.write(chart_with_points_and_text_temp)

        # # Opsional: Menampilkan data jika checkbox dicentang
        # if st.checkbox('Tampilkan Data', key='checkbox4'):
        #     st.write(avg_temp_per_day)
    
    q1, q2, q3 = st.columns([1, 2, 1])
    with q2:
        # Menghitung rata-rata suhu (Temp) per hari
        avg_humid_per_day = df.groupby('tgl_day')['Humid'].mean().reset_index()

        # Membuat line chart untuk rata-rata suhu (Temp)
        line_chart_humid = alt.Chart(avg_humid_per_day).mark_line(color='lightblue').encode(
            x=alt.X('tgl_day:T', axis=alt.Axis(title='Tanggal', format='%d-%m-%Y', labelAngle=90)),  
            y=alt.Y('Humid:Q', axis=alt.Axis(title='Rata-rata Kelembaban', grid=False)), 
        ).properties(
            width=700,
            height=400
        )

        # Menambahkan bullet points untuk rata-rata suhu (Temp)
        points_humid = line_chart_humid.mark_point(color='lightblue', size=100).encode(
            tooltip=['tgl_day', alt.Tooltip('Humid:Q', format='.2f')],
        )

        # Menambahkan layer teks di atas bullet untuk rata-rata suhu (Temp)
        text_humid = points_humid.mark_text(
            align='center',
            baseline='bottom',
            dx=7,
            dy=-10,
            color='yellow',  # Mengatur warna teks menjadi biru
            fontWeight='bold'  # Mengatur teks menjadi bold
        ).encode(
            text=alt.Text('Humid:Q', format='.2f')
        )

        # Menggabungkan line chart dengan bullet points dan teks di atas bullet
        chart_with_points_and_text_humid = (line_chart_humid + points_humid + text_humid)

        # Menampilkan grafik menggunakan Streamlit
        st.write(chart_with_points_and_text_humid)

    st.subheader('Rata Rata Per Provinsi')
    bpa1, bpa2, bpa3 = st.columns([1, 2, 1])

    with bpa2:
        # Menghitung rata-rata AQI per provinsi
        avg_aqi_per_province = df.groupby('Provinsi')['AQI'].mean().reset_index()

        # Menambahkan kolom status dan warna berdasarkan kriteria yang diberikan
        def get_status_color(rata_aqi):
            if rata_aqi >= 0 and rata_aqi < 51:
                return "GOOD", "green"
            elif rata_aqi >= 51 and rata_aqi < 101:
                return "MODERATE", "yellow"
            elif rata_aqi >= 101 and rata_aqi < 151:
                return "POOR", "orange"
            elif rata_aqi >= 151 and rata_aqi < 201:
                return "UNHEALTHY", "red"
            else:
                return "VERY UNHEALTHY", "darkred"

        avg_aqi_per_province['status'], avg_aqi_per_province['color'] = zip(*avg_aqi_per_province['AQI'].map(get_status_color))

        # Membuat bar chart rata-rata AQI per provinsi
        bar_chart_aqi = alt.Chart(avg_aqi_per_province).mark_bar().encode(
            x=alt.X('Provinsi:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('AQI:Q', axis=None),
            color=alt.Color('status:N', scale=alt.Scale(domain=['GOOD', 'MODERATE', 'POOR', 'UNHEALTHY', 'VERY UNHEALTHY'],
                                                    range=['green', 'yellow', 'orange', 'red', 'darkred']),
                            legend=alt.Legend(title="Status AQI")),
            tooltip=['Provinsi', alt.Tooltip('AQI:Q', format=',d'), 'status']
        ).properties(
            width=700,
            height=400,
        )

        # Menambahkan label data di dalam grafik dengan warna putih dan bold
        text = alt.Chart(avg_aqi_per_province).mark_text(
            align='center',
            baseline='middle',
            dx=0,  
            dy=10,
            color='black',
            fontWeight='bold'
        ).encode(
            x=alt.X('Provinsi:N', sort='-y', axis=alt.Axis(labelAngle=-45)),
            y='AQI:Q',
            text=alt.Text('AQI:Q', format='.0f')
        )

        # Menggabungkan grafik batang dengan label data di dalamnya
        chart_with_text = bar_chart_aqi + text

        # Menampilkan grafik menggunakan Streamlit
        st.write(chart_with_text)
    narasi_empat = """
    <p style='text-align: justify; text-indent: 50px;'>Dari 21 provinsi yang diamati, sebanyak 13 provinsi memiliki status kualitas udara "Moderat". Ini menunjukkan bahwa sebagian besar provinsi memiliki kualitas udara yang dapat diterima, meskipun masih memerlukan pemantauan dan kewaspadaan terhadap polusi udara.
    Sebanyak 6 provinsi lainnya memiliki status kualitas udara "Baik". Ini menunjukkan bahwa sebagian besar provinsi memiliki kualitas udara yang baik dan relatif bersih, dengan dampak terhadap kesehatan yang minimal.
    Sebanyak 2 provinsi yang memiliki status kualitas udara "Buruk". Ini mungkin menjadi perhatian khusus karena menunjukkan tingkat polusi udara yang tinggi di provinsi-provinsi tersebut, yang memerlukan tindakan lebih lanjut untuk mengurangi dampaknya terhadap kesehatan masyarakat.
    Dengan memperhatikan distribusi status kualitas udara di antara 22 provinsi yang diamati, kita dapat mengidentifikasi provinsi-provinsi yang memerlukan perhatian khusus dalam upaya menjaga kualitas udara yang sehat dan lingkungan yang bersih. Ini dapat menjadi dasar untuk pengembangan kebijakan dan program perlindungan lingkungan yang lebih efektif di masa depan.</p>
    """
    st.markdown(narasi_empat, unsafe_allow_html=True)
    sumber = """
    Sumber Data: [Indonesia Indeks Kualitas Udara (AQI)](https://www.aqi.in/id/dashboard/indonesia)
    """
    st.markdown(sumber)
