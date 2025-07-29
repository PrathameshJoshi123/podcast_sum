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


#latest
# import os
# import traceback
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# # No need to import Document if we're directly using text-embedding pairs
# import numpy as np # Import numpy for array conversion
# import uuid # For generating UUIDs if needed

# # Assuming InterviewState is correctly imported from app.model.state
# from app.model.state import InterviewState
# from app.graph.graph import GLOBAL_EMBEDDINGS_MODEL

# def vector_db_store_node(state: InterviewState) -> InterviewState:
#     try:    
#         print("inside vector_db_store_node")

#         if not state.all_processed_chunks:
#             state.error_message = "No chunks to store in vector DB."
#             print("No chunks found in state.all_processed_chunks, returning.")
#             return state

#         # Initialize the LangChain Embeddings model for FAISS
#         # IMPORTANT: This model_name should ideally match the one used in `semantic_summarizer_node`
#         embeddings_model = GLOBAL_EMBEDDINGS_MODEL

#         # Prepare data for FAISS.from_embeddings
#         # It expects an Iterable of tuples: (text_content: str, embedding: List[float])
#         text_embeddings_for_faiss = [] # Corrected argument name
        
#         # We will also collect metadata separately, as FAISS.from_embeddings takes 'metadatas' argument
#         # which is a list of dicts corresponding to each text-embedding pair.
#         metadatas_for_faiss = []

#         for chunk in state.all_processed_chunks:
#             text = chunk["text"]
#             embedding = chunk["embedding"] # This is already a numpy array
#             metadata = chunk["metadata"].copy() # Make a copy to avoid modifying original state if extended

#             # Ensure the 'id' is in metadata for good practice, if not already.
#             # It's already generated and part of the chunk dict, so let's ensure it's in metadata.
#             if "id" not in metadata:
#                 metadata["id"] = chunk.get("id", str(uuid.uuid4())) # Use existing ID or generate new if somehow missing

#             text_embeddings_for_faiss.append((text, embedding.tolist())) # Corrected argument name
#             metadatas_for_faiss.append(metadata)


#         if not text_embeddings_for_faiss: # Check the corrected list name
#             state.error_message = "No text-embedding pairs generated for vector DB."
#             print("No text-embedding pairs generated for FAISS, returning.")
#             return state

#         # Create the FAISS index using pre-computed embeddings and their corresponding texts and metadata
#         vector_db = FAISS.from_embeddings(
#             text_embeddings=text_embeddings_for_faiss, # Corrected argument name
#             embedding=embeddings_model, # Still needed for FAISS internal operations (e.g., loading, future query re-embedding)
#             metadatas=metadatas_for_faiss # Pass the list of metadata dictionaries
#         )
#         print(f"FAISS index created with {len(text_embeddings_for_faiss)} entries.")

#         # Save to disk
#         if state.source_type == "youtube":
#             video_id = state.video_id
#             if video_id:
#                 save_path = os.path.join("./faiss", video_id)
#                 os.makedirs(os.path.dirname(save_path), exist_ok=True) # Ensure directory exists
#                 vector_db.save_local(save_path)
#                 state.vector_db_path = save_path
#                 print(f"FAISS DB saved to {save_path}")
#             else:
#                 state.error_message = "Video ID not found for saving vector DB."
#                 print("Video ID missing in state for saving FAISS DB.")
                
#         elif state.source_type == "audio":
#             if state.audio_file_path: # Assuming you have an audio_file_path in your state
#                 file_name = os.path.basename(state.audio_file_path)
#                 name_without_ext = os.path.splitext(file_name)[0]
#                 save_path = os.path.join("./faiss", name_without_ext)
#                 os.makedirs(os.path.dirname(save_path), exist_ok=True) # Ensure directory exists
#                 vector_db.save_local(save_path)
#                 state.vector_db_path = save_path
#                 print(f"FAISS DB saved to {save_path}")
#             else:
#                 state.error_message = "Audio file path not found for saving vector DB."
#                 print("Audio file path missing in state for saving FAISS DB.")
#         else:
#             state.error_message = "Unknown source type for saving vector DB."
#             print(f"Unknown source type: {state.source_type}, cannot save FAISS DB.")

#         return state
    
#     except Exception as e:
#         state.error_message = f"An unexpected error occurred in vector_db_store_node: {e}"
#         print(f"ERROR: An unexpected error occurred: {e}")
#         traceback.print_exc() # This will print the full traceback
#         return state




