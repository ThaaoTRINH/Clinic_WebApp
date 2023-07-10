from flask import Flask, render_template, request
from datetime import date, datetime
from storage import json_data_manager

app = Flask(__name__)


# Registration the patient information
@app.route('/', methods=['GET', 'POST'])
def register():

    # convert the current day to asia date format
    current_date_show = date.today().strftime('%d/%m/%Y')
    # current_date = date.today()

    # fetching the source from the function in source file
    source_details_dict = {}
    source_reason_list = json_data_manager.get_reason_list()
    for reason in source_reason_list:
        source_details_dict[reason] = json_data_manager.get_details_list(reason)

    if request.method == 'POST':
        name = request.form['name']
        birth_year = request.form['birth_year']
        address = request.form['address']
        phone = request.form['phone']
        note = request.form['note']

        # Process the form submission
        reason_list = request.form.getlist('option')
        details_list_get = request.form.getlist('select_option')

        # remove the ' ' from details list
        details_list = []
        for detail in details_list_get:
            if detail != ' ':
                details_list.append(detail)

        # Count the amount which the patient should pay after visiting
        price_list = []
        for detail in details_list_get:
            price = json_data_manager.get_price(detail)
            if price is not None:
                price_list.append(price)
        amount = sum(price_list)
        formatted_amount = format(amount, ',')

        supply_price_list = []
        for detail in details_list_get:
            supply_price = json_data_manager.get_supply_price(detail)
            if supply_price is not None:
                supply_price_list.append(supply_price)

        current_date = date.today()
        current_day = int(current_date.day)
        # Fetch the patients list to get the next number id

        existing_ids = [line['number_id'] for line in json_data_manager.list_patients('day', current_day)] if \
            json_data_manager.list_patients('day', current_day) else 0
        max_id = max(existing_ids) if existing_ids else 0

        new_id = max_id + 1

        # create a new patient instance
        patient_info = {
            "number_id": new_id + 1,
            "date": current_date_show,
            "name": name,
            "birth_year": birth_year,
            "address": address,
            "phone": phone,
            "note": note,
            "reason": reason_list,
            "details": details_list,
            "price": price_list,
            'supply': supply_price_list
        }
        json_data_manager.save_patients(patient_info)

        return render_template('patient_show.html', current_date=current_date_show, number_id=new_id, date=date,
                               name=name, birth_year=birth_year,
                               address=address, phone=phone, note=note, reason=reason_list, details=details_list,
                               price=price_list, amount=formatted_amount)

    return render_template('registration.html', current_date=current_date_show, reason_list=source_reason_list,
                           details_dict=source_details_dict)

# Display all existing patients
@app.route('/patients_list', methods=['GET'])
def patients_list():
    current_date = date.today()
    month = int(current_date.month)
    data = json_data_manager.list_patients('month', month)
    search_key = 'Tong ket thang'
    total_amount = 0

    for i in range(len(data)):
        amount = sum(data[i]['price'])
        total_amount += amount
    formatted_total_amount = format(total_amount, ",")

    return render_template('patients_export.html', data=data, search=search_key, total_amount=formatted_total_amount)

# Filter all existing patients
@app.route('/filter/<key_word>', methods=['GET'])
def patients_filter(key_word):
    total_amount = 0
    cases = 0

    # set a key_word for searching
    if key_word.lower() == 'xnm':
        key_word = 'XET NGHIEM MAU'

    # Filter the existing patients by month
    source_data = json_data_manager.patients_filter(key_word)
    for line in source_data:
        total_amount += line['price']
        cases += 1
    search_key = f'Nguyen nhan dieu tri - "{key_word.upper()}"'

    formatted_total_amount = format(total_amount, ",")

    return render_template('patients_filter.html', data=source_data, cases=cases,
                           search=search_key, total_amount=formatted_total_amount)

# Display all fee should pay to supplier
@app.route('/patients_supply', methods=['GET'])
def patients_supply():
    current_date = date.today()
    month = int(current_date.month)
    data = json_data_manager.list_patients('month', month)
    search_key = 'Tong chi tra nha cung cap'
    total_amount = 0

    for i in range(len(data)):
        amount = sum(data[i]['supply'])
        total_amount += amount
    formatted_total_amount = format(total_amount, ",")

    return render_template('patients_supply.html', data=data, search=search_key, total_amount=formatted_total_amount)

