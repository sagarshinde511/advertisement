import streamlit as st
import mysql.connector
from datetime import date
import base64
from io import BytesIO

# Database Configuration
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def create_users_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AdveUsers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def register_user(username, password):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "INSERT INTO AdveUsers (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Registration successful! You can now log in.")
    except Exception as e:
        st.error(f"Error registering user: {e}")

def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT * FROM AdveUsers WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def insert_data(upload_date, file_data, file_type):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "INSERT INTO advertisement (date, file_data, file_type) VALUES (%s, %s, %s)"
        cursor.execute(query, (upload_date, file_data, file_type))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("File successfully inserted into the database!")
    except Exception as e:
        st.error(f"Error inserting file: {e}")

# Main app logic
create_users_table()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

if not st.session_state["logged_in"]:
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Register":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type='password')
        if st.button("Register"):
            register_user(new_user, new_pass)
    
    elif choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success(f"Welcome {username}!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Invalid username or password")
else:
    st.title("Upload Files with Date")
    date_selected = st.date_input("Select Date", date.today())
    
    st.subheader("Upload Advertisement Image/Video")
    uploaded_ad_file = st.file_uploader("Upload an Image or Video", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])
    if uploaded_ad_file is not None:
        file_bytes = uploaded_ad_file.read()
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')
        file_type = "video" if uploaded_ad_file.type.startswith("video/") else "image"
        if file_type == "image":
            st.image(uploaded_ad_file, caption="Uploaded Image", use_column_width=True)
        else:
            st.video(uploaded_ad_file)
        if st.button("Upload Advertisement to Database"):
            insert_data(date_selected, file_base64, file_type)
    
    st.subheader("Upload Payment Screenshot")
    payment_screenshot = st.file_uploader("Upload Payment Screenshot", type=["jpg", "jpeg", "png"])
    if payment_screenshot is not None:
        payment_bytes = payment_screenshot.read()
        payment_base64 = base64.b64encode(payment_bytes).decode('utf-8')
        st.image(payment_screenshot, caption="Payment Screenshot", use_column_width=True)
        if st.button("Upload Payment Screenshot to Database"):
            insert_data(date_selected, payment_base64, "payment_screenshot")
    
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.experimental_rerun()
