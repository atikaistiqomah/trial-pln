import streamlit as st
import sqlite3
from contextlib import closing
from db_set import save_user_data_to_db, get_db_connection, get_indicators_by_form_id, get_filter_options, get_form_id_by_filter, get_user_data

# ============================================== #

# Perhitungan dan akses form user
def user_input_form():
    username = st.session_state['user']
    user_input = {}
    total_score = 0

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
                        sub_scores.append(realisasi / pemetaan if pemetaan != 0 else 0)
                        user_input[indicator['name']][sub['name']] = sub_scores

                    average_sub_score = sum(sub_scores) / len(sub_scores) if sub_scores else 0
                    final_score = average_sub_score * indicator['weight']
                    total_score += final_score
                    user_input[indicator['name']]['final_score'] = final_score
                    st.write(f"Skor Akhir Indikator {indicator['name']}: {final_score:.4f}")
                else:
                    realisasi = st.number_input(f"Realisasi untuk {indicator['name']} (Target: {indicator['target_value']})", 
                                                min_value=0.0, step=1.0, 
                                                key=f"user_score_{indicator['name']}")
                    pemetaan = st.number_input(f"Terpetakan untuk {indicator['name']}", 
                                                min_value=0.0, step=1.0, 
                                                key=f"user_map_{indicator['name']}")
                    final_score = (realisasi / pemetaan if pemetaan != 0 else 0) * indicator['weight']
                    total_score += final_score
                    user_input[indicator['name']] = final_score
                    st.write(f"Skor Akhir Indikator {indicator['name']}: {final_score:.4f}")
            except ZeroDivisionError as e:
                st.error(f"Error occurred: {e}")
                
        if st.button("Simpan Data User"):
            if total_score > 0:
                save_user_data_to_db(
                    st.session_state['year'], 
                    st.session_state['semester'], 
                    username, 
                    user_input, 
                    st.session_state['form_id'], 
                    st.session_state['form_name'],
                    total_score, 
                    False
                )
                st.success("Data berhasil disimpan.")
            else:
                st.warning("Total bobot indikator adalah 0. Data tidak dapat disimpan.")
                
    except ZeroDivisionError as e:
        st.error(f"Error occurred: {e}")

# Tampilan form untuk diisi
def user_interface():
    st.title("Pilih Form untuk Diisi")

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

# Menampilkan seluruh data input user
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
        df = pd.DataFrame(userdata)
        st.dataframe(df)
    else:
        st.write("User belum mengisi form")

# Mengambil data user masing-masing yang telah divalidasi
def user_valid():
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
        df = pd.DataFrame(validated_data)
        st.dataframe(df)
    else:
        st.write("Belum ada data yang divalidasi oleh admin.")

# Grafik User
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
        df = pd.DataFrame(validated_data)
        st.dataframe(df)
    else:
        st.write("Belum ada data yang divalidasi oleh admin.")
