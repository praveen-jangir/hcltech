from flask import Flask, request
from flask_restx import Api, Resource
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api = Api(app, version='1.0', title='Excellent Mirror API',
    description='Backend API for the HCL Tech Hackathon project',
    doc='/docs'
)

ns = api.namespace('api', description='Core operations')

@ns.route('/health')
class Health(Resource):
    @ns.doc('health_check')
    def get(self):
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

GEMINI_API_KEY = "AIzaSyCMWY2XSlDRhbDhJ9x9oZne057u8GGnfDw"

vector_store = VectorStore(api_key=GEMINI_API_KEY)
llm_engine = LLMEngine(api_key=GEMINI_API_KEY)
evaluation_service = EvaluationService(api_key=GEMINI_API_KEY)

# Global variable to store latest document text (Direct Mode)
LATEST_DOCUMENT_TEXT = ""

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
        if 'file' not in request.files:
            return {'error': 'No file part'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'error': 'No selected file'}, 400
        
        # Restrict to PDF files only
        if not file.filename.lower().endswith('.pdf'):
            logger.warning(f"Rejected upload of non-PDF file: {file.filename}")
            return {'error': 'Only PDF files are supported'}, 400
            
        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                extracted_text = DocumentProcessor.extract_text(filepath)
                global LATEST_DOCUMENT_TEXT
                LATEST_DOCUMENT_TEXT = extracted_text
                print(f"DEBUG: Extracted text length: {len(LATEST_DOCUMENT_TEXT)}")
                print(f"DEBUG: Extracted text preview: {LATEST_DOCUMENT_TEXT[:500]}")

                # Vector store disabled for Direct Mode
                # chunks = DocumentProcessor.chunk_text(extracted_text)
                # print(chunks)
                # vector_store.add_documents(chunks, filename)
                
                # External upload disabled
                # logger.info(f"Uploading {filename} to external model...")
                # try:
                #     ext_response = external_service.upload_file(filepath)
                #     logger.info(f"External upload succeeded: {ext_response}")
                # except Exception as e:
                #     logger.error(f"External upload failed: {e}")
                #     ext_response = {"error": str(e)}
                ext_response = {"status": "disabled", "message": "External model disabled by user"}

                uploads_col.insert_one({
                    "filename": filename,
                    "upload_time": datetime.utcnow(),
                    "chunks_count": 1, # Treated as single chunk in direct mode
                    "status": "processed",
                    "external_status": ext_response
                })

                return {'message': 'File processed locally and external upload attempted', 'filename': filename, 'external_status': ext_response}, 200

            except Exception as e:
                return {'error': f'Processing Failed: {str(e)}'}, 500

@ns.route('/ask')
class Ask(Resource):
    @ns.doc('ask_question')
    def post(self):
        data = request.json
        query = data.get('query')
        
        if not query:
            return {'error': 'No query provided'}, 400
            
        try:
            # Direct Mode: Use global text
            global LATEST_DOCUMENT_TEXT
            if not LATEST_DOCUMENT_TEXT:
                return {'error': 'No document uploaded. Please upload a PDF first.'}, 400
            
            context = LATEST_DOCUMENT_TEXT
            
            # Vector store query disabled
            # rewritten_query = llm_engine.rewrite_query(query)
            # context = vector_store.query_documents(rewritten_query)
            rewritten_query = query # No rewrite in direct mode
            answer_internal = llm_engine.generate_answer(query, context)
            metrics_internal = evaluation_service.evaluate_all(query, context, answer_internal)
            
            # External query disabled
            # print("Querying external model...")
            # ext_data = external_service.ask_question(query)
            # answer_external = ext_data.get('answer', 'No answer from external model')
            answer_external = "External model disabled"
            ext_data = {}
            
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
        data = request.json
        new_url = data.get('url')
        if not new_url:
            return {'error': 'URL is required'}, 400
            
        external_service.set_base_url(new_url)
        return {'message': f'External URL updated to {new_url}'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