# import os
# import uuid
# import traceback
# import numpy as np
# import pandas as pd
# from langchain_core.documents import Document
# # Import InMemoryDocstore
# from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_community.vectorstores.faiss import FAISS
# import faiss
# from app.model.state import InterviewState
# from app.graph.graph import GLOBAL_EMBEDDINGS_MODEL  # Your global embedding model

# def vector_db_store_node(state: InterviewState) -> InterviewState:
#     """
#     Creates a FAISS vector database from transcript segments and their associated metadata.
#     The embeddings are weighted by a 'salience' score from the metadata and then normalized.
#     The resulting FAISS database is saved locally.

#     Args:
#         state (InterviewState): The current state object containing:
#             - formatted_transcript_segments: A list of dictionaries, each representing a segment
#               with 'text', 'start', and 'end' keys.
#             - csv_path: Path to a CSV file containing metadata for each segment,
#               including 'start', 'end', and 'final_salience_score'.
#             - source_type: Type of the source (e.g., "youtube", "audio").
#             - video_id: (Optional) Video ID if source_type is "youtube".
#             - audio_file_path: (Optional) Path to the audio file if source_type is "audio".
#             - error_message: (Output) Field to store any error messages.
#             - vector_db_path: (Output) Field to store the path where the FAISS DB is saved.

#     Returns:
#         InterviewState: The updated state object with the vector_db_path or an error_message.
#     """
#     try:
#         print("Inside vector_db_store_node")

#         segments = state.formatted_transcript_segments
#         csv_path = state.csv_path

#         # Validate required inputs
#         if not segments or not csv_path:
#             state.error_message = "Missing transcript segments or metadata CSV path."
#             return state

#         # Read metadata from CSV
#         metadata_df = pd.read_csv(csv_path)

#         # Check for segment-metadata mismatch
#         if len(segments) != len(metadata_df):
#             state.error_message = f"Mismatch: {len(segments)} transcript segments vs {len(metadata_df)} metadata rows"
#             return state

#         embedding_model = GLOBAL_EMBEDDINGS_MODEL
#         print(f"Generating salience-weighted embeddings for {len(segments)} segments...")

#         documents_for_docstore = {} # Dictionary to hold documents for InMemoryDocstore
#         embeddings = []
#         index_to_docstore_id = {} # Mapping from FAISS index to document ID

#         # Process each segment to create documents and weighted embeddings
#         for i, segment in enumerate(segments):
#             text = segment["text"]
#             start = segment.get("start")
#             end = segment.get("end")

#             # Find corresponding metadata row
#             meta_row = metadata_df[(metadata_df["start"] == start) & (metadata_df["end"] == end)]
#             if meta_row.empty:
#                 print(f"Skipping segment {i} due to missing metadata match.")
#                 continue

#             meta = meta_row.iloc[0].to_dict()
#             # Get salience score, default to 0.5 if not found
#             salience = float(meta.get("final_salience_score", 0.5))
#             # Clip salience to a reasonable range for weighting
#             weight = np.clip(salience, 0.1, 2.0)

#             # Generate embedding and apply salience weighting
#             embedding = np.array(embedding_model.embed_query(text))
#             scaled_embedding = scaled_embedding = embedding * weight
#             scaled_embedding = scaled_embedding / np.linalg.norm(scaled_embedding)  # Normalize

#             # Prepare metadata for the Langchain Document
#             doc_id = str(uuid.uuid4()) # Generate a unique ID for the document
#             metadata = {
#                 "id": doc_id,  # Unique ID for each document
#                 "start": start,
#                 "end": end,
#                 "duration_s": meta.get("duration_s"),
#                 "salience": salience,
#                 "mean_pitch": meta.get("mean_pitch"),
#                 # Add more fields from metadata_df as needed
#             }

#             current_document = Document(page_content=text, metadata=metadata)
#             documents_for_docstore[doc_id] = current_document # Store document in dictionary for docstore
#             embeddings.append(scaled_embedding)
#             # Map the current FAISS index (i) to the document's unique ID
#             index_to_docstore_id[i] = doc_id


#         # Check if any documents were successfully processed
#         if not documents_for_docstore:
#             state.error_message = "No valid document-embedding pairs created."
#             return state

#         # Create FAISS index manually
#         dim = len(embeddings[0])  # Dimension of the embeddings
#         index = faiss.IndexFlatL2(dim)  # L2 distance for similarity
#         index.add(np.array(embeddings).astype("float32")) # Add embeddings to the index

#         # Create the InMemoryDocstore
#         docstore = InMemoryDocstore(documents_for_docstore)

