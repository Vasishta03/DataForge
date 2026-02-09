from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
from pathlib import Path
import logging
from datetime import datetime
import zipfile
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for external access

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATASETS_PATH = Path("data/generated_datasets")
API_KEY = "algonomy"

def verify_api_key():
    """Verify API key from request header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    token = auth_header.replace('Bearer ', '')
    return token == API_KEY

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'datasets_available': len(list(DATASETS_PATH.glob('*'))) if DATASETS_PATH.exists() else 0
    })

@app.route('/api/datasets', methods=['GET'])
def list_datasets():
    """List all available datasets"""
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        datasets = []
        if DATASETS_PATH.exists():
            for keyword_dir in DATASETS_PATH.iterdir():
                if keyword_dir.is_dir():
                    files = []
                    total_size = 0
                    for csv_file in keyword_dir.glob('*.csv'):
                        file_size = csv_file.stat().st_size
                        total_size += file_size
                        files.append({
                            'filename': csv_file.name,
                            'size': file_size,
                            'created': datetime.fromtimestamp(csv_file.stat().st_ctime).isoformat(),
                            'download_url': f'/api/download/{keyword_dir.name}/{csv_file.name}'
                        })
                    
                    if files:
                        datasets.append({
                            'keyword': keyword_dir.name,
                            'files': files,
                            'file_count': len(files),
                            'total_size': total_size,
                            'zip_download_url': f'/api/download-zip/{keyword_dir.name}'
                        })
        
        return jsonify({
            'datasets': datasets,
            'total_keywords': len(datasets),
            'api_version': '2.0.0'
        })
    
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/download/<keyword>/<filename>', methods=['GET'])
def download_file(keyword, filename):
    """Download a specific CSV file"""
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        file_path = DATASETS_PATH / keyword / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        if not file_path.suffix.lower() == '.csv':
            return jsonify({'error': 'Only CSV files allowed'}), 403
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/download-zip/<keyword>', methods=['GET'])
def download_keyword_zip(keyword):
    """Download all files for a keyword as a ZIP"""
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        keyword_dir = DATASETS_PATH / keyword
        if not keyword_dir.exists():
            return jsonify({'error': 'Keyword not found'}), 404
        
        # Create temporary ZIP file
        temp_dir = tempfile.mkdtemp()
        zip_path = Path(temp_dir) / f"{keyword}_datasets.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for csv_file in keyword_dir.glob('*.csv'):
                zipf.write(csv_file, csv_file.name)
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{keyword}_datasets.zip",
            mimetype='application/zip'
        )
    
    except Exception as e:
        logger.error(f"Error creating ZIP: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/generate', methods=['POST'])
def trigger_generation():
    """Trigger dataset generation via API"""
    if not verify_api_key():
        return jsonify({'error': 'Invalid API key'}), 401
    
    try:
        data = request.get_json()
        keyword = data.get('keyword', '').strip()
        rows = data.get('rows', 500)
        variations = data.get('variations', 6)
        
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        # Import and run generator
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from dataforge.core.dataset_generator import DatasetGenerator
        from dataforge.config.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        generator = DatasetGenerator(config_manager.config)
        
        results = generator.generate_datasets(keyword, rows, variations)
        
        return jsonify({
            'status': 'success',
            'results': results,
            'download_urls': {
                'zip': f'/api/download-zip/{keyword}',
                'list': f'/api/datasets'
            }
        })
    
    except Exception as e:
        logger.error(f"Error in generation: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("DataForge API Server Starting")
    print("API Base URL: http://localhost:5000")
    print("API Key: algonomy")
    print("Endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/datasets")
    print("   GET  /api/download/<keyword>/<filename>")
    print("   GET  /api/download-zip/<keyword>")
    print("   POST /api/generate")
    print("\nUsage Example:")
    print("   curl -H 'Authorization: Bearer algonomy' http://localhost:5000/api/datasets")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
