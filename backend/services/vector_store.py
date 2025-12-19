
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
import time

class VectorStore:
    def __init__(self, api_key, collection_name="documents", db_path="./chroma_db"):
        genai.configure(api_key=api_key)
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # Custom Gemini Embedding Function
        self.embedding_fn = self._create_gemini_ef()
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name, 
            embedding_function=self.embedding_fn
        )

    def _create_gemini_ef(self):
        """Creates the custom embedding function wrapper."""
        class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
            def __call__(self, input: list[str]) -> list[list[float]]:
                embeddings = []
                for text in input:
                    try:
                        result = genai.embed_content(
                            model="models/embedding-001",
                            content=text,
                            task_type="retrieval_document",
                            title="Embedded Document" 
                        )
                        embeddings.append(result['embedding'])
                    except Exception as e:
                        print(f"Embedding failed: {e}")
                        embeddings.append([0.0]*768) 
                return embeddings
        return GeminiEmbeddingFunction()

    def add_documents(self, chunks, filename):
        """Adds text chunks to the vector store."""
        current_time = str(time.time())
        ids = [f"{filename}_{i}_{current_time}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        return len(chunks)

    def query_documents(self, query, n_results=3):
        """Queries the vector store for relevant context."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        # Flatten documents list
        if results['documents']:
             return "\n".join(results['documents'][0])
        return ""
