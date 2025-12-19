
import io
import json
from unittest.mock import patch, MagicMock

import pytest

from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upload_success_pdf(client):
    # Mock external upload and vector store interactions
    mock_ext_response = {"status": "ok"}
    with patch('backend.services.external_model_service.ExternalModelService.upload_file', return_value=mock_ext_response) as mock_upload, patch('backend.services.vector_store.VectorStore.add_documents', return_value=5) as mock_add:
        data = {
            'file': (io.BytesIO(b"dummy pdf content"), 'test.pdf')
        }
        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        resp_json = response.get_json()
        assert resp_json['filename'] == 'test.pdf'
        assert resp_json['external_status'] == mock_ext_response
        mock_upload.assert_called_once()
        mock_add.assert_called_once()

def test_upload_non_pdf_rejected(client):
    data = {
        'file': (io.BytesIO(b"some text"), 'test.txt')
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    resp_json = response.get_json()
    assert 'Only PDF files are supported' in resp_json['error']
