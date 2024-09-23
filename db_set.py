import streamlit as st
import sqlite3
from contextlib import closing
import json
import pandas as pd

def get_db_connection():
    conn = sqlite3.connect('db/new_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with closing(get_db_connection()) as conn:
        with conn:
            # Buat tabel untuk users (fix)
            conn.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT NOT NULL PRIMARY KEY,
                name TEXT,
                jenis_unit TEXT,
                password TEXT,
                role TEXT,
                UNIQUE (username)
            )''')
            
            conn.execute('''CREATE TABLE IF NOT EXISTS form_structure (
                form_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                year INT NOT NULL,
                semester INT NOT NULL,
                form_name TEXT,
                form_target REAL,
                UNIQUE (year, semester, form_name)
            )''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS indicators
                (
                    indicator_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    target_value REAL,
                    form_id INTEGER,
                    form_name TEXT,
                    UNIQUE (indicator_id, form_id, form_name),
                    FOREIGN KEY (form_id) REFERENCES form_structure (form_id),
                    FOREIGN KEY (form_name) REFERENCES form_structure (form_name)
                )
            ''')
            
            conn.execute('''CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                semester INTEGER NOT NULL,
                username TEXT,
                name TEXT,
                user_input TEXT,
                form_id INTEGER,
                form_name TEXT,
                value REAL,
                UNIQUE (id, year, semester, username, form_id, form_name),
                FOREIGN KEY (username) REFERENCES users (username),
                FOREIGN KEY (name) REFERENCES users (name),
                FOREIGN KEY (form_id) REFERENCES form_structure (form_id),
                FOREIGN KEY (year) REFERENCES form_structure (year),
                FOREIGN KEY (semester) REFERENCES form_structure (semester),
                FOREIGN KEY (form_name) REFERENCES form_structure (form_name)
            )''') 

# USER AND ACCOUNT CONFIG
def add_admin_user():
    try:
        with closing(get_db_connection()) as conn:
            with conn:
                conn.execute("INSERT OR IGNORE INTO users (username, name, jenis_unit, password, role) VALUES (?, ?, ?, ?, ?)", ('admin', 'admin pln', 'Kantor Pusat', 'adminpassword', 'admin'))

    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
        
def register_user(username, name, jenis_unit, password, role):
    with closing(get_db_connection()) as conn:
        with conn:
            try:
                conn.execute(
                    "INSERT INTO users (username, name, jenis_unit, password, role) VALUES (?, ?, ?, ?, ?)", 
                    (username, name, jenis_unit, password, role)
                )
                st.success(f"User {username} berhasil didaftarkan!")
            except sqlite3.IntegrityError:
                st.error("Username sudah ada!")
                
def change_password(username, new_password):
    with closing(get_db_connection()) as conn:
        with conn:
            conn.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
            st.success(f"Password untuk {username} berhasil diubah!")


# get usera account for users config
def get_all_user():
    with closing(get_db_connection()) as conn:
        with conn:
            rows = conn.execute('SELECT * FROM users').fetchall()
            users = []
            for row in rows:
                user = {
                    'Username': row['username'],
                    'Name': row['name'],
                    'Jenis Unit': row['jenis_unit'],
                    'Pass': row['password'],
                    'Role': row['role']
                }
                users.append(user)
    return users

# get user for login and logout authentication
def get_user(username):
    with closing(get_db_connection()) as conn:
        with conn:
            return conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
# cek form exist
def is_form_exist(year, semester, form_name):
    with get_db_connection() as conn:
        query = """
        SELECT COUNT(*) FROM form_structure 
        WHERE year = ? AND semester = ? AND form_name = ?
        """
        result = conn.execute(query, (year, semester, form_name)).fetchone()
    return result[0] > 0  # Return True if form exists

# save form to database
def save_form_to_db(year, semester, form_name, form_target):
    # if form_exists(year, semester, form_name):
    #     return False  # Indikasi bahwa form sudah ada
    with closing(get_db_connection()) as conn:
        with conn:
            conn.execute('''INSERT INTO form_structure(year, semester, form_name, form_target)
                        VALUES (?, ?, ?, ?)''', (year,semester, form_name, form_target))
                
#  save indicator to db
def save_indicator_to_db(indicator_name, target_value,form_id, form_name):
    try:
        with closing(get_db_connection()) as conn:
            with conn:
                # Mengonversi list subindikator ke format JSON
                conn.execute('''INSERT INTO indicators (name, target_value, form_id, form_name)
                            VALUES (?, ?, ?, ?)''', (indicator_name, target_value, form_id, form_name))
        
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")

def is_user_data_exist(year, semester, form_name, username):
    with get_db_connection() as conn:
        query = """
        SELECT COUNT(*) FROM user_data 
        WHERE year = ? AND semester = ? AND form_name = ? AND username = ?"""
        result = conn.execute(query, (year, semester, form_name, username)).fetchone()
    return result[0] > 0  # Return True if form exists

# simpan data inputan user ke database
def save_user_data_to_db(year, semester, username, name, user_input, form_id, form_name, value):
    with closing(get_db_connection()) as conn:
        with conn:
            username = st.session_state['user']['username']
              
            user_input_json = json.dumps(user_input)  # Mengonversi dictionary user_input ke format JSON
            print("User Input JSON:", user_input_json)
            conn.execute('''INSERT INTO user_data (year, semester, username, name, user_input, form_id, form_name, value)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (year, semester, username, name, user_input_json, form_id, form_name, value))
    
