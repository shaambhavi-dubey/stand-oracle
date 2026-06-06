import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer

class StandRetriever:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        index_path = os.path.join(project_root, "data", "stands_index.index")
        meta_path = os.path.join(project_root, "data", "stands_metadata.pkl")
        
        self.index = faiss.read_index(index_path)
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
            
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
    def query(self, profile_text, k=1):
        query_vector = self.model.encode([profile_text])
        faiss.normalize_L2(query_vector)
        
        distances, indices = self.index.search(query_vector, k)
        return [self.metadata[idx] for idx in indices[0]]