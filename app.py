import streamlit as st

from database import (
    create_database,
    add_file,
    get_user_files,
    share_file,
    get_shared_files,
    get_user_by_email,
    add_activity_log,
    get_activity_logs,
    get_files_shared_by_user,
    revoke_file_access
)

from auth import register_user, login_user
from file_manager import encrypt_file, decrypt_file


# =========================================================
# DATABASE
# =========================================================

create_database()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Secure File Sharing",
    page_icon="🔐",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# =========================================================
# LOGIN / REGISTER
# =========================================================

if not st.session_state.logged_in:

    st.title("Secure File Sharing System")

    st.write(
        "Upload, encrypt, store and securely share your files."
    )

    option = st.radio(
        "Choose an option",
        ["Login", "Register"]
    )

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    if option == "Login":

        st.subheader("Login")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            if not email or not password:

                st.warning(
                    "Please enter email and password."
                )

            else:

                user = login_user(
                    email,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user = user

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

    # -----------------------------------------------------
    # REGISTER
    # -----------------------------------------------------

    else:

        st.subheader("Create Account")

        username = st.text_input(
            "Username"
        )

        email = st.text_input(
            "Email"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Register"):

            if not username or not email or not password:

                st.warning(
                    "Please fill all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(password) < 6:

                st.warning(
                    "Password must contain at least 6 characters."
                )

            else:

                success = register_user(
                    username,
                    email,
                    password
                )

                if success:

                    st.success(
                        "Account created successfully. You can now login."
                    )

                else:

                    st.error(
                        "An account with this email already exists."
                    )


# =========================================================
# DASHBOARD
# =========================================================

else:

    user = st.session_state.user

    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.title("Secure Files")

        st.write(
            f"Logged in as **{user['username']}**"
        )

        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "My Files",
                "Shared With Me",
                "Shared By Me",
                "Security Activity"
            ]
        )

        st.divider()

        if st.button("Logout"):

            add_activity_log(
                user["id"],
                "Logout",
                f"User {user['email']} logged out"
            )

            st.session_state.logged_in = False
            st.session_state.user = None

            st.rerun()


    # =====================================================
    # DASHBOARD
    # =====================================================

    if page == "Dashboard":

        st.title("Dashboard")

        files = get_user_files(
            user["id"]
        )

        shared_with_me = get_shared_files(
            user["id"]
        )

        shared_by_me = get_files_shared_by_user(
            user["id"]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "My Files",
                len(files)
            )

        with col2:
            st.metric(
                "Shared With Me",
                len(shared_with_me)
            )

        with col3:
            st.metric(
                "Active Shares",
                len(shared_by_me)
            )

        st.divider()

        st.subheader("Security")

        st.info(
            "Files are encrypted before being stored. "
            "Passwords are protected using bcrypt hashing."
        )

        st.subheader("Quick Overview")

        if files:

            for (
                file_id,
                original_filename,
                stored_filename,
                upload_time
            ) in files[:5]:

                st.write(
                    f"📄 **{original_filename}**"
                )

                st.caption(
                    f"Uploaded: {upload_time}"
                )

        else:

            st.info(
                "No files uploaded yet."
            )


    # =====================================================
    # MY FILES
    # =====================================================

    elif page == "My Files":

        st.title("My Files")

        # -------------------------------------------------
        # UPLOAD
        # -------------------------------------------------

        st.subheader("Upload File")

        uploaded_file = st.file_uploader(
            "Choose a file"
        )

        if st.button("Encrypt & Upload"):

            if uploaded_file is None:

                st.warning(
                    "Please select a file first."
                )

            else:

                try:

                    stored_filename = encrypt_file(
                        uploaded_file
                    )

                    add_file(
                        user["id"],
                        uploaded_file.name,
                        stored_filename
                    )

                    add_activity_log(
                        user["id"],
                        "File Uploaded",
                        uploaded_file.name
                    )

                    st.success(
                        f"{uploaded_file.name} uploaded and encrypted successfully."
                    )

                except Exception as error:

                    st.error(
                        f"Upload failed: {error}"
                    )

        st.divider()

        # -------------------------------------------------
        # FILE LIST
        # -------------------------------------------------

        files = get_user_files(
            user["id"]
        )

        if not files:

            st.info(
                "You haven't uploaded any files yet."
            )

        else:

            for (
                file_id,
                original_filename,
                stored_filename,
                upload_time
            ) in files:

                st.write(
                    f"### {original_filename}"
                )

                st.caption(
                    f"Uploaded: {upload_time}"
                )

                col1, col2 = st.columns(2)

                # -----------------------------------------
                # DOWNLOAD
                # -----------------------------------------

                with col1:

                    try:

                        decrypted_data = decrypt_file(
                            stored_filename
                        )

                        if st.download_button(
                            "Download",
                            data=decrypted_data,
                            file_name=original_filename,
                            key=f"download_{file_id}"
                        ):

                            add_activity_log(
                                user["id"],
                                "File Downloaded",
                                original_filename
                            )

                    except Exception:

                        st.error(
                            "Unable to decrypt file."
                        )

                # -----------------------------------------
                # SHARE
                # -----------------------------------------

                with col2:

                    share_email = st.text_input(
                        "Share with email",
                        key=f"share_email_{file_id}"
                    )

                    if st.button(
                        "Share",
                        key=f"share_{file_id}"
                    ):

                        if not share_email:

                            st.warning(
                                "Enter the recipient's email."
                            )

                        elif share_email == user["email"]:

                            st.warning(
                                "You cannot share a file with yourself."
                            )

                        else:

                            recipient = get_user_by_email(
                                share_email
                            )

                            if recipient is None:

                                st.error(
                                    "User with this email does not exist."
                                )

                            else:

                                recipient_id = recipient[0]

                                success = share_file(
                                    file_id,
                                    user["id"],
                                    recipient_id
                                )

                                if success:

                                    add_activity_log(
                                        user["id"],
                                        "File Shared",
                                        f"{original_filename} shared with {share_email}"
                                    )

                                    st.success(
                                        "File shared successfully."
                                    )

                                else:

                                    st.warning(
                                        "This file is already shared with that user."
                                    )

                st.divider()


    # =====================================================
    # SHARED WITH ME
    # =====================================================

    elif page == "Shared With Me":

        st.title("Shared With Me")

        shared_files = get_shared_files(
            user["id"]
        )

        if not shared_files:

            st.info(
                "No files have been shared with you."
            )

        else:

            for (
                file_id,
                original_filename,
                stored_filename,
                expires_at,
                upload_time
            ) in shared_files:

                st.write(
                    f"### {original_filename}"
                )

                st.caption(
                    f"Uploaded: {upload_time}"
                )

                try:

                    decrypted_data = decrypt_file(
                        stored_filename
                    )

                    if st.download_button(
                        "Download Shared File",
                        data=decrypted_data,
                        file_name=original_filename,
                        key=f"shared_download_{file_id}"
                    ):

                        add_activity_log(
                            user["id"],
                            "Shared File Downloaded",
                            original_filename
                        )

                except Exception:

                    st.error(
                        "Unable to decrypt shared file."
                    )

                st.divider()


    # =====================================================
    # SHARED BY ME
    # =====================================================

    elif page == "Shared By Me":

        st.title("Shared By Me")

        shared_files = get_files_shared_by_user(
            user["id"]
        )

        if not shared_files:

            st.info(
                "You haven't shared any files yet."
            )

        else:

            st.write(
                "Manage users who currently have access to your files."
            )

            st.divider()

            for (
                share_id,
                file_id,
                filename,
                recipient_username,
                recipient_email,
                expires_at,
            ) in shared_files:

                col1, col2, col3 = st.columns(
                    [2, 2, 1]
                )

                with col1:

                    st.write(
                        f"**{filename}**"
                    )

                with col2:

                    st.write(
                        f"{recipient_username}"
                    )

                    st.caption(
                        recipient_email
                    )

                with col3:

                    if st.button(
                        "Revoke",
                        key=f"revoke_{share_id}"
                    ):

                        success = revoke_file_access(
                            share_id,
                            user["id"]
                        )

                        if success:

                            add_activity_log(
                                user["id"],
                                "Access Revoked",
                                f"Revoked access to {filename} "
                                f"from {recipient_email}"
                            )

                            st.success(
                                "Access revoked."
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Unable to revoke access."
                            )

                st.divider()


    # =====================================================
    # SECURITY ACTIVITY
    # =====================================================

    elif page == "Security Activity":

        st.title("Security Activity")

        logs = get_activity_logs(
            user["id"]
        )

        if not logs:

            st.info(
                "No activity recorded yet."
            )

        else:

            for (
                action,
                details,
                timestamp
            ) in logs:

                st.write(
                    f"**{action}**"
                )

                if details:

                    st.caption(
                        f"{details} | {timestamp}"
                    )

                else:

                    st.caption(
                        str(timestamp)
                    )