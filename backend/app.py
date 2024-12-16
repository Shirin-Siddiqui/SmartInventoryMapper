from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
from app.Preprocess import preprocess_data, compute_and_save_embeddings
from app.Mapper import run_matching_pipeline
from app.AccuracyCheck  import calculate_accuracy
import json


app = Flask(__name__)

CORS(app)  # Allow all origins

# Set the folder to store uploaded files and processed output
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for uploading files
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        filename1 = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        filename2 = os.path.join(app.config['UPLOAD_FOLDER'], file2.filename)

        file1.save(filename1)
        file2.save(filename2)

        return jsonify({
            'message': 'Files uploaded successfully'
        }), 200
    else:
        return jsonify({'message': 'Invalid file format. Only CSV files are allowed.'}), 400

# Route for preprocessing data
@app.route('/preprocess', methods=['POST'])
def preprocess_files():
    try:
        external_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Data_External.csv')
        internal_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Data_Internal.csv')

        if not os.path.exists(external_file) or not os.path.exists(internal_file):
            return jsonify({'message': 'Uploaded files not found'}), 404

        # Load and preprocess the files
        data_external = pd.read_csv(external_file)
        data_internal = pd.read_csv(internal_file)

        data_external_preprocessed = preprocess_data(data_external, "PRODUCT_NAME")
        data_internal_preprocessed = preprocess_data(data_internal, "LONG_NAME")

        # Save preprocessed files
        external_processed_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Processed_External.csv')
        internal_processed_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Processed_Internal.csv')

        data_external_preprocessed.to_csv(external_processed_file, index=False)
        data_internal_preprocessed.to_csv(internal_processed_file, index=False)

        # Compute and save embeddings
        external_embeddings_file = os.path.join(app.config['UPLOAD_FOLDER'], 'External_Embeddings.pkl')
        internal_embeddings_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Internal_Embeddings.pkl')

        compute_and_save_embeddings(data_external_preprocessed, 'original_name', 'cleaned_name', external_embeddings_file)
        compute_and_save_embeddings(data_internal_preprocessed, 'original_name', 'cleaned_name', internal_embeddings_file)

        return jsonify({
            'message': 'Preprocessing and embedding completed successfully',
            'external_processed_file': external_processed_file,
            'internal_processed_file': internal_processed_file,
            'external_embeddings_file': external_embeddings_file,
            'internal_embeddings_file': internal_embeddings_file
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error during preprocessing: {str(e)}'}), 500

# Route for running the matching pipeline
@app.route('/match', methods=['POST'])
def run_matching():
    try:
        external_embeddings_file = os.path.join(app.config['UPLOAD_FOLDER'], 'External_Embeddings.pkl')
        internal_embeddings_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Internal_Embeddings.pkl')

        if not os.path.exists(external_embeddings_file) or not os.path.exists(internal_embeddings_file):
            return jsonify({'message': 'Embeddings files not found. Please preprocess the data first.'}), 404

        # Load embeddings
        data_external = pd.read_pickle(external_embeddings_file)
        data_internal = pd.read_pickle(internal_embeddings_file)

        # Run the matching pipeline
        matches = run_matching_pipeline(data_external, data_internal, threshold=0.8)

        # Save the results
        results_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Matched_Results.csv')
        matches.to_csv(results_file, index=False)

        return jsonify({
            'message': 'Matching pipeline executed successfully',
            'results_file': results_file
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error during matching: {str(e)}'}), 500

# Route for downloading the final product list
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Ensure we are serving the file from the correct directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404

# Route for fetching the matched results as JSON
@app.route('/view-mapped', methods=['GET'])
def view_mapped_results():
    try:
        results_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Matched_Results.csv')

        if not os.path.exists(results_file):
            return jsonify({'message': 'Matched results file not found.'}), 404

        # Read the CSV file into a DataFrame and convert to JSON
        df = pd.read_csv(results_file).fillna("")  # Fill NaN with empty strings
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify({'message': f'Error fetching mapped results: {str(e)}'}), 500



@app.route('/check-accuracy', methods=['POST'])
def check_accuracy():
    if 'file' not in request.files:
        return jsonify({'message': 'No file uploaded.'}), 400

    file = request.files['file']

    if not file or not allowed_file(file.filename):
        return jsonify({'message': 'Invalid file format. Only CSV files are allowed.'}), 400

    # Save uploaded file
    uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(uploaded_file_path)

    # Define file paths
    actual_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Matched_Results.csv')
    predicted_file = uploaded_file_path

    # Check if files exist
    if not os.path.exists(actual_file):
        return jsonify({'message': 'Matched results file not found. Please run the matching process first.'}), 404

    # Calculate accuracy
    response = calculate_accuracy(actual_file, predicted_file)

    try:
        return jsonify(json.loads(response))
    except Exception as e:
        return jsonify({'message': f'Error processing accuracy check: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
