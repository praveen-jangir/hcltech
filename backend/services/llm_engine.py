
import google.generativeai as genai

class LLMEngine:
    def __init__(self, api_key, model_name='gemini-2.0-flash'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_answer(self, query, context):
        """Generates an answer using the LLM based on context."""
        prompt = f"""
        You are an expert assistant. Answer the question based strictly on the provided context below.
        If the answer isn't in the context, say "I don't have enough information in the uploaded documents."
        
        Context:
        {context}
        
        Question: {query}
        
        Answer:
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def rewrite_query(self, query):
        """Rewrites the user query to be more suitable for vector retrieval."""
        prompt = f"""
        Act as a search engine optimizer. Rewrite the following user query to be more specific and keyword-rich for retrieving technical documentation.
        Do not add any preamble or quotes. Just the rewritten query.
        
        Original Query: {query}
        
        Rewritten Query:
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return query # Fallback to original

    def evaluate_response(self, query, context, answer):
        """Evaluates the RAG response for Precision, Recall, and F1."""
        # Note: True Precision/Recall requires ground truth. Here we use LLM-as-a-Judge to estimate quality.
        prompt = f"""
        You are an expert evaluator for a RAG system.
        Evaluate the quality of the generated answer based on the retrieved context and original question.
        
        Question: {query}
        Context: {context}
        Generated Answer: {answer}
        
        Provide a JSON response with the following integer scores (0-100):
        - precision: How much of the answer is supported by the context?
        - recall: How much of the question was answered by the context?
        - f1_score: Harmonic mean of precision and recall.
        
        Format:
        {{
            "precision": 85,
            "recall": 90,
            "f1_score": 87
        }}
        Return ONLY valid JSON.
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            import json
            return json.loads(text)
        except Exception as e:
            print(f"Eval failed: {e}")
            return {"precision": 0, "recall": 0, "f1_score": 0}
