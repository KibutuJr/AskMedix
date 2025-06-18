from flask import Flask, render_template, request
from dotenv import load_dotenv
from src.helper import download_hugging_face_embeddings
from src.prompt import system_prompt

from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import HuggingFaceHub  

import os

app = Flask(__name__)

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
HUGGINGFACEHUB_API_TOKEN = os.environ.get('HUGGINGFACEHUB_API_TOKEN')

# Set Hugging Face token
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Load sentence-transformer embeddings
embeddings = download_hugging_face_embeddings()

# Load existing Pinecone index
index_name = "AskMediX"
vectorstore = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

# Retriever
retriever = vectorstore.as_retriever(
    search_type="similarity", search_kwargs={"k": 3}
)

# Hugging Face LLM (You can change the model if needed)
llm = HuggingFaceHub(
    repo_id="google/flan-t5-base",  # or use bigger like 'tiiuae/falcon-7b-instruct' if hosted
    model_kwargs={"temperature": 0.5, "max_length": 500}
)

# Prompt + Chain setup
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

qa_chain = create_stuff_documents_chain(llm, prompt_template)
rag_chain = create_retrieval_chain(retriever, qa_chain)

# Routes
@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    try:
        user_input = request.form["msg"]
        response = rag_chain.invoke({"input": user_input})
        answer = response.get("answer", "Sorry, I couldn't find a suitable answer.")
        return str(answer)
    except Exception as e:
        print(f"Error: {e}")
        return "Oops! Something went wrong while generating a response."

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
