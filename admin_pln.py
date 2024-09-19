import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from db_set import  save_indicator_to_db, save_form_to_db, get_latest_form_id, get_latest_form_name, update_user_validation_status_in_db, delete_form_indi, is_form_exist, get_filter_options, get_form_id_by_filter, get_indicators_by_form_id, register_user, get_all_user, change_password, delete_akun, get_filtered_user_data_admin
# , get_indicators_from_db, get_user_data, 

# ============================================== #

# TRIAL FORM BUILDER, FUNGSINYA TERPISAH DARI FUNGSI DI ATAS ATAS
# Fungsi untuk menambahkan indikator atau subindikator

# def clear_form():
#     st.session_state['username'] = ""
#     st.session_state['name'] = ""
#     st.session_state['email'] = ""
#     st.session_state['password'] = ""

# Fungsi untuk menampilkan form registrasi user
def admin_register_user():
    st.header("Registrasi User Baru")

    username = st.text_input("Username", key="username")
    name = st.text_input("Nama", key="name")
    email = st.text_input("Email", key="email")
    jenis_unit = st.selectbox("Jenis Unit", ["Kantor Pusat", "SH/AP", "Holding"])
    password = st.text_input("Password", type="password", key="password")
    role = st.selectbox("Role", ["user"])

    if st.button("Register User"):
        if username and name and jenis_unit and email and password:
            register_user(username, name, jenis_unit, email, password, role)
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
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        with col1:
            st.write(f"{user['Name']}")
        with col2:
            st.write(f"{user['Jenis Unit']}")
        with col3:
            st.write(f"{user['Email']}")
        with col4:
            confirm_delete = st.checkbox(f" ", key=f"confirm_delete_{user['Username']}")
        with col5:
            if st.button('Delete', disabled=not confirm_delete, key=f"delete_{user['Username']}"):
                delete_akun(user['Username'])
                st.rerun()

# INDICATOR CONFIG
def indicator_form(indicator_index):
    # Menampilkan form indikator
    indicator_name = st.text_input(f"Nama Indikator {indicator_index+1}", key=f"indicator_name_{indicator_index}")
    weight = st.number_input(f"Bobot Indikator {indicator_index+1}", min_value=0.0, max_value=1.0, step=0.01, key=f"indicator_weight_{indicator_index}")
    target_value = st.number_input(f"Nilai Target Indikator {indicator_index+1}", min_value=0.0, step=1.0, key=f"indicator_target_{indicator_index}")

    subindicators = []
    add_sub = st.checkbox(f"Tambah Subindikator untuk Indikator {indicator_index+1}", key=f"add_sub_{indicator_index}")
    subindicator_count = st.session_state.get(f"subindicator_count_{indicator_index}", 0)

    if add_sub:
        if st.button(f"Tambah Subindikator Baru untuk Indikator {indicator_index+1}", key=f"add_sub_button_{indicator_index}"):
            subindicator_count += 1
            st.session_state[f"subindicator_count_{indicator_index}"] = subindicator_count

        # Menampilkan dan mengelola subindikator
        for i in range(subindicator_count):
            col1, col2 = st.columns([4, 1])
            with col1:
                sub_name = st.text_input(f"Nama Subindikator {i+1} untuk Indikator {indicator_index+1}", key=f"sub_name_{indicator_index}_{i}")
                sub_target = st.number_input(f"Nilai Target Subindikator {i+1} untuk Indikator {indicator_index+1}", min_value=0.0, step=1.0, key=f"sub_target_{indicator_index}_{i}")
                subindicators.append({
                    'name': sub_name,
                    'target_value': sub_target
                })
            with col2:
                if st.button(f"Hapus Subindikator {i+1}", key=f"remove_sub_{indicator_index}_{i}"):
                    # Menghapus subindikator dari session state
                    del st.session_state[f"sub_name_{indicator_index}_{i}"]
                    del st.session_state[f"sub_target_{indicator_index}_{i}"]
                    st.session_state[f"subindicator_count_{indicator_index}"] -= 1
                    break

    # Simpan input indikator sementara ke session_state
    st.session_state[f'indicator_{indicator_index}'] = {
        'name': indicator_name,
        'weight': weight,
        'target_value': target_value,
        'subindicators': subindicators
    }

