import streamlit as st
import pandas as pd
import os
import random
from datetime import datetime

# File name
FILE_NAME = "complaints.xlsx"
ADMIN_PASSWORD = "admin123"  # change as needed


# ------------------ Helper Functions ------------------ #
def load_complaints():
    try:
        df = pd.read_excel(FILE_NAME, dtype=str)
        expected_cols = ["Complaint_ID", "Complaint_Text", "Status", "Timestamp"]
        for col in expected_cols:
            if col not in df.columns:
                df = pd.DataFrame(columns=expected_cols)
                save_complaints(df)
                break
    except Exception:
        df = pd.DataFrame(columns=["Complaint_ID", "Complaint_Text", "Status", "Timestamp"])
        save_complaints(df)
    return df


def save_complaints(df):
    df.to_excel(FILE_NAME, index=False)


def generate_complaint_id():
    today = datetime.now().strftime("%y%m%d")  # YYMMDD
    rand_num = random.randint(1000, 9999)  # 4-digit random
    return f"{today}{rand_num}"


# ------------------ Streamlit App ------------------ #
st.set_page_config(page_title="Netmark Anonymous Complaint Portal", layout="wide")
st.title("📝 Netmark Anonymous Complaint Portal")

menu = ["Submit Complaint", "Check Status", "Admin Portal"]
choice = st.sidebar.selectbox("Menu", menu)

# ------------------ Submit Complaint ------------------ #
if choice == "Submit Complaint":
    st.subheader("📩 Submit a New Complaint")

    complaint_text = st.text_area("Enter your complaint", "")
    if st.button("Submit Complaint"):
        if complaint_text.strip() == "":
            st.error("⚠️ Complaint cannot be empty.")
        else:
            df = load_complaints()
            complaint_id = generate_complaint_id()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            new_row = pd.DataFrame(
                [[complaint_id, complaint_text, "Pending", timestamp]],
                columns=["Complaint_ID", "Complaint_Text", "Status", "Timestamp"],
            )

            df = pd.concat([df, new_row], ignore_index=True)
            save_complaints(df)

            st.success(f"✅ Complaint submitted successfully! Your Complaint ID is **{complaint_id}**")
            st.info("ℹ️ Please save this ID to check your complaint status later.")

# ------------------ Check Status ------------------ #
elif choice == "Check Status":
    st.subheader("🔍 Check Complaint Status")

    complaint_id = st.text_input("Enter your Complaint ID")
    if st.button("Check Status"):
        df = load_complaints()
        if complaint_id in df["Complaint_ID"].values:
            row = df[df["Complaint_ID"] == complaint_id].iloc[0]
            st.success(f"📌 Complaint Found!\n\n**Status:** {row['Status']}\n\n**Complaint:** {row['Complaint_Text']}")
        else:
            st.error("❌ Complaint ID not found. Please check and try again.")

# ------------------ Admin Portal ------------------ #
elif choice == "Admin Portal":
    st.subheader("🔑 Admin Portal")

    # Initialize session state
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    # Not logged in yet
    if not st.session_state["admin_logged_in"]:
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state["admin_logged_in"] = True
                st.success("✅ Login successful")
            else:
                st.error("❌ Incorrect password")

    # Logged in
    else:
        st.success("Welcome, Mario! 🎉")
        if st.button("Logout"):
            st.session_state["admin_logged_in"] = False
            st.rerun()

        df = load_complaints()
        if not df.empty:
            # Show KPIs
            total = len(df)
            pending = (df["Status"] == "Pending").sum()
            in_progress = (df["Status"] == "In Progress").sum()
            resolved = (df["Status"] == "Resolved").sum()

            st.markdown("### 📊 Dashboard")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📌 Total", total)
            col2.metric("🕒 Pending", pending)
            col3.metric("⏳ In Progress", in_progress)
            col4.metric("✅ Resolved", resolved)

            # Manage complaints
            st.markdown("### 🗂 Manage Complaints")
            for idx, row in df.iterrows():
                with st.expander(f"Complaint ID: {row['Complaint_ID']} | Status: {row['Status']}"):
                    st.write(f"**Complaint:** {row['Complaint_Text']}")
                    new_status = st.selectbox(
                        "Update Status",
                        ["Pending", "In Progress", "Resolved"],
                        index=["Pending", "In Progress", "Resolved"].index(row["Status"]),
                        key=f"status_{row['Complaint_ID']}",
                    )
                    if st.button("Save Update", key=f"btn_{row['Complaint_ID']}"):
                        df.at[idx, "Status"] = new_status
                        save_complaints(df)
                        st.success(f"✅ Status updated for Complaint {row['Complaint_ID']}")
        else:
            st.info("No complaints submitted yet.")
