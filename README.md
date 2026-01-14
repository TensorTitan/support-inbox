# support-inbox
AI Powered Support Inbox

This project is an AI powered support inbox system built using a microservice and event-driven architecture.
The goal of the project is to simulate a real customer support workflow where messages are processed in real time and enriched asynchronously with AI generated insights.

The system is designed for educational purposes and demonstrates usage of distributed systems, message queues, WebSockets and local large language models.

Project Description

The application allows an operator to send and receive messages in a support inbox interface.
Each message is stored immediately, while AI analysis is done in background without blocking the user.

AI generates:

detected intent of the message

short summary

suggested reply for the operator

All AI processing is done locally using Ollama, without external APIs.

System Architecture

The project is built as a set of independent services communicating through RabbitMQ.

Main Components

Gateway Service

Handles authentication using JWT

Manages WebSocket connections

Sends messages to messaging service

Broadcasts AI completion events to frontend

Messaging Service

Stores conversations and messages in PostgreSQL

Publishes message creation events

Stores AI insights

Provides conversation read model for UI

AI Worker

Listens for message creation events

Sends message content to local LLM

Parses and validates AI response

Stores AI insights

Publishes AI completion events

RabbitMQ

Event bus using topic exchanges

Decouples services

Enables asynchronous processing

PostgreSQL

Stores messages, conversations and AI insights

Frontend

Simple operator inbox UI

Uses WebSockets for real time updates

Polling fallback for reliability

Ollama

Runs local LLM models

No internet or cloud dependency

Event Flow

Operator sends message from UI

Gateway forwards message to Messaging service

Messaging service stores message

Messaging service publishes message.created event

AI Worker consumes event and runs AI analysis

AI insights are stored in database

AI Worker publishes ai.completed event

Gateway broadcasts update to connected clients

UI reloads conversation and displays AI output

AI Processing

The AI Worker uses Ollama with local models such as:

tinyllama

phi3:mini

llama3

Because LLM output is not always strict JSON, defensive parsing is implemented:

Markdown code blocks are removed

Extra text is stripped

Invalid output is rejected safely

This prevents AI errors from breaking the system.

Frontend Behavior

The frontend shows AI status clearly:

processing

available

unavailable

When a message is sent:

message appears instantly

AI status switches to processing

UI polls backend until AI insight is available

This approach ensures reliability even if WebSocket events are delayed.

Technology Stack

Backend

Python

FastAPI

SQLAlchemy

Messaging

RabbitMQ

Database

PostgreSQL

AI

Ollama

Local LLM models

Frontend

HTML

CSS

Vanilla JavaScript

Infrastructure

Docker

Docker Compose

API Endpoints
Gateway

POST /login

POST /messages

WebSocket /ws

Messaging

POST /messages

POST /ai-insights

GET /conversations/{conversation_id}

Environment Configuration

All services use environment variables.

Important variables:

JWT_SECRET

RABBITMQ_HOST

MESSAGING_BASE_URL

OLLAMA_URL

OLLAMA_MODEL

Running the Project
Requirements

Docker

Docker Compose

Ollama installed locally

Start
docker compose up --build

Access

Frontend: http://localhost

Gateway API: http://localhost:8000

Messaging API: http://localhost:8001

RabbitMQ UI: http://localhost:15672

Error Handling

Automatic reconnect for RabbitMQ

AI failures do not block message delivery

Invalid AI output is safely ignored

UI falls back to polling if needed

Limitations

Single node deployment

AI output depends on model quality

Polling adds small delay

No advanced role management
