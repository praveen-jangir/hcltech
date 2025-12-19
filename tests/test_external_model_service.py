
import unittest
from unittest.mock import patch, Mock
from backend.services.external_model_service import ExternalModelService

class TestExternalModelService(unittest.TestCase):
    def setUp(self):
        self.service = ExternalModelService(base_url="http://example.com")

    @patch('backend.services.external_model_service.requests.post')
    def test_ask_question_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"answer": "test answer"}
        mock_post.return_value = mock_response
        result = self.service.ask_question("test")
        self.assertEqual(result, {"answer": "test answer"})
        mock_post.assert_called_once()

    @patch('backend.services.external_model_service.requests.post')
    def test_ask_question_non_json(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "plain text response"
        mock_response.json.side_effect = ValueError()
        mock_post.return_value = mock_response
        result = self.service.ask_question("test")
        self.assertIn("answer", result)
        self.assertEqual(result["answer"], "plain text response")
        self.assertIn("raw_response", result)
        self.assertEqual(result["raw_response"], "plain text response")

    @patch('backend.services.external_model_service.requests.post')
    def test_ask_question_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_response.raise_for_status.side_effect = Exception("500 Server Error")
        mock_post.return_value = mock_response
        result = self.service.ask_question("test")
        self.assertIn("error", result)
        self.assertTrue(result["error"].startswith("External error"))

if __name__ == '__main__':
    unittest.main()
