import streamlit as st
import mysql.connector
from datetime import date
import base64

# Database Configuration
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def insert_data(upload_date, img_data, payment_data):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "INSERT INTO advertisement (date, img, payment) VALUES (%s, %s, %s)"
        cursor.execute(query, (upload_date, img_data, payment_data))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Files successfully inserted into the database!")
    except Exception as e:
        st.error(f"Error inserting files: {e}")

# Main app logic
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

if not st.session_state["logged_in"]:
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.rerun()
else:
    st.title("Upload Advertisement and Payment Screenshot")
    date_selected = st.date_input("Select Date", date.today())
    
    st.subheader("Upload Advertisement Image/Video")
    uploaded_ad_file = st.file_uploader("Upload an Image or Video", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])
    
    st.subheader("Upload Payment Screenshot")
    payment_screenshot = st.file_uploader("Upload Payment Screenshot", type=["jpg", "jpeg", "png"])
    
    if st.button("Submit"):
        if uploaded_ad_file and payment_screenshot:
            ad_bytes = uploaded_ad_file.read()
            payment_bytes = payment_screenshot.read()
            ad_base64 = base64.b64encode(ad_bytes).decode('utf-8')
            payment_base64 = base64.b64encode(payment_bytes).decode('utf-8')
            insert_data(date_selected, ad_base64, payment_base64)
        else:
            st.error("Please upload both advertisement and payment screenshot")
    
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()
