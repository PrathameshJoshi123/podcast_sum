import nltk
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("punkt")
embedder = SentenceTransformer("all-mpnet-base-v2")

def hybrid_chunk(text, min_words=100, max_words=300):
    """Segment text by semantic shifts and approximate word count."""
    sentences = nltk.sent_tokenize(text)
    chunks, current_chunk = [], []
    current_len = 0

    for i, sent in enumerate(sentences):
        words = sent.split()
        current_chunk.append(sent)
        current_len += len(words)

        # Check if we hit semantic shift (next sentence very different)
        if i + 1 < len(sentences):
            next_emb = embedder.encode([sentences[i+1]])[0]
            curr_emb = embedder.encode([sent])[0]
            sim = cosine_similarity([curr_emb], [next_emb])[0][0]
            semantic_break = sim < 0.6
        else:
            semantic_break = True

        if current_len >= min_words and (semantic_break or current_len >= max_words):
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def score_importance(chunks, transcript_embedding):
    """Compute importance score per chunk."""
    chunk_embeddings = embedder.encode(chunks)
    scores = cosine_similarity(chunk_embeddings, [transcript_embedding]).flatten()
    return scores

def adaptive_representatives(chunks, scores, transcript_length_words):
    """Select adaptive number of representatives based on transcript length and score."""
    num_representatives = max(1, int(transcript_length_words / 500))
    top_indices = np.argsort(scores)[::-1][:num_representatives]
    return [chunks[i] for i in top_indices]

def semantic_summarizer_node(state):
    """Adaptive summarizer for variable transcript length."""
    if not state.transcript:
        state.error_message = "Transcript not available"
        return state

    try:
        transcript_words = len(state.transcript.split())

        # Chunk adaptively
        chunks = hybrid_chunk(state.transcript)

        if len(chunks) < 2:
            state.representative_sentences = [state.transcript]
            state.global_summary = state.transcript
            return state

        # Global embedding
        global_embedding = embedder.encode([state.transcript])[0]

        # Score chunks
        scores = score_importance(chunks, global_embedding)

        # Select representatives
        rep_chunks = adaptive_representatives(chunks, scores, transcript_words)

        # Generate summary
        summary = " ".join(rep_chunks)

        state.representative_sentences = rep_chunks
        state.global_summary = summary

    except Exception as e:
        state.error_message = f"Semantic summarization failed: {str(e)}"

    return state
