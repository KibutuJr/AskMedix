import os
import uuid
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# LangChain and vector DB
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface.llms import HuggingFaceEndpoint
from langchain_community.vectorstores import Pinecone as LangchainPinecone

# External services
from twilio.rest import Client as TwilioClient
import sendgrid
from sendgrid.helpers.mail import Mail
from sheets_utils import get_sheet

# Pinecone official SDK v3
from pinecone import Pinecone, ServerlessSpec

# ------------------- Load environment -------------------
load_dotenv()

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER")

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

# ------------------- PDF + Embeddings -------------------
pdf_path = "data/Medical_book.pdf"
if not os.path.exists(pdf_path):
    raise FileNotFoundError("📁 PDF file not found at 'data/Medical_book.pdf'.")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ------------------- Pinecone Index -------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "askmedix-index"

# Wrapper to mimic pinecone.Index for LangChain compatibility
class FakePineconeIndex:
    def __init__(self, real_index):
        self._real_index = real_index

    def __getattr__(self, item):
        return getattr(self._real_index, item)

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # matches MiniLM-L6-v2
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT)
    )
    with st.spinner("⚙️ Creating and populating Pinecone index..."):
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = splitter.split_documents(pages)

        index = FakePineconeIndex(pc.Index(index_name))
        vectorstore = LangchainPinecone.from_documents(
            docs,
            embedding=embeddings,
            index_name=index_name,
            text_key="text",
            namespace="",  # Optional
        )
else:
    index = FakePineconeIndex(pc.Index(index_name))
    vectorstore = LangchainPinecone(
        index=index,
        embedding=embeddings,
        text_key="text",
        namespace="",  # Optional
    )

# ------------------- Hugging Face LLM -------------------
llm = HuggingFaceEndpoint(
    repo_id="google/flan-t5-base",
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
    task="text2text-generation",
    max_new_tokens=256,
    temperature=0.5
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="AskMediX", page_icon="🩺", layout="centered")
st.title("🩺 AskMediX - Your AI Medical Assistant")
st.success("✅ AskMediX is ready. Ask your medical question below.")

query = st.text_input("Ask your medical question:")

if query:
    with st.spinner("Thinking..."):
        try:
            result = qa_chain.invoke({"query": query})
            st.markdown("### 💬 Answer:")
            st.write(result["result"])

            with st.expander("📄 Sources"):
                for doc in result["source_documents"]:
                    st.markdown(f"• **Page excerpt:** `{doc.page_content[:200]}...`")

            try:
                sheet = get_sheet()
                sheet.append_row([query, result["result"]])
            except Exception as e:
                st.error(f"❌ Google Sheet error: {e}")

        except Exception as e:
            st.error(f"❌ Error processing your query: {e}")

# ------------------- Appointment Form -------------------
if st.button("📅 Schedule a Doctor Visit"):
    with st.form("appointment_form"):
        st.markdown("### Fill in your details:")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number (e.g., +254...)")
        date = st.date_input("Preferred Date")
        time = st.time_input("Preferred Time")
        submitted = st.form_submit_button("Submit")

        if submitted:
            appointment_time = datetime.combine(date, time)
            cancel_token = str(uuid.uuid4())
            cancel_url = f"http://localhost:5000/cancel/{cancel_token}"

            try:
                sheet = get_sheet()
                sheet.append_row([
                    full_name, email, phone,
                    appointment_time.strftime("%Y-%m-%d %H:%M:%S"),
                    cancel_token
                ])
                st.success("✅ Appointment scheduled successfully!")
            except Exception as e:
                st.error(f"❌ Google Sheets error: {e}")

            try:
                twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                msg_body = f"""
Hi {full_name}, your AskMediX doctor visit is scheduled on {appointment_time}.
To cancel, click: {cancel_url}
"""
                twilio_client.messages.create(body=msg_body, from_=TWILIO_PHONE, to=phone)
                twilio_client.messages.create(body=msg_body, from_=TWILIO_WHATSAPP, to=f"whatsapp:{phone}")
                st.success("📲 SMS and WhatsApp reminders sent!")
            except Exception as e:
                st.error(f"❌ Twilio error: {e}")

            try:
                sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
                email_content = f"""
Hello {full_name},

Your AskMediX appointment is confirmed for:
📅 {appointment_time.strftime('%A, %d %B %Y')} at ⏰ {appointment_time.strftime('%I:%M %p')}

To cancel, click: {cancel_url}

Stay healthy! 🩺
"""
                message = Mail(
                    from_email=FROM_EMAIL,
                    to_emails=email,
                    subject="AskMediX Appointment Confirmation",
                    plain_text_content=email_content
                )
                sg.send(message)
                st.success("📧 Email reminder sent!")
            except Exception as e:
                st.error(f"❌ SendGrid error: {e}")