# get latest form id
def get_latest_form_id():
    with closing(get_db_connection()) as conn:
        with conn:
            result = conn.execute('SELECT MAX(form_id) FROM form_structure').fetchone()
            return result[0] if result else None

def get_latest_form_name():
    with closing(get_db_connection()) as conn:
        with conn:
            # Mengambil nama form yang paling terakhir dibuat berdasarkan form_id terbaru
            query = '''
                SELECT form_name
                FROM form_structure
                ORDER BY form_id DESC
                LIMIT 1
            '''
            result = conn.execute(query).fetchone()
            return result[0] if result else None


def get_forms():
    with closing(get_db_connection()) as conn:
        with conn:
            rows = conn.execute('SELECT * FROM form_structure').fetchall()
            forms = []
            for row in rows:
                form = {
                    'id': row['form_id'],
                    'Nama Form': row['form_name'],
                    'Semester': row['semester'],
                    'Tahun': row['year'],
                    'Target Aspek' :row['form_target']
                }
                forms.append(form)
    return forms

# get form that has been made
def get_indicators_from_db():
    with closing(get_db_connection()) as conn:
        with conn:
            rows = conn.execute('SELECT * FROM indicators').fetchall()
            indicators = []
            for row in rows:
                indicator = {
                    'name': row['name'],
                    'target_value': row['target_value'],
                    'form_id': row['form_id'],
                    'form_name': row['form_name']
                }
                indicators.append(indicator)
    return indicators

# get indicators for user
def get_indicators_by_form_id(form_id):
    with closing(get_db_connection()) as conn:
        with conn:
            rows = conn.execute('''SELECT name, target_value
                                   FROM indicators
                                   WHERE form_id = ?''', (form_id,)).fetchall()

            indicators = []
            for row in rows:
                indicator = {
                    'name': row['name'],
                    'target_value': row['target_value']
                }
                indicators.append(indicator)

    return indicators
  
# get user_data yang sudah divalidasi
def get_user_data(username=None):
    with closing(get_db_connection()) as conn:
        with conn:
            if username:
                rows = conn.execute('SELECT * FROM user_data WHERE username = ?', (username,)).fetchall()
            else:
                rows = conn.execute('SELECT * FROM user_data').fetchall()
            user_data = []
            for row in rows:
                data = {
                    'id' : row['id'],
                    'User': row['username'],  # Tambahkan ID ke data yang diambil,
                    'Name': row['name'],
                    'Input': json.loads(row['user_input']),  # Mengonversi format JSON ke dictionary,
                    'Year': row['year'],
                    'Semester': row['semester'],
                    'Form Name' : row['form_name'],
                    'Nilai' : row['value']
                }
                user_data.append(data)
    return user_data
        
# filter tampilkan form berdasarkan tahun, semester, dan nama form   
def get_filter_options():
    with closing(get_db_connection()) as conn:
        with conn:
            years = conn.execute('SELECT DISTINCT year FROM form_structure').fetchall()
            semesters = conn.execute('SELECT DISTINCT semester FROM form_structure').fetchall()
            form_names = conn.execute('SELECT DISTINCT form_name FROM form_structure').fetchall()
            
    return {
        'years': [year['year'] for year in years],
        'semesters': [semester['semester'] for semester in semesters],
        'form_names': [form_name['form_name'] for form_name in form_names]
    }

def get_filter_options_rekap():
    with closing(get_db_connection()) as conn:
        with conn:
            # Fetch distinct data for filtering
            units = conn.execute('SELECT DISTINCT name FROM user_data').fetchall()
            years = conn.execute('SELECT DISTINCT year FROM user_data').fetchall()
            semesters = conn.execute('SELECT DISTINCT semester FROM user_data').fetchall()
            form_names = conn.execute('SELECT DISTINCT form_name FROM user_data').fetchall()

    return {
        'units': [unit['name'] for unit in units],
        'years': [year['year'] for year in years],
        'semesters': [semester['semester'] for semester in semesters],
        'form_names': [form_name['form_name'] for form_name in form_names]
    }
    

