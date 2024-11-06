import streamlit as st
import seaborn as sns
import pandas as pd
import json
import plotly.express as px
import matplotlib.pyplot as plt
from db_set import  save_indicator_to_db, save_form_to_db, get_latest_form_id, get_latest_form_name, delete_form_indi, is_form_exist, get_filter_options, get_form_id_by_filter, get_indicators_by_form_id, register_user, get_all_user, change_password, delete_akun, get_filtered_user_data_admin, get_filter_options_rekap, get_user_data_by_filter
# , get_indicators_from_db, get_user_data, 

# ============================================== #

# Fungsi untuk menampilkan form registrasi user
def admin_register_user():
    st.header("Registrasi User Baru")

    username = st.text_input("Username", key="username")
    name = st.text_input("Nama", key="name")
    jenis_unit = st.selectbox("Jenis Unit", ["Kantor Pusat", "SH/AP", "Holding"])
    password = st.text_input("Password", type="password", key="password")
    role = st.selectbox("Role", ["user"])

    if st.button("Register User"):
        if username and name and jenis_unit and password:
            register_user(username, name, jenis_unit, password, role)
            # clear_form()  # Kosongkan form setelah sukses
        else:
            st.error("Semua field harus diisi!")
            
def admin_change_password():
    st.header("Ubah Password User")
    
    # Memilih user yang akan diubah passwordnya
    users = get_all_user()  # Fungsi untuk mengambil semua user dari database
    selected_user = st.selectbox("Pilih User", [user['Username'] for user in users])
    
    new_password = st.text_input(f"Password Baru untuk {selected_user}", type="password")
    
    if st.button("Change Password"):
        if new_password:
            change_password(selected_user, new_password)
        else:
            st.error("Password baru harus diisi!")
            
def display_user():
    # users = st.session_state.get('form_structures', [])
    users = get_all_user()
    for user in users:
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.write(f"{user['Name']}")
        with col2:
            st.write(f"{user['Jenis Unit']}")
        with col3:
            confirm_delete = st.checkbox(f" ", key=f"confirm_delete_{user['Username']}")
        with col4:
            if st.button('Delete', disabled=not confirm_delete, key=f"delete_{user['Username']}"):
                delete_akun(user['Username'])
                st.rerun()

# INDICATOR CONFIG
def indicator_form(indicator_index):
    # Menampilkan form indikator
    indicator_name = st.selectbox(f"Nama Indikator {indicator_index+1}", ["Leading 1", "Leading 2", "Leading 3", "Leading 4", "Leading 5", "Lagging Output 1", "Lagging Output 2", "Lagging Output 3", "Lagging Output 4", "Lagging Output 5", "Lagging Outcome 2", "Lagging Outcome 3", "Lagging Outcome 4", "Lagging Outcome 5"])

    target_value = st.number_input(f"Nilai Target Indikator {indicator_index+1}", min_value=0.0, step=1.0, key=f"indicator_target_{indicator_index}")

    # Simpan input indikator sementara ke session_state
    st.session_state[f'indicator_{indicator_index}'] = {
        'name': indicator_name,
        'target_value': target_value,
    }

# menampilkan dan menyimpan form yang dibuat
def admin_interface():
    st.title("Admin Form Builder")
    
    year = st.number_input("Tahun", min_value=2020, step=1)
    semester = st.selectbox("Semester", [1, 2])
    form_name = st.selectbox("Aspek", ["HCR", "OCR L", "OCR A", "OCR C", "OCR BE"])
    form_target = st.number_input("Target Aspek", min_value=0, step=1)

    if 'indicator_count' not in st.session_state:
        st.session_state['indicator_count'] = 1

    indicator_count = st.session_state['indicator_count']

    # Menampilkan setiap indikator
    for i in range(indicator_count):
        st.write(f"### Indikator {i+1}")
        col1, col2 = st.columns([4, 1])
        with col1:
            indicator_form(i)
        with col2:
            if st.button(f"Hapus Indikator {i+1}", key=f"remove_indicator_{i}"):
                # Menghapus indikator dari session state
                del st.session_state[f"indicator_{i}"]
                st.session_state['indicator_count'] -= 1
                break

    # Tombol untuk menambah indikator baru
    if st.button("Tambah Indikator Baru"):
        st.session_state['indicator_count'] += 1

    # Tombol untuk menyimpan semua indikator
    if st.button("Simpan Semua Indikator"):
        if year and semester and form_name:
            if not is_form_exist(year, semester, form_name):
                save_form_to_db(year, semester, form_name, form_target)
                form_id = get_latest_form_id()
                form_name = get_latest_form_name()
                
                # Loop melalui semua indikator yang telah diinput
                for i in range(st.session_state['indicator_count']):
                    indicator_data = st.session_state.get(f'indicator_{i}', {})
                    if indicator_data:  # Jika ada data indikator
                        save_indicator_to_db(
                            indicator_data['name'],
                            indicator_data['target_value'],
                            form_id,
                            form_name
                        )
                st.success("Semua indikator berhasil disimpan!")
            else:
                st.warning("Form dengan tahun, semester, dan nama yang sama sudah ada")
                
            # Reset form setelah menyimpan
        for key in list(st.session_state.keys()):
            if key.startswith('indicator_'):
                del st.session_state[key]