# menampilkan dan menyimpan form yang dibuat
def admin_interface():
    st.title("Admin Form Builder")
    
    year = st.number_input("Tahun", min_value=2020, step=1)
    semester = st.selectbox("Semester", [1, 2])
    form_name = st.text_input("Jenis Form")

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
                if f"subindicator_count_{i}" in st.session_state:
                    del st.session_state[f"subindicator_count_{i}"]
                st.session_state['indicator_count'] -= 1
                break

    # Tombol untuk menambah indikator baru
    if st.button("Tambah Indikator Baru"):
        st.session_state['indicator_count'] += 1

    # Tombol untuk menyimpan semua indikator
    if st.button("Simpan Semua Indikator"):
        if year and semester and form_name:
            if not is_form_exist(year, semester, form_name):
                save_form_to_db(year, semester, form_name)
                form_id = get_latest_form_id()
                form_name = get_latest_form_name()
                
                # Loop melalui semua indikator yang telah diinput
                for i in range(st.session_state['indicator_count']):
                    indicator_data = st.session_state.get(f'indicator_{i}', {})
                    if indicator_data:  # Jika ada data indikator
                        save_indicator_to_db(
                            indicator_data['name'],
                            indicator_data['weight'],
                            indicator_data['target_value'],
                            indicator_data['subindicators'],
                            form_id,
                            form_name
                        )
                st.success("Semua indikator berhasil disimpan!")
            else:
                st.warning("Form dengan tahun, semester, dan nama yang sama sudah ada")
                
            # Reset form setelah menyimpan
        for key in list(st.session_state.keys()):
            if key.startswith('indicator_') or key.startswith('sub_name_') or key.startswith('sub_target_'):
                del st.session_state[key]

def verif_user():
    
    
    
    # Menampilkan data user yang telah diisi
    user_data = st.session_state.get('users_data', [])
    if user_data:
        st.write("### Data User yang Dimasukkan:")
        
        # Looping untuk tiap baris data user
        for idx, data in enumerate(user_data):
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])  # Membuat kolom

            # Kolom pertama untuk informasi User ID
            with col1:
                st.write(f"User: {data['User']}")
                st.write(f"Tahun: {data['Year']}")
                st.write(f"Semester: {data['Semester']}")
                st.write(f"Form: {data['Form Name']}")
                st.write(f" ")

            # Kolom kedua untuk informasi detail user
            with col2:
                st.dataframe(data['Input'])
                st.write(f"Nilai: {data['Nilai']}")

            # Kolom ketiga untuk checkbox validasi
            with col3:
                verified = st.checkbox("Valid", value=data['verified'], key=f"verified_{idx}")

            # Kolom keempat untuk tombol simpan hasil validasi
            with col4:
                if st.button("Simpan", key=f"simpan_{idx}"):
                    # Update status validasi di database
                    update_user_validation_status_in_db(data['id'], verified)

                    # Update session state setelah validasi
                    st.session_state['users_data'][idx]['verified'] = verified
                    st.success(f"Status validasi untuk {data['User']} berhasil diperbarui.")

    else:
        st.write("Belum ada data user yang diinputkan.")
# ================================

# def verif_user():
#     # Menampilkan data user yang telah diisi
#     user_data = st.session_state.get('users_data', [])
#     if user_data:
#         # Memastikan status validasi dan update
#         for idx, data in enumerate(user_data):
#             st.write(f"Data User {idx+1}:")
#             st.dataframe(data['Input'])
            
