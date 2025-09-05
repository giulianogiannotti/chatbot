import os
import glob
import re
from concurrent.futures import ThreadPoolExecutor

import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# --- Configuración de página ---
st.set_page_config(page_title="Bot de Resoluciones", layout="wide")
st.title("🔍 Bot de Resoluciones")
st.write("Consultá resoluciones y obtené respuestas detalladas con cita de archivos.")

# --- Función para extraer metadatos de resoluciones ---
PATRONES = [
    re.compile(r'(?P<letras>[A-Z]{1,5})-(?P<num1>\d{3})[-\.](?P<num2>\d{2,4})', re.IGNORECASE),
    re.compile(r'(?P<letras>[A-Z]{3,5})[-\.](?P<letras2>[A-Z]{2,4})[-\.](?P<num>\d{1,4})', re.IGNORECASE),
    re.compile(r'(?P<letras1>[A-Z]{1})-(?P<letras2>[A-Z]{3})[-\.](?P<num>\d{2,4})', re.IGNORECASE),
    re.compile(r'(?P<letras>[A-Z]{3,5})[-\.](?P<num1>\d{1,4})[-\.](?P<num2>\d{1,4})', re.IGNORECASE),
    re.compile(r'(?P<letras>[A-Z]{3,5})[-\.](?P<num1>\d{1,4})', re.IGNORECASE),
    re.compile(r'(?P<letras>[A-Z]{3,5})\s+(?P<num1>\d{3})[-\.](?P<num2>\d{2,4})', re.IGNORECASE),
    re.compile(r'(?P<letras>[A-Z]{3,5})-?\s*(?P<num1>\d{3})[-\.]{1,2}(?P<num2>\d{2,4})', re.IGNORECASE),
    re.compile(r'(?P<letras>[A-Z]{1,2})-(?P<num1>\d{3})[-\.](?P<num2>\d{2})', re.IGNORECASE),
    re.compile(r'(?P<letras>[A-Z]{3,5})-\.(?P<num1>\d{2,4})', re.IGNORECASE),
]

def extraer_metadato_resolucion(nombre_archivo):
    for patron in PATRONES:
        match = patron.search(nombre_archivo)
        if match:
            return match.group(0)
    return nombre_archivo  # fallback

# --- Cargar documentos y generar vectorstore ---
@st.cache_resource
def load_vectorstore():
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    DOCS_PATH = os.path.join(BASE_PATH, "RESOLUCIONES_2", "RESOLUCIONES")

    if not os.path.exists(DOCS_PATH):
        st.error(f"No se encontró la carpeta {DOCS_PATH}")
        return None

    doc_paths = glob.glob(f"{DOCS_PATH}/**/*.docx", recursive=True)
    pdf_paths = glob.glob(f"{DOCS_PATH}/**/*.pdf", recursive=True)
    all_paths = doc_paths + pdf_paths

    documents = []

    def load_document(file_path):
        try:
            if file_path.endswith(".docx"):
                loader = UnstructuredWordDocumentLoader(file_path)
            elif file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            else:
                return []
            docs = loader.load()
            nombre_archivo = os.path.basename(file_path)
            identificador = extraer_metadato_resolucion(nombre_archivo)
            for doc in docs:
                doc.metadata["resolucion"] = identificador
                doc.metadata["source"] = nombre_archivo
            return docs
        except Exception as e:
            print(f"Error al cargar {file_path}: {e}")
            return []

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = executor.map(load_document, all_paths)
        for doc_list in results:
            documents.extend(doc_list)

    splitter_small = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits_small = splitter_small.split_documents(documents)
    for chunk in splits_small:
        res = chunk.metadata.get("resolucion", "Sin identificador")
        name = os.path.basename(chunk.metadata.get("source", "Sin archivo"))
        chunk.page_content = f"[Resolución: {res} | Archivo: {name}]\n{chunk.page_content}"

    embedding = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-small",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vectorstore = FAISS.from_documents(splits_small, embedding)
    return vectorstore

vectorstore = load_vectorstore()
if vectorstore is None:
    st.stop()
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5})

token = st.secrets["HUGGINGFACEHUB_API_TOKEN"]
# --- Inicializar LLM y QA chain ---
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Devstral-Small-2505",
    temperature=0.5,
    max_new_tokens=500,
    stop_sequences=["Pregunta:", "Respuesta:"],
    huggingfacehub_api_token=token
)

prompt_template = """Usa el siguiente contexto para responder en español.
Incluye todos los detalles relevantes que encuentres.
Siempre que sea posible, **cita la resolución o archivo fuente donde se encuentra la información**.
Si no tienes suficiente información, responde que no puedes dar una respuesta con certeza.

Contexto: {context}
Pregunta: {question}
Respuesta detallada con cita:"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt_template)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
)

# --- Historial de preguntas y respuestas ---
if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Escribí tu pregunta:")

if query:
    with st.spinner("Buscando respuesta..."):
        resp = qa_chain.invoke(query)
        st.session_state.history.append({"question": query, "answer": resp["result"]})

# --- Mostrar historial ---
if st.session_state.history:
    for i, qa in enumerate(st.session_state.history[::-1]):  # mostrar desde la última
        st.markdown(f"**Pregunta:** {qa['question']}")
        st.markdown(f"**Respuesta:** {qa['answer']}")
        st.markdown("---")