#         # Initialize FAISS vector database with the custom index, the docstore, and the mapping
#         vector_db = FAISS(embedding_model.embed_query, index, docstore, index_to_docstore_id)

#         # Determine save directory and file key based on source type
#         save_dir = "./faiss"
#         if state.source_type == "youtube":
#             file_key = state.video_id
#         elif state.source_type == "audio":
#             file_key = os.path.splitext(os.path.basename(state.audio_file_path))[0]
#         else:
#             file_key = f"unknown_{uuid.uuid4()}" # Fallback for unknown source types

#         # Construct save path and ensure directory exists
#         save_path = os.path.join(save_dir, file_key)
#         os.makedirs(os.path.dirname(save_path), exist_ok=True)
#         vector_db.save_local(save_path) # Save the FAISS DB

#         state.file_key = file_key
#         state.vector_db_path = save_path
#         print(f"FAISS DB saved to {save_path}")

#         return state

#     except Exception as e:
#         # Catch and report any unexpected errors
#         state.error_message = f"Unexpected error in vector_db_store_node: {e}"
#         traceback.print_exc() # Print full traceback for debugging
#         return state



import os
import uuid
import traceback
import numpy as np
import pandas as pd
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores.faiss import FAISS
import faiss
from app.model.state import InterviewState
from app.graph.graph import GLOBAL_EMBEDDINGS_MODEL  # Your global embedding model

def vector_db_store_node(state: InterviewState) -> InterviewState:
    """
    Creates a FAISS vector database from transcript segments and their associated metadata.
    Embeddings are stored without weighting or normalization.

    Args:
        state (InterviewState): The current state object containing:
            - formatted_transcript_segments: A list of dictionaries with 'text', 'start', 'end'.
            - csv_path: Path to metadata CSV.
            - source_type: "youtube" or "audio".
            - video_id or audio_file_path for file naming.
            - Output: vector_db_path or error_message.

    Returns:
        InterviewState: Updated with vector_db_path or error_message.
    """
    try:
        print("Inside vector_db_store_node")

        segments = state.formatted_transcript_segments
        csv_path = state.csv_path

        if not segments or not csv_path:
            state.error_message = "Missing transcript segments or metadata CSV path."
            return state

        metadata_df = pd.read_csv(csv_path)

        if len(segments) != len(metadata_df):
            state.error_message = f"Mismatch: {len(segments)} segments vs {len(metadata_df)} metadata rows"
            return state

        embedding_model = GLOBAL_EMBEDDINGS_MODEL
        print(f"Generating unweighted embeddings for {len(segments)} segments...")

        documents_for_docstore = {}
        embeddings = []
        index_to_docstore_id = {}

        for i, segment in enumerate(segments):
            text = segment["text"]
            start = segment.get("start")
            end = segment.get("end")

            meta_row = metadata_df[(metadata_df["start"] == start) & (metadata_df["end"] == end)]
            if meta_row.empty:
                print(f"Skipping segment {i} due to missing metadata match.")
                continue

            meta = meta_row.iloc[0].to_dict()
            salience = float(meta.get("final_salience_score", 0.5))  # Not used in embedding, only stored

            embedding = np.array(embedding_model.embed_query(text))  # No weighting or normalization

            doc_id = str(uuid.uuid4())
            metadata = {
                "id": doc_id,
                "start": start,
                "end": end,
                "duration_s": meta.get("duration_s"),
                "salience": salience,
                "mean_pitch": meta.get("mean_pitch"),
                # Additional metadata fields can be added here
            }

            current_document = Document(page_content=text, metadata=metadata)
            documents_for_docstore[doc_id] = current_document
            embeddings.append(embedding)
            index_to_docstore_id[i] = doc_id

        if not documents_for_docstore:
            state.error_message = "No valid document-embedding pairs created."
            return state

        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings).astype("float32"))

        docstore = InMemoryDocstore(documents_for_docstore)
        vector_db = FAISS(embedding_model.embed_query, index, docstore, index_to_docstore_id)

        save_dir = "./faiss"
        if state.source_type == "youtube":
            file_key = state.video_id
        elif state.source_type == "audio":
            file_key = os.path.splitext(os.path.basename(state.wav_file_path))[0]
        else:
            file_key = f"unknown_{uuid.uuid4()}"

        save_path = os.path.join(save_dir, file_key)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        vector_db.save_local(save_path)

        state.file_key = file_key
        state.vector_db_path = save_path
        print(f"FAISS DB saved to {save_path}")

        return state

    except Exception as e:
        state.error_message = f"Unexpected error in vector_db_store_node: {e}"
        traceback.print_exc()
        return state
