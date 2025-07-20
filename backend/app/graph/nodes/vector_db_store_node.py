# import os
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings

# from app.model.state import InterviewState

# def vector_db_store_node(state: InterviewState) -> InterviewState:
#     print("inside vec")
#     if not state.representative_sentences:
#         state.error_message = "No sentences to store in vector DB"
#         return state

#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#     # Create texts and metadata
#     texts = state.representative_sentences
#     metadatas = [{"source": f"sentence_{i}"} for i in range(len(texts))]

#     # Build FAISS index
#     vector_db = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)

#     if state.source_type == "youtube":
#         video_id = state.video_id
#         # Save to disk or keep in memory
#         vector_db.save_local(f"./faiss/{video_id}")
#         state.vector_db_path = f"./faiss/{video_id}"
#     elif state.source_type == "audio":
#         file_name = os.path.basename(state.source_type)
#         name_without_ext = os.path.splitext(file_name)[0]
#         # Save to disk or keep in memory
#         vector_db.save_local(f"./faiss/{name_without_ext}")
#         state.vector_db_path = f"./faiss/{name_without_ext}"
#     return state

import os
import traceback
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# No need to import Document if we're directly using text-embedding pairs
import numpy as np # Import numpy for array conversion
import uuid # For generating UUIDs if needed

# Assuming InterviewState is correctly imported from app.model.state
from app.model.state import InterviewState
from app.graph.graph import GLOBAL_EMBEDDINGS_MODEL

def vector_db_store_node(state: InterviewState) -> InterviewState:
    try:    
        print("inside vector_db_store_node")

        if not state.all_processed_chunks:
            state.error_message = "No chunks to store in vector DB."
            print("No chunks found in state.all_processed_chunks, returning.")
            return state

        # Initialize the LangChain Embeddings model for FAISS
        # IMPORTANT: This model_name should ideally match the one used in `semantic_summarizer_node`
        embeddings_model = GLOBAL_EMBEDDINGS_MODEL

        # Prepare data for FAISS.from_embeddings
        # It expects an Iterable of tuples: (text_content: str, embedding: List[float])
        text_embeddings_for_faiss = [] # Corrected argument name
        
        # We will also collect metadata separately, as FAISS.from_embeddings takes 'metadatas' argument
        # which is a list of dicts corresponding to each text-embedding pair.
        metadatas_for_faiss = []

        for chunk in state.all_processed_chunks:
            text = chunk["text"]
            embedding = chunk["embedding"] # This is already a numpy array
            metadata = chunk["metadata"].copy() # Make a copy to avoid modifying original state if extended

            # Ensure the 'id' is in metadata for good practice, if not already.
            # It's already generated and part of the chunk dict, so let's ensure it's in metadata.
            if "id" not in metadata:
                metadata["id"] = chunk.get("id", str(uuid.uuid4())) # Use existing ID or generate new if somehow missing

            text_embeddings_for_faiss.append((text, embedding.tolist())) # Corrected argument name
            metadatas_for_faiss.append(metadata)


        if not text_embeddings_for_faiss: # Check the corrected list name
            state.error_message = "No text-embedding pairs generated for vector DB."
            print("No text-embedding pairs generated for FAISS, returning.")
            return state

        # Create the FAISS index using pre-computed embeddings and their corresponding texts and metadata
        vector_db = FAISS.from_embeddings(
            text_embeddings=text_embeddings_for_faiss, # Corrected argument name
            embedding=embeddings_model, # Still needed for FAISS internal operations (e.g., loading, future query re-embedding)
            metadatas=metadatas_for_faiss # Pass the list of metadata dictionaries
        )
        print(f"FAISS index created with {len(text_embeddings_for_faiss)} entries.")

        # Save to disk
        if state.source_type == "youtube":
            video_id = state.video_id
            if video_id:
                save_path = os.path.join("./faiss", video_id)
                os.makedirs(os.path.dirname(save_path), exist_ok=True) # Ensure directory exists
                vector_db.save_local(save_path)
                state.vector_db_path = save_path
                print(f"FAISS DB saved to {save_path}")
            else:
                state.error_message = "Video ID not found for saving vector DB."
                print("Video ID missing in state for saving FAISS DB.")
                
        elif state.source_type == "audio":
            if state.audio_file_path: # Assuming you have an audio_file_path in your state
                file_name = os.path.basename(state.audio_file_path)
                name_without_ext = os.path.splitext(file_name)[0]
                save_path = os.path.join("./faiss", name_without_ext)
                os.makedirs(os.path.dirname(save_path), exist_ok=True) # Ensure directory exists
                vector_db.save_local(save_path)
                state.vector_db_path = save_path
                print(f"FAISS DB saved to {save_path}")
            else:
                state.error_message = "Audio file path not found for saving vector DB."
                print("Audio file path missing in state for saving FAISS DB.")
        else:
            state.error_message = "Unknown source type for saving vector DB."
            print(f"Unknown source type: {state.source_type}, cannot save FAISS DB.")

        return state
    
    except Exception as e:
        state.error_message = f"An unexpected error occurred in vector_db_store_node: {e}"
        print(f"ERROR: An unexpected error occurred: {e}")
        traceback.print_exc() # This will print the full traceback
        return state
