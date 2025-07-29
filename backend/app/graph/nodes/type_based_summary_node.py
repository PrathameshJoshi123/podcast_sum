# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.chains import create_retrieval_chain
# from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
# from langchain.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq
# from app.model.state import InterviewState
# from dotenv import load_dotenv
# load_dotenv()
# import os

# def type_based_summary_node(state: InterviewState) -> InterviewState:
#     print("inside type")
#     if not state.vector_db_path or not state.podcast_type:
#         state.error_message = "Vector DB or podcast type missing"
#         return state

#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#     vector_db = FAISS.load_local(state.vector_db_path, embeddings, allow_dangerous_deserialization=True)
#     retriever = vector_db.as_retriever(search_kwargs={"k": 10})

#     llm = ChatGroq(model="llama3-70b-8192", temperature=0.2)
#     # Define system prompt
#     if state.podcast_type == "interview":
#     # System prompt for summary
#         system_prompt_summary = (
#            f"You are an expert podcast summarizer. Your task is to generate a detailed, topic-based summary of the following podcast transcript. The goal is to provide a comprehensive overview that allows a reader to understand the entire conversation, including key insights, arguments, and examples, without needing to listen to the audio. Please provide in {state.summary_language} language. PLease try to find the host name in {state.channel_and_title}."
#         )

#         # System prompt for Q&A extraction
#         system_prompt_qa = (
#             f"You are an expert transcript analyst. Your task is to meticulously extract all questions and their corresponding answers from the following podcast transcript. The goal is to create a clear and accurate record of the interview's dialogue flow. Please provide in {state.summary_language} language. PLease try to find the host name in {state.channel_and_title}."
#         )

#         # Prompt for summary
#         prompt_summary = ChatPromptTemplate.from_messages([
#             ("system", system_prompt_summary),
#             ("human", """Here is the transcript or partial context:
#     {context}

# **Instructions:**

# Based on the provided transcript, please generate the following:

# **1. Catchy Title:**
# * Provide engaging and catchy title for this podcast episode. These title should accurately reflect the core themes of the conversation.

# **2. Participants:**
# * **Host:** Identify the host of the podcast.
# * **Guest(s):** Identify the guest or guests featured in this episode.

# **3. Detailed Topic-Based Summary:**
# * First, identify the main topics discussed throughout the podcast.
# * For each identified topic, provide a detailed summary try to make it of atleast 4 sentences. This summary should include:
#     * The key points made by the host and guest(s).
#     * Any significant arguments, disagreements, or elaborations.
#     * Important examples, anecdotes, or data points mentioned.
#     * The overall sentiment or conclusion related to the topic.
# * Structure the summary with clear headings for each topic to ensure readability. The summary should be substantial in length to cover all nuances of the conversation.

# **4. Key Takeaways:**
# * Conclude with a bulleted list of the 5-7 most important takeaways from the entire podcast. This should serve as a quick, scannable overview of the essential information.

# **Output Format:**

# Please structure your response using markdown for clear formatting. The final output should be well-organized, coherent, and easy to read.
#     """)
#         ])

#         # Prompt for Q&A extraction
#         prompt_qa = ChatPromptTemplate.from_messages([
#             ("system", system_prompt_qa),
#             ("human", """Here is the transcript or partial context:
#     {context}

#     Please process the provided transcript and perform the following actions:

# **1. Identify Participants:**
# * **Interviewer/Host:** Clearly identify the person asking the questions.
# * **Respondent/Guest(s):** Clearly identify the person or people answering the questions.

# **2. Extract Question and Answer Pairs:**
# * Go through the entire transcript from beginning to end.
# * For **every single question** asked by the Interviewer/Host, you must extract it verbatim.
# * For each question, synthesize a **detailed and comprehensive answer** based *exclusively* on the Respondent's/Guest's response in the provided context.
# * The answer should be thorough, capturing the key points, explanations, and any examples or data the respondent provided in their reply. Do not infer information or answer from outside the transcript.
# * If a single answer from a guest addresses multiple questions at once, list all the preceding questions followed by the consolidated, detailed answer.

# **Output Format:**

# Present the output in a clean, sequential, "Question and Answer" format. Use markdown for clarity. Number each pair sequentially.

# **Example Structure:**

# **Interviewer:** [Name of Host]
# **Guest:** [Name of Guest]

