import json
import os
from typing import List
import uuid
from langchain_huggingface import HuggingFaceEmbeddings
import librosa
import librosa.display
import numpy as np
import pandas as pd
from pydub import AudioSegment
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import re

import faiss

from app.graph.graph import GLOBAL_EMBEDDINGS_MODEL
from app.model.state import InterviewState, ProcessedChunk

try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')

def process_sentence_audio(sent_info, y, sr):
    start_time = sent_info['start']
    end_time = sent_info['end']
    text = sent_info['text']
    original_index = sent_info.get('original_index', None)

    start_sample = int(start_time * sr)
    end_sample = int(end_time * sr)
    sentence_audio = y[start_sample:end_sample]

    if len(sentence_audio) == 0:
        return {
            'sentence_text': text,
            'duration_s': end_time - start_time,
            'word_count': len(word_tokenize(text)),
            'mean_pitch': np.nan,
            'rme_energy': np.nan,
            'speaking_rate': np.nan,
            'pause_before_s': np.nan,  # Will fill later
            'pause_after_s': np.nan,   # Will fill later
            'pitch_std': np.nan,
            'loudness_rms_db': np.nan,
            'mfccs_mean': [np.nan] * 13,
            'original_index': original_index,
            'start': start_time,
            'end': end_time
        }

    duration_s = end_time - start_time
    rms_energy = librosa.feature.rms(y=sentence_audio).mean()

    f0, voiced_flag, voiced_probs = librosa.pyin(
        sentence_audio, 
        fmin=librosa.note_to_hz('C2'), 
        fmax=librosa.note_to_hz('C5'), 
        sr=sr
    )
    mean_pitch = np.nanmean(f0[voiced_flag]) if np.any(voiced_flag) else 0
    pitch_std = np.nanstd(f0[voiced_flag]) if np.any(voiced_flag) else 0

    word_count = len(word_tokenize(text))
    speaking_rate = word_count / duration_s if duration_s > 0 else 0
    loudness_rms_db = librosa.amplitude_to_db(rms_energy + np.finfo(float).eps, ref=np.max)

    mfccs = librosa.feature.mfcc(y=sentence_audio, sr=sr, n_mfcc=13)
    mfccs_mean = np.mean(mfccs, axis=1)

    return {
        'sentence_text': text,
        'duration_s': duration_s,
        'word_count': word_count,
        'mean_pitch': mean_pitch,
        'rme_energy': rms_energy,
        'speaking_rate': speaking_rate,
        'pause_before_s': np.nan,
        'pause_after_s': np.nan,
        'pitch_std': pitch_std,
        'loudness_rms_db': loudness_rms_db,
        'mfccs_mean': mfccs_mean.tolist(),
        'original_index': original_index,
        'start': start_time,
        'end': end_time
    }


def extract_audio_features(audio_path, transcript_data):
    print("inside extract")
    print(audio_path)
    if not audio_path:
        raise ValueError("Invalid audio path: None or empty string.")

    try:
        y, sr = librosa.load(audio_path, sr=None)
    
        print("Loaded the file")
        from joblib import Parallel, delayed
        sentence_features = Parallel(n_jobs=6)(
            delayed(process_sentence_audio)(sent_info, y, sr) for sent_info in transcript_data
        )

        # Calculate pause_before_s and pause_after_s
        for i in range(len(transcript_data)):
            if i > 0:
                pause_before = transcript_data[i]['start'] - transcript_data[i-1]['end']
                sentence_features[i]['pause_before_s'] = max(0, pause_before)

            if i < len(transcript_data) - 1:
                pause_after = transcript_data[i+1]['start'] - transcript_data[i]['end']
                sentence_features[i]['pause_after_s'] = max(0, pause_after)

        return pd.DataFrame(sentence_features)
    except Exception as e:
        print(e)

