from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from app.model.state import InterviewState
from dotenv import load_dotenv
load_dotenv()
import os

def type_based_summary_node(state: InterviewState) -> InterviewState:
    if not state.vector_db_path or not state.podcast_type:
        state.error_message = "Vector DB or podcast type missing"
        return state

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db = FAISS.load_local(state.vector_db_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vector_db.as_retriever(search_kwargs={"k": 10})

    llm = ChatGroq(model="llama3-70b-8192", temperature=0.2)
    # Define system prompt
    if state.podcast_type == "interview":
    # System prompt for summary
        system_prompt_summary = (
           f"You are an expert podcast summarizer. Your task is to generate a detailed, topic-based summary of the following podcast transcript. The goal is to provide a comprehensive overview that allows a reader to understand the entire conversation, including key insights, arguments, and examples, without needing to listen to the audio. Please provide in {state.summary_language} language. PLease try to find the host name in {state.channel_and_title}."
        )

        # System prompt for Q&A extraction
        system_prompt_qa = (
            f"You are an expert transcript analyst. Your task is to meticulously extract all questions and their corresponding answers from the following podcast transcript. The goal is to create a clear and accurate record of the interview's dialogue flow. Please provide in {state.summary_language} language. PLease try to find the host name in {state.channel_and_title}."
        )

        # Prompt for summary
        prompt_summary = ChatPromptTemplate.from_messages([
            ("system", system_prompt_summary),
            ("human", """Here is the transcript or partial context:
    {context}

**Instructions:**

Based on the provided transcript, please generate the following:

**1. Catchy Title:**
* Provide engaging and catchy title for this podcast episode. These title should accurately reflect the core themes of the conversation.

**2. Participants:**
* **Host:** Identify the host of the podcast.
* **Guest(s):** Identify the guest or guests featured in this episode.

**3. Detailed Topic-Based Summary:**
* First, identify the main topics discussed throughout the podcast.
* For each identified topic, provide a detailed summary try to make it of atleast 4 sentences. This summary should include:
    * The key points made by the host and guest(s).
    * Any significant arguments, disagreements, or elaborations.
    * Important examples, anecdotes, or data points mentioned.
    * The overall sentiment or conclusion related to the topic.
* Structure the summary with clear headings for each topic to ensure readability. The summary should be substantial in length to cover all nuances of the conversation.

**4. Key Takeaways:**
* Conclude with a bulleted list of the 5-7 most important takeaways from the entire podcast. This should serve as a quick, scannable overview of the essential information.

**Output Format:**

Please structure your response using markdown for clear formatting. The final output should be well-organized, coherent, and easy to read.
    """)
        ])

        # Prompt for Q&A extraction
        prompt_qa = ChatPromptTemplate.from_messages([
            ("system", system_prompt_qa),
            ("human", """Here is the transcript or partial context:
    {context}

    Please process the provided transcript and perform the following actions:

**1. Identify Participants:**
* **Interviewer/Host:** Clearly identify the person asking the questions.
* **Respondent/Guest(s):** Clearly identify the person or people answering the questions.

**2. Extract Question and Answer Pairs:**
* Go through the entire transcript from beginning to end.
* For **every single question** asked by the Interviewer/Host, you must extract it verbatim.
* For each question, synthesize a **detailed and comprehensive answer** based *exclusively* on the Respondent's/Guest's response in the provided context.
* The answer should be thorough, capturing the key points, explanations, and any examples or data the respondent provided in their reply. Do not infer information or answer from outside the transcript.
* If a single answer from a guest addresses multiple questions at once, list all the preceding questions followed by the consolidated, detailed answer.

**Output Format:**

Present the output in a clean, sequential, "Question and Answer" format. Use markdown for clarity. Number each pair sequentially.

**Example Structure:**

**Interviewer:** [Name of Host]
**Guest:** [Name of Guest]

---

**1. Question:** [The first exact question asked by the host.]
** Answer:** [A detailed summary of the guest's response to this specific question, based on the transcript.]

**2. Question:** [The second exact question asked by the host.]
** Answer:** [A detailed summary of the guest's response to this specific question, based on the transcript.]

**(Continue this format for all questions in the podcast)**
    """)
        ])

        # Create separate chains
        doc_chain_summary = create_stuff_documents_chain(llm=llm, prompt=prompt_summary)
        doc_chain_qa = create_stuff_documents_chain(llm=llm, prompt=prompt_qa)

        # Create separate retrieval chains
        qa_chain_summary = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain_summary)
        qa_chain_qa = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain_qa)

        # Invoke both
        response_summary = qa_chain_summary.invoke({"input": ""})
        response_qa = qa_chain_qa.invoke({"input": ""})

        # Store results
        state.final_summary = response_summary.get("answer") or response_summary.get("output") or response_summary
        state.qa = response_qa.get("answer") or response_qa.get("output") or response_qa

        return state
    else:
        # Existing logic for other podcast types
        if state.podcast_type == "panel":
            system_prompt = f"You are a professional podcast summarizer who highlights key points and different perspectives from panel discussions. Please provide in {state.summary_language} language. PLease try to find the host name in {state.channel_and_title}."
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", """Here is the transcript or partial context:
    {context}
