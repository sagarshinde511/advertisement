import streamlit as st
import mysql.connector
from datetime import date
import base64

# --- Database Configuration ---
DB_CONFIG = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

# --- Database Utilities ---
def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def insert_user(username, password):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Registration successful! Please login.")
    except mysql.connector.errors.IntegrityError:
        st.error("Username already exists.")
    except Exception as e:
        st.error(f"Error: {e}")

def check_credentials(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user is not None

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

def get_all_ads():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, date FROM advertisement ORDER BY id DESC")
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records
    except Exception as e:
        st.error(f"Error fetching records: {e}")
        return []

def delete_advertisement(ad_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM advertisement WHERE id = %s", (ad_id,))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Advertisement deleted successfully.")
    except Exception as e:
        st.error(f"Error deleting record: {e}")

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

# --- Auth Pages ---
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if not st.session_state["logged_in"]:
    if menu == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if check_credentials(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    
    elif menu == "Register":
        st.subheader("Register New Account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            if new_username and new_password:
                insert_user(new_username, new_password)
            else:
                st.error("Please enter both username and password.")

# --- Main App ---
else:
    st.title("Advertisement Management Panel")

    # Tabs: Only show Delete tab if admin
    if st.session_state["username"] == "admin":
        tab1, tab2 = st.tabs(["Upload Advertisement", "Delete Advertisement"])