def get_user_data_by_filter(year, semester, form_name, username):
    with closing(get_db_connection()) as conn:
        with conn:
            # Query to fetch user data based on filters
            query = '''
                SELECT ud.name AS unit_name, ud.form_name, ud.user_input, ud.year, ud.semester
                FROM user_data ud
                WHERE ud.year = ? 
                AND ud.semester = ? 
                AND ud.form_name = ? 
                AND ud.name = ?
            '''
            params = (year, semester, form_name, username)
            results = conn.execute(query, params).fetchall()

            if not results:
                st.warning("Data tidak ditemukan untuk filter yang dipilih.")
                return pd.DataFrame()

            # List to store data for display
            rekap_data = []

            for row in results:
                # Convert user input JSON string to dictionary
                user_input = json.loads(row['user_input'])

                # Get target indicators associated with the form
                indicators = conn.execute('''
                    SELECT name, target_value 
                    FROM indicators 
                    WHERE form_name = ?
                ''', (form_name,)).fetchall()

                # Calculate percentage achievements based on target and user input values
                for indicator in indicators:
                    indikator_name = indicator['name']
                    target_value = float(indicator['target_value'])

                    # Fetch the corresponding user value from user input dictionary
                    user_value = float(user_input.get(indikator_name, 0))

                    # Calculate percentage if target is not zero
                    percentage = (user_value / target_value) * 100 if target_value else 0

                    # Append the calculated data to the rekap_data list
                    rekap_data.append({
                        'Nama Form': row['form_name'],
                        'Nama Unit': row['unit_name'],
                        'Tahun': row['year'],
                        'Semester': row['semester'],
                        'Indikator': indikator_name,
                        'Nilai': user_value,
                        'Target': target_value,
                        'Persentase': f"{percentage:.2f}%"
                    })

    # Convert rekap_data to DataFrame for display
    return pd.DataFrame(rekap_data)


# Fungsi untuk mendapatkan data user terfilter (untuk user sendiri)
def get_filtered_user_data_user(year, semester, form_name):
    with closing(get_db_connection()) as conn:
        with conn:
            # Base query untuk pengambilan data user sesuai filter tahun, semester, nama form dan username
            query = '''
                SELECT name, form_name, value
                FROM user_data 
                WHERE year = ? 
                AND semester = ?
                AND username = ?
            '''
            params = [year, semester, form_name]

            try:
                # Eksekusi query dan ambil hasil
                result = conn.execute(query, params).fetchall()

                # Jika tidak ada hasil, kembalikan DataFrame kosong
                if not result:
                    return pd.DataFrame(columns=['name', 'form_name', 'value'])

                # Konversi hasil query ke dalam DataFrame
                data = pd.DataFrame(result, columns=['name', 'form_name', 'value'])

                return data

            except Exception as e:
                # Tangani error saat query gagal
                st.error(f"Terjadi kesalahan saat mengambil data: {e}")
                return pd.DataFrame(columns=['name', 'form_name', 'value'])

# Fungsi untuk mendapatkan data user terfilter (untuk admin)
def get_filtered_user_data_admin(year, semester, form_name):
    with closing(get_db_connection()) as conn:
        with conn:
            # Base query untuk pengambilan data user sesuai filter tahun, semester, dan nama form
            query = '''
                SELECT name, value 
                FROM user_data 
                WHERE year = ? 
                AND semester = ? 
                AND form_name = ?
            '''
            params = [year, semester, form_name]

            try:
                # Eksekusi query dan ambil hasil
                result = conn.execute(query, params).fetchall()

                # Jika tidak ada hasil, kembalikan DataFrame kosong
                if not result:
                    return pd.DataFrame(columns=['name', 'value'])

                # Konversi hasil query ke dalam DataFrame
                data = pd.DataFrame(result, columns=['name', 'value'])

                return data

            except Exception as e:
                # Tangani error saat query gagal
                st.error(f"Terjadi kesalahan saat mengambil data: {e}")
                return pd.DataFrame(columns=['name', 'value'])


# get form by filter
def get_form_id_by_filter(year, semester, form_name):
    with closing(get_db_connection()) as conn:
        with conn:
            result = conn.execute('''SELECT form_id FROM form_structure 
                                     WHERE year = ? AND semester = ? AND form_name = ?''', 
                                  (year, semester, form_name)).fetchone()
            return result['form_id'] if result else None

# def get_user_data_by_filter(year, semester, form_name):
#     with closing(get_db_connection()) as conn:
#         with conn:
#             result = conn.execute('''SELECT id FROM user_data 
#                                      WHERE year = ? AND semester = ? AND form_name = ?''', 
#                                   (year, semester, form_name)).fetchone()
#             return result['id'] if result else None


def delete_form_indi(id):
    with closing(get_db_connection()) as conn:
        with conn:
            conn.execute('DELETE FROM indicators WHERE form_id = ?', (id,))
            conn.execute('DELETE FROM form_structure WHERE form_id = ?', (id,))
            
def delete_user_input(user_id):
    # Fungsi untuk menghapus input user
    with closing(get_db_connection()) as conn:
        with conn:
            conn.execute('DELETE FROM user_data WHERE id = ? AND username = ?', (user_id, st.session_state['user']['username']))
            
def delete_akun(username):
    with closing(get_db_connection()) as conn:
        with conn:
            conn.execute('DELETE FROM users WHERE username = ?', (username,))
            