import streamlit as st
from contextlib import closing
import matplotlib.pyplot as plt
from db_set import  save_user_data_to_db, get_indicators_by_form_id, get_filter_options, get_form_id_by_filter, get_user_data, delete_user_input, is_user_data_exist, get_filtered_user_data_user

# ============================================== #

# TRIAL FORM BUILDER, FUNGSINYA TERPISAH DARI FUNGSI DI ATAS ATAS

# perhitungan dan akses form user
def user_input_form(selected_year,selected_semester,selected_form_name):
    # username diambil dari session state
    username = st.session_state['user']
    unit_name = st.session_state['user']['name']
    user_input = {}
    total_real = 0
    sub_score = []

# Iterasi indikator yang ada di session state
    for indicator in st.session_state['indicators']:
        st.subheader(indicator['name'])
        user_input[indicator['name']] = {}
        
        st.number_input(f"Target untuk {indicator['name']}", value=indicator['target_value'], key=f"user_map_{indicator['name']}", disabled=True)
        realisasi = st.number_input(f"Realisasi untuk {indicator['name']}",value=1.0, min_value=0.0, step=1.0, key=f"user_score_{indicator['name']}")

        sub_score.append(realisasi)
        final_score = sum(sub_score)/len(sub_score) if sub_score else 0

        total_real += final_score
        user_input[indicator['name']] = f"{realisasi:.4f}"
                
                
    # Simpan data user ke database jika tombol ditekan
    if st.button("Simpan Data User"):
        if not is_user_data_exist(selected_year,selected_semester,selected_form_name, username['username']):
            if realisasi > 0:
                save_user_data_to_db(
                    st.session_state['year'], 
                    st.session_state['semester'], 
                    username, 
                    unit_name,
                    user_input, 
                    st.session_state['form_id'], 
                    st.session_state['form_name'],  # Pastikan form_name juga disimpan
                    f"{total_real:.4f}", 
                    # False  # Data belum diverifikasi saat disimpan
                )
                st.success("Data berhasil disimpan.")
            else:
                st.warning("Realisasi indikator adalah 0. Data tidak dapat disimpan.")
        else:
            st.warning("Form sudah pernah diisi")

# tampilan form untuk diisi
def user_interface():
    st.title("Pilih Form untuk Diisi")

    # Dapatkan form yang sesuai dengan filter
    filter_options = get_filter_options()
    selected_year = st.selectbox("Pilih Tahun", filter_options['years'])
    selected_semester = st.selectbox("Pilih Semester", filter_options['semesters'])
    selected_form_name = st.selectbox("Pilih Aspek", filter_options['form_names'])
    
    form_id = get_form_id_by_filter(selected_year, selected_semester, selected_form_name)

    if form_id:
        st.session_state['form_id'] = form_id
        st.session_state['year'] = selected_year
        st.session_state['semester'] = selected_semester
        st.session_state['form_name'] = selected_form_name
        st.session_state['indicators'] = get_indicators_by_form_id(form_id)

        st.write(f"Form: {selected_form_name}, Tahun: {selected_year}, Semester: {selected_semester}")
        user_input_form(selected_year,selected_semester,selected_form_name)
        
    else:
        st.warning("Data tidak ditemukan untuk filter yang dipilih.")

# menampilkan seluruh data input user
def form_filled():
    st.write("### Data yang telah diisi:")
    
    user_data = get_user_data(username=st.session_state['user']['username'])
    if not user_data:
        st.write("User belum mengisi form")
    else:
        for data in user_data:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
            with col1:
                st.write(f"Form: {data['Form Name']}")
            with col2:
                st.write(f"Nilai: {data['Nilai']}")
            with col3:
                st.write(f"Semester: {data['Semester']}")
                st.write(f"Year: {data['Year']}")

            with col4:
                confirm_delete = st.checkbox(f" ", key=f"confirm_delete_{data['id']}")
            with col5:
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

    # Dapatkan data user yang difilter
    filtered_data = get_filtered_user_data_user(selected_year, selected_semester, username)

    # Tampilkan grafik jika data tersedia
    if not filtered_data.empty:
        st.table(filtered_data)
        
        fig = px.bar(
            filtered_data,
            x='value',
            y='form_name',
            orientation='h',
            labels={'value': 'Nilai', 'form_name': 'Aspek'},
            title=f'Grafik Capaian {username} Tahun {selected_year} Semester {selected_semester}',
            text='value'  # Menampilkan nilai di atas bar
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
            xaxis_title='Nilai',
            yaxis_title='Aspek',
            font=dict(
                color='black',  # Mengubah font grafik menjadi hitam
                size=12         # Ukuran font (opsional, bisa disesuaikan)
            )
        )

        # Tampilkan grafik di Streamlit
        st.plotly_chart(fig, use_container_width=True)
        
        
    else:
        st.warning("Belum ada data yang tersedia untuk filter yang dipilih.")
