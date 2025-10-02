import asyncio
import hashlib
import json
import ast
import re
from typing import Any, Iterable
import json5
from pydantic_ai import Agent
import requests
import psycopg2
from psycopg2.extras import Json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.models.openai import OpenAIChatModel

model = "nomic-embed-text"

chunking_agent = Agent(
    model=OpenAIChatModel(
        model_name='llama3:8b',
        provider=OllamaProvider(base_url="http://localhost:11434/v1"),
    ),
    deps_type=str,
    output_type=str,
    system_prompt="""
        Role: You are a highly precise document analyst and semantic chunking engine. Your task is to process a large document and divide it into sections that are maximally cohesive and self-contained.
        Task: Read the entire provided text carefully. Identify all major topical breaks, such as new headings, introduction/conclusion transitions, or a shift to a new key concept. Your primary directive is to ensure that no single idea, complete sentence, or data point is ever split across two chunks.
        Constraint: Each resulting chunk must be between 300 and 500 words (or approximately 2,000 to 4,000 characters) unless a full, coherent section is slightly smaller or larger. Always prioritize semantic completeness over word count.
        Output Format: Output the results as a clean JSON array of strings. Each string in the array will be one single, complete chunk. Do not include anything except the JSON array.
    """
)

metadata_agent = Agent(
    model=OpenAIChatModel(
        model_name='llama3:8b',
        provider=OllamaProvider(base_url="http://localhost:11434/v1"),
    ),
    deps_type=str,
    output_type=str,
    system_prompt="""
        You are an indexing and summarization expert. Your job is to generate precise, keyword-rich metadata for a single provided text chunk to maximize its retrievability in a vector database.
        Task: You have been given a single chunk of text. Generate a concise Title, a short Summary, and a list of up to 5 relevant Keywords for this specific chunk only.
        Constraint: The Title must be 3-8 words long. The Summary must be exactly one sentence and capture the chunk's main argument. The Keywords should be extracted directly from the text.
        Input: [Insert Chunk of Text Here]
        Output Format: Output the results as a single JSON object. Do not include anything except the JSON object.
            Example: 
            {
                "title": "Korean-Vietnam Business Directory Contact",
                "summary": "A Korean-Vietnam business directory listing publicly available company phone number and email, along with owner name Lee Moon Young.",
                "keywords": ["Korean-Vietnam", "business directory", "public contact", "phone number", "company email"]
            }
    """
)

# --- DB connection ---
conn = psycopg2.connect(
    dbname="clt-chatbot",
    user="postgres",
    password="postgres",
    host="10.0.0.85",
    port=54334,
)
cur = conn.cursor()

# --- Call Ollama nomic-embed-text ---


