# AskMediX - Medical Chatbot

**LangChain-powered self-hosted medical chatbot**, branded as *AskMediX*, leveraging Hugging Face’s Inference API for LLM calls and Pinecone for efficient vector indexing and retrieval.

---

##  Table of Contents

- [About](#about)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Prerequisites](#prerequisites)  
- [Installation & Setup](#installation--setup)  
- [Usage](#usage)  
- [Configuration](#configuration)  
- [Suggested Workflow](#suggested-workflow)  
- [Running Scripts](#running-scripts)  
- [Deployment & CI/CD](#deployment--ci-cd)  
- [Story & Real-World Impact](#story--real-world-impact)  
- [Contributing](#contributing)  
- [Contact](#contact)  
- [License](#license)  

---

##  About

AskMediX is a locally deployable medical chatbot that processes user queries by generating embeddings via Hugging Face and retrieving relevant medical information using Pinecone's vector search. It’s ideal for secure, offline, or isolated environments where direct dependency control and privacy are essential.

---

##  Features

- **Interactive chatbot UI** powered by Flask  
- **Embedding-based retrieval** for fast and relevant medical responses  
- **Configurable via environment variables**, making setup flexible  
- **Open architecture** allowing you to swap out LLM providers or vector stores  
- **Designed for extensibility**—add more scripts, data sources, or UI improvements

---

##  Tech Stack

- **Python 3.10**  
- **LangChain** for prompt orchestration  
- **Flask** for web UI and HTTP service  
- **Hugging Face Inference API** for LLM-powered responses  
- **Pinecone** for vector embeddings and fast similarity search  
- **Docker** support via `Dockerfile` for containerized deployment

---

##  Prerequisites

Ensure you have the following installed:

- Python 3.10  
- (Optional) Conda or virtual environment tool  
- Access to Hugging Face Inference API Token  
- Pinecone account and valid API key  

---

##  Installation & Setup

1. **Clone the repository**
   ```
   git clone https://github.com/KibutuJr/AskMedix.git
   cd AskMedix
```

2. **Create and activate a Python environment**

   ```
   conda create -n askmedix python=3.10 -y
   conda activate askmedix
   ```

3. **Install required packages**

   ```
   pip install -r requirements.txt
   pip install huggingface-hub transformers
   ```

4. **Configure environment variables** by creating a `.env` file:

   ```
   PINECONE_API_KEY="your_pinecone_api_key"
   HUGGINGFACE_API_TOKEN="your_huggingface_token"
   ```

---

## Suggested Workflow

1. Create embeddings and load them into Pinecone:

   ```
   python store_index.py
   ```
2. Start the web server:

   ```
   python app.py
   ```
3. Open your browser at `http://localhost:5000`, and start interacting with AskMediX.

---

## Available Scripts

| Script             | Purpose                                                                  |
| ------------------ | ------------------------------------------------------------------------ |
| `store_index.py`   | Generates document embeddings and uploads them to Pinecone               |
| `app.py`           | Runs the Flask app serving the chatbot UI                                |
| `chatbot_ui.py`    | Handles front-end UI elements (if separated from `app.py`)               |
| `sheets_utils.py`  | Utility functions for processing data from Google Sheets (if applicable) |
| `template.py`      | Template utilities or prompt scaffolding (project-specific)              |
| `cancel_server.py` | Gracefully stops or resets the running server (if present)               |

---

## Deployment & CI/CD

* **Containerization**: Use the existing `Dockerfile` to build and run the app in a container:

  ```
  docker build -t askmedix .
  docker run -e PINECONE_API_KEY -e HUGGINGFACE_API_TOKEN -p 5000:5000 askmedix
  ```
* **Continuous Deployment**: You can integrate GitHub Actions for CI/CD workflows to automate testing and deployment.

---

## Story & Real-World Impact

Access to reliable medical information remains a challenge for many communities worldwide. Patients often rely on generic search engines or unverified sources, leading to misinformation, delayed diagnoses, or anxiety. *AskMediX* was built to bridge this gap by providing an intelligent, localized, and **self-hosted medical assistant** capable of delivering fast, relevant, and trustworthy responses.

By combining **natural language processing**, **vector search**, and **flexible deployment**, AskMediX can be adapted for hospitals, telemedicine providers, or even rural clinics with limited internet access. The project demonstrates how AI can be responsibly applied in healthcare technology—offering guidance and educational support while maintaining privacy and customizability.

---

## Contributing

We welcome contributions to make AskMediX more impactful. Whether it's improving UI/UX, adding more medical datasets, enhancing security, or refining deployment scripts, your input is valuable.

---

## Contact

**Fred Kibutu**
*Data Analyst | Data Engineer | Software Developer*
📧 [Email][Kibutujr@gmail.com]
[LinkedIn][https://www.linkedin.com/in/fred-kibutu/] 
[Portfolio][https://kibutujr.github.io/Portfolio-KibutuJr/]

---

## License

This project is licensed under the terms specified in the included `LICENSE` file.

---

```
Do you want me to also design a **professional badges section** (Python, Flask, LangChain, Hugging Face, Pinecone, Docker) at the top to make the README look more polished?
```
