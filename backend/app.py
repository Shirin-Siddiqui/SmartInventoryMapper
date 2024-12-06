from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
from app.mapper import preprocess_data, compute_and_save_embeddings, run_matching_pipeline

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

        # Process the files using the intelligent mapper functions
        external_embeddings_file = os.path.join(app.config['UPLOAD_FOLDER'], 'external_embeddings.pkl')
        internal_embeddings_file = os.path.join(app.config['UPLOAD_FOLDER'], 'internal_embeddings.pkl')

        if not os.path.exists(external_embeddings_file):
            compute_and_save_embeddings(external_data, 'cleaned_name', external_embeddings_file)

        if not os.path.exists(internal_embeddings_file):
            compute_and_save_embeddings(internal_data, 'cleaned_name', internal_embeddings_file)

        external_data = pd.read_pickle(external_embeddings_file)
        internal_data = pd.read_pickle(internal_embeddings_file)

        matches = run_matching_pipeline(external_data, internal_data, threshold=0.85)

        # Save the results in the UPLOAD_FOLDER
        results_file = os.path.join(app.config['UPLOAD_FOLDER'], 'Final_Matched_Products.csv')
        matches.to_csv(results_file, index=False)

        return jsonify({
            'message': 'Files uploaded and processed successfully',
            'results_file': results_file  # Return path of the results file
        })
    else:
        return jsonify({'message': 'Invalid file format. Only CSV files are allowed.'}), 400

# Route for downloading the final product list
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Ensure we are serving the file from the correct directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
