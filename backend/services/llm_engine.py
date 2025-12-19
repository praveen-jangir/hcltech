
import google.generativeai as genai

class LLMEngine:
    def __init__(self, api_key, model_name='gemini-2.0-flash'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_answer(self, query, context):
        prompt = f"""
        Answer only using the information given below.If the information is not available, respond with:
        "I don't have enough information in the uploaded documents."
        
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
        prompt = f"""
        Rewrite the query to improve technical document retrieval. Output only the rewritten query.
        
        Original Query: {query}
        
        Rewritten Query:
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return query # Fallback to original

    def evaluate_response(self, query, context, answer):
        prompt = f"""
        Evaluate the RAG answer using the question and retrieved context.
        
        Question: {query}
        Context: {context}
        Generated Answer: {answer}
        

        
        
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