# ---

# **1. Question:** [The first exact question asked by the host.]
# ** Answer:** [A detailed summary of the guest's response to this specific question, based on the transcript.]

# **2. Question:** [The second exact question asked by the host.]
# ** Answer:** [A detailed summary of the guest's response to this specific question, based on the transcript.]

# **(Continue this format for all questions in the podcast)**
#     """)
#         ])

#         # Create separate chains
#         doc_chain_summary = create_stuff_documents_chain(llm=llm, prompt=prompt_summary)
#         doc_chain_qa = create_stuff_documents_chain(llm=llm, prompt=prompt_qa)

#         # Create separate retrieval chains
#         qa_chain_summary = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain_summary)
#         qa_chain_qa = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain_qa)

#         # Invoke both
#         response_summary = qa_chain_summary.invoke({"input": ""})
#         response_qa = qa_chain_qa.invoke({"input": ""})

#         # Store results
#         state.final_summary = response_summary.get("answer") or response_summary.get("output") or response_summary
#         state.qa = response_qa.get("answer") or response_qa.get("output") or response_qa

#         return state
#     else:
#         # Existing logic for other podcast types
#         if state.podcast_type == "panel":
#             system_prompt = f"You are a professional podcast summarizer who highlights key points and different perspectives from panel discussions. Please provide in {state.summary_language} language. PLease try to find the host name in {state.channel_and_title}."
#             prompt = ChatPromptTemplate.from_messages([
#                 ("system", system_prompt),
#                 ("human", """Here is the transcript or partial context:
#     {context}
# **Here are the specific requirements for your output:**

# 1.  **Catchy Discussion Title:**
#     * Generate a compelling, concise, and catchy title for the panel discussion that accurately reflects its central themes, key questions, and any potential areas of controversy or debate.

# 2.  **Speaker Identification & Affiliation:**
#     * **Identify all individual speakers** present in the transcript.
#     * For each speaker, provide their **full name** and any **available affiliation, title, or relevant background** mentioned in the discussion or clearly implied by their role. If an affiliation is not mentioned, state "Affiliation not mentioned."

# 3.  **Detailed Topic-Based Summary with Perspective Preservation & Disagreement Highlighting:**
#     * Segment the entire panel discussion into distinct, logical topics or themes as they unfold.
#     * For each identified topic:
#         * Provide a detailed summary of the discussion within that topic. This section MUST be at least four (4) sentences long.
#         * **Clearly attribute** key arguments, insights, questions, and significant statements to the specific speakers who made them, **using their identified names.**
#         * **Preserve and articulate the multiple perspectives** presented on the topic. Ensure that different viewpoints are explained in a neutral, balanced, and fair manner, reflecting the essence of each speaker's stance.
#         * **Explicitly highlight any points of disagreement, contention, or debate** between the speakers.
#             * Describe the nature of the disagreement (what exactly they disagree on).
#             * Outline the core arguments and reasoning of each side involved in the contention.
#             * Use phrases like "However, [Speaker X] countered by stating...", "A point of contention arose when...", "While [Speaker A] argued for X, [Speaker B] presented an opposing view on Y..."

# 4.  **Overall Goal:**
#     * The final output should give a reader a thorough and nuanced understanding of the entire panel discussion, including the key topics, the different perspectives of the speakers, and any debates that occurred, without needing to listen to the audio.

# **Output Format:**

# ---
# **Discussion Title:**
# [Your Catchy Title Here]

# ---
# **Speakers Identified:**
# * **[Speaker 1 Full Name]:** [Affiliation/Title, if available. Otherwise, "Affiliation not mentioned."]
# * **[Speaker 2 Full Name]:** [Affiliation/Title, if available. Otherwise, "Affiliation not mentioned."]
# * ... [List all identified speakers]

# ---
# **Podcast Overview:**
# [A brief, 1-2 sentence introductory paragraph setting the stage for the panel discussion's main subject and the range of perspectives involved.]

# ---
# **Detailed Topic Breakdown & Summary:**

# **Topic 1: [Descriptive and Concise Title for Topic 1]**
# [Detailed summary of Topic 1. This section MUST be at least 4 sentences long. Ensure it covers all key aspects discussed under this topic comprehensively, actively integrating speaker attributions and different perspectives. For example: "Initially, **Dr. Anya Sharma** introduced the concept of AI ethics in healthcare, emphasizing the need for transparency. **Mr. Ben Carter**, however, raised concerns about the practical implementation of such policies in current hospital systems."]

