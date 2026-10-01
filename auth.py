import bcrypt

from database import add_user, get_user_by_email, add_activity_log


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def register_user(username, email, password):
    hashed_password = hash_password(password)

    success = add_user(
        username,
        email,
        hashed_password
    )

    return success


def login_user(email, password):
    user = get_user_by_email(email)

    if user is None:
        return None

    user_id, username, user_email, hashed_password = user

    if verify_password(password, hashed_password):

        add_activity_log(
            user_id,
            "Login Successful",
            f"User {user_email} logged in"
        )

        return {
            "id": user_id,
            "username": username,
            "email": user_email
        }

    return None