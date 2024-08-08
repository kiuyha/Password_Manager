# Password Manager

This Password Manager uses encryption, compression, and other techniques to securely manage your passwords. Below is an overview of how the program works:

## Features
- **Encryption**: Encrypts your passwords using the `cryptography` module.
- **Compression**: Stores encrypted passwords in a `.7z` file using the `py7zr` module.
- **Clipboard Integration**: Copies passwords to your clipboard using the `pyperclip` module.
- **Random Password Generation**: Generates strong random passwords using the `secrets` module.

## How It Works
1. **Startup**:
   - On the first run, the program will ask you to set a password for the manager. You can either set your own password or allow the program to generate a random one using the `secrets` module.
   - If this is not your first time using the program, it will ask for the password you previously set.

2. **Data Storage**:
   - A `pandas` DataFrame is created with three columns: `platform`, `username`, and `pass`.
   - The DataFrame is converted to a `.csv` format and stored in a buffer using the `io` module. This avoids writing sensitive data to disk, reducing the risk of malware reading it.

3. **Encryption and Compression**:
   - The `.csv` file in the buffer is encrypted using the `cryptography` module.
   - Both the encrypted file and the encryption key are stored in a `.7z` archive, which is password-protected using the password set earlier. The `py7zr` module is used for this process.

4. **File Reading**:
   - The program can read the `.7z` file using the `SevenZipFile` class from the `py7zr` module. Since the file is returned as a dictionary, the program separates the password and the key.
   - The encrypted file is then decrypted using the stored key.

5. **User Interaction**:
   - The program provides four options:
     1. **Add**: Allows you to add a new password. You will be prompted for the platform and username. The new data is combined with the existing data using `.concat`, and the updated DataFrame is displayed.
     2. **Access**: Allows you to search for a specific platform and displays the corresponding passwords. You can select an index to copy the password to your clipboard.
     3. **Remove**: **Remove a Password**: Similar to accessing passwords, but instead of copying, you can select and delete entries by their index. Multiple indexes can be deleted at once by inputting a list. The program uses `.drop()` to remove the selected rows.
     4. 4. **Exit the Program**:After any changes (addition, access, or removal), the program will overwrite the existing `.7z` file, using the same principles as when creating a new password manager. The encryption key changes each time the file is overwritten, enhancing security.

6. **Security Features**
   - The use of in-memory operations (RAM) ensures that sensitive data isn't exposed on disk.
   - Each time the data is modified and saved, a new encryption key is generated, making the data more secure against repeated attacks.
