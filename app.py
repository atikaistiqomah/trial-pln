import streamlit as st
from auth import login, logout
# from main_program.user_pln import fill_form_structure
# from main_program.admin_pln import create_form_structure
from db_set import get_user_data, create_tables, get_indicators_from_db, add_admin_user, get_forms_from_db
from admin_pln import admin_interface, verif_user, validasi_form, grafik_admin
from user_pln import user_interface, user_valid, grafik_user, form_filled

# set layout web
st.set_page_config(page_title="PLN HCR",
                   layout="wide",
                   page_icon="Logo-PLN.png",
                   initial_sidebar_state="auto")

# logo
LOGO_PLN = "images (1).png"
st.logo(
    LOGO_PLN,
    icon_image=LOGO_PLN,
)

st.html("""
  <style>
    [alt=Logo] {
      height: 3rem;
    }
  </style>
""")

# atur judul homepage
st.title(":bulb: Pelaporan PLN HCR-OCR")

# Membuat tabel jika belum ada
create_tables()

# ============================================== #

# EDIT DAN SESUAIKAN LAGI

# Inisialisasi session state untuk form dan indikator
def session_initiate():
    if 'form_structures' not in st.session_state:
        st.session_state['form_structures'] = get_forms_from_db()
        st.session_state['indicators'] = get_indicators_from_db()

    # Inisialisasi session state untuk user data
    if 'user_data' not in st.session_state:
        st.session_state['users_data'] = get_user_data()

def main():  
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False

    if not st.session_state.is_authenticated:
        login()
        if st.session_state.is_authenticated:
            st.rerun()
        return

    st.sidebar.title("Navigation")
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()

    if st.session_state.is_admin:
        page = st.sidebar.radio("Pilih Halaman Admin", ["Buat Form", "Daftar Form", "Verifikasi Data", "Hasil Validasi", "Grafik Capaian"])
        if page == "Buat Form":
            # create_form_structure()
            admin_interface()
        elif page == "Daftar Form":
            # admin_user_score_matrix()
            st.dataframe(get_forms_from_db()) # sementara
        elif page == "Verifikasi Data":
            session_initiate()
            verif_user()
        elif page == "Hasil Validasi":
            # user_data_list = get_user_data()
            session_initiate()
            validasi_form()
        elif page == "Grafik Capaian":
            grafik_admin()
            
    else:
        page = st.sidebar.radio("Pilih Halaman User", ["Pengisian Form", "Form Terisi", "Hasil Validasi", "Grafik Capaian"])
        if page == "Pengisian Form":
            session_initiate()
            # fill_form_structure()
            if 'form_structures' in st.session_state and st.session_state['indicators']:
                user_interface()
            else:
                st.write("Admin belum menyelesaikan penambahan indikator.")
        elif page == "Form Terisi":
            session_initiate()
            form_filled()
        elif page == "Hasil Validasi":
            # username = st.session_state['user']
            # if username in st.session_state['user_data']:
            #     session_initiate()
            #     st.session_state['user_data']
            session_initiate()
            user_valid()
        elif page == "Grafik Capaian":
            grafik_user()


if __name__ == "__main__":
    add_admin_user()
    main()