**Here are the specific requirements for your output:**

1.  **Catchy Discussion Title:**
    * Generate a compelling, concise, and catchy title for the panel discussion that accurately reflects its central themes, key questions, and any potential areas of controversy or debate.

2.  **Speaker Identification & Affiliation:**
    * **Identify all individual speakers** present in the transcript.
    * For each speaker, provide their **full name** and any **available affiliation, title, or relevant background** mentioned in the discussion or clearly implied by their role. If an affiliation is not mentioned, state "Affiliation not mentioned."

3.  **Detailed Topic-Based Summary with Perspective Preservation & Disagreement Highlighting:**
    * Segment the entire panel discussion into distinct, logical topics or themes as they unfold.
    * For each identified topic:
        * Provide a detailed summary of the discussion within that topic. This section MUST be at least four (4) sentences long.
        * **Clearly attribute** key arguments, insights, questions, and significant statements to the specific speakers who made them, **using their identified names.**
        * **Preserve and articulate the multiple perspectives** presented on the topic. Ensure that different viewpoints are explained in a neutral, balanced, and fair manner, reflecting the essence of each speaker's stance.
        * **Explicitly highlight any points of disagreement, contention, or debate** between the speakers.
            * Describe the nature of the disagreement (what exactly they disagree on).
            * Outline the core arguments and reasoning of each side involved in the contention.
            * Use phrases like "However, [Speaker X] countered by stating...", "A point of contention arose when...", "While [Speaker A] argued for X, [Speaker B] presented an opposing view on Y..."

4.  **Overall Goal:**
    * The final output should give a reader a thorough and nuanced understanding of the entire panel discussion, including the key topics, the different perspectives of the speakers, and any debates that occurred, without needing to listen to the audio.

**Output Format:**

---
**Discussion Title:**
[Your Catchy Title Here]

---
**Speakers Identified:**
* **[Speaker 1 Full Name]:** [Affiliation/Title, if available. Otherwise, "Affiliation not mentioned."]
* **[Speaker 2 Full Name]:** [Affiliation/Title, if available. Otherwise, "Affiliation not mentioned."]
* ... [List all identified speakers]

