import tkinter as tk  # tkinter for GUI

from tkinter import messagebox, ttk  # messagebox for popups, ttk for input boxes


from storage import load_vault, save_vault, reset_vault  # vault functions
from crypto_utils import (
    generate_salt,  
    derive_key,  
    encrypt_password,  
    decrypt_password,  
    bytes_to_base64,  
    base64_to_bytes,  
)

# this file runs the main password manager screen

def main():
    window = tk.Tk()
    window.title("Credential Manager")
    window.geometry("560x620")  # fixed size so layout stays the same
    window.resizable(False, False)  # resize was disabled because it was breaking spacing
    # app state while program is open
    show_saved_password = False
    is_authenticated = False
    authenticated_key = None
    is_first_time_user = False
    setup_ready = False

    # remembers the last loaded entry from the dropdown
    # used to know if user changed something after loading it
    loaded_service_name = None
    loaded_username_value = ""
    loaded_password_value = ""

    style = ttk.Style()

    # simple button style
    style.configure(
        "Custom.TButton",
        padding=(8, 5),
        background="#e6e6e6",
        foreground="black"
    )



    def hide_saved_password():
        nonlocal show_saved_password
        show_saved_password = False
        password_entry.config(show="*")  # hide with * again
        password_toggle_button.config(text="SHOW")

    def toggle_saved_password():
        nonlocal show_saved_password
        show_saved_password = not show_saved_password  # switch state


        if show_saved_password:
            password_entry.config(show="")  # show real text
            password_toggle_button.config(text="HIDE")
        else:
            password_entry.config(show="*")  # hide again
            password_toggle_button.config(text="SHOW")

    def check_vault_state():
        nonlocal is_first_time_user

        vault = load_vault()


        # if no salt or no entries exist yet, then treat it as first time setup

        if vault["salt"] is None or not vault["entries"]:
            is_first_time_user = True
        else:
            is_first_time_user = False

    def show_credentials_section():
        credentials_frame.pack(fill="x", pady=(0, 0))  #  show hidden credentials area

    def hide_credentials_section():
        credentials_frame.pack_forget()  # hide it without deleting it


    def update_confirm_row():
        # confirm password only matters during first use
        if is_first_time_user and not setup_ready:
            confirm_row.pack(fill="x", pady=(0, 10))
        else:
            confirm_row.pack_forget()

    def update_save_button_text():
        service = service_entry.get().strip()  # remove accidental spaces
        username = username_entry.get().strip()  # same here
        password = password_entry.get()  #keep exact value for password

        # if no loaded entry exist, keep normal save text
        if not service or loaded_service_name is None:
            save_button.config(text="SAVE CREDENTIALS")
            return

        # compare current values with the ones that were previously loaded
        if service.lower() == loaded_service_name.lower():  # ignore upper/lower case
            if username != loaded_username_value or password != loaded_password_value:
                save_button.config(text="UPDATE CREDENTIALS")  # existing entry was edited
            else:
                save_button.config(text="SAVE CREDENTIALS")  # loaded but unchanged
        else:
            save_button.config(text="SAVE CREDENTIALS")  # different service means new save


    def reset_loaded_entry_state():
        nonlocal loaded_service_name
        nonlocal loaded_username_value
        nonlocal loaded_password_value

        # clears remembered loaded values
        loaded_service_name = None
        loaded_username_value = ""
        loaded_password_value = ""
        save_button.config(text="SAVE CREDENTIALS")

    def update_auth_ui():
        # updates helper text and main button depending on app state


        if is_first_time_user:
            if setup_ready:
                master_helper_label.config(
                    text="Master password set. You can now save your first credentials.",
                    foreground="green"
                )
                authenticate_button.config(text="LOCK", command=lock_vault)
                reset_button.pack(side=tk.BOTTOM, pady=(10, 0))
            else:
                master_helper_label.config(
                    text="Set a master password to get started!",
                    foreground="gray40"
                )
                authenticate_button.config(text="GET STARTED", command=authenticate_user)
                reset_button.pack_forget()  # no need for reset yet

        else:
            if is_authenticated:
                master_helper_label.config(
                    text="Unlocked. Saved services loaded.",
                    foreground="green"
                )
                authenticate_button.config(text="LOCK", command=lock_vault)
                reset_button.pack(side=tk.BOTTOM, pady=(10, 0))

            else:
                master_helper_label.config(
                    text="Enter your master password to load saved services.",
                    foreground="gray40"
                )
                authenticate_button.config(text="UNLOCK", command=authenticate_user)
                reset_button.pack_forget()


        update_confirm_row()  # refresh confirm row too

    def lock_vault():
        nonlocal is_authenticated
        nonlocal authenticated_key
        nonlocal setup_ready

        is_authenticated = False
        authenticated_key = None

        # if still in first time flow, go back to setup stage
        setup_ready = False if is_first_time_user else setup_ready


        master_entry.delete(0, tk.END)
        confirm_entry.delete(0, tk.END)
        clear_fields()
        hide_credentials_section()
        service_entry["values"] = []  # remove loaded services
        reset_loaded_entry_state()
        update_auth_ui()
        status_label.config(text="", foreground="green")

    def reset_all_data():
        nonlocal is_authenticated
        nonlocal authenticated_key
        nonlocal is_first_time_user
        nonlocal setup_ready

        # popup confirmation used so user does not delete everything by mistake
        confirm = messagebox.askyesno(
            "Reset Vault",
            "This will delete all saved credentials and reset the vault.\nDo you want to continue?"
        )

        if not confirm:
            return

        reset_vault()



        # after reset the app should act like first time use
        is_authenticated = False
        authenticated_key = None
        is_first_time_user = True
        setup_ready = False

        master_entry.delete(0, tk.END)
        confirm_entry.delete(0, tk.END)
        clear_fields()
        hide_credentials_section()
        service_entry["values"] = []
        reset_loaded_entry_state()

        update_auth_ui()
        status_label.config(text="Vault reset successfully!", foreground="green")


    def reset_auth_state():
        nonlocal is_authenticated
        nonlocal authenticated_key
        nonlocal setup_ready

         #if master password fields change, old unlocked state should not stay valid
        is_authenticated = False
        authenticated_key = None
        setup_ready = False
        service_entry["values"] = []
        service_entry.set("")
        reset_loaded_entry_state()
        update_auth_ui()
        hide_credentials_section()

    def on_master_password_change(event=None):
        reset_auth_state()
        clear_loaded_data()  #clears old loaded data from fields

    def on_confirm_password_change(event=None):
        reset_auth_state()
        clear_loaded_data()

    def on_username_change(event=None):
        update_save_button_text()  #  check if button text should change to update

    def on_password_change(event=None):
        update_save_button_text()

    def clear_fields():
        service_entry.set("")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        status_label.config(text="", foreground="green")
        hide_saved_password()  # hide password again (default)
        reset_loaded_entry_state()

    def clear_loaded_data():
          # only clears loaded entry part, not the master password area
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        status_label.config(text="", foreground="green")
        hide_saved_password()
        reset_loaded_entry_state()

    def find_service_entry(service_name):
        vault = load_vault()

        # lower() makes Gmail and gmail count as the same service f
        for entry in vault["entries"]:
            if entry["service"].lower() == service_name.lower():
                return entry

        return None


    def auto_load_selected_service(event=None):
        nonlocal loaded_service_name
        nonlocal loaded_username_value
        nonlocal loaded_password_value

        service = service_entry.get().strip()

        if not is_authenticated:
            return  # do not load anything if vault is still locked

        if not service:
            return

        entry = find_service_entry(service)

        if entry is None:
            reset_loaded_entry_state()
            return
        try:
            nonce = base64_to_bytes(entry["nonce"])  # convert saved text back to bytes
            ciphertext = base64_to_bytes(entry["ciphertext"])  # encrypted password data

              # decrypt saved password using the key from the master password
            decrypted_password = decrypt_password(ciphertext, nonce, authenticated_key)

            username_entry.delete(0, tk.END)
            username_entry.insert(0, entry["username"])

            password_entry.delete(0, tk.END)
            password_entry.insert(0, decrypted_password)

            hide_saved_password()  # still hide it first after loadiing

            # store original loaded values for compare later
            loaded_service_name = entry["service"]
            loaded_username_value = entry["username"]
            loaded_password_value = decrypted_password

            status_label.config(text="", foreground="green")
            update_save_button_text()

        except Exception:
            # if load fails, clear fields so wrong data is not displayed
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            hide_saved_password()
            reset_loaded_entry_state()
            status_label.config(text="Could not load saved credentials.", foreground="red")


    def on_service_change(event=None):
        # if user types another service, old loaded values should disappear
        clear_loaded_data()

    def authenticate_user():
        nonlocal is_authenticated
        nonlocal authenticated_key
        nonlocal setup_ready

        master_password = master_entry.get()
        vault = load_vault()

        if not master_password:
            status_label.config(text="", foreground="green")
            return

        if is_first_time_user:
            confirm_password = confirm_entry.get()

            if not confirm_password:
                master_helper_label.config(
                    text="Please confirm the master password.",
                    foreground="red"
                )
                return
            # both boxes must match before continuing
            if master_password != confirm_password:
                master_helper_label.config(
                    text="Passwords do not match. Try again!",
                    foreground="red"
                )
                return

            # first setup unlocks the form first, real key is made on first save
            is_authenticated = True
            authenticated_key = None
            setup_ready = True
            update_auth_ui()
            show_credentials_section()
            status_label.config(text="", foreground="green")
            return

        salt = base64_to_bytes(vault["salt"])  # get original salt
        key = derive_key(master_password, salt)  # rebuild key from typed password

        try:
            # easiest way to test password is trying to decrypt one saved entry
            first_entry = vault["entries"][0]
            nonce = base64_to_bytes(first_entry["nonce"])
            ciphertext = base64_to_bytes(first_entry["ciphertext"])
            decrypt_password(ciphertext, nonce, key)  # if this works, password is correct

            is_authenticated = True
            authenticated_key = key

            services = [entry["service"] for entry in vault["entries"]]
            unique_services = sorted(set(services), key=str.lower)  # remove duplicates and sort
            service_entry["values"] = unique_services

            update_auth_ui()
            show_credentials_section()
            status_label.config(text="", foreground="green")

        except Exception:
            is_authenticated = False
            authenticated_key = None
            service_entry["values"] = []
            service_entry.set("")
            hide_credentials_section()
            reset_loaded_entry_state()
            master_helper_label.config(
                text="Master password not correct. Try again! ",
                foreground="red"
            )
            status_label.config(text="", foreground="green")

    def save_password():
        nonlocal is_first_time_user
        nonlocal authenticated_key

        master_password = master_entry.get()
        service = service_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get()

        if not master_password or not service or not username or not password:
            status_label.config(text="Please fill in all fields!", foreground="red")
            return

        if not is_authenticated:
            status_label.config(text="Please unlock first.", foreground="red")
            return
        vault = load_vault()

        # salt is only created once, on first real save to help make the key more secure
        if vault["salt"] is None:
            salt = generate_salt()
            vault["salt"] = bytes_to_base64(salt)  # stored as text
            save_vault(vault)
        else:
            salt = base64_to_bytes(vault["salt"])


        # first time save creates the real key here
        if authenticated_key is None:
            authenticated_key = derive_key(master_password, salt)  # password + salt = key

        key = authenticated_key


        # extra check so app does not save with a wrong password state
        if vault["entries"]:
            try:
                first_entry = vault["entries"][0]
                test_nonce = base64_to_bytes(first_entry["nonce"])
                test_ciphertext = base64_to_bytes(first_entry["ciphertext"])
                decrypt_password(test_ciphertext, test_nonce, key)
            except Exception:
                status_label.config(text="Wrong master password. Cannot save credentials!", foreground="red")
                return

        # password is encrypted before saving
        nonce, ciphertext = encrypt_password(password, key)


        entry = {
            "service": service,
            "username": username,
            "nonce": bytes_to_base64(nonce),  # saved as text
            "ciphertext": bytes_to_base64(ciphertext),  # saved as text
        }

        existing_index = None

        # check if same service already exists
        for i, saved_entry in enumerate(vault["entries"]):
            if saved_entry["service"].lower() == service.lower():
                existing_index = i
                break

        if existing_index is not None:
            confirm = messagebox.askyesno(
                "Duplicate Entry",
                f"An entry for '{service}' already exists.\nDo you want to overwrite it?"
            )

            # ask first so overwrite does not happen automatically
            if confirm:
                vault["entries"][existing_index] = entry
                status_label.config(text="Credentials updated successfully.", foreground="green")
            else:
                hide_saved_password()
                status_label.config(text="Save cancelled.", foreground="red")
                return
        else:
            vault["entries"].append(entry)
            status_label.config(text="Credentials saved successfully.", foreground="green")

        save_vault(vault)


        # after first save, app is no longer in setup mode
        is_first_time_user = False
        update_auth_ui()



        services = [entry["service"] for entry in vault["entries"]]
        unique_services = sorted(set(services), key=str.lower)
        service_entry["values"] = unique_services

        # clear boxes after save so form is ready again
        service_entry.set("")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        hide_saved_password()
        reset_loaded_entry_state()

    # outside frame adds spacing around the full app
    main_frame = tk.Frame(window, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    #  helps keep content centered
    center_frame = tk.Frame(main_frame)
    center_frame.pack(fill="both", expand=True)

     # top area for title and form
    top_frame = tk.Frame(center_frame)
    top_frame.pack()

    title_label = tk.Label(
        top_frame,
        text="Credential Manager",
        font=("Arial", 19, "bold")
    )
    title_label.pack(pady=(0, 6))

    subtitle_label = tk.Label(
        top_frame,
        text="Encrypt login details using AES-GCM",
        font=("Arial", 11),
        fg="gray40",
        wraplength=420,
        justify="center"
    )
    subtitle_label.pack(pady=(0, 18))

    # auth section at top
    auth_frame = tk.Frame(top_frame)
    auth_frame.pack(fill="x", pady=(0, 8))

    master_label = tk.Label(
        auth_frame,
        text="Master Password",
        font=("Arial", 12, "bold"),
        anchor="w"
    )
    master_label.pack(fill="x", pady=(0, 4))

    # grid used here so entry and button line up better
    master_row = tk.Frame(auth_frame)
    master_row.pack(fill="x", pady=(0, 10))
    master_row.grid_columnconfigure(0, weight=1)  # first column can stretch

    master_entry = ttk.Entry(
        master_row,
        show="*",
        font=("Arial", 12),
        width=28
    )
    master_entry.grid(row=0, column=0, sticky="ew")
    master_entry.bind("<KeyRelease>", on_master_password_change)
    master_entry.bind("<Return>", lambda event: authenticate_user())  # Enter also triggers unlock

    authenticate_button = tk.Button(
        master_row,
        text="UNLOCK",
        command=authenticate_user,
        font=("Arial", 10, "bold"),
        bg="#e6e6e6",
        activebackground="#d9d9d9",
        relief="raised",
        bd=1,
        padx=10,
        pady=4
    )
    authenticate_button.grid(row=0, column=1, padx=(8, 0))

    # only shown during first setup
    confirm_row = tk.Frame(auth_frame)
    confirm_row.grid_columnconfigure(0, weight=1)

    confirm_label = tk.Label(
        confirm_row,
        text="Confirm Master Password",
        font=("Arial", 12, "bold"),
        anchor="w"
    )
    confirm_label.grid(row=0, column=0, sticky="w", pady=(0, 4))

     # spacer  labels help keep both rows lined up correctly
    confirm_spacer = tk.Label(
        confirm_row,
        text="",
        width=10
    )
    confirm_spacer.grid(row=0, column=1, padx=(8, 0))

    confirm_entry = ttk.Entry(

        confirm_row,
        show="*",
        font=("Arial", 12),
        width=28

    )
    confirm_entry.grid(row=1, column=0, sticky="ew")
    confirm_entry.bind("<KeyRelease>", on_confirm_password_change)
    confirm_entry.bind("<Return>", lambda event: authenticate_user())

    confirm_spacer_2 = tk.Label(

        confirm_row,
        text="",
        width=10

    )
    confirm_spacer_2.grid(row=1, column=1, padx=(8, 0))

    master_helper_label = tk.Label(
        auth_frame,
        text="",
        font=("Arial", 10),
        anchor="w",
        justify="left",
        wraplength=420
    )
    master_helper_label.pack(fill="x", pady=(0, 10))

    # credentials section starts hidden until unlock works

    credentials_frame = tk.Frame(top_frame)

    service_label = tk.Label(
        credentials_frame,
        text="Service",
        font=("Arial", 12, "bold"),
        anchor="w"
    )
    service_label.pack(fill="x", pady=(0, 4))

    service_entry = ttk.Combobox(
        credentials_frame,
        font=("Arial", 12),
        width=36
    )
    service_entry.pack(fill="x", pady=(0, 12))
    service_entry.bind("<KeyRelease>", on_service_change)
    service_entry.bind("<<ComboboxSelected>>", auto_load_selected_service)  # get saved service and auto load it

    username_label = tk.Label(
        credentials_frame,
        text="Username",
        font=("Arial", 12, "bold"),
        anchor="w"
    )
    username_label.pack(fill="x", pady=(0, 4))

    username_entry = ttk.Entry(
        credentials_frame,
        font=("Arial", 12),
        width=36
    )
    username_entry.pack(fill="x", pady=(0, 12))
    username_entry.bind("<KeyRelease>", on_username_change)

    password_label = tk.Label(
        credentials_frame,
        text="Password",
        font=("Arial", 12, "bold"),
        anchor="w"
    )


    password_label.pack(fill="x", pady=(0, 4))

    # row for password field and show/hide button
    password_frame = tk.Frame(credentials_frame)
    password_frame.pack(fill="x", pady=(0, 14))
    password_frame.grid_columnconfigure(0, weight=1)  # entry stretches, button stays fixed

    password_entry = ttk.Entry(
        password_frame,
        show="*",
        font=("Arial", 12),
        width=28
    )

    password_entry.grid(row=0, column=0, sticky="ew")
    password_entry.bind("<KeyRelease>", on_password_change)

    password_toggle_button = tk.Button(
        password_frame,
        text="SHOW",
        command=toggle_saved_password,
        font=("Arial", 10, "bold"),
        bg="#e6e6e6",
        activebackground="#d9d9d9",
        relief="raised",
        bd=1,
        padx=10,
        pady=4
    )
    password_toggle_button.grid(row=0, column=1, padx=(8, 0))

    # buttons for save and clear
    button_frame = tk.Frame(credentials_frame)
    button_frame.pack(fill="x")



    save_button = tk.Button(
        button_frame,
        text="SAVE CREDENTIALS", #save
        command=save_password,
        font=("Arial", 10, "bold"),
        bg="#e6e6e6",
        activebackground="#d9d9d9",
        relief="raised",
        bd=1,
        padx=10,
        pady=4
    )
    save_button.pack(fill="x", pady=(0, 10))

    clear_button = tk.Button(
        button_frame,
        text="CLEAR FIELDS", #clear
        command=clear_fields,
        font=("Arial", 10, "bold"),
        bg="#e6e6e6",
        activebackground="#d9d9d9",
        relief="raised",
        bd=1,
        padx=10,
        pady=4
    )
    clear_button.pack(fill="x")

    # bottom area for messages and reset button
    bottom_frame = tk.Frame(center_frame)
    bottom_frame.pack(side=tk.BOTTOM, fill="x")

    status_label = tk.Label(
        bottom_frame,
        text="",
        font=("Arial", 10),
        wraplength=420,
        justify="center"
    )
    status_label.pack(pady=(18, 0))

    reset_button = tk.Button(

        bottom_frame,
        text="Reset", #resert
        command=reset_all_data,
        font=("Arial", 10, "bold"),
        bg="#e6e6e6",
        activebackground="#d9d9d9",
        relief="raised",
        bd=1,
        padx=10,
        pady=4
    )



    # decide startup mode
    check_vault_state()
    update_auth_ui()
    hide_credentials_section()

    window.mainloop()





if __name__ == "__main__":
    main()