def calculate_text_importance(df):
    sentences = df['sentence_text'].tolist()

    stop_words = set(stopwords.words('english'))
    cleaned_sentences = []

    for sen in sentences:
        sen = re.sub(r'[^\w\s]', '', sen)
        words = word_tokenize(sen.lower())
        filtered_words = [word for word in words if word not in stop_words]
        cleaned_sentences.append(" ".join(filtered_words))
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned_sentences)

    document_vector = tfidf_matrix.mean(axis=0).A1

    sentence_doc_similarity = cosine_similarity(tfidf_matrix, document_vector.reshape(1, -1)).flatten()
    df['text_tfidf_similarity'] = sentence_doc_similarity

    print("Loading Sentence-BERT model")
    model = GLOBAL_EMBEDDINGS_MODEL
    
    sentence_embeddings = model.embed_documents(sentences)
    df['sentence_embedding'] = sentence_embeddings

    document_embedding = np.mean(sentence_embeddings, axis=0)

    sentence_embedding_similarity = cosine_similarity(sentence_embeddings, document_embedding.reshape(1, -1)).flatten()
    df['text_embedding_similarity'] = sentence_embedding_similarity

    df['text_importance_score'] = df['text_embedding_similarity']

    return df, model, sentence_embeddings


def normalize_features(df, features_to_normalize, mfcc_feature='mfccs_mean', drop_threshold=0.5):
    scaler = StandardScaler()
    df_normalized = df.copy()

    for feature in features_to_normalize:
        if df[feature].isna().mean() > drop_threshold:
            print(f"Dropping feature '{feature}' due to excessive NaNs ('{df[feature].isna().mean()*100:.1f}'%)")
            continue
        
        if feature == mfcc_feature:
            try:

                col_imputer = SimpleImputer(strategy='mean')
                mfcc_data = col_imputer.fit_transform(mfcc_data)

                mfcc_scaled = scaler.fit_transform(mfcc_data)
                df_normalized[feature] = [row.tolist() for row in mfcc_scaled]
            except Exception as e:
                print(f"Error processing MFCC feature '{feature}': {e}")

        else:
            if df_normalized[feature].isna().any():
                print(f"Imputing NaNs in '{feature}' with mean")
            imputer = SimpleImputer(strategy='mean')
            df_normalized[[feature]] = imputer.fit_transform(df_normalized[[feature]])
            df_normalized[[feature]] = scaler.fit_transform(df_normalized[[feature]])

    return df_normalized

def calculate_multimodal_salience(df_features_normalized):
    """
    Computes final salience score using weighted fusion of text, prosody, and MFCCs.
    Specifically tailored for podcast/audio summarization.
    """

    # --- Weights (tune or learn in ML stage) ---
    w_text = 0.5
    w_duration = 0.05
    w_pitch_mean = 0.1
    w_energy = 0.1
    w_speaking_rate = 0.05
    w_pause_before = 0.05
    w_pause_after = 0.05
    w_pitch_std = 0.05
    w_loudness = 0.05
    w_mfcc_var = 0.05  # new weight for MFCCs

    # --- Derived absolute deviation features ---
    df = df_features_normalized.copy()
    df['mean_pitch_abs_dev'] = np.abs(df['mean_pitch'])
    df['rme_energy_abs_dev'] = np.abs(df['rme_energy'])
    df['speaking_rate_abs_dev'] = np.abs(df['speaking_rate'])
    df['pitch_std_abs_dev'] = np.abs(df['pitch_std'])
    df['loudness_rms_db_abs_dev'] = np.abs(df['loudness_rms_db'])

    # --- Collapse MFCC vector into a scalar (variance) ---
    df['mfccs_var'] = df['mfccs_mean'].apply(lambda x: np.var(x) if isinstance(x, list) and len(x) > 0 else 0.0)

    # --- Final weighted sum ---
    df['final_salience_score'] = (
        w_text * df['text_importance_score'] +
        w_duration * df['duration_s'] +
        w_pitch_mean * df['mean_pitch_abs_dev'] +
        w_energy * df['rme_energy_abs_dev'] +
        w_speaking_rate * df['speaking_rate_abs_dev'] +
        w_pause_before * df['pause_before_s'] +
        w_pause_after * df['pause_after_s'] +
        w_pitch_std * df['pitch_std_abs_dev'] +
        w_loudness * df['loudness_rms_db_abs_dev'] +
        w_mfcc_var * df['mfccs_var']
    )

    
    return df

