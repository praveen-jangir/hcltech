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
        return {'status': 'healthy', 'message': 'Excellent Mirror Backend is runninng'}


UPLOAD_FOLDER = 'uploads'
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import os
from pymongo import MongoClient
from datetime import datetime

from services.document_processor import DocumentProcessor
from services.vector_store import VectorStore
from services.llm_engine import LLMEngine
from services.evaluation_service import EvaluationService
from services.external_model_service import ExternalModelService

GEMINI_API_KEY = "AIzaSyDLqhoMwfr2VFIPH3UlouR-xF60PhG_CwQ"

vector_store = VectorStore(api_key=GEMINI_API_KEY)
llm_engine = LLMEngine(api_key=GEMINI_API_KEY)
evaluation_service = EvaluationService(api_key=GEMINI_API_KEY)
external_service = ExternalModelService()

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["hcl_tech_rag"]
uploads_col = db["uploads"]
chats_col = db["chats"]

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@ns.route('/upload')
class Upload(Resource):
    @ns.doc('upload_file')
    def post(self):
        """Handle file uploads - Local + External"""
        if 'file' not in request.files:
            return {'error': 'No file part'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No selected file'}, 400
            
        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                extracted_text = DocumentProcessor.extract_text(filepath)
                chunks = DocumentProcessor.chunk_text(extracted_text)
                vector_store.add_documents(chunks, filename)
                
                print("Uploading to external model...")
                ext_response = external_service.upload_file(filepath)
                print(f"External Upload Response: {ext_response}")

                uploads_col.insert_one({
                    "filename": filename,
                    "upload_time": datetime.utcnow(),
                    "chunks_count": len(chunks),
                    "status": "processed",
                    "external_status": ext_response
                })

                return {'message': f'File processed locally and sent to external model!', 'filename': filename}, 200

            except Exception as e:
                return {'error': f'Processing Failed: {str(e)}'}, 500

@ns.route('/ask')
class Ask(Resource):
    @ns.doc('ask_question')
    def post(self):
        """Dual RAG: Query Local + External Models"""
        data = request.json
        query = data.get('query')
        
        if not query:
            return {'error': 'No query provided'}, 400
            
        try:
            rewritten_query = llm_engine.rewrite_query(query)
            context = vector_store.query_documents(rewritten_query)
            answer_internal = llm_engine.generate_answer(query, context)
            metrics_internal = evaluation_service.evaluate_all(query, context, answer_internal)
            
            print("Querying external model...")
            ext_data = external_service.ask_question(query)
            answer_external = ext_data.get('answer', 'No answer from external model')
            
            chats_col.insert_one({
                "query": query,
                "internal": {
                    "answer": answer_internal,
                    "metrics": metrics_internal,
                    "rewritten": rewritten_query
                },
                "external": {
                    "answer": answer_external,
                    "raw_response": ext_data
                },
                "timestamp": datetime.utcnow()
            })
            
            return {
                'internal': {
                    'answer': answer_internal,
                    'metrics': metrics_internal,
                    'rewritten_query': rewritten_query
                },
                'external': {
                    'answer': answer_external
                }
            }, 200
            
        except Exception as e:
             return {'error': f'Dual RAG Error: {str(e)}'}, 500

@ns.route('/set-url')
class SetURL(Resource):
    @ns.doc('set_external_url')
    def post(self):
        """Update the External Model Base URL"""
        data = request.json
        new_url = data.get('url')
        if not new_url:
            return {'error': 'URL is required'}, 400
            
        external_service.set_base_url(new_url)
        return {'message': f'External URL updated to {new_url}'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
