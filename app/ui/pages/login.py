from __future__ import annotations

import uuid

from nicegui import app as nicegui_app
from nicegui import ui

from app.core.auth import create_access_token
from app.db.users import authenticate_user, create_user, get_user_by_username


def login_page() -> None:
    # Header
    with ui.header().classes(
        "bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-lg"
    ):
        with ui.row().classes("w-full items-center justify-center px-8 py-6"):
            ui.label("Quack Query").classes("text-3xl font-black tracking-tight")

    with ui.column().classes("w-full max-w-md mx-auto px-8 py-16 gap-6"):
        # Tabs for login/signup
        with ui.tabs().classes("w-full") as tabs:
            login_tab = ui.tab("Login")
            signup_tab = ui.tab("Sign Up")

        with ui.tab_panels(tabs, value=login_tab).classes("w-full"):
            # Login panel
            with ui.tab_panel(login_tab):
                with ui.card().classes("w-full bg-white border border-slate-200 p-6"):
                    ui.label("Login").classes("text-2xl font-bold text-slate-900 mb-4")

                    username_input = ui.input(
                        label="Username", placeholder="Enter your username"
                    ).classes("w-full")

                    password_input = ui.input(
                        label="Password",
                        password=True,
                        placeholder="Enter your password",
                    ).classes("w-full")

                    login_status = ui.label("").classes("text-sm text-slate-600")

                    def handle_login() -> None:
                        username = username_input.value.strip()
                        password = password_input.value.strip()

                        if not username or not password:
                            login_status.set_text("Please enter username and password")
                            login_status.classes(
                                "text-red-600", remove="text-slate-600"
                            )
                            return

                        user = authenticate_user(username, password)
                        if not user:
                            login_status.set_text("Invalid username or password")
                            login_status.classes(
                                "text-red-600", remove="text-slate-600"
                            )
                            return

                        # Create token and store in server session
                        token = create_access_token(
                            {"sub": user.username, "user_id": user.id}
                        )
                        nicegui_app.storage.general["token"] = token

                        login_status.set_text("Login successful!")
                        login_status.classes("text-green-600", remove="text-slate-600")

                        # Navigate
                        ui.navigate.to("/")

                    ui.button("Login", on_click=handle_login).classes(
                        "w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2"
                    )

            # Signup panel
            with ui.tab_panel(signup_tab):
                with ui.card().classes("w-full bg-white border border-slate-200 p-6"):
                    ui.label("Create Account").classes(
                        "text-2xl font-bold text-slate-900 mb-4"
                    )

                    signup_username = ui.input(
                        label="Username", placeholder="Choose a username"
                    ).classes("w-full")

                    signup_email = ui.input(
                        label="Email", placeholder="Enter your email"
                    ).classes("w-full")

                    signup_password = ui.input(
                        label="Password", password=True, placeholder="Choose a password"
                    ).classes("w-full")

                    signup_status = ui.label("").classes("text-sm text-slate-600")

                    def handle_signup() -> None:
                        username = signup_username.value.strip()
                        email = signup_email.value.strip()
                        password = signup_password.value.strip()

                        if not username or not email or not password:
                            signup_status.set_text("Please fill in all fields")
                            signup_status.classes(
                                "text-red-600", remove="text-slate-600"
                            )
                            return

                        if len(password) < 6:
                            signup_status.set_text(
                                "Password must be at least 6 characters"
                            )
                            signup_status.classes(
                                "text-red-600", remove="text-slate-600"
                            )
                            return

                        # Check if user exists
                        if get_user_by_username(username):
                            signup_status.set_text("Username already taken")
                            signup_status.classes(
                                "text-red-600", remove="text-slate-600"
                            )
                            return

                        try:
                            user_id = uuid.uuid4().hex
                            create_user(user_id, username, email, password)

                            # Auto-login
                            token = create_access_token(
                                {"sub": username, "user_id": user_id}
                            )
                            nicegui_app.storage.general["token"] = token

                            signup_status.set_text("Account created! Redirecting...")
                            signup_status.classes(
                                "text-green-600", remove="text-slate-600"
                            )

                            # Navigate
                            ui.navigate.to("/")
                        except Exception as e:
                            signup_status.set_text(f"Error: {str(e)[:50]}")
                            signup_status.classes(
                                "text-red-600", remove="text-slate-600"
                            )

                    ui.button("Sign Up", on_click=handle_signup).classes(
                        "w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2"
                    )
