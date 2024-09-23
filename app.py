import streamlit as st
from streamlit_option_menu import option_menu
from set_app.auth import login, logout
# from main_program.user_pln import fill_form_structure
# from main_program.admin_pln import create_form_structure
from set_app.db_set import get_user_data, create_tables, get_indicators_from_db, add_admin_user, get_forms
from main_program.admin_pln import admin_interface, show_admin_graph, daftar_form, detail_view, admin_register_user, admin_change_password, display_user, rekap_target
from main_program.user_pln import user_interface, show_user_graph, form_filled
# verif_user, validasi_form,

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
        st.session_state['form_structures'] = get_forms()
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
        page = st.sidebar.selectbox("Pilih Halaman Admin", ["Buat Form", "Daftar Form", "Detail Form", "Rekap Target", "Grafik Capaian", "Daftarkan Unit", "Ubah Password Akun"])
        if page == "Buat Form":
            # create_form_structure()
            admin_interface()
        elif page == "Daftar Form":
            # admin_user_score_matrix()
            session_initiate()
            daftar_form()
        elif page == "Detail Form":
            # fill_form_structure()
            # if 'form_structures' in st.session_state and st.session_state['indicators']:
            
            detail_view()
            # else:
            #     st.write("Admin belum menyelesaikan penambahan indikator.")

        elif page == "Rekap Target":
            # user_data_list = get_user_data()
            session_initiate()
            rekap_target()
        elif page == "Grafik Capaian":
            show_admin_graph()
        elif page == "Daftarkan Unit":
            if st.session_state['user']['role'] == 'admin':
                admin_register_user()
                
        elif page == "Ubah Password Akun":
            if st.session_state['user']['role'] == 'admin':
                display_user()
                admin_change_password()
                
            
    else:
        page = st.sidebar.selectbox("Pilih Halaman User", ["Pengisian Form", "Form Terisi", "Grafik Capaian"])
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
        elif page == "Grafik Capaian":
            show_user_graph()


if __name__ == "__main__":
    add_admin_user()
    main()
