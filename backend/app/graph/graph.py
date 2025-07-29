from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.graph import StateGraph, END, START
from app.model.state import InterviewState
from faster_whisper import WhisperModel
GLOBAL_EMBEDDINGS_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2", model_kwargs={'device': 'cuda'})
# GLOBAL_FASTER_WHISPER_MODEL = WhisperModel(model_size_or_path="small", device="cuda", compute_type="int8")
def build_graph():
    # ✅ Import node functions with proper aliases
    from app.graph.nodes.yt_audio_download_node import yt_audio_download_node
    from app.graph.nodes.audio_transcribe_node import audio_transcribe_node as standard_transcribe_node
    from app.graph.nodes.live_audio_transcript import audio_transcribe_node as live_transcribe_node
    from app.graph.nodes.semantic_reduction_node import semantic_summarizer_node
    from app.graph.nodes.vector_db_store_node import vector_db_store_node
    from app.graph.nodes.type_based_summary_node import type_based_summary_node
    from app.graph.nodes.output_node import output_node
    from app.graph.nodes.audio_analysis_node1 import audio_analysis_node
    from app.graph.nodes.doubt_solving_node import doubt_solving_node


    # 1️⃣ Create a state graph
    graph = StateGraph(InterviewState)

    # 2️⃣ Add nodes
    graph.add_node("yt_audio_download_node", yt_audio_download_node)
    graph.add_node("audio_transcribe_node", standard_transcribe_node)
    graph.add_node("live_transcribe_node", live_transcribe_node)
    graph.add_node("semantic_summarizer_node", semantic_summarizer_node)
    graph.add_node("vector_db_store_node", vector_db_store_node)
    graph.add_node("type_based_summary_node", type_based_summary_node)
    graph.add_node("output_node", output_node)
    graph.add_node("audio_analysis_node", audio_analysis_node)
    graph.add_node("doubt_solving_node", doubt_solving_node)

    # ✅ Conditional router at START
    def start_router(state: InterviewState) -> str:
        if state.source_type == "audio":
            return "audio_transcribe_node"
        elif state.is_question == True:
            return "doubt_solving_node"
        else:
            return "yt_audio_download_node"

    graph.add_conditional_edges(START, start_router, {
        "live_transcribe_node": "live_transcribe_node",
        "audio_transcribe_node": "audio_transcribe_node",
        "doubt_solving_node" : "doubt_solving_node",
        "yt_audio_download_node": "yt_audio_download_node"
    })

    # 📄 Path for YouTube
    graph.add_edge("yt_audio_download_node", "audio_transcribe_node")
    
    # 📄 Common processing steps for audio and YouTube
    graph.add_edge("audio_transcribe_node", "audio_analysis_node")
    graph.add_edge("audio_analysis_node", "vector_db_store_node")
    graph.add_edge("vector_db_store_node", "type_based_summary_node")
    graph.add_edge("type_based_summary_node", "output_node")

    # 📄 Path for live: directly to output
    graph.add_edge("live_transcribe_node", "output_node")

    # ✅ Final edge
    graph.add_edge("output_node", END)

    graph.add_edge("doubt_solving_node", END)

    return graph.compile()
