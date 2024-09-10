import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from set_app.db_set import  save_indicator_to_db, save_form_to_db, get_latest_form_id, get_latest_form_name, update_user_validation_status_in_db
# , get_indicators_from_db, get_user_data, 

# ============================================== #

# TRIAL FORM BUILDER, FUNGSINYA TERPISAH DARI FUNGSI DI ATAS ATAS
# Fungsi untuk menambahkan indikator atau subindikator

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
            # Reset form setelah menyimpan
            for key in list(st.session_state.keys()):
                if key.startswith('indicator_') or key.startswith('sub_name_') or key.startswith('sub_target_'):
                    del st.session_state[key]

# BELUM BERHASIL
# def admin_user_score_matrix():
#     st.title("Matriks Skor User Berdasarkan Indikator")

#     # Ambil seluruh user dan data yang sudah mereka input
#     all_user_data = get_user_data_from_db()  # Mendapatkan seluruh data user dari database
#     all_indicators = get_indicators_from_db()  # Mendapatkan seluruh indikator dari database

#     # Buat header untuk tabel, yaitu seluruh nama indikator
#     indicator_names = [indicator['name'] for indicator in all_indicators]

#     # Buat dictionary untuk menyimpan data skor user
#     user_scores = {}

#     # Loop untuk setiap user
#     for user in all_user_data:
#         if user['verified']:  # Hanya proses data yang sudah divalidasi
#             username = user['username']
#             user_scores[username] = {}
            
#             # Loop untuk setiap indikator
#             for indicator in all_indicators:
#                 indicator_name = indicator['name']
#                 if indicator_name in user['Input']:  # Jika user mengisi indikator ini
#                     user_scores[username][indicator_name] = user['Input'][indicator_name].get('final_score', 0)
#                 else:  # Jika user belum mengisi indikator ini
#                     user_scores[username][indicator_name] = 0
#         else:
#             continue  # Skip user yang belum divalidasi

#     # Tampilkan hasil dalam bentuk matriks
#     if user_scores:
#         import pandas as pd
        
#         # Konversi dictionary ke DataFrame untuk ditampilkan sebagai tabel
#         df = pd.DataFrame(user_scores).T.fillna(0)  # Transpose agar user di baris dan indikator di kolom
#         df = df[indicator_names]  # Pastikan urutan kolom sesuai dengan urutan indikator
        
#         st.write("### Matriks Skor Berdasarkan Indikator")
#         st.dataframe(df)
#     else:
#         st.write("Belum ada user yang datanya divalidasi.")

def verif_user():
        # Menampilkan data user yang telah diisi
    user_data = st.session_state.get('users_data', [])
    if user_data:
        st.write("### Data User yang Dimasukkan:")
        
        # Looping untuk tiap baris data user
        for idx, data in enumerate(user_data):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])  # Membuat kolom

            # Kolom pertama untuk informasi User ID
            with col1:
                st.write(f"User: {data['User']}")
                st.write(f"Form: {data['Form Name']}, Tahun: {data['Year']}, Semester: {data['Semester']}, Nilai: {data['Nilai']}")

            # Kolom kedua untuk informasi detail user
            with col2:
                st.dataframe(data['Input'])

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

def grafik_admin():
    # Ambil data dari session state
    user_data = st.session_state.get('users_data', [])

    # Pastikan data tidak kosong dan dalam bentuk DataFrame
    if user_data:
        # Jika user_data berbentuk list, ubah ke DataFrame
        if isinstance(user_data, list):
            df = pd.DataFrame(user_data, columns=['User', 'Nilai'])
        else:
            df = pd.DataFrame(user_data)
        
        # Buat plot dengan seaborn
        plt.figure(figsize=(10, 6))
        sns.barplot(x='User', y='Nilai', data=df)
        plt.title('Nilai Pengguna')
        plt.xlabel('Pengguna')
        plt.ylabel('Nilai')

        # Tampilkan plot di Streamlit
        st.pyplot(plt)
    else:
        st.write("Belum ada data pengguna untuk ditampilkan.")