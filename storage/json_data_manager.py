import json
from datetime import date
import os

# Get the directory of the Flask app
app_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the expenses.json file
expenses_filename = os.path.join(app_dir, 'expenses.json')

# Path to the json_data_source.json file
data_filename = os.path.join(app_dir, 'json_data_source.json')

# Fetching source database from json file
def get_data_json(source_filename):
    with open(source_filename, 'r') as file:
        source_data = json.loads(file.read())
    return source_data

# store the data to json filename
def save_to_json(filename, database):
    json_str = json.dumps(database)
    with open(filename, 'w') as file:
        file.write(json_str)


# Fetching the reason and details from source file.
reasons_details = get_data_json(data_filename)

# Get all the reason from source data
def get_reason_list():
    reason_list = []
    for i in range(len(reasons_details)):
        reason_list.append(reasons_details[i]['name'])
    return reason_list

# Get all the details, price from source data based on the reason
def get_details_list(reason_name):
    source_details_list = []
    for line in reasons_details:
        if line['name'].upper() == reason_name.upper():
            for i in range(len(line['details'])):
                name = line['details'][i]['name']
                price = line['details'][i]['price']
                supply = line['details'][i]['supply']
                source_details_list.append((name, price, supply))
    return source_details_list

# Get the price based on reason and details
def get_price(detail):
    price_list = []
    for line in reasons_details:
        for i in range(len(line['details'])):
            price_line = {
                f"{line['details'][i]['name']}": f"{line['details'][i]['price']}"
            }
            price_list.append(price_line)
    for item in price_list:
        for key, value in item.items():
            if key.lower() == detail.lower():
                return int(value)

# Get the supply price should pay based on reason and details
def get_supply_price(detail):
    supply_price_list = []
    for line in reasons_details:
        for i in range(len(line['details'])):
            supply_price_line = {
                f"{line['details'][i]['name']}": f"{line['details'][i]['supply']}"
            }
            supply_price_list.append(supply_price_line)
    for item in supply_price_list:
        for key, value in item.items():
            if key.lower() == detail.lower():
                return int(value)

# print(get_supply_price('dau do'))

# Fetch data from all json files in a directory
def get_data_json_files(directory):
    data = []

    # Iterate over each file in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                file_data = json.load(file)
                data.extend(file_data)

    return data

# fetching all patients as time_key (day, month) and number
def list_patients(time_key, number):
    all_data = []
    current_date = date.today()
    year = str(current_date.year)
    month = str(current_date.month)

    time_key_list = ['day', 'month']
    if time_key.lower() in time_key_list:
        if time_key.lower() == 'day' and (number >= 1) and (number <= 31):
            # Specify the directory path
            directory_path = os.path.join(app_dir, 'data', year, month)
            filename = f'patients_{number}.json'
            file_path = os.path.join(directory_path, filename)

            if os.path.exists(file_path):
                all_data = get_data_json(file_path)

        elif time_key.lower() == 'month' and (number >= 1) and (number <= 12):
            month_number = str(number)
            # Specify the directory path
            directory_path = os.path.join(app_dir, 'data', year, month_number)
            all_data = get_data_json_files(directory_path)

        else:
            print('first error')
    else:
        print('error')

    return all_data

# data = list_patients('month', 7)
# print(data)


"""check the directory and file mandatory to store the patients database
example is July 01, 2023 - means patients will be stored in patients_01.json that 
placed in directory 07 which is placed in another directory name 2023
path: storage/data/2023/07/patients_01.json"""
def save_patients(patient_data):

    current_date = date.today()
    current_day = int(current_date.day)
    year = str(current_date.year)
    month = str(current_date.month)
    filename = f'patients_{current_day}.json'
    directory_path = os.path.join('storage/data', year, month)

    # Create the directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    file_path = os.path.join(directory_path, filename)

    if os.path.exists(file_path):
        existing_patients = list_patients('day', current_day)
    else:
        existing_patients = []

    existing_patients.append(patient_data)
    json_str = json.dumps(existing_patients)

    with open(file_path, 'w') as file:
        file.write(json_str)

def patients_filter(key_word):
    current_date = date.today()
    month = int(current_date.month)
    data = []

    source_data = list_patients('month', month)
    for line in source_data:
        for i in range(len(line['reason'])):
            if line['reason'][i] == key_word.upper():
                filter_patient = {
                    'date': line['date'],
                    'name': line['name'],
                    'birth_year': line['birth_year'],
                    'address': line['address'],
                    'phone': line['phone'],
                    'note': line['note'],
                    'reason': line['reason'][i],
                    'detail': line['details'][i],
                    'price': line['price'][i]
                }
                data.append(filter_patient)
    return data

def patients_year(year):

    directory_path = os.path.join(app_dir, 'data', year)
    data = []

    # Recursively iterate over all directories and files in the current directory
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith(".json"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    file_data = json.load(file)
                    data.extend(file_data)

    return data
