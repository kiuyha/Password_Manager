from py7zr import SevenZipFile
import pandas as pd
import secrets
import string
import os
import io
import pyperclip
import time
import sys
from cryptography.fernet import Fernet
import tempfile

pd.set_option('display.max_rows', None)
data = None
path_file = 'PasswordManager.7z'
Global_Password = None

def clean_screen(choice):
    if choice:
        input()
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_dots(duration):
    end_time = time.time() + duration
    dots = ['.', '..', '...']
    
    while time.time() < end_time:
        for dot in dots:
            sys.stdout.write(f'\rLoading{dot}')
            sys.stdout.flush()
            time.sleep(1)  # Wait for 1 second
    sys.stdout.write('\rDone!           \n')

def clipboard(password):
    if input('Do you want to copy it (y or n)? ').lower() == 'y':
        pyperclip.copy(password)
        print("Password copied to clipboard.")

def password():
    req = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(req) for i in range(8))
        if (any(c.islower() for c in password) and 
            any(c.isupper() for c in password) and 
            sum(c.isdigit() for c in password) >= 1 and
            any(c in string.punctuation for c in password)): 
            return password

def read_file(password):
    global data
    global path_file
    global Global_Password
    with SevenZipFile(path_file, 'r', password=password) as archive:
        files = archive.readall()
        with files['password'] as obj1:
            encrypt_file = obj1.read()
        with files['key'] as obj2:
            key = obj2.read()
        cipher = Fernet(key)
        decrypt = cipher.decrypt(encrypt_file)
        buffer = io.BytesIO(decrypt)
        dataframe = pd.read_csv(buffer)   
        data = dataframe
    Global_Password = password

def write_file(new_df):
    global path_file
    global Global_Password
    with SevenZipFile(path_file, mode='w', password=Global_Password) as archive:
        buffer = io.BytesIO()
        new_df.to_csv(buffer, index=False)
        csv_byte = buffer.getvalue()
        key = Fernet.generate_key()
        cipher = Fernet(key)
        csv_encrypt = cipher.encrypt(csv_byte)
        with tempfile.NamedTemporaryFile('wb', delete=False) as temp_file1, \
             tempfile.NamedTemporaryFile('wb', delete=False) as temp_file2:
            temp_file1.write(csv_encrypt)
            temp_file1.flush()
            temp_file2.write(key)
            temp_file2.flush()
        archive.write(temp_file1.name, 'password')
        archive.write(temp_file2.name, 'key')
        os.remove(temp_file1.name)
        os.remove(temp_file2.name)

def create_file():
    print('Sorry, it seems the password file does not exist.')
    clean_screen(0)
    password = input("Enter a password for the manager (or type 'r' for a random password): ")
    if password.lower() == 'r':
        password = password()
        print(f'Random password: {password}')
        clipboard(password)
    print('Creating a new password manager...')
    loading_dots(5)
    new_df = pd.DataFrame(columns=['platform', 'Username', 'pass'])
    write_file(new_df)
    print('Password Manager setup has been successful.')
    clean_screen(0)
    read_file(password)

def append_file():
    global data
    try:
        write_file(data)
    except Exception as e:
        print(f'An error occurred: {e}')
    else:
        print('Data has been successfully updated.')
        time.sleep(1.5)
        clean_screen(0)

def display_dataframe_with_range(numbers):
    global data
    df_head = data.head()
    df_tail = data.tail()
    df_with_ellipsis = []
    ellipsis_row = pd.DataFrame([['...']*data.shape[1]], columns=data.columns.tolist(), index=['..'])
    for number in numbers:
        if number - 3 <= 0:
            df_head = data.head(number + 3)
        elif number + 5 >= len(data):
            df_tail = data.tail(len(data) - (number - 2))
        else:
            df_middle = data.iloc[number - 2:number + 3]
            df_with_ellipsis.append(pd.concat([ellipsis_row, df_middle]))
    new_df = pd.concat([df_head] + df_with_ellipsis + [ellipsis_row] + [df_tail])
    return new_df

class Choice:
    def user_choice(self):
        global data
        while True:
            clean_screen(0)
            user_choice = input('What would you like to do?\n'\
                                '1. Add a new password\n'\
                                '2. Access existing passwords\n'\
                                '3. Remove old passwords\n'\
                                "4. Exit\n"\
                                'Choice: ')
            if user_choice == '1':
                self.adding()
            elif user_choice == '2':
                self.access_password()
            elif user_choice == '3':
                self.remove()
            elif user_choice == '4':
                break
            else:
                print(f"Sorry, your input is incorrect. Type 'exit' to exit.")
                clean_screen(1)

    def adding(self):
        clean_screen(0)
        global data
        platform = input('Enter the platform name: ')
        username = input('Enter the desired username: ')
        password = password()
        new_dic = {'platform': [platform], 'Username': [username], 'pass': [password]}
        new_data = pd.DataFrame(new_dic)
        try:
            data = pd.concat([data, new_data], ignore_index=True)
            print(f'Addition successful!')
            clean_screen(1)
            print(f"Here is the added data:")
            print(data.tail())
            clipboard(password)
        except AttributeError:
            print(f'An error occurred: object does not have the concat method.')
        except Exception as e:
            print(f'An error occurred: {e}')

    def Password_index(self):
        global data
        try:
            user_input = int(input('Index of the password you want: '))
            password = data.iloc[user_input]
            clipboard(password)
        except:
            print('Sorry, your input is incorrect. Please enter a number.')
            self.Password_index()

    def access_password(self):
        clean_screen(0)
        global data
        search_platform = input("What platform are you looking for, or type 'all' to see everything: ")
        if search_platform.lower() == 'all':
            result = data
            print(f'Here is the data you are looking for\n{result}')
            self.Password_index()
        else:
            result = data[data['platform'].str.contains(search_platform, case=False, na=False)]
            if result.empty:
                print(f'Sorry, the data you are looking for does not exist.')
                clean_screen(1)
                return self.access_password()
            else:
                print(f'Here is the data you are looking for\n{result}')
                self.Password_index()
        return result

    def remove(self):
        global data
        search_platform = input("What platform are you looking for, or type 'all' to see everything: ")
        if search_platform.lower() == 'all':
            result = data
            print(f'Here is the data you are looking for\n{result}')
        else:
            result = data[data['platform'].str.contains(search_platform, case=False, na=False)]
            if result.empty:
                print(f'Sorry, the data you are looking for does not exist.')
                clean_screen(1)
                return self.remove()
            else:
                print(f'Here is the data you are looking for\n{result}')
        
        if not result.empty:
            remove_index = input('Index to be deleted (if more than one, separate with commas (,)): ').split(',')
            remove_index_int = list(map(int, remove_index))
            try:
                data.drop(remove_index_int, axis='index', inplace=True)
                data.reset_index(drop=True, inplace=True)
                print(f'Deletion successful!')
                clean_screen(1)
                print(f"Here is the data that has been deleted:")
                print(display_dataframe_with_range(remove_index_int))
                clean_screen(1)
            except AttributeError:
                print(f'An error occurred: object does not have the drop method.')
            except Exception as e:
                print(f'An error occurred: {e}')

def main():
    global path_file
    if os.path.exists(path_file):
        try:
            user_input = input('Enter the password manager password: ')
            clean_screen(0)
            read_file(user_input)
            choice = Choice()
            choice.user_choice()
            append_file()
        except Exception as e:
            print(f'Your input is incorrect: {e}')
            if user_input.lower() == 'exit':
                exit()
            else:
                main()
    else:
        create_file()

if __name__ == '__main__':
    main()