def generate_extractive_summary(df, summary_ratio):
    # Sort sentences by final salience score in descending order
    df_sorted = df.sort_values(by='final_salience_score', ascending=False).reset_index(drop=True)

    # Determine how many sentences to select
    num_sentences_to_select = max(1, int(len(df_sorted) * summary_ratio))

    # Select the top N sentences
    summary_sentences_df = df_sorted.head(num_sentences_to_select)

    # Reorder selected sentences based on their original appearance in the podcast
    summary_sentences_df = summary_sentences_df.sort_values(by='original_index')

    summary_text = " ".join(summary_sentences_df['sentence_text'].tolist())
    return summary_text

def audio_analysis_node(state: InterviewState) -> InterviewState:
    import time
    start_1 = time.time()
    print("Starting podcast summarization process...")

    
    if state.source_type == "audio":
        audio_file = state.wav_file_path
        print("audio file", audio_file)
    else:
        audio_file = state.audio_file_path

    transcript_data = state.formatted_transcript_segments

    # Add original index to keep track of sentence order
    for i, item in enumerate(transcript_data):
        item['original_index'] = i
    
    # 3. Extract Audio Features
    df_features = extract_audio_features(audio_file, transcript_data)
    print("\n--- Extracted Audio Features ---")
    print(df_features[['sentence_text', 'duration_s', 'mean_pitch', 'rme_energy', 'speaking_rate', 'pause_before_s', 'pitch_std', 'loudness_rms_db']].head())

    # 4. Calculate Text Importance and get embedding model
    df_features, sbert_model, sentence_embeddings = calculate_text_importance(df_features)
    print("\n--- Calculated Text Importance ---")
    print(df_features[['sentence_text', 'text_tfidf_similarity', 'text_embedding_similarity', 'text_importance_score']].head())

    # 5. Normalize Features
    features_to_normalize = [
        'duration_s', 'mean_pitch', 'rme_energy', 'speaking_rate', 
        'pause_before_s', 'pause_after_s', 'pitch_std', 'loudness_rms_db', 
        'mfccs_mean'
    ]
    df_features_normalized = normalize_features(df_features.copy(), features_to_normalize)
    print("\n--- Normalized Features Sample ---")
    print(df_features_normalized[['sentence_text', 'duration_s', 'mean_pitch', 'rme_energy']].head())

    # 6. Calculate Multimodal Salience Score (for extractive summary)
    df_final = calculate_multimodal_salience(df_features_normalized)
    print("\n--- Final Salience Scores ---")
    print(df_final[['sentence_text', 'final_salience_score']].head())
    

    
    if state.source_type == "audio":
        audio_filename = os.path.basename(state.wav_file_path)
    else:
        audio_filename = os.path.basename(state.audio_file_path)# e.g., "interview_clip.mp3"
    name_without_ext = os.path.splitext(audio_filename)[0]     # e.g., "interview_clip"
    csv_save_path = os.path.join("./csv", f"{name_without_ext}.csv")

    os.makedirs("./csv", exist_ok=True)  # Make sure the folder exists
    df_final.to_csv(csv_save_path, index=False)

    print(f"CSV saved to: {csv_save_path}")
    

    state.csv_path = csv_save_path
    # # --- Original Extractive Summary (still useful for general overview) ---
    # print("\n--- Generating Extractive Summary (using salience scores) ---")
    # extractive_summary = generate_extractive_summary(df_final, 0.6)
    # print("\n--- Generated Extractive Summary ---")
    # print(extractive_summary)

    
    # state.extractive_summary = extractive_summary

    print(time.time() - start_1)
    return state
    
