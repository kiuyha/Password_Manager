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
     3. **Remove**: Allows you to remove a password by specifying its index. Multiple
