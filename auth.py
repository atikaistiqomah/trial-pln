import streamlit as st
from db_set import get_user

def authenticate(username, password):
    user = get_user(username)
    if user and user['password'] == password:
        return user
    return None

def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state.user = user
            st.session_state.is_authenticated = True
            st.session_state.is_admin = (user['role'] == 'admin')
            st.sidebar.success("Login successful as {user['username']}")
        else:
            st.sidebar.error("Invalid credentials")

def logout():
    if 'user' in st.session_state:
        del st.session_state['user']
        st.session_state.is_authenticated = False
        st.session_state.is_admin = False
        st.sidebar.success("Logged out")