#             verified = st.checkbox("Tandai sebagai valid", value=data['verified'], key=f"verify_{idx}")
#             if st.button(f"Simpan Status Validasi untuk Data User {idx+1}"):
#                 update_user_validation_status_in_db(data['id'], verified)
#                 st.session_state['users_data'][idx]['verified'] = verified  # Update session state setelah validasi
#                 st.success(f"Status validasi untuk Data User {idx+1} telah diperbarui.")
#     else:
#         st.write("Belum ada data user yang diinputkan.")

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
        st.write("Belum ada data form yang dibuat.")
        
# detail form
def detail_form():
    user_input = {}
    total_score = 0

# Iterasi indikator yang ada di session state
    for indicator in st.session_state['indicators']:
        st.subheader(indicator['name'])
        user_input[indicator['name']] = {}
        if indicator['subindicators']:
            sub_scores = []
            for sub in indicator['subindicators']:
                realisasi = st.number_input(f"Realisasi untuk {sub['name']} (Target: {sub['target_value']})", value=1.0, disabled=True)
                pemetaan = st.number_input(f"Terpetakan untuk {sub['name']}", value=1.0, disabled=True)
                sub_scores.append(realisasi/pemetaan)

            average_sub_score = sum(sub_scores) / len(sub_scores) if sub_scores else 0
            final_score = average_sub_score * indicator['weight']
            total_score += final_score
            # total_weight += indicator['weight']
            st.write(f"Skor Akhir Indikator {indicator['name']}: {final_score:.4f}")
        else:
            realisasi = st.number_input(f"Realisasi untuk {indicator['name']} (Target: {indicator['target_value']})", value=1.0, disabled=True)
            pemetaan = st.number_input(f"Terpetakan untuk {indicator['name']}", value=1.0, disabled=True)
            final_score = (realisasi/pemetaan) * indicator['weight']
            total_score += final_score
            # total_weight += indicator['weight']
            st.write(f"Skor Akhir Indikator {indicator['name']}: {final_score:.4f}")  
                
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

def validasi_form():
    # Menampilkan data user yang telah diisi
    user_data = st.session_state.get('users_data', [])
    if user_data:
        st.write("### Data User yang Dimasukkan:")
        
        data_for_table = [
            {
                "Nama User": data['User'],
                "Form Name": data['Form Name'],
                "Total Score": data['Nilai'],
                "Year": data['Year'],
                "Semester" : data['Semester'],
                "Status": "Sudah Valid" if data['verified'] else "Belum Valid"
            }
            for data in user_data
        ]
        
        st.table(data_for_table)
    else:
        st.write("Belum ada data user yang diinputkan.")


def show_admin_graph():
    st.title("Grafik Capaian User")

    # Ambil filter tahun, semester, dan form name
    filter_options = get_filter_options()
    
    selected_year = st.selectbox("Pilih Tahun", filter_options['years'])
    selected_semester = st.selectbox("Pilih Semester", filter_options['semesters'])
    selected_form_name = st.selectbox("Pilih Nama Form", filter_options['form_names'])
    validation_status = st.radio(
        "Tampilkan Status Validasi", 
        ['Semua', 'Sudah Divalidasi', 'Belum Divalidasi'], 
        index=0
    )

    # Dapatkan data yang difilter sesuai input admin
    filtered_data = get_filtered_user_data_admin(selected_year, selected_semester, selected_form_name, validation_status)

    # Tampilkan grafik jika data tersedia
    if not filtered_data.empty:
        st.write(filtered_data)

        # Misalnya gunakan matplotlib untuk menampilkan grafik
        fig, ax = plt.subplots()
        ax.barh(filtered_data['username'], filtered_data['value'])
        ax.set_xlabel('User')
        ax.set_ylabel('Nilai')
        ax.set_title(f'Grafik Capaian {selected_form_name} Tahun {selected_year} Semester {selected_semester}')
        st.pyplot(fig)
    else:
        st.warning("Belum ada data yang tersedia untuk filter yang dipilih.")
