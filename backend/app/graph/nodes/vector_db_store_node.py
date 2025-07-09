import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.model.state import InterviewState

def vector_db_store_node(state: InterviewState) -> InterviewState:
    if not state.representative_sentences:
        state.error_message = "No sentences to store in vector DB"
        return state

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create texts and metadata
    texts = state.representative_sentences
    metadatas = [{"source": f"sentence_{i}"} for i in range(len(texts))]

    # Build FAISS index
    vector_db = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)

    if state.source_type == "youtube":
        video_id = state.video_id
        # Save to disk or keep in memory
        vector_db.save_local(f"./faiss/{video_id}")
        state.vector_db_path = f"./faiss/{video_id}"
    elif state.source_type == "audio":
        file_name = os.path.basename(state.source_type)
        name_without_ext = os.path.splitext(file_name)[0]
        # Save to disk or keep in memory
        vector_db.save_local(f"./faiss/{name_without_ext}")
        state.vector_db_path = f"./faiss/{name_without_ext}"
    return state
