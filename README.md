# AI Chatbot

An AI-powered chatbot web application built with FastAPI, PostgreSQL, OpenRouter, JWT authentication, chat sessions, PDF document upload, and Retrieval-Augmented Generation (RAG).

## Features

- User registration and login
- JWT-based authentication
- Secure password hashing
- AI chatbot powered by OpenRouter
- Multiple chat sessions
- Chat history
- Create, switch, and delete chat sessions
- PDF document upload
- PDF removal from chat sessions
- Text extraction and chunking from PDFs
- Embeddings using Hugging Face
- FAISS vector store for similarity search
- RAG-based question answering from uploaded PDFs
- Markdown and code formatting
- AI thinking indicator
- Responsive HTML/CSS/JavaScript interface
- Error handling and edge-case validation
- Logout functionality

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT
- Passlib / bcrypt

### AI & RAG
- OpenRouter API
- LangChain
- Hugging Face Embeddings
- Sentence Transformers
- FAISS
- PyPDF

### Frontend
- HTML
- CSS
- JavaScript

### Tools
- Git
- GitHub

## Project Structure

```text
Ai-chatbot/
│
├── app/
│   ├── api/
│   ├── auth/
│   ├── config/
│   ├── database/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── security/
│   └── services/
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── create_tables.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md