# * **Key Perspectives/Arguments:**
#     * **[Speaker 1 Name]:** [Summarize their main argument(s) on this topic.]
#     * **[Speaker 2 Name]:** [Summarize their main argument(s) on this topic.]
#     * ... [List all relevant speaker perspectives]

# * **Points of Disagreement/Contention:**
#     * [If a disagreement occurred, explain it here. For example: "A clear disagreement emerged regarding the role of government regulation versus industry self-regulation. **Dr. Sharma** argued that robust governmental oversight is essential to prevent misuse of data, citing recent privacy breaches. Conversely, **Mr. Carter** contended that industry-led initiatives would be more agile and responsive to technological advancements, fearing that government regulation could stifle innovation."]

# ---

# **Topic 2: [Descriptive and Concise Title for Topic 2]**
# [Detailed summary of Topic 2. This section MUST be at least 4 sentences long. Ensure it covers all key aspects discussed under this topic comprehensively, actively integrating speaker attributions and different perspectives.]

# * **Key Perspectives/Arguments:**
#     * **[Speaker 1 Name]:** [Summarize their main argument(s) on this topic.]
#     * **[Speaker 2 Name]:** [Summarize their main argument(s) on this topic.]
#     * ... [List all relevant speaker perspectives]

# * **Points of Disagreement/Contention:**
#     * [If a disagreement occurred, explain it here.]

# ---

# ... [Continue this format for ALL significant topics discussed in the panel discussion. Ensure complete coverage.]

# ---

# **Overall Concluding Thoughts & Key Debates:**
# [A final paragraph that ties together the main themes, highlights the most significant unresolved debates or shared understandings, and provides a concluding perspective on the panel's overall message or implications.]

# ---""")
#             ])

#             doc_chain_summary = create_stuff_documents_chain(llm=llm, prompt=prompt)
#             doc_retrival_chain_summary = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain_summary)

#             response_summary = doc_retrival_chain_summary.invoke({"input": ""})

#             state.final_summary = response_summary.get("answer") or response_summary.get("output") or response_summary

#             return state
#         elif state.podcast_type == "monologue":
#             system_prompt = f"You are an expert AI summarizer specializing in monologue podcasts. Your task is to provide an exceptionally detailed, topic-segmented, and analytical summary of the provided podcast transcript. The summary must be comprehensive enough that a reader gains a complete and proper overview of the podcast's content without needing to listen to the original audio.. Please provide in {state.summary_language} language. PLease try to find the host name in {state.channel_and_title}."
#             prompt = ChatPromptTemplate.from_messages([
#                 ("system", system_prompt),
#                 ("human", """Here is the transcript or partial context:
#     {context}
# **Here are the specific requirements for your output:**

# 1.  **Speaker Identification:**
#     * Carefully read the transcript and **identify the name of the speaker**. If the speaker's name is not explicitly mentioned but can be reasonably inferred (e.g., "I am [Name]"), state it. If it cannot be identified, state "Speaker's name not identified."
#     * Integrate the speaker's name naturally into the overall summary where appropriate (e.g., "The podcast, hosted by [Speaker's Name], delves into...").

# 2.  **Catchy Podcast Title:**
#     * Generate a compelling, concise, and catchy title for the podcast discussion that accurately reflects its central theme and intrigues potential listeners.

# 3.  **Detailed Topic-Based Summary (Comprehensive Coverage):**
#     * Segment the entire podcast into distinct, logical topics or themes as discussed by the speaker.
#     * For each identified topic, provide a detailed summary. Each topic summary MUST be at least four (4) sentences long.
#     * Ensure that ALL significant topics, sub-topics, and key points presented in the podcast are covered thoroughly. Do not omit any major discussions.
#     * The overall length of this combined topic-based summary should be substantial, providing a deep dive into the podcast's content rather than just a brief abstract. Aim for a summary that truly replaces the need to listen to the full podcast for understanding.

