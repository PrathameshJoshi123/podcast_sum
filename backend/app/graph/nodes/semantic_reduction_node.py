import nltk
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import uuid # For unique IDs for vector DB entries
from typing import List, Dict, Any, Optional

from app.model.state import InterviewState


# Download NLTK punkt tokenizer data
nltk.download("punkt", quiet=True)

# --- Configuration Constants ---
MIN_CHUNK_WORDS = 80
MAX_CHUNK_WORDS = 250
SEMANTIC_BREAK_THRESHOLD = 0.6
REPRESENTATIVE_WORD_RATIO = 750
MIN_REPRESENTATIVES = 3
MAX_REPRESENTATIVES_TOKENS_PERCENT = 0.7
AVERAGE_CHUNK_TOKENS = 200

LLM_CONTEXT_WINDOW_TOKENS = 120000

MAX_REPRESENTATIVES = int((LLM_CONTEXT_WINDOW_TOKENS * MAX_REPRESENTATIVES_TOKENS_PERCENT) / AVERAGE_CHUNK_TOKENS)
MAX_REPRESENTATIVES = max(MIN_REPRESENTATIVES, MAX_REPRESENTATIVES)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Global HuggingFaceEmbeddings Embedder ---
# Define the HuggingFaceEmbeddings globally to ensure consistency and single-time loading
# This model_name MUST match the one used in GLOBAL_EMBEDDINGS_MODEL in vector_db_store_node
from app.graph.graph import GLOBAL_EMBEDDINGS_MODEL
GLOBAL_LANGCHAIN_EMBEDDER = GLOBAL_EMBEDDINGS_MODEL


# --- Core Functions (remain largely the same, but use GLOBAL_LANGCHAIN_EMBEDDER) ---

def hybrid_chunk(text: str) -> List[Dict[str, Any]]:
    """Segment text by semantic shifts and approximate word count.
    Returns a list of dictionaries, each representing a chunk with its ID, text, embedding, and metadata.
    """
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        logger.warning("No sentences found in text, returning empty chunks.")
        return []

    logger.info(f"Tokenizing and encoding {len(sentences)} sentences for chunking stability.")
    # Use the global LangChain embedder's embed_documents method
    sentence_embeddings = GLOBAL_LANGCHAIN_EMBEDDER.embed_documents(sentences)
    # Convert to numpy array for cosine_similarity if needed later, or ensure cosine_similarity handles lists
    sentence_embeddings_np = np.array(sentence_embeddings)


    chunks_data: List[Dict[str, Any]] = []
    current_chunk_sentences: List[str] = []
    current_len = 0
    chunk_index = 0

    for i, sent in enumerate(sentences):
        words = sent.split()
        current_chunk_sentences.append(sent)
        current_len += len(words)

        semantic_break = False
        if i + 1 < len(sentences):
            # Use the numpy array version for cosine_similarity
            curr_emb = sentence_embeddings_np[i]
            next_emb = sentence_embeddings_np[i+1]
            sim = cosine_similarity([curr_emb], [next_emb])[0][0]
            semantic_break = sim < SEMANTIC_BREAK_THRESHOLD
        else:
            semantic_break = True # Force a break at the end of the text

        if current_len >= MIN_CHUNK_WORDS and (semantic_break or current_len >= MAX_CHUNK_WORDS):
            chunk_text = " ".join(current_chunk_sentences)
            # Embed the full chunk using embed_query (for a single string)
            chunk_embedding = GLOBAL_LANGCHAIN_EMBEDDER.embed_query(chunk_text)
            chunks_data.append({
                "id": str(uuid.uuid4()), # Unique ID
                "text": chunk_text,
                "embedding": np.array(chunk_embedding), # Store as numpy array for consistency with other parts
                "metadata": {"original_index": chunk_index} # Track original order
            })
            logger.debug(f"Chunk {chunk_index} created. Word count: {current_len}")
            current_chunk_sentences = []
            current_len = 0
            chunk_index += 1

    if current_chunk_sentences: # Add any remaining sentences as a final chunk
        chunk_text = " ".join(current_chunk_sentences)
        # Use the global embedder's embed_query method
        chunk_embedding = GLOBAL_LANGCHAIN_EMBEDDER.embed_query(chunk_text)
        chunks_data.append({
            "id": str(uuid.uuid4()),
            "text": chunk_text,
            "embedding": np.array(chunk_embedding), # Store as numpy array
            "metadata": {"original_index": chunk_index}
        })
        logger.debug(f"Final chunk {chunk_index} added. Word count: {current_len}")

    return chunks_data

