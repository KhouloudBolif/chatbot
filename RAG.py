import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions
from PyPDF2 import PdfReader

# Charger les variables d'environnement
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

# Initialisation des fonctions d'embedding et de ChromaDB
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=openai_key, model_name="text-embedding-3-small"
)
client = OpenAI(api_key=openai_key)
chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection_name = "document_qa_collection"
collection = chroma_client.get_or_create_collection(
    name=collection_name, embedding_function=openai_ef
)

# Fonction pour charger les documents
def load_documents_from_directory(directory_path):
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            with open(
                os.path.join(directory_path, filename), "r", encoding="utf-8"
            ) as file:
                documents.append({"id": filename, "text": file.read()})
        elif filename.endswith(".pdf"):
            try:
                pdf_reader = PdfReader(os.path.join(directory_path, filename))
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text()
                documents.append({"id": filename, "text": pdf_text})
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return documents

# Fonction pour découper les documents
def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks

# Fonction pour indexer les documents
def index_documents(directory_path):
    documents = load_documents_from_directory(directory_path)
    chunked_documents = []

    for doc in documents:
        chunks = split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunked_documents.append({"id": f"{doc['id']}_chunk{i+1}", "text": chunk})

    for doc in chunked_documents:
        if not document_has_embedding(doc["id"]):
            embedding = get_openai_embedding(doc["text"])
            collection.upsert(
                ids=[doc["id"]], documents=[doc["text"]], embeddings=[embedding]
            )
    return "indexation successfuly"

# Vérifier si un document a déjà un embedding
def document_has_embedding(doc_id):
    results = collection.query(query_texts=[doc_id], n_results=1)
    return bool(results["documents"])

# Fonction pour générer les embeddings
def get_openai_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

# Fonction pour interroger les documents
def query_documents(question, n_results=2):
    results = collection.query(query_texts=[question], n_results=n_results)
    relevant_chunks = [doc for sublist in results["documents"] for doc in sublist]
    return relevant_chunks

# Fonction pour générer une réponse
def generate_response(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)
    prompt = (
        "You are an assistant for question-answering tasks. Use the following pieces of "
        "retrieved context to answer the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the answer concise."
        "\n\nContext:\n" + context + "\n\nQuestion:\n" + question
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    answer = response.choices[0].message
    return answer
