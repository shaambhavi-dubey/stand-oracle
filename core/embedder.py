# core/embedder.py

import os
import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer

def run_ingestion():
    print("🔮 Starting Stand Oracle Ingestion Pipeline...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    excel_path = os.path.join(project_root, "data", "stands.xlsx")
    index_out = os.path.join(project_root, "data", "stands_index.index")
    meta_out = os.path.join(project_root, "data", "stands_metadata.pkl")
    
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Missing spreadsheet target at absolute location: {excel_path}")
        
    # Read the file exactly as it is written
    df = pd.read_excel(excel_path).fillna("None")

    documents = []
    metadata_records = df.to_dict(orient="records")
    
    # MATCHING YOUR EXACT HEADERS HERE (Capitalized with spaces)
    for record in metadata_records:
        doc_string = (
            f"Stand Name: {record.get('Stand Name', 'Unknown')}\n"
            f"Combat Capabilities: {record.get('Ability', '')}\n"
            f"User Personality Resonance: {record.get('User Personality', '')}"
        )
        documents.append(doc_string)

    print("🧠 Generating 384-Dimensional Vectors via all-MiniLM-L6-v2...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vectors = model.encode(documents, show_progress_bar=True)
    vectors = np.array(vectors).astype("float32")

    dimension = 384
    index = faiss.IndexFlatIP(dimension)
    faiss.normalize_L2(vectors)
    index.add(vectors)

    os.makedirs(os.path.dirname(index_out), exist_ok=True)
    faiss.write_index(index, index_out)
    with open(meta_out, "wb") as f:
        pickle.dump(metadata_records, f)
        
    print(f"✨ Success! Cached {index.ntotal} vectors into 'data/' database folder.")

if __name__ == "__main__":
    run_ingestion()