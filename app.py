from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import uuid

app = Flask(__name__)

# Load the trained model using pickle
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Global dictionary to store results temporarily
results_store = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    try:
        # Read the Excel file
        df = pd.read_excel(file)

        results = []
        for index, row in df.iterrows():
            # Extract data from the row
            data = {
                'engine_rpm': row['Engine RPM'],
                'oil_pressure': row['Lub oil pressure'],
                'fuel_pressure': row['Fuel pressure'],
                'coolant_pressure': row['Coolant pressure'],
                'oil_temperature': row['Lub oil temperature'],
                'coolant_temperature': row['Coolant temp']
            }

            # Prepare the input for the model
            input_data = np.array([[data['engine_rpm'], data['oil_pressure'], data['fuel_pressure'], data['coolant_pressure'], data['oil_temperature'], data['coolant_temperature']]])

            # Predict engine health status
            prediction = model.predict(input_data)
            engine_health_status = int(prediction[0])

            # Create a unique vehicle ID using UUID
            vehicle_id = uuid.uuid4().int % 10**8

            # Get the current timestamp in YYYYMMDDHHMM format
            timestamp = int(datetime.now().strftime("%Y%m%d%H%M"))

            # Store the data in the global dictionary
            results.append({
                "VEHICLEID": vehicle_id,
                "ENGINEHEALTH": engine_health_status,
                "TIMESTAMP": timestamp
            })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
