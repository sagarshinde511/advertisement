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

# --- Database Functions ---
def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def insert_user(username, password):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Advusers (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        cursor.close()
        conn.close()
        st.sidebar.success("Registration successful! Please login.")
    except mysql.connector.errors.IntegrityError:
        st.sidebar.error("Username already exists.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

def check_credentials(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Advusers WHERE username=%s AND password=%s", (username, password))
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

# --- Sidebar Authentication ---
if not st.session_state["logged_in"]:
    st.sidebar.title("User Access")
    auth_choice = st.sidebar.radio("Choose Action", ["Login", "Register"])

    if auth_choice == "Login":
        username = st.sidebar.text_input("Username", key="login_user")
        password = st.sidebar.text_input("Password", type="password", key="login_pass")
        if st.sidebar.button("Login"):
            if check_credentials(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.sidebar.error("Invalid username or password.")

    elif auth_choice == "Register":
        new_user = st.sidebar.text_input("New Username", key="reg_user")
        new_pass = st.sidebar.text_input("New Password", type="password", key="reg_pass")
        if st.sidebar.button("Register"):
            if new_user and new_pass:
                insert_user(new_user, new_pass)
            else:
                st.sidebar.error("Please fill in all fields.")

# --- Main App After Login ---
else:
    st.title("Advertisement Management Panel")
    st.sidebar.write(f"Welcome, **{st.session_state['username']}**")
    
    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

    # Tabs: Admin sees extra "Delete" tab
    if st.session_state["username"] == "admin":
        tab1, tab2 = st.tabs(["Upload Advertisement", "Delete Advertisement"])
    else:
        tab1, = st.tabs(["Upload Advertisement"])

    # --- Upload Tab ---
    with tab1:
        st.subheader("Upload Advertisement and Payment Screenshot")
        date_selected = st.date_input("Select Date", date.today())
        uploaded_ad_file = st.file_uploader("Upload an Image or Video", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])
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

    # --- Admin Delete Tab ---
    if st.session_state["username"] == "admin":
        with tab2:
            st.subheader("Delete Advertisement Entry")
            ads = get_all_ads()
            if ads:
                ad_options = {f"ID: {ad[0]} | Date: {ad[1]}": ad[0] for ad in ads}
                selected_ad = st.selectbox("Select Advertisement to Delete", list(ad_options.keys()))
                if st.button("Delete Selected"):
                    ad_id = ad_options[selected_ad]
                    delete_advertisement(ad_id)
            else:
                st.info("No advertisements found.")