---
**Podcast Overview:**
[A brief, 1-2 sentence introductory paragraph setting the stage for the panel discussion's main subject and the range of perspectives involved.]

---
**Detailed Topic Breakdown & Summary:**

**Topic 1: [Descriptive and Concise Title for Topic 1]**
[Detailed summary of Topic 1. This section MUST be at least 4 sentences long. Ensure it covers all key aspects discussed under this topic comprehensively, actively integrating speaker attributions and different perspectives. For example: "Initially, **Dr. Anya Sharma** introduced the concept of AI ethics in healthcare, emphasizing the need for transparency. **Mr. Ben Carter**, however, raised concerns about the practical implementation of such policies in current hospital systems."]

* **Key Perspectives/Arguments:**
    * **[Speaker 1 Name]:** [Summarize their main argument(s) on this topic.]
    * **[Speaker 2 Name]:** [Summarize their main argument(s) on this topic.]
    * ... [List all relevant speaker perspectives]

* **Points of Disagreement/Contention:**
    * [If a disagreement occurred, explain it here. For example: "A clear disagreement emerged regarding the role of government regulation versus industry self-regulation. **Dr. Sharma** argued that robust governmental oversight is essential to prevent misuse of data, citing recent privacy breaches. Conversely, **Mr. Carter** contended that industry-led initiatives would be more agile and responsive to technological advancements, fearing that government regulation could stifle innovation."]

---

**Topic 2: [Descriptive and Concise Title for Topic 2]**
[Detailed summary of Topic 2. This section MUST be at least 4 sentences long. Ensure it covers all key aspects discussed under this topic comprehensively, actively integrating speaker attributions and different perspectives.]

* **Key Perspectives/Arguments:**
    * **[Speaker 1 Name]:** [Summarize their main argument(s) on this topic.]
    * **[Speaker 2 Name]:** [Summarize their main argument(s) on this topic.]
    * ... [List all relevant speaker perspectives]

* **Points of Disagreement/Contention:**
    * [If a disagreement occurred, explain it here.]

---

... [Continue this format for ALL significant topics discussed in the panel discussion. Ensure complete coverage.]

---

**Overall Concluding Thoughts & Key Debates:**
[A final paragraph that ties together the main themes, highlights the most significant unresolved debates or shared understandings, and provides a concluding perspective on the panel's overall message or implications.]

---""")
            ])

            doc_chain_summary = create_stuff_documents_chain(llm=llm, prompt=prompt)
            doc_retrival_chain_summary = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain_summary)

            response_summary = doc_retrival_chain_summary.invoke({"input": ""})

            state.final_summary = response_summary.get("answer") or response_summary.get("output") or response_summary

            return state
        elif state.podcast_type == "monologue":
            system_prompt = f"You are an expert AI summarizer specializing in monologue podcasts. Your task is to provide an exceptionally detailed, topic-segmented, and analytical summary of the provided podcast transcript. The summary must be comprehensive enough that a reader gains a complete and proper overview of the podcast's content without needing to listen to the original audio.. Please provide in {state.summary_language} language. PLease try to find the host name in {state.channel_and_title}."
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", """Here is the transcript or partial context:
    {context}
**Here are the specific requirements for your output:**

1.  **Speaker Identification:**
    * Carefully read the transcript and **identify the name of the speaker**. If the speaker's name is not explicitly mentioned but can be reasonably inferred (e.g., "I am [Name]"), state it. If it cannot be identified, state "Speaker's name not identified."
    * Integrate the speaker's name naturally into the overall summary where appropriate (e.g., "The podcast, hosted by [Speaker's Name], delves into...").

2.  **Catchy Podcast Title:**
    * Generate a compelling, concise, and catchy title for the podcast discussion that accurately reflects its central theme and intrigues potential listeners.

3.  **Detailed Topic-Based Summary (Comprehensive Coverage):**
    * Segment the entire podcast into distinct, logical topics or themes as discussed by the speaker.
    * For each identified topic, provide a detailed summary. Each topic summary MUST be at least four (4) sentences long.
    * Ensure that ALL significant topics, sub-topics, and key points presented in the podcast are covered thoroughly. Do not omit any major discussions.
    * The overall length of this combined topic-based summary should be substantial, providing a deep dive into the podcast's content rather than just a brief abstract. Aim for a summary that truly replaces the need to listen to the full podcast for understanding.

4.  **Argument Structure Detection (Per Topic or Overall):**
    * For each major topic or segment you identify, clearly outline the speaker's argument structure.
    * Identify the main premise(s) or claims made by the speaker within that segment.
    * Detail the supporting points, evidence, examples, anecdotes, or logical reasoning used by the speaker to back up their claims.
    * State the conclusion(s) or key takeaways derived from that argument.
    * If a continuous argument spans multiple topics, describe its progression.

**Output Format:**

---
**Podcast Title:**
[Your Catchy Title Here]

**Speaker Name:**
[Identified Speaker Name or "Not Identified"]

---
**Podcast Overview:**
[A brief, 1-2 sentence introductory paragraph setting the stage for the podcast's main subject or overarching goal, ideally incorporating the speaker's name.]

---
**Detailed Topic Breakdown & Summary:**

**Topic 1: [Descriptive and Concise Title for Topic 1]**
[Detailed summary of Topic 1. This section MUST be at least 4 sentences long. Ensure it covers all key aspects discussed under this topic comprehensively.]

* **Argument Structure for Topic 1:**
    * **Main Premise(s):**
        * [List key premise 1]
        * [List key premise 2, if applicable]
    * **Supporting Evidence/Reasoning:**
        * [Describe supporting point/evidence 1]
        * [Describe supporting point/evidence 2]
        * [Describe any examples, statistics, or logical steps used]
    * **Conclusion/Takeaway for Topic 1:**
        * [State the speaker's main conclusion or implication from this segment]

---

**Topic 2: [Descriptive and Concise Title for Topic 2]**
[Detailed summary of Topic 2. This section MUST be at least 4 sentences long. Ensure it covers all key aspects discussed under this topic comprehensively.]

* **Argument Structure for Topic 2:**
    * **Main Premise(s):**
        * [List key premise 1]
        * [List key premise 2, if applicable]
    * **Supporting Evidence/Reasoning:**
        * [Describe supporting point/evidence 1]
        * [Describe supporting point/evidence 2]
        * [Describe any examples, statistics, or logical steps used]
    * **Conclusion/Takeaway for Topic 2:**
        * [State the speaker's main conclusion or implication from this segment]

---

... [Continue this format for ALL significant topics discussed in the podcast. Ensure complete coverage.]

---

**Overall Concluding Thoughts/Key Implications:**
[A final paragraph that ties together the main themes or provides a concluding perspective on the podcast's overall message or impact.]

---""")
            ])

            doc_chain_summary = create_stuff_documents_chain(llm=llm, prompt=prompt)
            doc_retrival_chain_summary = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain_summary)

            response_summary = doc_retrival_chain_summary.invoke({"input": ""})

            state.final_summary = response_summary.get("answer") or response_summary.get("output") or response_summary

            return state
        else:
            system_prompt = "Provide a clear, concise general summary of this podcast episode."

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", """Here is the transcript or partial context:
    {context}

    Your task: Write a clear, engaging, and informative summary of this episode in Markdown format. Focus on the most important ideas and keep it concise.
    """)
        ])

        doc_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        qa_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=doc_chain)

        response = qa_chain.invoke({"input": ""})
        state.final_summary = response.get("answer") or response.get("output") or response

        return state
