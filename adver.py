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

def insert_data(upload_date, image_data):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
        INSERT INTO advertisement (date, img) VALUES (%s, %s)
        """
        cursor.execute(query, (upload_date, image_data))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Data successfully inserted into the database!")
    except Exception as e:
        st.error(f"Error inserting data: {e}")

st.title("Upload Image with Date")

# Select Date
date_selected = st.date_input("Select Date", date.today())

# Upload Image
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read image and convert to base64
    image_bytes = uploaded_file.read()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    if st.button("Upload to Database"):
        insert_data(date_selected, image_base64)
