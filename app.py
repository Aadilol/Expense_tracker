from flask import Flask, render_template, request, redirect
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient('mongodb+srv://adilal:Illumination12@cluster0.r4du1xf.mongodb.net/?retryWrites=true&w=majority')
db = client['expense_tracker']
expenses_collection = db['expenses']


@app.route('/')
def home():
    expenses = list(expenses_collection.find())
    
    return render_template('index.html', expenses=expenses)


@app.route('/add_expense', methods=['POST'])
def add_expense():
    amount = float(request.form['amount'])
    date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    category = request.form['category']
    person = request.form['person']

    date = datetime.combine(date, datetime.min.time())
    
    expense = {
        'amount': amount,
        'date': date,
        'category': category,
        'person': person
    }
    expenses_collection.insert_one(expense)

    return redirect('/')


@app.route('/remove_expense', methods=['POST'])
def remove_expense():
    expense_id = request.form['expense_id']
    expenses_collection.delete_one({'_id': ObjectId(expense_id)})

    return redirect('/view_persons')

# def add_category():
#     category = request.form['category']
    
#     # Check if category already exists in expenses dictionary
#     if category not in expenses:
#         expenses[category] = {'expenses': [], 'total_amount': 0.0}
    
#     # Recalculate the total amount for the category
#     expenses[category]['total_amount'] = sum(expense['amount'] for expense in expenses[category]['expenses'])
        
#     return render_template('index.html', expenses=expenses)


@app.route('/view_persons')
def view_persons():
    persons_data = {}
    cursor = expenses_collection.find({})  # Assuming 'expenses_collection' is your MongoDB collection
    for expense in cursor:
        person = expense['person']
        if person not in persons_data:
            persons_data[person] = {'expenses': []}
        persons_data[person]['expenses'].append(expense)
    
    return render_template('persons.html', persons=persons_data)


@app.route('/edit_expense', methods=['POST'])
def edit_expense():
    person = request.form['person']
    amount = float(request.form['amount'])
    index = int(request.form['index'])

    # Retrieve the expense for the person from the MongoDB collection
    expenses_data = expenses_collection.find({'person': person})

    # Get the specific expense document using the index
    expense = expenses_data[index]

    # Update the amount field of the expense
    expense['amount'] = amount

    # Update the expense in the MongoDB collection
    expenses_collection.update_one({'_id': expense['_id']}, {'$set': expense})

    return redirect('/view_persons')




@app.route('/view_expenses')
def view_expenses():
    expenses = list(expenses_collection.find())
    return render_template('expenses.html', expenses=expenses)



if __name__ == '__main__':
    app.run(debug=True)