def daftar_form():
    form_data = st.session_state.get('form_structures', [])
    if form_data:
        st.write("### Formulir yang Dibuat:")
        
        # Looping untuk tiap baris data user
        for data in form_data:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])  # Membuat kolom

            # Kolom pertama untuk informasi User ID
            with col1:
                st.write(f"Form: {data['Nama Form']}")

            # Kolom kedua untuk informasi detail user
            with col2:
                st.write(f"Semester: {data['Semester']}")

            # Kolom ketiga untuk checkbox validasi
            with col3:
                st.write(f"Tahun: {data['Tahun']}")

            # Kolom keempat untuk tombol simpan hasil validasi
            with col4:
                confirm_delete = st.checkbox(f"Hapus: {data['Nama Form']}", key=f"confirm_delete_{data['id']}")

            with col5:
                if st.button("Delete", key=f"delete_{data['id']}", disabled=not confirm_delete):
                    delete_form_indi(data['id'])
                    # st.success(f"{data['Nama Form']} berhasil dihapus.")
                    # st.rerun()

    else:
        st.warning("Belum ada data form yang dibuat.")
        
# detail form
def detail_form():
    user_input = {}

# Iterasi indikator yang ada di session state
    for indicator in st.session_state['indicators']:
        st.subheader(indicator['name'])
        user_input[indicator['name']] = {}
        
        st.number_input(f"Target untuk {indicator['name']}", value=indicator['target_value'], key=f"user_map_{indicator['name']}", disabled=True)
        realisasi = st.number_input(f"Realisasi untuk {indicator['name']} (Target: {indicator['target_value']})",value=1.0, key=f"user_score_{indicator['name']}", disabled=True)

        user_input[indicator['name']] = f"{realisasi:.4f}" 
                
    # Simpan data user ke database jika tombol ditekan
    if st.button("Simpan Data User", disabled=True):
        st.write("Dummy")

# tampilan form untuk diisi
def detail_view():
    st.title("Detail Form")

    # Dapatkan form yang sesuai dengan filter
    filter_options = get_filter_options()
    selected_year = st.selectbox("Pilih Tahun", filter_options['years'])
    selected_semester = st.selectbox("Pilih Semester", filter_options['semesters'])
    selected_form_name = st.selectbox("Pilih Nama Form", filter_options['form_names'])
    
    form_id = get_form_id_by_filter(selected_year, selected_semester, selected_form_name)

    if form_id:
        st.session_state['form_id'] = form_id
        st.session_state['year'] = selected_year
        st.session_state['semester'] = selected_semester
        st.session_state['form_name'] = selected_form_name
        st.session_state['indicators'] = get_indicators_by_form_id(form_id)

        st.write(f"Form: {selected_form_name}, Tahun: {selected_year}, Semester: {selected_semester}")
        detail_form()

    else:
        st.warning("Belum ada data form yang dibuat.")
    
        
# FILTER PER USER, TAHUN, SEMESTER, FORM
def rekap_target():
    # Mendapatkan opsi filter
    filter_options = get_filter_options_rekap()

    # Create filter inputs
    selected_year = st.selectbox('Pilih Tahun', filter_options['years'])
    selected_semester = st.selectbox('Pilih Semester', filter_options['semesters'])
    selected_form_name = st.selectbox('Pilih Nama Form', filter_options['form_names'])
    selected_unit = st.selectbox('Pilih Nama Unit', filter_options['units'])

    # Display rekap if all filters are selected

    df_rekap = get_user_data_by_filter(selected_year,selected_semester, selected_form_name, selected_unit)
    if not df_rekap.empty:
        st.table(df_rekap)
    else:
        st.write("Tidak ada data yang ditemukan.")


def show_admin_graph():
    # st.title("Grafik Capaian User")

    # Ambil filter tahun, semester, dan form name
    filter_options = get_filter_options()
    
    selected_year = st.selectbox("Pilih Tahun", filter_options['years'])
    selected_semester = st.selectbox("Pilih Semester", filter_options['semesters'])
    selected_form_name = st.selectbox("Pilih Nama Form", filter_options['form_names'])

    # Dapatkan data yang difilter sesuai input admin
    filtered_data = get_filtered_user_data_admin(selected_year, selected_semester, selected_form_name)

    # Tampilkan grafik jika data tersedia
    if not filtered_data.empty:
        st.table(filtered_data)

        # Menggunakan Plotly untuk membuat grafik interaktif
        fig = px.bar(
            filtered_data,
            x='Skor',
            y='Unit',
            orientation='h',
            labels={'Skor': 'Skor', 'Unit': 'Unit'},
            title=f'Grafik Capaian {selected_form_name} Tahun {selected_year} Semester {selected_semester}',
            text='Skor'  # Menampilkan nilai di atas bar
        )

        # Update layout untuk menampilkan nilai saat hover
        fig.update_traces(
            texttemplate='%{text:.2f}',  # Format nilai dengan dua desimal
            textposition='outside',     # Posisi teks di luar bar
            hovertemplate='<b>%{y}</b>: %{x:.2f}'  # Template teks yang muncul saat hover
        )
        fig.update_layout(
            height=500,  # Atur tinggi grafik
            width=1000,  # Atur lebar grafik
            xaxis_title='Skor',
            yaxis_title='Unit',
            font=dict(
                color='black',  # Mengubah font grafik menjadi hitam
                size=12         # Ukuran font (opsional, bisa disesuaikan)
            )
        )

        # Tampilkan grafik di Streamlit
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Belum ada data yang tersedia untuk filter yang dipilih.")
