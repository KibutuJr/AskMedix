# AskMediX

A self‑hosted, LangChain‑powered medical chatbot branded as AskMediX, using Hugging Face’s Inference API for LLM calls and Pinecone for vector indexing.

## Table of Contents

How to Run

Configuration

Scripts

Tech Stack

AWS CI/CD Deployment with GitHub Actions

License

## How to Run

## 1. Clone the Repository

git clone https://github.com/<your-org>/AskMediX.git
cd AskMediX

## 2. Set Up Python Environment

Create and activate a conda environment:

conda create -n askmedix python=3.10 -y
conda activate askmedix

## 3. Install Dependencies

pip install -r requirements.txt
pip install huggingface-hub transformers

## 4. Configure Environment Variables

Create a .env file in the project root with the following:

PINECONE_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
HUGGINGFACE_API_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

## 5. Build the Pinecone Index

Run the indexing script to embed your medical documents and push to Pinecone:

python store_index.py

## 6. Launch the Flask App

python app.py

By default, the server will start on port 5000. Open your browser and navigate to:

http://localhost:5000

Configuration
All configuration is loaded via environment variables. The main variables are:

PINECONE_API_KEY – Your Pinecone API key.

HUGGINGFACE_API_TOKEN – Your Hugging Face Hub token (with Inference API access).

Available Scripts
store_index.py – Reads your documents, generates embeddings via Hugging Face, and upserts them into your Pinecone index.

app.py – Starts the Flask web server and exposes the AskMediX chat UI.

Feel free to extend or modify these scripts to fit your own data sources or LLM settings.

Tech Stack
Python 3.10

LangChain – Orchestration for prompt management and chaining.

Flask – Lightweight web framework for hosting the AskMediX chat UI and API.

Hugging Face Inference API – For all LLM calls (e.g. text-generation, chat-completion).

Pinecone – Vector database for similarity search.

AWS CI/CD Deployment with GitHub Actions
Automate build, push, and deploy your AskMediX Docker image to AWS using GitHub Actions.

## 1. IAM User & Permissions

Create an IAM user with the following managed policies:

AmazonEC2ContainerRegistryFullAccess

AmazonEC2FullAccess

## 2. Create an ECR Repository

aws ecr create-repository --repository-name askmedix --region ap-south-1
Save the returned URI, e.g.:
970547337635.dkr.ecr.ap-south-1.amazonaws.com/askmedix

## 3. Provision an EC2 Instance (Ubuntu)

Launch an Ubuntu EC2 instance.

SSH into the instance.

## 4. Install Docker on EC2

sudo apt-get update -y
sudo apt-get upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
newgrp docker

## 5. Configure EC2 as a Self‑Hosted GitHub Runner

In your GitHub repo, go to Settings → Actions → Runners → New self‑hosted runner.

Copy the registration commands and run them on your EC2 host.

## 6. GitHub Secrets

Add the following in your repo’s Settings → Secrets:

AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY

AWS_DEFAULT_REGION (e.g. ap-south-1)

ECR_REPO (your ECR repository URI, e.g. 970547337635.dkr.ecr.ap-south-1.amazonaws.com/askmedix)

PINECONE_API_KEY

HUGGINGFACE_API_TOKEN

## 7. Sample .github/workflows/deploy.yml

name: CI/CD Pipeline

on:
push:
branches: [ main ]

jobs:
build-and-push:
runs-on: ubuntu-latest
steps: - name: Checkout code
uses: actions/checkout@v3

      - name: Log in to ECR
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build Docker image
        run: |
          docker build -t ${{ secrets.ECR_REPO }}:latest .

      - name: Push to ECR
        run: |
          docker push ${{ secrets.ECR_REPO }}:latest

deploy:
needs: build-and-push
runs-on: self-hosted
steps: - name: SSH & Deploy
uses: appleboy/ssh-action@v0.1.5
with:
host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            docker pull ${{ secrets.ECR_REPO }}:latest
            docker stop askmedix || true
            docker rm askmedix || true
            docker run -d --name askmedix -p 5000:5000 \
              -e PINECONE_API_KEY=${{ secrets.PINECONE_API_KEY }} \
 -e HUGGINGFACE_API_TOKEN=${{ secrets.HUGGINGFACE_API_TOKEN }} \
 ${{ secrets.ECR_REPO }}:latest

## License

Distributed under the MIT License. See LICENSE for more information.
