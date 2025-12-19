from flask import Flask, request
from flask_restx import Api, Resource
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

api = Api(app, version='1.0', title='Excellent Mirror API',
    description='Backend API for the HCL Tech Hackathon project',
    doc='/docs'
)

ns = api.namespace('api', description='Core operations')

@ns.route('/health')
class Health(Resource):
    @ns.doc('health_check')
    def get(self):
        """Health check endpoint"""
        return {'status': 'healthy', 'message': 'Excellent Mirror Backend is running! 🚀'}


# In-memory storage for demo purposes
UPLOAD_FOLDER = 'uploads'
import os
import time

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@ns.route('/upload')
class Upload(Resource):
    @ns.doc('upload_file')
    def post(self):
        """Handle file uploads"""
        if 'file' not in request.files:
            return {'error': 'No file part'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No selected file'}, 400
            
        if file:
            filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return {'message': f'File {filename} uploaded successfully!', 'filename': filename}, 200

@ns.route('/ask')
class Ask(Resource):
    @ns.doc('ask_question')
    def post(self):
        """Process user query"""
        data = request.json
        query = data.get('query')
        
        # Simulate AI processing time
        time.sleep(1)
        
        if not query:
            return {'error': 'No query provided'}, 400
            
        return {
            'answer': f"This is a mocked AI response to: '{query}'. In a real integration, this would come from the LLM based on your documents.",
            'sources': ['doc1.pdf', 'image.png']
        }, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
