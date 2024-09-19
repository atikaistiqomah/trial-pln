import streamlit as st
from contextlib import closing
import matplotlib.pyplot as plt
from set_app.db_set import  save_user_data_to_db,get_db_connection, get_indicators_by_form_id, get_filter_options, get_form_id_by_filter, get_user_data, delete_user_input, is_user_data_exist, get_filtered_user_data_user

# ============================================== #

# TRIAL FORM BUILDER, FUNGSINYA TERPISAH DARI FUNGSI DI ATAS ATAS

# perhitungan dan akses form user
def user_input_form(selected_year,selected_semester,selected_form_name):
    # username diambil dari session state
    username = st.session_state['user']
    unit_name = st.session_state['user']['name']
    user_input = {}
    total_score = 0
    # total_weight = 0

# Iterasi indikator yang ada di session state
    for indicator in st.session_state['indicators']:
        st.subheader(indicator['name'])
        user_input[indicator['name']] = {}
        if indicator['subindicators']:
            sub_scores = []
            for sub in indicator['subindicators']:
                realisasi = st.number_input(f"Realisasi untuk {sub['name']} (Target: {sub['target_value']})", value=1.0, min_value=0.0, step=1.0, 
                        key=f"user_score_{indicator['name']}_{sub['name']}")
                pemetaan = st.number_input(f"Terpetakan untuk {sub['name']}", value=1.0, min_value=0.0,
                        step=1.0, 
                        key=f"user_map_{indicator['name']}_{sub['name']}")
                sub_scores.append(realisasi/pemetaan)
                user_input[indicator['name']][sub['name']] = f"{realisasi/pemetaan:.4f}"

            average_sub_score = sum(sub_scores) / len(sub_scores) if sub_scores else 0
            final_score = average_sub_score * indicator['weight']
            total_score += final_score
            # SESUAIKAN LAGI HITUNGANNYA, DAN PIKIRKAN CARA MENYIMPAN YANG TEPAT
            # total_weight += indicator['weight']
            user_input[indicator['name']]['final_score'] = f"{final_score:.4f}"
            st.write(f"Skor Akhir Indikator {indicator['name']}: {final_score:.4f}")
        else:
            realisasi = st.number_input(f"Realisasi untuk {indicator['name']} (Target: {indicator['target_value']})", value=1.0, min_value=0.0, step=1.0, key=f"user_score_{indicator['name']}")
            pemetaan = st.number_input(f"Terpetakan untuk {indicator['name']}", value=1.0, min_value=0.0, step=1.0, key=f"user_map_{indicator['name']}")
            final_score = (realisasi/pemetaan) * indicator['weight']
            total_score += final_score
            # total_weight += indicator['weight']
            user_input[indicator['name']] = f"{final_score:.4f}"
            st.write(f"Skor Akhir Indikator {indicator['name']}: {final_score:.4f}")  
                
    # Simpan data user ke database jika tombol ditekan
    if st.button("Simpan Data User"):
        if not is_user_data_exist(selected_year,selected_semester,selected_form_name, username['username']):
            if total_score > 0:
                save_user_data_to_db(
                    st.session_state['year'], 
                    st.session_state['semester'], 
                    username, 
                    unit_name,
                    user_input, 
                    st.session_state['form_id'], 
                    st.session_state['form_name'],  # Pastikan form_name juga disimpan
                    f"{total_score:.4f}", 
                    False  # Data belum diverifikasi saat disimpan
                )
                st.success("Data berhasil disimpan.")
            else:
                st.warning("Total bobot indikator adalah 0. Data tidak dapat disimpan.")
        else:
            st.warning("Form sudah pernah diisi")

# tampilan form untuk diisi
def user_interface():
    st.title("Pilih Form untuk Diisi")

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
        user_input_form(selected_year,selected_semester,selected_form_name)

# menampilkan seluruh data input user
def form_filled():
    st.write("### Data yang telah diisi:")
    
    user_data = get_user_data(username=st.session_state['user']['username'])
    if not user_data:
        st.write("User belum mengisi form")
    else:
        for data in user_data:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 1, 1])
            with col1:
                st.write(f"Form: {data['Form Name']}")
            with col2:
                st.write(f"Nilai: {data['Nilai']}")
            with col3:
                st.write(f"Semester: {data['Semester']}")
                st.write(f"Year: {data['Year']}")
            with col4:
                if data['verified']:
                    st.write("Status : Sudah Valid")
                else:
                    st.write("Status : Belum Valid")
            with col5:
                confirm_delete = st.checkbox(f" ", key=f"confirm_delete_{data['id']}")
            with col6:
                if st.button('Delete', disabled=not confirm_delete, key=f"delete_{data['id']}"):
                    delete_user_input(data['id'])
                    st.rerun()

        
def show_user_graph():
    st.title("Grafik Capaian Anda")

    # Ambil username dari session state
    username = st.session_state['user']['username']

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

    # Dapatkan data user yang difilter
    filtered_data = get_filtered_user_data_user(selected_year, selected_semester, selected_form_name, validation_status, username)

    # Tampilkan grafik jika data tersedia
    if not filtered_data.empty:
        st.write(filtered_data)

        # Misalnya gunakan matplotlib untuk menampilkan grafik
        fig, ax = plt.subplots()
        ax.barh(filtered_data['name'], filtered_data['value'])
        ax.set_xlabel('Indikator')
        ax.set_ylabel('Nilai')
        ax.set_title(f'Grafik Capaian {selected_form_name} Tahun {selected_year} Semester {selected_semester}')
        st.pyplot(fig)
    else:
        st.warning("Belum ada data yang tersedia untuk filter yang dipilih.")