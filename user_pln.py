import streamlit as st
import sqlite3
from contextlib import closing
from db_set import  save_user_data_to_db,get_db_connection, get_indicators_by_form_id, get_filter_options, get_form_id_by_filter, get_user_data

# ============================================== #

# TRIAL FORM BUILDER, FUNGSINYA TERPISAH DARI FUNGSI DI ATAS ATAS

# perhitungan dan akses form user
def user_input_form():
    # username diambil dari session state
    username = st.session_state['user']
    user_input = {}
    total_score = 0
    # total_weight = 0

# Iterasi indikator yang ada di session state
    try:
        for indicator in st.session_state['indicators']:
            st.subheader(indicator['name'])
            user_input[indicator['name']] = {}
            try:
                if indicator['subindicators']:
                    sub_scores = []
                    for sub in indicator['subindicators']:
                        realisasi = st.number_input(f"Realisasi untuk {sub['name']} (Target: {sub['target_value']})", 
                                                min_value=0.0, step=1.0, 
                                                key=f"user_score_{indicator['name']}_{sub['name']}")
                        pemetaan = st.number_input(f"Terpetakan untuk {sub['name']}", 
                                    min_value=0.0, step=1.0, 
                                    key=f"user_map_{indicator['name']}_{sub['name']}")
                        sub_scores.append(realisasi/pemetaan)
                        user_input[indicator['name']][sub['name']] = sub_scores

                    average_sub_score = sum(sub_scores) / len(sub_scores) if sub_scores else 0
                    final_score = average_sub_score * indicator['weight']
                    total_score += final_score
                    # total_weight += indicator['weight']
                    user_input[indicator['name']]['final_score'] = final_score
                    st.write(f"Skor Akhir Indikator {indicator['name']}: {final_score:.4f}")
                else:
                    realisasi = st.number_input(f"Realisasi untuk {indicator['name']} (Target: {indicator['target_value']})", 
                                            min_value=0.0, step=1.0, 
                                            key=f"user_score_{indicator['name']}")
                    pemetaan = st.number_input(f"Terpetakan untuk {indicator['name']}", 
                                            min_value=0.0, step=1.0, 
                                            key=f"user_map_{indicator['name']}")
                    final_score = (realisasi/pemetaan) * indicator['weight']
                    total_score += final_score
                    # total_weight += indicator['weight']
                    user_input[indicator['name']] = final_score
                    st.write(f"Skor Akhir Indikator {indicator['name']}: {final_score:.4f}")
            except ZeroDivisionError as e:
                print(f"Error occurred: {e}")    
                
        # Simpan data user ke database jika tombol ditekan
        if st.button("Simpan Data User"):
            if total_score > 0:
                save_user_data_to_db(
                    st.session_state['year'], 
                    st.session_state['semester'], 
                    username, 
                    user_input, 
                    st.session_state['form_id'], 
                    st.session_state['form_name'],  # Pastikan form_name juga disimpan
                    total_score, 
                    False  # Data belum diverifikasi saat disimpan
                )
                st.success("Data berhasil disimpan.")
            else:
                st.warning("Total bobot indikator adalah 0. Data tidak dapat disimpan.")
                
    except ZeroDivisionError as e:
        print(f"Error occurred: {e}")

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
        user_input_form()

# menampilkan seluruh data input user
def form_filled():
    st.write("### Data Anda yang Telah Divalidasi:")
    username = st.session_state['user']['username']
    userdata = [
        {
            "Form Name": data['Form Name'],
            "Year": data['Year'],
            "Semester": data['Semester'],
            "Nilai": data['Nilai'],
            "Status": "Sudah Valid" if data['verified'] else "Belum Valid"
        }
        for data in get_user_data(username)
    ]

    if userdata:
        st.data_editor(userdata)
    else:
        st.write("User belum mengisi form")

# mengambil data user masing-masing yang telah divalidasi
def user_valid():
    st.write("### Data Anda yang Telah Divalidasi:")
    username = st.session_state['user']['username']
    validated_data = [
        {
            # "Indikator": key,
            "Year": data['Year'],
            "Semester": data['Semester'],
            "Form Name": data['Form Name'],
            "Skor Akhir": data['Input']['final_score']
        }
        for data in get_user_data(username)
        # if data['verified'] for key in data['Input']
        # if 'final_score' in data['Input'][key]
    ]

    if validated_data:
        st.dataframe(validated_data)
    else:
        st.write("Belum ada data yang divalidasi oleh admin.")
        
# def user_valid():
#     st.write("### Hasil Validasi Formulir Anda:")
#     username = st.session_state['user']['username']  # Mengambil username dari session state
#     user_data = get_user_data(username)  # Mendapatkan data user dari database
    
#     # Filter data yang sudah diverifikasi oleh admin
#     verified_data = [data for data in user_data if data['verified']]
    
#     if verified_data:
#         # Menampilkan hasil per formulir dengan total skor
#         for form in verified_data:
#             st.write(f"**Formulir:** {st.session_state['form_name']}")
#             st.write(f"Tahun: {st.session_state['year']}, Semester: {st.session_state['semester']}")
#             st.write(f"**Nilai Akhir (Total):** {form['total_score']:.2f}")
#             with st.expander("Lihat detail"):
#                 st.json(form['Input'])  # Menampilkan detail input dari user dalam format JSON
#     else:
#         st.write("Belum ada formulir yang divalidasi oleh admin.")

def grafik_user():
    st.write("### Data Anda yang Telah Divalidasi:")
    username = st.session_state['user']['username']
    validated_data = [
        {
            "Indikator": key,
            "Year": data['Year'],
            "Semester": data['Semester'],
            "Form Name": data['Form Name'],
            "Skor Akhir": data['Input'][key]['final_score']
        }
        for data in get_user_data(username)
        if data['verified'] for key in data['Input']
        if 'final_score' in data['Input'][key]
    ]

    if validated_data:
        st.dataframe(validated_data)
    else:
        st.write("Belum ada data yang divalidasi oleh admin.")
