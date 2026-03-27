import tkinter as tk
from tkinter import messagebox, ttk

from storage import load_vault, save_vault
from crypto_utils import (
    generate_salt,
    derive_key,
    encrypt_password,
    decrypt_password,
    bytes_to_base64,
    base64_to_bytes,
)

# app.py
# This file runs the password manager UI
# it connects user input with the backed logic (encryption + storage)


def main():
    # Create the main app window
    window = tk.Tk() #initialize the Tkinter app
    window.title("Password Manager") # title
    window.geometry("500x540") # window size
    window.resizable(False, False) # prevent resizing to keep consistency

    # Load eye icons from /assets for password hide/show toggle
    try:
        eye_open_img_raw = tk.PhotoImage(file="assets/eye_open.png")
        eye_closed_img_raw = tk.PhotoImage(file="assets/eye_closed.png")

        # Resize images using subsample
        eye_open_img = eye_open_img_raw.subsample(18, 18)
        eye_closed_img = eye_closed_img_raw.subsample(18, 18)

    except Exception:
        # Fallback in case images are missing or path is incorrect
        eye_open_img = None
        eye_closed_img = None

    # Track whether passwords are visible or hidden (show/hide toggle)
    show_master_password = False
    show_saved_password = False

    # Hide master password again
    def hide_master_password():
        nonlocal show_master_password #allows modifying outer variable
        show_master_password = False # reset to hidden state
        master_entry.config(show="*") # hide/mask input with *
        master_toggle_button.config(image=eye_open_img) # reset icon to hidden/default state

    # Hide saved password again
    def hide_saved_password():
        nonlocal show_saved_password
        show_saved_password = False
        password_entry.config(show="*") # hide password again
        password_toggle_button.config(image=eye_open_img) # reset icon to hidden/default state

    # Function to show/hide the master password
    # Uses eye icons instead of text
    def toggle_master_password():
        nonlocal show_master_password
        show_master_password = not show_master_password # switch between true/false

        # if visible,then remove masking
        if show_master_password:
            master_entry.config(show="") # show the actual text
            master_toggle_button.config(image=eye_closed_img)
        else:
            # if hidden, then mask again
            master_entry.config(show="*")
            master_toggle_button.config(image=eye_open_img)

    # Function to show / hide the saved password
    # Same logic as master password but for the stored password part
    def toggle_saved_password():
        nonlocal show_saved_password
        show_saved_password = not show_saved_password

        if show_saved_password:
            password_entry.config(show="") # show password
            password_toggle_button.config(image=eye_closed_img)
        else: 
            password_entry.config(show="*") # hide password
            password_toggle_button.config(image=eye_open_img)





    # Clear visible fields
    # This clears the main editable fields in the form
    def clear_fields():
        service_entry.delete(0, tk.END) # remove text
        username_entry.delete(0, tk.END) # remove username
        password_entry.delete(0, tk.END) #remove password
        status_label.config(text="") # clear any old success/error message
        hide_saved_password() # make sure the password field goes back to hidden mode

    # Clear only loaded data when service changes
    # If the user starts typing a different service, it clears the old retrieved details on the screen
    def clear_loaded_data():
        username_entry.delete(0, tk.END) # clear loaded username
        password_entry.delete(0, tk.END) #clear password
        status_label.config(text="") # remove old message as context changed
        hide_saved_password() # hide password again

    # Reset loaded data when service changes
    # Triggered while typing in the service field
    def on_service_change(event=None):
        clear_loaded_data()
        hide_master_password()


    # Load saved services into the combobox
    # Only loads services if the correct master password is provided
    def refresh_service_list():
        master_password = master_entry.get()  # get entered master password

        # Prevent loading services without authentication from master password
        if not master_password:
            status_label.config(text="Enter master password to load services.", fg="red")
            return

        vault = load_vault()

        # If no data exists, nothing to load
        if vault["salt"] is None or not vault["entries"]:
            service_entry["values"] = []
            return

        # Recreate key using entered master password
        salt = base64_to_bytes(vault["salt"])
        key = derive_key(master_password, salt)

        # Validate master password using first entry
        try:
            first_entry = vault["entries"][0]
            nonce = base64_to_bytes(first_entry["nonce"])
            ciphertext = base64_to_bytes(first_entry["ciphertext"])
            decrypt_password(ciphertext, nonce, key)
        except Exception:
            status_label.config(text="Wrong master password. Cannot load services.", fg="red") # if decryption fails, password is incorrect
            return

        # If valid, then load services
        services = [entry["service"] for entry in vault["entries"]]

        # Remove duplicates and sort
        unique_services = sorted(set(services), key=str.lower)

        service_entry["values"] = unique_services

        status_label.config(text="Services loaded.", fg="green")



    # Function to save a password
    # This handles the full save flow: get user input -> validate -> prepare encryption -> save safely in the vault
    def save_password():
        master_password = master_entry.get() # the password used to unlock the vault
        service = service_entry.get().strip() # service name (trim spaces from start/end)
        username = username_entry.get().strip() # username for the service
        password = password_entry.get() # actual password to store

        # Check if all fields are filled in
        # Saving should only happen when the user provided all required data
        if not master_password or not service or not username or not password:
            clear_fields()
            hide_master_password()
            status_label.config(text="Please fill in all fields.", fg="red")
            return # stop here if any field is missing

        # Load current vault data (JSON file)
        vault = load_vault()

        # Create a salt if the vault does not have one yet
        # Needed for key derivation and is generated only once for a vault
        if vault["salt"] is None:
            salt = generate_salt() # create a new random salt
            vault["salt"] = bytes_to_base64(salt) # convert bytes to text so JSON can store it
            save_vault(vault) # save the new salt
        else:
            salt = base64_to_bytes(vault["salt"]) # conver stored Base64 text back into bytes

        # Create the encryption key from the master password (master password is first turned into a key using PBKDF2)
        key = derive_key(master_password, salt)

        # If vault already has entries, verify the master password first
        #Prevents user from saving new data with the wrong master password
        if vault["entries"]:
            try:
                first_entry = vault["entries"][0] # use an existing entry to test the key
                test_nonce = base64_to_bytes(first_entry["nonce"])
                test_ciphertext = base64_to_bytes(first_entry["ciphertext"])
                decrypt_password(test_ciphertext, test_nonce, key) # if this fails, password is wrong
            except Exception:
                hide_master_password()
                status_label.config(text="Wrong master password. Cannot save password.", fg="red")
                return

        # Encrypt the password
        # Service password is encrypted before storing it
        nonce, ciphertext = encrypt_password(password, key)

        # Create entry to save
        # Nonce and ciphertext are converted to Base64 so be stored in JSON
        entry = {
            "service": service,
            "username": username,
            "nonce": bytes_to_base64(nonce),
            "ciphertext": bytes_to_base64(ciphertext),
        }

        # Check if service already exists (avoids duplicate entries for the same service)
        existing_index = None

        for i, saved_entry in enumerate(vault["entries"]):
            if saved_entry["service"].lower() == service.lower():
                existing_index = i # remember where the existing service is stored
                break

        # If duplicate found, ask user before overwriting (gives the user control instead of replacing data automatically)
        if existing_index is not None:
            confirm = messagebox.askyesno(
                "Duplicate Entry",
                f"An entry for '{service}' already exists.\nDo you want to overwrite it?"
            )

            if confirm:
                vault["entries"][existing_index] = entry # replace old entry with new one
                status_label.config(text="Password updated successfully.", fg="green")
            else:
                hide_master_password()
                hide_saved_password()
                status_label.config(text="Save cancelled.", fg="red")
                return
        else: 
            vault["entries"].append(entry) # add as new entry if no duplicate exists
            status_label.config(text="Password saved successfully.", fg="green")

        save_vault(vault) # save the updated vault
        refresh_service_list() 

        # Clear normal input fields after saving (clears sensitive input on the screen)
        service_entry.delete(0, tk.END)
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

        # Hide passwords again after saving (hide should always be the default one)
        hide_master_password()
        hide_saved_password()

    # Function to load a password
    # reverse process: get user input -> validate -> recreate key -> find entry -> decrypt and display it
    def load_password():
        master_password = master_entry.get() # password used to unlock the vault
        service = service_entry.get().strip() #service to search for

        # Check required fields
        # To load an entry, at least master password and service name must be provided
        if not master_password or not service:
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            hide_master_password()
            hide_saved_password()
            status_label.config(text="Enter master password and service.", fg="red")
            return

        # Load current vault data
        vault = load_vault()

        # Check if vault has a salt
        if vault["salt"] is None:
            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            hide_master_password()
            hide_saved_password()
            status_label.config(text="No saved passwords found.", fg="red")
            return

        # Recreate the key from master password
        # The same salt + same master password should produce the same key as before
        salt = base64_to_bytes(vault["salt"])
        key = derive_key(master_password, salt)

        # Search for the matching service (case-insensitive)
        for entry in vault["entries"]:
            if entry["service"].lower() == service.lower():
                try:
                    nonce = base64_to_bytes(entry["nonce"])
                    ciphertext = base64_to_bytes(entry["ciphertext"])
                    decrypted_password = decrypt_password(ciphertext, nonce, key)

                    # Fill the fields with loaded data
                    username_entry.delete(0, tk.END)
                    username_entry.insert(0, entry["username"])

                    password_entry.delete(0, tk.END)
                    password_entry.insert(0, decrypted_password)

                    # Always hide passwords by default after loading
                    hide_master_password()
                    hide_saved_password()

                    status_label.config(text="Password loaded successfully.", fg="green")
                    return
                except Exception:
                    # if decryption fails, it usually means master password was wrong or stored data is damaged/correcpted
                    username_entry.delete(0, tk.END)
                    password_entry.delete(0, tk.END)
                    hide_master_password()
                    hide_saved_password()
                    status_label.config(text="Wrong master password or corrupted data.", fg="red")
                    return

        # if no matching service was found, clear old output data
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        hide_master_password()
        hide_saved_password()
        status_label.config(text="Service not found.", fg="red")



    # App title (shown at the top of the window)
    title_label = tk.Label(window, text="Password Manager", font=("Arial", 16, "bold"))
    title_label.pack(pady=10) # vertical spacing for better layout

    # Master password
    master_label = tk.Label(window, text="Master Password")
    master_label.pack()

    # used to place input field and button side by side
    master_frame = tk.Frame(window)
    master_frame.pack(pady=5)

    # entry field for master password with *
    master_entry = tk.Entry(master_frame, show="*", width=25)
    master_entry.pack(side=tk.LEFT)
    master_entry.bind("<Return>", lambda event: refresh_service_list()) # Load services when user finishes typing master password
    # Also trigger when focus leaves the master password field
    master_entry.bind("<FocusOut>", lambda event: refresh_service_list())

    # Button to toggle hide/show of master password (eye icon instead of text)
    master_toggle_button = tk.Button(
        master_frame,
        image=eye_open_img,
        command=toggle_master_password,
        borderwidth=0
    )
    master_toggle_button.pack(side=tk.LEFT, padx=5)


    # Service name using a Combobox
    service_label = tk.Label(window, text="Service")
    service_label.pack()

    # Combobox behaves as both input field and dropdown
    service_entry = ttk.Combobox(window, width=28)
    service_entry.pack(pady=5)

    # check changes when user types OR selects from dropdown to ensures old loaded data is cleared when typed
    service_entry.bind("<KeyRelease>", on_service_change)
    service_entry.bind("<<ComboboxSelected>>", on_service_change)



    # Username (username associated with the service)
    username_label = tk.Label(window, text="Username")
    username_label.pack()
    username_entry = tk.Entry(window, width=30)
    username_entry.pack(pady=5)

    # Password (password to be encrypted)
    password_label = tk.Label(window, text="Password")
    password_label.pack()

    password_frame = tk.Frame(window) # align password input and toggle button horizontally
    password_frame.pack(pady=5)
   
    # Password input field (hidden by default)
    password_entry = tk.Entry(password_frame, show="*", width=25)
    password_entry.pack(side=tk.LEFT)

    # Button to toggle hide/show saved password (eye icon style as the master password field)
    password_toggle_button = tk.Button(
        password_frame,
        image=eye_open_img,
        command=toggle_saved_password,
        borderwidth=0
    )
    password_toggle_button.pack(side=tk.LEFT, padx=5)

    # Save button (triggers encryption + storage process)
    save_button = tk.Button(window, text="Save Password", width=20, command=save_password)
    save_button.pack(pady=5)

    # Load button (retrieves and decrypts a stored password)
    load_button = tk.Button(window, text="Load Password", width=20, command=load_password)
    load_button.pack(pady=5)

    # Clear button
    clear_button = tk.Button(window, text="Clear Fields", width=20, command=clear_fields)
    clear_button.pack(pady=5)

    # Status message (display feedback)
    status_label = tk.Label(window, text="", fg="green")
    status_label.pack(pady=10)

    # Run the window (start the GUI)
    window.mainloop()


if __name__ == "__main__":
    main()