import json
from flask import Flask, request, jsonify, render_template_string
import spacy

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Load JSON data
with open('data.json') as f:
    data = json.load(f)

def query_energy_data(data, year, sector):
    # Initialize the total consumption
    total_consumption = 0
    
    # Check if the data contains annual data for the given year
    if "Annual Data" in data:
        for record in data["Annual Data"]:
            if record.get("Year") == year:
                # Get the key for total energy consumed by the given sector
                key = f"Total Energy Consumed by the {sector} Sector"
                return record.get(key, "Data not available")
    
    # Check if the data contains monthly data for the given year
    if "Monthly Data" in data:
        for record in data["Monthly Data"]:
            if record.get("Month", "").endswith(str(year)):
                # Get the key for total energy consumed by the given sector
                key = f"Total Energy Consumed by the {sector} Sector"
                total_consumption += record.get(key, 0)
        
        # Return the total consumption if monthly data is found
        if total_consumption > 0:
            return total_consumption
    
    return "Data not available"

def parse_query(query):
    doc = nlp(query)
    year = None
    sector = None
    
    # Extract year
    for ent in doc.ents:
        if ent.label_ == "DATE":
            year_text = ent.text
            # Extracting year from the text
            for token in year_text.split():
                if token.isdigit() and len(token) == 4:
                    year = int(token)
                    break
    
    # Extract sector
    for token in doc:
        if token.text.lower() in ["residential", "commercial", "industrial"]:
            sector = token.text.capitalize()
            break
    
    return year, sector

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
        <!doctype html>
        <html>
        <head>
            <title>Energy Consumption Query</title>
        </head>
        <body>
            <h1>Query Energy Consumption Data</h1>
            <form action="/query" method="post">
                <label for="query">Ask a question:</label>
                <input type="text" id="query" name="query" style="width: 400px;"><br><br>
                <input type="submit" value="Submit">
            </form>
            {% if result %}
            <h2>Result:</h2>
            <p>{{ result }}</p>
            {% endif %}
        </body>
        </html>
    ''')

@app.route('/query', methods=['POST'])
def query():
    user_query = request.form['query']
    year, sector = parse_query(user_query)
    
    if year and sector:
        result = query_energy_data(data, year, sector)
    else:
        result = "Could not parse the query. Please ensure you specify a year and a sector."
    
    return render_template_string('''
        <!doctype html>
        <html>
        <head>
            <title>Energy Consumption Query</title>
        </head>
        <body>
            <h1>Query Energy Consumption Data</h1>
            <form action="/query" method="post">
                <label for="query">Ask a question:</label>
                <input type="text" id="query" name="query" style="width: 400px;"><br><br>
                <input type="submit" value="Submit">
            </form>
            <h2>Result:</h2>
            <p>{{ result }}</p>
        </body>
        </html>
    ''', result=result)

if __name__ == "__main__":
    app.run(debug=True)
