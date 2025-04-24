from flask import Flask, render_template, request, redirect, url_for
import os, csv
from datetime import datetime

app = Flask(__name__)

# show index page
@app.route('/')
def index():
    return render_template('index.html')

# save data to csv
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict(flat=False)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"record_{now}.csv"

    os.makedirs('uploads', exist_ok=True)
    with open(os.path.join('uploads', filename), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Key', 'Value'])
        for key, values in data.items():
            for value in values:
                writer.writerow([key, value])

    return redirect(url_for('index'))  # submit and redirect to index

if __name__ == '__main__':
    app.run(debug=True)
