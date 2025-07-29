import os 
from langchain_community.vectorstores import FAISS
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from app.model.state import InterviewState
from dotenv import load_dotenv
load_dotenv()

from app.graph.graph import GLOBAL_EMBEDDINGS_MODEL

def create_summary_qa_system(llm, retriever, content_type="summary"):
    """
    Creates a refined Q&A system for answering questions based on summaries.
    
    Args:
        llm: Language model instance
        retriever: FAISS retriever for semantic search
        content_type: Type of content (e.g., "summary", "article summary", "meeting notes")
    """
    
    system_prompt = f"""You are a helpful chatbot that provides clear, informative answers using {content_type} content.

RESPONSE STYLE:
- Answer directly without casual phrases like "So you want to know about..." or "Well..."
- Write as if you're explaining something important to the user
- Be conversational but professional and helpful
- Use keywords from the user's question naturally in your response
- Focus on providing valuable information
- Respond in the language question is asked

CONTENT REQUIREMENTS:
- Use ONLY information from the provided {content_type}
- Start directly with the answer or information
- Present information clearly and helpfully
- Make the user feel they're getting valuable insights"""

    human_prompt = f"""Answer the user's question using the {content_type} content below. Be helpful and informative, avoiding casual phrases.

CONTENT:
{{context}}

QUESTION:
{{input}}

Take the context from the transcript but provide the answer in simple words in your style

U can reframe the answer but mandatorily preseve facts and meaning extracted

Provide a clear, helpful answer that directly addresses their question. Use relevant keywords from their question naturally. Start with the most important information first. Avoid casual openings like "So you want to know..." or "Well..." - instead jump straight into providing valuable information. Keep it focused and around 4-6 sentences.

If the information isn't available, simply say "I don't have that information" and mention what related info is available."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])
    
    # Create the document chain
    qa_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=prompt
    )
    
    # Create the retrieval chain
    retrieval_chain = create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=qa_chain
    )
    
    return retrieval_chain

def optimize_query_for_search(llm, original_question):
    """
    Optimizes the user question for better semantic search results.
    """
    query_optimization_prompt = """Rewrite the following question to optimize it for semantic search in a vector database.

Guidelines:
- Focus on key concepts and entities
- Remove conversational elements and filler words
- Use clear, specific terminology
- Maintain the core intent of the question
- Output ONLY the optimized query, nothing else

Original question: {question}

Optimized query:"""
    
    response = llm.invoke(query_optimization_prompt.format(question=original_question))
    
    # Extract and clean the optimized query
    optimized_query = response.content.strip().split("\n")[0].strip('"').strip("'")
    
    return optimized_query


def doubt_solving_node(state: InterviewState) -> InterviewState:

    try:

        folder_path = os.path.join("./faiss", state.id)

        vector_db = FAISS.load_local(folder_path, GLOBAL_EMBEDDINGS_MODEL, allow_dangerous_deserialization=True)

        retriver = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 30})

        llm = ChatGroq(model="llama3-70b-8192", temperature=0.4)

        
        # Create the QA system
        qa_system = create_summary_qa_system(llm, retriver)
        
        # Optimize the query for better retrieval
        optimized_query = optimize_query_for_search(llm, state.question)
        print(f"Optimized query: {optimized_query}")
        
        # Get the response
        response = qa_system.invoke({"input": optimized_query, "content_type": "summary"})
        
        print(response)
        state.answer =  response.get("answer") or "Sorry, I couldn't find an answer to your question."


        return state
    
    except Exception as e:
        print(e)
        return state