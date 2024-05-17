from flask import Flask, render_template, jsonify, request
import os
import csv

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Read CSV file
def read_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

# unique languages depends on url's
@app.route('/api/languages')
def get_languages():
    url_type = request.args.get('urlType', 'avc_url')
    csv_data = read_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_file.csv'))
    languages = set(row['language'] for row in csv_data if row[url_type])
    return jsonify({'languages': list(languages)})

# Endpoint  HLS URLs based on language 
@app.route('/api/hls_urls')
def get_hls_urls():
    language = request.args.get('language')
    url_type = request.args.get('urlType', 'avc_url')
    
    csv_data = read_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_file.csv'))
    
    if not language:
        # If no language specified, return all URLs of the specified type
        hls_data = [{'url': row[url_type], 'platform': row['platform']} for row in csv_data if row[url_type]]
    else:
        # Filter by language and return URLs of the specified type
        hls_data = [{'url': row[url_type], 'platform': row['platform']} for row in csv_data if row['language'] == language and row[url_type]]
    
    return jsonify({'hls_data': hls_data})

# Serve HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to upload CSV file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'csvFile' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['csvFile']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = 'uploaded_file.csv'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully'})

    return jsonify({'error': 'Invalid file format'})

if __name__ == '__main__':
    app.run(debug=True)