# 4.  **Argument Structure Detection (Per Topic or Overall):**
#     * For each major topic or segment you identify, clearly outline the speaker's argument structure.
#     * Identify the main premise(s) or claims made by the speaker within that segment.
#     * Detail the supporting points, evidence, examples, anecdotes, or logical reasoning used by the speaker to back up their claims.
#     * State the conclusion(s) or key takeaways derived from that argument.
#     * If a continuous argument spans multiple topics, describe its progression.

# **Output Format:**

# ---
# **Podcast Title:**
# [Your Catchy Title Here]

# **Speaker Name:**
# [Identified Speaker Name or "Not Identified"]

# ---
# **Podcast Overview:**
# [A brief, 1-2 sentence introductory paragraph setting the stage for the podcast's main subject or overarching goal, ideally incorporating the speaker's name.]

# ---
# **Detailed Topic Breakdown & Summary:**

# **Topic 1: [Descriptive and Concise Title for Topic 1]**
# [Detailed summary of Topic 1. This section MUST be at least 4 sentences long. Ensure it covers all key aspects discussed under this topic comprehensively.]

# * **Argument Structure for Topic 1:**
#     * **Main Premise(s):**
#         * [List key premise 1]
#         * [List key premise 2, if applicable]
#     * **Supporting Evidence/Reasoning:**
#         * [Describe supporting point/evidence 1]
#         * [Describe supporting point/evidence 2]
#         * [Describe any examples, statistics, or logical steps used]
#     * **Conclusion/Takeaway for Topic 1:**
#         * [State the speaker's main conclusion or implication from this segment]

# ---

# **Topic 2: [Descriptive and Concise Title for Topic 2]**
# [Detailed summary of Topic 2. This section MUST be at least 4 sentences long. Ensure it covers all key aspects discussed under this topic comprehensively.]

# * **Argument Structure for Topic 2:**
#     * **Main Premise(s):**
#         * [List key premise 1]
#         * [List key premise 2, if applicable]
#     * **Supporting Evidence/Reasoning:**
#         * [Describe supporting point/evidence 1]
#         * [Describe supporting point/evidence 2]
#         * [Describe any examples, statistics, or logical steps used]
#     * **Conclusion/Takeaway for Topic 2:**
#         * [State the speaker's main conclusion or implication from this segment]

# ---

# ... [Continue this format for ALL significant topics discussed in the podcast. Ensure complete coverage.]

# ---

# **Overall Concluding Thoughts/Key Implications:**
# [A final paragraph that ties together the main themes or provides a concluding perspective on the podcast's overall message or impact.]

# ---""")
#             ])

#             doc_chain_summary = create_stuff_documents_chain(llm=llm, prompt=prompt)
#             doc_retrival_chain_summary = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain_summary)

#             response_summary = doc_retrival_chain_summary.invoke({"input": ""})

#             state.final_summary = response_summary.get("answer") or response_summary.get("output") or response_summary

#             return state
#         else:
#             system_prompt = "Provide a clear, concise general summary of this podcast episode."

#         prompt = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human", """Here is the transcript or partial context:
#     {context}

#     Your task: Write a clear, engaging, and informative summary of this episode in Markdown format. Focus on the most important ideas and keep it concise.
#     """)
#         ])

#         doc_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
#         qa_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain)

#         response = qa_chain.invoke({"input": ""})
#         state.final_summary = response.get("answer") or response.get("output") or response

#         return state

import os
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from app.model.state import InterviewState
from dotenv import load_dotenv
load_dotenv()
import logging

logger = logging.getLogger(__name__) # Use the logger from semantic_summarizer_node if possible, or define here
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Initialize the embeddings model globally or pass it in
# This ensures consistency and avoids redundant loading
# IT MUST MATCH THE MODEL USED TO CREATE THE FAISS INDEX
from app.graph.graph import GLOBAL_EMBEDDINGS_MODEL


