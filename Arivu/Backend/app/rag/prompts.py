"""Prompt templates for RAG generation and query rewriting.

Uses LangChain ChatPromptTemplate for structured prompts.
Token counting uses LangChain's built-in utilities.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

# ── RAG Prompts ──────────────────────────────────────────

RAG_SYSTEM_PROMPT = """\
You are a knowledgeable and detailed question-answering assistant. Your goal is to provide comprehensive, well-structured, and accurate answers based on the provided context.

CORE PRINCIPLES:
1. BASE YOUR ANSWER ON THE CONTEXT: Prioritize information found in the context. However, you are encouraged to provide helpful explanations and background information that connects to the context to make the answer more readable and complete.
2. BE DETAILED AND THOROUGH: Provide multiple paragraphs of explanation. Do not be brief. Expand on the implications, background, and key concepts mentioned in the context.
3. CITE YOUR SOURCES: For every specific claim or fact derived from the context, you MUST use the exact format: [Source N] where N is the source number. Place citations immediately after the relevant sentence.
4. FORMAT YOUR OUTPUT: Use Markdown (headers, bolding, lists, and tables) to make your response visually appealing and easy to parse.
5. NO HALLUCINATIONS: Do not state facts that contradict the context or provided knowledge. If the context is completely irrelevant to the question, state that you don't have enough specific information in the documents, but then offer a general helpful response if possible while clarifying it's not from the docs.

CITATION EXAMPLES:
✓ "The system architecture is based on microservices [Source 1]. This allows for independent scaling [Source 2]."
✗ "According to the context, the system uses microservices." (missing specific source number citation)
"""

RAG_USER_TEMPLATE = """\
CONTEXT:
{context}

QUESTION: {input}

INSTRUCTIONS: Answer the question using ONLY the context above. Cite sources using [Source N] format.

ANSWER:"""

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", RAG_SYSTEM_PROMPT),
    ("human", RAG_USER_TEMPLATE),
])

CONDENSE_QUESTION_PROMPT = """\
Given the following conversation and a follow-up question, rephrase the follow-up question \
to be a standalone question.

Chat History:
{chat_history}

Follow Up Input: {question}

Standalone question:"""

CONDENSE_QUESTION_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("system", "Given the conversation and follow-up question, rephrase it to be a standalone question."),
])

# ── Query Rewrite Prompts ────────────────────────────────

QUERY_REWRITE_PROMPT = """\
You are a search query optimizer. Given a user question, rewrite it as a clear, \
specific search query that will retrieve the most relevant document chunks.
Only output the rewritten query, nothing else.

User question: {question}

Rewritten query:"""

QUERY_REWRITE_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a search query optimizer."),
    ("human", QUERY_REWRITE_PROMPT),
])

MULTI_QUERY_PROMPT = """\
You are an expert search query generator. 
The user's question is: {question}

Your goal is to generate exactly 3 alternative search queries that will help find the answer to the user's question. 
Derive these queries directly from the user's specific question. 

RULES:
- Provide ONLY the 3 queries, one per line.
- Do NOT include any intro text, numbers, or bullet points.
- Do NOT use generic queries like 'what is the meaning of life'.

3 Alternative Search Queries:"""

MULTI_QUERY_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("human", MULTI_QUERY_PROMPT),
])

# ── RAPTOR Prompt ────────────────────────────────────────

RAPTOR_SUMMARIZATION_PROMPT = """\
You are an expert summarizer. The following is a collection of related text chunks from a document:

{context}

Please provide a detailed summary of the key information contained in these chunks. \
Preserve important details, numbers, and entities. The summary should be cohesive and \
stand as a representative overview of this cluster of information.

Summary:"""

RAPTOR_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("human", RAPTOR_SUMMARIZATION_PROMPT),
])


# ── Study Mode Prompts ───────────────────────────────────

STUDY_GUIDE_PROMPT = """\
You are an expert tutor creating a study guide.
The following is a high-level summary of the course material:

{context}

Your task is to generate {count} items for a {mode}.
Topic Focus (if any): {topic}

Instructions:
- If 'quiz': Generate multiple-choice questions with answers.
- If 'flashcards': Generate Term - Definition pairs.
- If 'summary': Generate a structured overview of key concepts.

Ensure the content covers the material comprehensively.
Output:"""

STUDY_GUIDE_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert tutor."),
    ("human", STUDY_GUIDE_PROMPT),
])


# ── Utility functions ────────────────────────────────────

def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context string.

    Each chunk dict should have at minimum 'text' and 'filename'.
    """
    parts: list[str] = []
    for i, c in enumerate(chunks, 1):
        header = f"[Source {i}] {c.get('filename', 'unknown')}"
        if c.get("page") is not None:
            header += f" (page {c['page']})"
        text = c.get("text", "")
        if not text:
            continue
        parts.append(f"{header}\n{text}")
    return "\n\n---\n\n".join(parts)


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using LangChain's get_num_tokens.
    Falls back to char-based estimate.
    """
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=model)
        return llm.get_num_tokens(text)
    except Exception:
        # Fallback: ~4 chars per token (conservative)
        return len(text) // 4


def truncate_context(
    chunks: list[dict],
    *,
    max_tokens: int = 6000,
    model: str = "gpt-4",
) -> list[dict]:
    """Truncate chunks to fit within max_tokens budget."""
    import logging

    log = logging.getLogger(__name__)

    selected = []
    total_tokens = 0

    for chunk in chunks:
        chunk_text = f"[Source {len(selected)+1}] {chunk.get('filename', '')}\n{chunk['text']}"
        chunk_tokens = count_tokens(chunk_text, model)

        if total_tokens + chunk_tokens > max_tokens:
            log.warning(
                "Context truncated: %d/%d chunks (exceeded %d tokens)",
                len(selected),
                len(chunks),
                max_tokens,
            )
            break

        selected.append(chunk)
        total_tokens += chunk_tokens

    return selected