# Listing the expenses in a current month
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    current_month = date.today().month
    current_year = date.today().year
    time_show = f'{current_month}/{current_year}'
    # load all expense from expenses.json
    expenses_filename = json_data_manager.expenses_filename
    existing_expenses = json_data_manager.get_data_json(expenses_filename)

    if request.method == 'POST':
        day = request.form['day']
        description = request.form['description']
        quantity = request.form['quantity']
        unit = request.form['unit']
        unit_price = request.form['unit_price']
        amount = int(quantity) * int(unit_price)
        note = request.form['note']

        expenses_list = request.form.get('expenses_select')

        expense = {
            'day': day,
            'description': description,
            'quantity': quantity,
            'unit': unit,
            'unit_price': unit_price,
            'amount': amount,
            'expenses': expenses_list,
            'note': note
        }
        existing_expenses.append(expense)

        # Save expenses to exist json file
        json_data_manager.save_to_json(expenses_filename, existing_expenses)

        return render_template('expenses.html')
    return render_template('expenses.html', time_show=time_show)

# Listing the expenses in a current month
@app.route('/expenses_show', methods=['GET'])
def expenses_show():

    # load all expense from expenses.json
    expenses_filename = json_data_manager.expenses_filename
    existing_expenses = json_data_manager.get_data_json(expenses_filename)

    sum_thuoc = 0
    sum_vpp = 0
    sum_vh = 0
    for line in existing_expenses:
        if line['expenses'] == 'Thuoc - Vat tu y te':
            sum_thuoc += line['amount']
        elif line['expenses'] == 'Van phong pham':
            sum_vpp += line['amount']
        else:
            sum_vh += line['amount']
    totally_amount = format(sum_thuoc + sum_vpp + sum_vh, ',')
    return render_template('expenses_show.html', expenses_list=existing_expenses, sum_thuoc=format(sum_thuoc, ','),
                           sum_vpp=format(sum_vpp, ','), sum_vh=format(sum_vh, ','),
                           totally_amount=totally_amount)

# Fetching all patients in current year and search by keyword
@app.route('/search_patient/search_date', methods=['GET', 'POST'])
def search_patient_date():
    # Extract all patients in current year
    current_date = date.today()
    year = str(current_date.year)
    source_data = json_data_manager.patients_year(year)

    if request.method == 'POST':
        date_search = request.form['date_search']
        date_obj = datetime.strptime(date_search, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d/%m/%Y")

        search_patient_list = []

        for line in source_data:
            if formatted_date == line['date']:
                search_patient_list.append(line)

        return render_template('patients_export.html', data=search_patient_list)

    return render_template('registration.html')

# Fetching all patients in current year and search by keyword
@app.route('/search_patient/search_name', methods=['GET', 'POST'])
def search_patient_name():
    # Extract all patients in current year
    current_date = date.today()
    year = str(current_date.year)
    source_data = json_data_manager.patients_year(year)

    if request.method == 'POST':
        name_search = request.form['patient_search']

        search_patient_list = []

        for line in source_data:
            if (name_search.upper() in str(line['name']).upper()) \
                    or (name_search.upper() in str(line['reason']).upper()) or (name_search == line['phone']):
                search_patient_list.append(line)

        return render_template('patients_export.html', data=search_patient_list)

    return render_template('registration.html')

# Fetching all patients in current year and search by keyword
@app.route('/search_patient/search_month', methods=['GET', 'POST'])
def search_patient_month():

    if request.method == 'POST':
        month_search = request.form['month_search']
        year_search = request.form['year_search']

        # Extract all patients in current year
        source_data = json_data_manager.patients_year(year_search)

        search_patient_list = []
        for line in source_data:
            if int(line['date'][3:5]) == int(month_search):
                search_patient_list.append(line)

        return render_template('patients_export.html', data=search_patient_list)

    return render_template('registration.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