def type_based_summary_node(state: InterviewState) -> InterviewState:
    logger.info("inside type_based_summary_node") # Changed print to logger.info

    if not state.vector_db_path or not state.podcast_type:
        state.error_message = "Vector DB path or podcast type missing in state."
        logger.warning(state.error_message)
        return state
    
    # Check if Groq API key is available
    if not os.getenv("GROQ_API_KEY"):
        state.error_message = "GROQ_API_KEY environment variable not set."
        logger.error(state.error_message)
        return state

    try:
        vector_db = FAISS.load_local(state.vector_db_path, GLOBAL_EMBEDDINGS_MODEL, allow_dangerous_deserialization=True)
        
        num_segments = len(state.formatted_transcript_segments)
        k = max(30, int(0.6 * num_segments))  

        retriever = vector_db.as_retriever(search_kwargs={"k": k}) 
        
        llm_doc_limit = int(0.2 * num_segments)


        llm = ChatGroq(model="llama3-70b-8192", temperature=0.2)

        # Define system prompt for summary
        if state.podcast_type == "interview" and state.is_question == False:
            system_prompt_summary = (
        f"""You are an expert podcast summarizer. Generate a comprehensive, topic-based summary 
        that captures the complete essence of the podcast. Provide response in {state.summary_language}. 
        Extract host name from {state.channel_and_title} if available."""
    )
            
            # Refined prompt for summary
            prompt_summary = ChatPromptTemplate.from_messages([
                ("system", system_prompt_summary),
                ("human", """Transcript: {context}

        Generate the following:

        *1. Title:* Create an engaging title reflecting core themes.

        *2. Participants:* Identify host and guest(s). Leave blank if unclear.

        *3. Topic-Based Summary:*
        - Identify main topics discussed
        - For each topic, provide 4+ sentence summary including:
        * Key points from host and guest
        * Arguments, disagreements, elaborations
        * Examples, anecdotes, data points
        * Overall sentiment/conclusions
        - Use clear topic headings

        *4. Key Takeaways:* List 5-7 most important insights in bullet format.

        Use markdown formatting for clarity.""")
            ])

            # Refined system prompt for Q&A
            system_prompt_qa = (
                f"""You are an expert transcript analyst. Extract all questions and answers from this 
                podcast interview to create a clear dialogue record. Provide response in {state.summary_language}. 
                Extract host name from {state.channel_and_title} if available."""
            )

            # Refined prompt for Q&A
            prompt_qa = ChatPromptTemplate.from_messages([
    ("system", system_prompt_qa),
    ("human", """Transcript: {context}

Process the transcript and provide a polished Q&A dialogue record.

*1. Participants:*
- *Host:* The person asking the majority of questions
- *Guest:* The person primarily providing answers

*2. Question-Answer Extraction Guidelines:*
- Identify and extract each full question verbatim from the host
- If the host's question is fragmented or unclear, rewrite it as a complete, clear question based on context
- Synthesize the guest’s full answer using only their responses in the transcript
- Include all key points, explanations, and relevant examples
- Eliminate redundancy and filler language
- Use a consistent, clear, and professional tone

*3. Format and Style:*
- Number each Q&A pair sequentially
- Format exactly as follows:

*Host:* [Host Name]  
*Guest:* [Guest Name]  

---

*1. Question:* [Cleaned and complete version of the host's question]  
*Answer:* [Structured, complete, and coherent summary of the guest’s answer]

*2. Question:* [Next cleaned question]  
*Answer:* [Corresponding summarized answer]

Continue until all relevant Q&A pairs from the transcript are captured.""")
])

            relevant_docs_int_sum = retriever.invoke("Retrieve key moments and important discussions across all major topics from this podcast episode.")
            logger.info(f"Retrieved {len(relevant_docs_int_sum)} documents from FAISS for summary context.")

            if any("salience" in doc.metadata for doc in relevant_docs_int_sum):
                relevant_docs_int_sum = sorted(
                    relevant_docs_int_sum,
                    key=lambda doc: doc.metadata.get("salience", 0.5),
                    reverse=True
                )

            relevant_docs_int_sum = relevant_docs_int_sum[:llm_doc_limit]
            print("lenght", len(relevant_docs_int_sum))

            relevant_docs_qa = retriever.invoke("Retrieve question and answer pairs from this podcast episode.")
            logger.info(f"Retrieved {len(relevant_docs_qa)} documents from FAISS for Q&A context.")

            if any("salience" in doc.metadata for doc in relevant_docs_qa):
                relevant_docs_qa = sorted(
                    relevant_docs_qa,
                    key=lambda doc: doc.metadata.get("salience", 0.5),
                    reverse=True
                )

            relevant_docs_qa = relevant_docs_qa[:llm_doc_limit]

            # Create chains and invoke
            doc_chain_summary = create_stuff_documents_chain(llm=llm, prompt=prompt_summary)
            doc_chain_qa = create_stuff_documents_chain(llm=llm, prompt=prompt_qa)

            response_summary = doc_chain_summary.invoke({"input": relevant_docs_int_sum, "context": relevant_docs_int_sum})
            response_qa = doc_chain_qa.invoke({"input": relevant_docs_qa, "context": relevant_docs_qa})

            # Store results
            state.final_summary = response_summary
            state.qa = response_qa

            logger.info("Interview summary and Q&A generated.")
            return state
        
        # --- Existing logic for other podcast types (Panel, Monologue, General) ---
        elif state.podcast_type == "panel" and state.is_question == False:
            relevant_docs_panel = retriever.invoke("Key disagreements, debates, and contrasting opinions between panelists.")
            
            if any("salience" in doc.metadata for doc in relevant_docs_panel):
                relevant_docs_panel = sorted(
                    relevant_docs_panel,
                    key=lambda doc: doc.metadata.get("salience", 0.5),
                    reverse=True
                )

            relevant_docs_panel = relevant_docs_panel[:llm_doc_limit]

            system_prompt = f"You are a professional podcast summarizer who highlights key points and different perspectives from panel discussions. Please provide in {state.summary_language} language. PLease try to find the host name in {state.channel_and_title}."
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", """Here is the transcript or partial context:
    {context}
