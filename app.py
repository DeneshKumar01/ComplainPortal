import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

# File to store complaints
FILE_NAME = "complaints.xlsx"

# Ensure the file exists with correct structure
if not os.path.exists(FILE_NAME):
    df = pd.DataFrame(columns=["Complaint_ID", "Complaint_Text", "Status", "Timestamp"])
    df.to_excel(FILE_NAME, index=False)

# Load complaints
def load_complaints():
    return pd.read_excel(FILE_NAME)

# Save complaints
def save_complaints(df):
    df.to_excel(FILE_NAME, index=False)

# Generate complaint ID (YYYYMMDD + 4-digit random)
def generate_complaint_id():
    today = datetime.now().strftime("%y%m%d")  # e.g., 250917
    rand = str(random.randint(1000, 9999))     # 4 digit random
    return today + rand

# --- Streamlit UI ---
st.set_page_config(page_title="Anonymous Complaint Portal", layout="wide")
st.title("📢 Anonymous Complaint Portal")

menu = st.sidebar.radio("Navigation", ["Submit Complaint", "Check Status", "Admin Portal"])

# Submit Complaint
if menu == "Submit Complaint":
    st.subheader("Submit a New Complaint")
    complaint = st.text_area("Enter your complaint here:")

    if st.button("Submit Complaint"):
        if complaint.strip() == "":
            st.warning("⚠️ Complaint cannot be empty.")
        else:
            df = load_complaints()
            comp_id = generate_complaint_id()
            new_row = pd.DataFrame(
                [[comp_id, complaint, "In Progress", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                columns=["Complaint_ID", "Complaint_Text", "Status", "Timestamp"]
            )
            df = pd.concat([df, new_row], ignore_index=True)
            save_complaints(df)
            st.success(f"✅ Complaint submitted successfully! Your Complaint ID: **{comp_id}**")
            st.info("⚠️ Please save your Complaint ID to check the status later.")

# Check Status
elif menu == "Check Status":
    st.subheader("Check Complaint Status")
    comp_id = st.text_input("Enter your Complaint ID:")

    if st.button("Check Status"):
        df = load_complaints()
        if comp_id in df["Complaint_ID"].astype(str).values:
            status = df.loc[df["Complaint_ID"].astype(str) == comp_id, "Status"].values[0]
            st.success(f"✅ Complaint Status: **{status}**")
        else:
            st.error("❌ Complaint ID not found. Please check again.")

# Admin Portal
elif menu == "Admin Portal":
    st.subheader("🔑 Admin Login")
    password = st.text_input("Enter Admin Password:", type="password")

    if st.button("Submit Login"):
        if password == "admin123":  # Replace with secure password
            st.success("✅ Logged in as Admin")

            df = load_complaints()

            # --- Dashboard KPIs ---
            st.markdown("### 📊 Dashboard Overview")
            total_complaints = len(df)
            in_progress = (df["Status"] == "In Progress").sum()
            resolved = (df["Status"] == "Resolved").sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Complaints", total_complaints)
            col2.metric("In Progress", in_progress)
            col3.metric("Resolved", resolved)

            st.markdown("---")
            st.subheader("📋 Manage Complaints")

            if not df.empty:
                for i, row in df.iterrows():
                    with st.expander(f"Complaint ID: {row['Complaint_ID']} | Status: {row['Status']}"):
                        st.write(f"**Complaint Text:** {row['Complaint_Text']}")
                        new_status = st.selectbox(
                            "Update Status",
                            ["In Progress", "Resolved"],
                            index=0 if row['Status'] == "In Progress" else 1,
                            key=f"status_{i}"
                        )
                        if st.button("Update Status", key=f"update_{i}"):
                            df.at[i, "Status"] = new_status
                            save_complaints(df)
                            st.success(f"✅ Status updated for Complaint ID: {row['Complaint_ID']}")
        else:
            st.error("❌ Incorrect password.")
