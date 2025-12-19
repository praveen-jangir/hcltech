
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu
import google.generativeai as genai
import json

class EvaluationService:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)

    def get_embedding(self, text):
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document",
                title="Eval Text"
            )
            return result['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
            return [0.0] * 768

    def calculate_cosine_similarity(self, text1, text2):
        vec1 = np.array(self.get_embedding(text1)).reshape(1, -1)
        vec2 = np.array(self.get_embedding(text2)).reshape(1, -1)
        return float(cosine_similarity(vec1, vec2)[0][0])

    def calculate_rouge_bleu(self, reference, hypothesis):
        scores = self.scorer.score(reference, hypothesis)
        rouge1 = scores['rouge1'].fmeasure
        
        reference_tokens = [reference.split()]
        hypothesis_tokens = hypothesis.split()
        bleu = sentence_bleu(reference_tokens, hypothesis_tokens, weights=(1, 0, 0, 0))
        
        return rouge1, bleu

    def evaluate_retrieval(self, query, retrieved_docs):
        prompt = f"""
        You are a search quality evaluator.
        Query: {query}
        
        Retrieved Documents:
        {json.dumps(retrieved_docs)}
        
        Task: Rate each document as 1 (Relevant) or 0 (Irrelevant) to the query.
        Return a JSON array of integers, e.g., [1, 0, 1].
        """
        try:
            response = self.model.generate_content(prompt)
            relevance_scores = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        except Exception:
            relevance_scores = [0] * len(retrieved_docs)
            
        mrr = 0
        for i, score in enumerate(relevance_scores):
            if score == 1:
                mrr = 1 / (i + 1)
                break
                
        relevant_count = sum(relevance_scores)
        precision_at_k = relevant_count / len(retrieved_docs) if retrieved_docs else 0
        
        return {
            "mrr": round(mrr, 2),
            "relevant_docs_count": relevant_count,
            "precision_at_k": round(precision_at_k, 2)
        }

    def evaluate_all(self, query, context, answer):
        cosine_sim = self.calculate_cosine_similarity(answer, context)
        
        rouge, bleu = self.calculate_rouge_bleu(context, answer)
        retrieval_metrics = self.evaluate_retrieval(query, [context])
        
        return {
            "cosine_similarity": round(cosine_sim, 4),
            "rouge_1": round(rouge, 4),
            "bleu": round(bleu, 4),
            "mrr": retrieval_metrics['mrr']
        }