**Here are the specific requirements for your output:**

1.  **Discussion Title:**
    * Generate a compelling, concise, and catchy title for the panel discussion that accurately reflects its central themes, key questions, and any potential areas of controversy or debate.

2.  **Speaker Identification & Affiliation:**
    * **Identify all individual speakers** present in the transcript.
    * For each speaker, provide their **full name** and any **available affiliation, title, or relevant background** mentioned in the discussion or clearly implied by their role.
    If affiliation not found please ignore it.

3.  Organize discussion into major topics. For each topic, provide detailed analysis (6-8 sentences) covering:

## Content & Disagreement Analysis
- *Arguments*: Attribute key positions to speakers by name with supporting evidence
- *Conflicts*: Identify direct confrontations, ideological tensions, factual disputes, solution disagreements, and implicit contradictions
- *Dynamics*: Note alliances, power patterns, rhetorical strategies, and emotional undertones
- *Outcomes*: Highlight unresolved issues, emerging consensus, new questions raised, and practical implications

## Attribution Rules
- Use actual speaker names
- Preserve position nuance and evolution
- Distinguish core beliefs from tactical arguments

4.  **Overall Goal:**
    * The final output should give a reader a thorough and nuanced understanding of the entire panel discussion, including the key topics, the different perspectives of the speakers, and any debates that occurred, without needing to listen to the audio.

Output Format
Discussion Title: [Descriptive title]
Speakers:

[Name]: [Affiliation]

Overview: [4-6 sentences on main subject and perspectives]
Topic Analysis:
Topic 1: [Title]
[6-8 sentence detailed summary integrating speaker attributions and perspectives]
Key Arguments:

[Speaker]: [Main position and reasoning]

Disagreements:

