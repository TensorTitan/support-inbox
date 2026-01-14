AI Powered Support Inbox

An AI-powered support inbox system built using a microservice and event-driven architecture.
The project simulates a real-world customer support workflow where messages are processed in real time and enriched asynchronously with AI-generated insights.

This project is designed for educational purposes and demonstrates practical usage of:

Distributed systems

Message queues

Event-driven communication

WebSockets

Local Large Language Models (LLMs)

All AI processing is done locally using Ollama, with no external APIs or cloud dependencies.

Features

Real-time support inbox UI

Asynchronous AI message analysis

Event-driven microservices architecture

Local LLM inference via Ollama

WebSocket updates with polling fallback

Fault-tolerant AI processing

AI Capabilities

For each message, the AI generates:

Detected intent

Short summary

Suggested reply for the operator

AI processing never blocks the user experience.

System Architecture

The system consists of independent services communicating via RabbitMQ.

Frontend
   |
WebSocket / HTTP
   |
Gateway Service
   |
RabbitMQ (Events)
   |
---------------------------
| Messaging Service       |
| AI Worker               |
---------------------------
   |
PostgreSQL

Components
Gateway Service

Handles authentication (JWT)

Manages WebSocket connections

Forwards messages to Messaging Service

Broadcasts AI completion events to clients

Messaging Service

Stores conversations and messages in PostgreSQL

Publishes message.created events

Stores AI insights

Provides conversation read models for UI

AI Worker

Consumes message.created events

Sends message content to local LLM via Ollama

Parses and validates AI output defensively

Stores AI insights

Publishes ai.completed events

RabbitMQ

Acts as the event bus

Uses topic exchanges

Enables asynchronous and decoupled processing

PostgreSQL

Stores:

Conversations

Messages

AI insights

Frontend

Simple operator inbox UI

Real-time updates via WebSockets

Polling fallback for reliability

Ollama

Runs local LLM models

No internet or cloud dependency

Event Flow

Operator sends a message from the UI

Gateway forwards the message to Messaging Service

Messaging Service stores the message

Messaging Service publishes message.created event

AI Worker consumes the event

AI Worker runs AI analysis using Ollama

AI insights are stored in PostgreSQL

AI Worker publishes ai.completed event

Gateway broadcasts updates via WebSocket

UI reloads conversation and displays AI output

AI Processing Details

The AI Worker uses local Ollama models such as:

tinyllama

phi3:mini

llama3

Defensive Parsing

Because LLM output is not always strict JSON:

Markdown code blocks are stripped

Extra text is removed

Invalid output is safely rejected

This ensures AI failures never break the system.

Frontend Behavior

Messages appear instantly after sending

AI status indicators:

processing

available

unavailable

UI polls backend until AI insight is available

WebSocket updates provide real-time feedback

Polling fallback ensures reliability if events are delayed

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
Gateway Service
POST /login
POST /messages
WebSocket /ws

Messaging Service
POST /messages
POST /ai-insights
GET /conversations/{conversation_id}

Environment Configuration

All services are configured using environment variables.

Required Variables
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

Start the System
docker compose up --build

Access Points

Frontend UI: http://localhost

Gateway API: http://localhost:8000

Messaging API: http://localhost:8001

RabbitMQ Management UI: http://localhost:15672

Error Handling & Reliability

Automatic RabbitMQ reconnection

AI failures do not block message delivery

Invalid AI output is safely ignored

WebSocket + polling hybrid approach

Event-driven design minimizes coupling

Limitations

Single-node deployment

AI output quality depends on model choice

Polling introduces a small delay

No advanced role or permission management

Purpose

This project is intended as a learning reference for:

Event-driven microservices

Asynchronous AI processing

Real-time systems

Local LLM integration

Fault-tolerant system design