def get_embedding(text: str):
    url = "http://localhost:11434/api/embeddings"
    payload = {
        "model": model,
        "prompt": text
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()["embedding"]


def string_to_chunk_dicts(raw_str: str) -> list[dict]:
    """
    Convert a string that looks like a list[str] into a list[dict]
    with each dict having a single key 'chunk'.
    """
    try:
        # Safely evaluate into a real Python list
        string_list = ast.literal_eval(raw_str)
    except Exception as e:
        raise ValueError(f"Invalid input format: {e}")

    if not isinstance(string_list, list):
        raise ValueError("Input string must represent a list of strings")

    return [{"chunk": s} for s in string_list]


def convert_wrapped_json(raw_str: str):
    """
    Convert a JSON string wrapped in extra quotes into a Python dict.
    """
    try:
        # Remove leading/trailing quotes if present
        cleaned = raw_str.strip()
        if cleaned.startswith("'") and cleaned.endswith("'"):
            cleaned = cleaned[1:-1]

        # Now parse as JSON
        print(f"Converting JSON: {raw_str}")
        return json5.loads(cleaned)
    except json.JSONDecodeError as e:
        print(raw_str)
        raise ValueError(f"Invalid JSON: {e}")


def chunk_document(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,     # max chars per chunk
        chunk_overlap=200    # sliding window overlap
    )
    return splitter.split_text(text)

# --- Ingest document + chunks ---


def ingest_document(chunks):
    # Insert chunks & Embedding
    index = 1
    for chunk in chunks:
        chunk_data = chunk["chunk"]
        embedding = get_embedding(chunk_data)
        token_count = len(chunk_data.split())
        checksum = hashlib.sha256(chunk_data.encode("utf-8")).hexdigest()
        cur.execute(
            """
            INSERT INTO doc_chunks (chunk_index, text, token_count, checksum, model, vector, metadata)
            VALUES (%s, %s, %s, %s, %s,  %s, %s)
            RETURNING chunk_id
            """,
            (index, chunk_data, token_count, checksum,
             model, embedding, Json(chunk["metadata"]))
        )

    conn.commit()
    print(f"Inserted document with {len(chunks)} chunks")


async def main():
    doc_text = """
    CyberLogitec Vietnam (CLT Vietnam) is a key part of the global CyberLogitec/CLT organization, primarily functioning as a major Offshore Development Center (ODC) and IT service provider.
    Here is a summary of the information available about the company in Vietnam:
    Core Identity and Focus
        Function: It operates as an Offshore Development Center (ODC) for the global CyberLogitec company.
        Specialization: It provides IT outsourcing services for Software Development, Testing, and 24/7 Service Desk support.
        Industry Focus: They specialize in IT solutions for the logistics business, particularly shipping, port/terminal, forwarding, warehouse, and trucking.
        Global Support: CLT Vietnam supports the entire global network, providing IT services to customers in over 10 countries, including Korea, Singapore, Japan, the USA, and more.
        R&D: They also engage in research of new technologies, including machine learning (computer vision & chatbot), web, mobile, and virtual reality.
    Services and Solutions (Provided from Vietnam)
        The Vietnam branch leverages its local IT manpower to offer services for the global CyberLogitec customers and its own solutions:
        Outsourcing Services	Development Outsourcing (ODC)	Provides a dedicated team or manpower offering model for SW development, maintenance, and operation, securing required personnel quickly and strengthening cost competitiveness for clients.
        Global Service Desk	Offers 24/7 technical support and service.
        SW Testing and Inspection	Professional testing and inspection services to find errors and vulnerabilities.
        Digital Content	Transforming material into engaging digital content.
        Document Auto Processing (SHINE)	A tool for automatically extracting and converting various document data with high accuracy.
        Proprietary Solutions	Forwarding (CARIS)	A web-based single platform for Freight Forwarding and 3PL companies to manage global cargo/freight transportation.
        Factory Solutions (VALOR)	An integrated platform for managing key business processes and functions in a centralized manner.
        VisionAI	AI vision solutions using machine learning for analyzing visual data.
        Container Tracking (SMILE Tracking)	Offers real-time location monitoring of sea shipments in one place.
    
CyberLogitec Vietnam (CLT Vietnam) is a key part of the global CyberLogitec/CLT organization, primarily functioning as a major Offshore Development Center (ODC) and IT service provider.

Here is a summary of the information available about the company in Vietnam:

Core Identity and Focus
Function: It operates as an Offshore Development Center (ODC) for the global CyberLogitec company.

Specialization: It provides IT outsourcing services for Software Development, Testing, and 24/7 Service Desk support.

Industry Focus: They specialize in IT solutions for the logistics business, particularly shipping, port/terminal, forwarding, warehouse, and trucking.

Global Support: CLT Vietnam supports the entire global network, providing IT services to customers in over 10 countries, including Korea, Singapore, Japan, the USA, and more.

R&D: They also engage in research of new technologies, including machine learning (computer vision & chatbot), web, mobile, and virtual reality.

Services and Solutions (Provided from Vietnam)
The Vietnam branch leverages its local IT manpower to offer services for the global CyberLogitec customers and its own solutions:
ODC / Development Outsourcing: Provides dedicated team, turn-key project, and manpower models to quickly secure IT resources and improve client cost competitiveness.

Global Service Desk: Provides 24/7 support for global customers.

Document Auto Processing (SHINE): A tool for high-accuracy document data extraction and conversion.

CARIS: Forwarding system for Freight Forwarding and 3PL companies (web-based platform).

VisionAI: AI vision solutions utilizing machine learning for visual data analysis.

SMILE Tracking: Container tracking solution offering real-time sea shipment monitoring.
    Size and Location
        Headquarters/Office: Ho Chi Minh City, Vietnam.
        Address: SCETPA Building, 19A Cong Hoa Street, Ward 12, Tan Binh District, HCMC, Vietnam.
        Company Size: The company size is typically listed in the range of 501 - 1,000 employees, with some sources indicating over 1,000 powerful staff available for outsourcing services.
        Duration: The Vietnam entity has been in the industry for more than 9 years (as of a 2025 reference date).
    """
    chunks = await chunking_agent.run(user_prompt=f"""
        Task: Read the entire provided text carefully.
        Identify all major topical breaks, such as new headings, introduction/conclusion transitions, or a shift to a new key concept.
        Your primary directive is to ensure that no single idea, complete sentence, or data point is ever split across two chunks.
        Below this the text you need to split chunk:
            {doc_text}
    """, deps="")

    chunk_list = string_to_chunk_dicts(chunks.output)

    for chunk in chunk_list:
        metadata = await metadata_agent.run(user_prompt=f"""
            Task: You have been given a single chunk of text. Generate a concise Title, a short Summary, and a list of up to 5 relevant Keywords for this specific chunk only.
            Below this the text you need to give metada:
                {chunk["chunk"]}
        """, deps="")
        chunk["metadata"] = convert_wrapped_json(metadata.output)
        print(f"[Processed]: {chunk}")

    ingest_document(chunk_list)

# --- Example usage ---
if __name__ == "__main__":
    asyncio.run(main())
    # doc_title = "RAG Demo"
    # doc_text = """
    #     Name / Korean form: Moon-Young Lee (이문영).
    #     KICC

    #     Current role: Managing Director / Head (listed as Managing Director / MD / CEO of CyberLogitec Vietnam in public profiles).
    #     LinkedIn
    #     +1

    #     Company / location: CyberLogitec Vietnam — IT company focused on shipping, ports, logistics and smart-logistics solutions; office in Ho Chi Minh City, Vietnam. The company is described in press profiles as having grown to ~1,000+ IT staff.
    #     Craft.co
    #     +1

    #     Education (publicly listed): Yonsei University (listed on LinkedIn profile).
    #     LinkedIn

    #     Recent public activity / news: Quoted as head/CEO of CyberLogitec Vietnam in recent Korea–Vietnam partnership announcements (e.g., MOU with AproTech on AI collaboration).
    #     벤처스퀘어
    #     +1

    #     Public contact / company listing

    #     A Korean–Vietnam business directory lists company phone and a public contact email (sslee@cyberlogitec.com
    #     ) and shows the owner name as 이문영 (Lee Moon Young). Treat this as business contact info published by a local directory.
    # """

    # chunks = await chunking_agent.run()
    # metadata = {"source": "local_file", "author": "An Le"}

    # ingest_document(doc_title, doc_text, metadata)

    # cur.close()
    # conn.close()