[Detailed explanation of conflicts, including nature of disagreement and each side's reasoning]

[Repeat format for all topics]
Conclusion: [Summary of main debates, unresolved issues, and overall implications]
                 
---""")
            ])

            doc_chain_summary = create_stuff_documents_chain(llm=llm, prompt=prompt)
            # Invoke directly, using relevant_docs (either from representative_chunks or retrieved from DB)
            response_summary = doc_chain_summary.invoke({"input": relevant_docs_panel, "context": relevant_docs_panel})

            state.final_summary = response_summary
            logger.info("Panel summary generated.")
            return state

        elif state.podcast_type == "monologue" and state.is_question == False:
            system_prompt = f"""You are an expert AI summarizer specializing in monologue podcasts. Your expertise includes identifying narrative structures, argument flows, thematic progressions, personal storytelling, logical reasoning chains, and speaker credibility in single-speaker content.

        Your task is to provide a detailed, analytically rich summary of the monologue podcast transcript. The summary must be thorough enough that readers gain complete understanding of the speaker's message, arguments, and key insights without listening to the original audio.

        Please provide the summary in {state.summary_language} language. Identify the host/speaker name from {state.channel_and_title} and transcript content."""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", """Here is the monologue podcast transcript:
        {context}

        *SUMMARIZATION REQUIREMENTS:*

        ## SPEAKER & TITLE
        - Identify speaker's name through self-introductions, channel context, or inferential clues
        - Note credentials, expertise areas, or authority indicators
        - Create compelling podcast title capturing core message and unique perspective

        ## COMPREHENSIVE TOPIC ANALYSIS
        *For Each Topic (minimum 5-6 sentences):*
        - Cover all key points, stories, examples, and insights
        - Include personal anecdotes, data, research mentioned
        - Explain practical advice and emotional context
        - Show connections to broader themes

        ## ARGUMENT STRUCTURE ANALYSIS
        *For Each Major Topic:*
        - Identify argument type (logical, experiential, expert opinion, data-driven)
        - Map reasoning chains and evidence types
        - Note rhetorical techniques and persuasive devices
        - Explain logical progression between arguments

        ---

        ## OUTPUT FORMAT:

        *🎙 PODCAST TITLE:* [Compelling Title]

        *👤 SPEAKER:* 
        - *Name:* [Name or "Not Determinable"]
        - *Credentials:* [Qualifications/background mentioned]
        - *Perspective:* [Unique approach or worldview]

        *📋 OVERVIEW:* [2-3 sentences setting context and previewing main themes]

        *🔍 TOPIC BREAKDOWN:*

        ### *Topic 1: [Descriptive Title]*
        *Context:* [How topic was introduced]

        [Detailed 5-6 sentence summary covering key aspects, examples, stories, insights, and speaker's reasoning]

        *🧠 Analysis:*
        - *Core Premises:* [Primary and secondary claims]
        - *Evidence:* [Personal experiences, data, research, examples used]
        - *Rhetorical Approach:* [Storytelling, logic, emotion, etc.]
        - *Key Takeaway:* [Main conclusion or action item]

        ### *Topic 2: [Descriptive Title]* 
        [Follow same format...]

        *🎯 SYNTHESIS:*
        - *Central Message:* [Core point speaker wanted to convey]
        - *Actionable Insights:* [Practical takeaways]
        - *Broader Implications:* [Connection to larger trends/issues]
        - *Call-to-Action:* [Specific actions or changes encouraged]

        *📚 ASSESSMENT:*
        - *Depth:* [Surface/Intermediate/Deep-dive]
        - *Audience:* [Who benefits most]
        - *Unique Value:* [What makes it distinctive]
        - *Follow-up Potential:* [Topics for further exploration]

        *Goal:* Create a summary comprehensive enough for informed discussion without listening to the original.""")
        ])
            
            relevant_docs_monologue = retriever.invoke(
    "Extract the speaker’s thesis, key arguments, and supporting examples. "
    "Focus on their reasoning, narrative flow, and practical takeaways."
)


            if any("salience" in doc.metadata for doc in relevant_docs_monologue):
                relevant_docs_monologue = sorted(
                    relevant_docs_monologue,
                    key=lambda doc: doc.metadata.get("salience", 0.5),
                    reverse=True
                )

            relevant_docs_monologue = relevant_docs_monologue[:llm_doc_limit]

            doc_chain_summary = create_stuff_documents_chain(llm=llm, prompt=prompt)
            # Invoke directly, using relevant_docs (either from representative_chunks or retrieved from DB)
            response_summary = doc_chain_summary.invoke({"input": relevant_docs_monologue, "context": relevant_docs_monologue})

            state.final_summary =  response_summary
            logger.info("Monologue summary generated.")
            return state

        elif state.is_question == True: 
            system_prompt = "Provide a clear, concise general summary of this podcast episode."
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", """Here is the transcript or partial context:
    {context}

    Your task: Write a clear, engaging, and informative summary of this episode in Markdown format. Focus on the most important ideas and keep it concise.
    """)
            ])

            doc_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
            # Invoke directly, using relevant_docs (either from representative_chunks or retrieved from DB)
            response = doc_chain.invoke({"input": relevant_docs, "context": relevant_docs})

            state.final_summary = response
            logger.info("General summary generated.")
            return state

    except Exception as e:
        state.error_message = f"Error in type_based_summary_node: {str(e)}"
        logger.error(f"Error during type-based summarization: {e}", exc_info=True)
        return state