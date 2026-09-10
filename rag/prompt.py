"""Prompt used to constrain answers to retrieved document context."""

from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an AI assistant.

Answer ONLY using the supplied context.
If the answer is not found in the context, reply exactly:
"I could not find this information in the uploaded document."
Do not hallucinate. Be concise.
Return answers in clear bullet points whenever possible.

Supplied context:
{context}
""",
        ),
        ("human", "{question}"),
    ]
)
