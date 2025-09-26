# RAG + Pathway Powered Chatbot

Hackathon Wall is an intelligent chatbot platform built using **Flask**, **RAG (Retrieval-Augmented Generation)**, and **Pathway**.  
It allows users to interact with an AI assistant that retrieves relevant information from Slack channels and generates context-aware responses in real time.

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/UnnathiCS/Code_Cubicle_5.0_RAG_pathway.git
cd Code_Cubicle_5.0_RAG_pathway
```

### 2. Install Python

Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/).

### 3. Create and Activate a Virtual Environment (Recommended)

```sh
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

all the commands to be run on WSL terminal for pathway to work
<img width="1204" height="472" alt="image" src="https://github.com/user-attachments/assets/982bd999-6531-4ad0-8734-f13682d4487f" />

### 4. Install Dependencies

```sh
pip install flask python-dotenv pathway
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root:

```
SLACK_BOT_TOKEN=your-slack-bot-token-here
```

### 6. Start the Flask Server

```
python slack_pathway/src/app.py
```

---

## Slack Integration Setup

### 1. Expose Local Server to the Internet

Download and install [ngrok](https://ngrok.com/download).
<img width="1064" height="648" alt="image" src="https://github.com/user-attachments/assets/9409479d-ce7a-4389-94df-7dd0935a59d6" />

```sh
ngrok http 5000
```

Copy the HTTPS forwarding URL.
<img width="1225" height="658" alt="image" src="https://github.com/user-attachments/assets/56b228dd-dbff-477b-8eac-bb9a642da050" />

### 2. Configure Slack App

- Go to [Slack API Apps](https://api.slack.com/apps).
- Set your event request URL to `https://<ngrok-url>/slack/events`.
- Add necessary scopes (e.g., `chat:write`, `channels:history`, etc.).
- <img width="1461" height="766" alt="image" src="https://github.com/user-attachments/assets/5bdd878d-c437-4352-86a8-d5be3efa7692" />

- Install the app to your workspace.

- <img width="1682" height="771" alt="image" src="https://github.com/user-attachments/assets/f99b8d3f-9635-4257-b537-aff3be578529" />
  <img width="1467" height="636" alt="image" src="https://github.com/user-attachments/assets/ad8c0bda-8cd0-4236-9797-de012031bd26" />

### 3. Test the Endpoint

Use curl or Postman to send test events. Slack will send a `url_verification` event when you set the endpoint.

```sh
curl -X POST http://127.0.0.1:5000/slack/events \
-H "Content-Type: application/json" \
-d '{
  "event": {
    "type": "message",
    "user": "U123456",
    "text": "Hello world!",
    "ts": "1695120000.000"
  }
}'

```

### 4. Monitor Logs

Check your terminal for incoming events and messages.

---

## Running the Application

Start the Flask Backend (API + Frontend)

```sh
python slack_pathway/src/app.py
```

By default, the server runs at : http://127.0.0.1:5000/

- Opening http://127.0.0.1:5000 will show the Landing Page.
- Clicking “Try Me” will open the Chatbot UI.
- Type your queries & the bot will answer, using the real time data.

---
# Hackathon RAG System with Pathway Database 🚀

A real-time Retrieval Augmented Generation (RAG) system that monitors hackathon chat messages from Slack/Discord/Telegram and provides AI-powered insights about team problems, trending topics, and common questions. **Built with Pathway's built-in database engine - no external databases required!**

## Features

- **Real-time Message Ingestion**: Connects to Slack/Discord/Telegram APIs
- **AI-Powered Analysis**: Uses Google Gemini models for intelligent insights
- **Live Dashboard**: Real-time monitoring of hackathon activity
- **Interactive Chatbot**: Ask questions about current hackathon status
- **Pathway Built-in Database**: Native database engine with SQL-like queries
- **Stream Processing**: Real-time data handling and analytics
- **No External Dependencies**: No PostgreSQL, Redis, or MongoDB needed!

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Slack/Discord │───▶│   Flask API     │───▶│   Pathway       │
│   Webhooks      │    │   (Ingestion)   │    │   (Built-in DB) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Frontend      │    │   RAG Service   │
                       │   (Dashboard)   │    │   (Gemini AI)   │
                       └─────────────────┘    └─────────────────┘
```

## Pathway Database Benefits

- **Built-in Database Engine**: No setup of external databases
- **Real-time SQL Queries**: Query streaming data with SQL-like syntax
- **Incremental Updates**: Automatic indexing and query optimization
- **Memory Efficient**: Optimized for streaming workloads
- **Schema Management**: Automatic schema evolution
- **Analytics Ready**: Built-in aggregations and time-series support

## Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to project
cd slack_pathway

# Run setup script
python setup.py

# Edit .env file with your API keys
# Copy env_template.txt to .env and fill in your keys
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -e .

# Or manually install
pip install flask python-dotenv pathway google-generativeai requests numpy pandas
```

### 3. Configure API Keys

Edit `.env` file:

```env
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Slack Configuration
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

# Discord Configuration (optional)
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

### 4. Run the System

```bash
# Start the complete Pathway-based system
python src/main.py

# The system includes:
# - Flask web application
# - Pathway database engine
# - Real-time stream processing
# - RAG service with Gemini AI
```

### 5. Access the Interface

- **Landing Page**: http://localhost:5000
- **AI Chatbot**: http://localhost:5000/chatbot
- **Live Dashboard**: http://localhost:5000/dashboard

## Configuration

### Slack Setup

1. Create a Slack App at https://api.slack.com/apps
2. Enable Event Subscriptions
3. Set Request URL to: `https://your-domain.com/slack/events`
4. Subscribe to `message.channels` events
5. Install app to workspace

### Discord Setup

1. Create a Discord Application at https://discord.com/developers/applications
2. Create a webhook in your server
3. Set webhook URL in `.env`

## API Endpoints

### Chat Interface
- `POST /api/query` - Send query to RAG system
- `GET /api/insights` - Get predefined insights
- `GET /api/stats` - Get message statistics
- `GET /api/messages` - Get recent messages

### Pathway Database Endpoints
- `GET /api/pathway/status` - Get Pathway system status
- `POST /api/pathway/search` - Search messages using Pathway database
- `GET /api/pathway/problems` - Get problem messages
- `GET /api/pathway/questions` - Get question messages
- `GET /api/pathway/urgent` - Get urgent messages

### Webhook Endpoints
- `POST /slack/events` - Slack webhook endpoint

## Predefined Queries

The system comes with built-in queries for common hackathon monitoring:

- "What problems are teams facing right now?"
- "What are the most asked questions?"
- "What topics are trending in the chat?"
- "Summarize the current hackathon activity"

## Demo Scenarios

### Scenario 1: Real-time Problem Detection
1. Teams post problems in Slack/Discord
2. AI analyzes messages in real-time
3. Dashboard shows current issues
4. Organizers can respond quickly

### Scenario 2: Trend Analysis
1. Monitor chat for trending topics
2. Identify popular technologies/frameworks
3. Track team progress and morale
4. Generate insights for judges

### Scenario 3: FAQ Generation
1. Collect common questions
2. Generate FAQ responses
3. Help teams find answers quickly
4. Reduce organizer workload
   
## Demo

[Watch the Demo](https://drive.google.com/file/d/1Zxly9lonrItgFcECndJABLpM5WSFtQKk/view?usp=sharing)


---

## 💖 Made with Love

Made with ❤️ by She-E-Os

---






