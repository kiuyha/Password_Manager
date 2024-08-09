from py7zr.py7zr import SevenZipFile
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

def clipboard(Password,Username = None):
    if Username:
        if input('Do you want to copy the username (y or n)? ').lower() == 'y':
            pyperclip.copy(Username)
            print("Username copied to clipboard.")
    if input('Do you want to copy the password (y or n)? ').lower() == 'y':
        pyperclip.copy(Password)
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

def read_file(Password):
    global data
    global path_file
    global Global_Password
    with SevenZipFile(path_file, 'r', password=Password) as archive:
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
    Global_Password = Password

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
    time.sleep(3)
    clean_screen(0)
    Password = input("Enter a password for the manager (or type 'r' for a random password): ")
    if Password.lower() == 'r':
        Password = password()
        print(f'Random password: {Password}')
        clipboard(Password)
    print('Creating a new password manager...')
    loading_dots(5)
    new_df = pd.DataFrame(columns=['platform', 'Username', 'pass'])
    write_file(new_df)
    print('Password Manager setup has been successful.')
    clean_screen(0)
    read_file(Password)

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
                                '2. Add password with a file\n'\
                                '3. Access existing passwords\n'\
                                '4. Remove old passwords\n'\
                                '5. Remove the Password Manager\n'\
                                "6. Exit\n"\
                                'Choice: ')
            if user_choice == '1':
                self.add_password()
            elif user_choice == '2':
                self.add_File()
            elif user_choice == '3':
                self.access_password()
            elif user_choice == '4':
                self.remove_password()
            elif user_choice == '5':
                self.delete_manager()
            elif user_choice == '6' or user_choice == 'exit':
                break
            else:
                print(f"Sorry, your input is incorrect. Type 'exit' to exit.")
                clean_screen(1)

    def add_password(self):
        clean_screen(0)
        global data
        platform = input('Enter the platform name: ')
        username = input('Enter the desired username: ')
        Password = password()
        new_dic = {'platform': [platform], 'Username': [username], 'pass': [Password]}
        new_data = pd.DataFrame(new_dic)
        try:
            data = pd.concat([data, new_data], ignore_index=True)
            print(f'Addition successful!')
            clean_screen(1)
            print(f"Here is the added data:")
            print(data.tail())
            clipboard(Password)
        except AttributeError:
            print(f'An error occurred: object does not have the concat method.')
        except Exception as e:
            print(f'An error occurred: {e}')

    def Password_index(self):
        global data
        try:
            user_input = input('Index of the password you want ("exit" to exit): ')
            if user_input.lower() == 'exit':
                return
            Password = data.iloc[int(user_input)]['pass']
            Username = data.iloc[int(user_input)]['Username']
            clipboard(Password,Username)
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

    def remove_password(self):
        clean_screen(0)
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
                return self.remove_password()
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

    def add_File(self):
        clean_screen(0)
        global data
        try:
            file_path = input(r'Please enter the path of your file: ').replace('"',"").replace("'","")
            _, extension = os.path.splitext(file_path)
            if extension == '.csv':
                file_df = pd.read_csv(file_path,header=None)
            elif extension == '.xlsx' or extension == '.xls':
                file_df = pd.read_excel(file_path,header=None)
            else:
                print('Sorry the file is not supported. Only support .csv, .xlsx and .xls')
                clean_screen(1)
                return
            print ('File read successfully.')
            clean_screen(1)
        except:
            print('The file was not found. Please check the file path and try again.')
            clean_screen(1)
            return self.add_File()
        desired_columns = ['platform', 'Username', 'pass']
        for df_col in range(0,len(file_df.columns)-1):
            for col in desired_columns:
                result = file_df[file_df[df_col].str.contains(col, case=False, na=False)]
                result_list = result.index.tolist()
                file_df.drop(result_list,axis='index',inplace=True)
        file_df.columns = desired_columns
        data = file_df
    
    def delete_manager(self):
        global path_file
        clean_screen(0)
        user_input = input('Are you sure to delete the password manager(y or n)?')
        if user_input == 'y':
            os.remove(path_file)
            print('Deletion process sucessfuly')
            sys.exit()
        elif user_input == 'n':
            print('Deletion process cancelled!')
            clean_screen(1)
            return
        else:
            print ('Sorry, your input is incorrect')
            clean_screen(1)
            return self.delete_manager()

def main():
    global path_file
    if os.path.exists(path_file):
        try:
            user_input = input('Enter the password manager password: ')
            clean_screen(0)
            read_file(user_input)
        except:
            print(f'Your input is wrong password')
            if user_input.lower() == 'exit':
                exit()
            else:
                main()
    else:
        create_file()
    Choice().user_choice()
    append_file()

if __name__ == '__main__':
    main()          