def score_importance(chunks_data: List[Dict[str, Any]], transcript_embedding: np.ndarray) -> np.ndarray:
    """Compute importance score per chunk based on cosine similarity to the full transcript embedding."""
    if not chunks_data:
        return np.array([])
    chunk_embeddings = np.array([chunk["embedding"] for chunk in chunks_data]) # Ensure these are numpy arrays
    scores = cosine_similarity(chunk_embeddings, [transcript_embedding]).flatten()
    return scores

def adaptive_representatives(chunks_data: List[Dict[str, Any]], scores: np.ndarray, transcript_length_words: int) -> List[Dict[str, Any]]:
    """
    Select an adaptive number of representative chunks based on transcript length and importance score,
    constrained by the overall MAX_REPRESENTATIVES limit (which is based on LLM context).
    """
    num_representatives = int(transcript_length_words / REPRESENTATIVE_WORD_RATIO)
    num_representatives = max(MIN_REPRESENTATIVES, min(MAX_REPRESENTATIVES, num_representatives))

    logger.info(f"Attempting to select {num_representatives} representative chunks from {len(chunks_data)} available.")

    if num_representatives > len(chunks_data):
        num_representatives = len(chunks_data)
        logger.warning(f"Reduced number of representatives to {num_representatives} as there are fewer chunks available.")

    top_indices = np.argsort(scores)[::-1][:num_representatives]
    selected_rep_chunks_data = [chunks_data[i] for i in top_indices]

    selected_rep_chunks_data.sort(key=lambda x: x['metadata'].get('original_index', 0))

    return selected_rep_chunks_data

# --- The LangGraph Node Function ---

def semantic_summarizer_node(state: InterviewState) -> InterviewState:
    """
    LangGraph node: Chunks the transcript and identifies key representative chunks.
    This node does NOT store in a vector DB or call an LLM. It prepares the data
    for subsequent nodes.
    """
    if not state.transcript:
        state.error_message = "Transcript not available for semantic processing."
        logger.warning("Transcript is empty, cannot perform semantic processing.")
        return state

    logger.info("Starting semantic processing node (chunking and representative selection).")
    try:
        transcript_words = len(state.transcript.split())
        logger.info(f"Transcript word count: {transcript_words}")

        # --- Step 1: Hybrid Chunking ---
        # This function now returns dicts including 'text' and 'embedding'
        all_podcast_chunks_data = hybrid_chunk(state.transcript)
        state.all_processed_chunks = all_podcast_chunks_data
        logger.info(f"Generated {len(all_podcast_chunks_data)} initial chunks.")

        if not all_podcast_chunks_data:
            state.error_message = "No chunks generated from transcript."
            logger.warning("No chunks generated, setting error and empty lists.")
            return state

        # Handle very short transcripts where chunking might result in few chunks
        if len(all_podcast_chunks_data) < MIN_REPRESENTATIVES:
            logger.info("Fewer chunks than MIN_REPRESENTATIVES. All chunks will be considered representative.")
            state.representative_chunks_for_summary = all_podcast_chunks_data
            # If the original transcript is itself very short, make that the summary placeholder
            if transcript_words < MIN_CHUNK_WORDS:
                state.global_summary = state.transcript # Placeholder for very short transcripts
            return state


        # --- Step 2: Global Embedding and Importance Scoring ---
        logger.info("Encoding full transcript for global embedding.")
        # Use the global LangChain embedder's embed_query method for the full transcript
        global_transcript_embedding = np.array(GLOBAL_LANGCHAIN_EMBEDDER.embed_query(state.transcript))

        scores = score_importance(all_podcast_chunks_data, global_transcript_embedding)
        logger.info("Chunks scored for importance relative to the entire transcript.")

        # --- Step 3: Select Adaptive Representative Chunks ---
        selected_rep_chunks_data = adaptive_representatives(
            all_podcast_chunks_data, scores, transcript_words
        )
        state.representative_chunks_for_summary = selected_rep_chunks_data
        logger.info(f"Identified {len(selected_rep_chunks_data)} representative chunks for summary.")

    except Exception as e:
        state.error_message = f"Semantic processing failed: {str(e)}"
        logger.error(f"Error during semantic processing: {e}", exc_info=True)

    return state