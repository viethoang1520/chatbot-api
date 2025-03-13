# Claims Processing Chatbot

A multi-agent chatbot system built using OpenAI's Swarm framework to handle claims processing requests through an intelligent conversation interface.

## Overview

This project implements a conversational AI system that helps users manage claims. It features a multi-agent architecture with specialized agents handling different aspects of the claims process.

### Key Features

- **Multi-agent Architecture**: Uses a triage system to route user requests to specialized agents
- **Claims Management**: Create claims, view claim details, and fetch user claim history
- **Database Integration**: PostgreSQL database for persistent storage of claims data
- **Docker Support**: Containerized deployment for easy setup and scaling

## System Architecture

The chatbot system consists of two primary agents:

1. **Triage Agent**: Handles initial user interactions and routes requests to appropriate specialized agents
2. **Claims Agent**: Specialized in managing claim-related requests including:
   - Creating new claims
   - Retrieving claim details by claim ID
   - Fetching all claims for a specific user

## Technical Stack

- **Python 3.9+**: Core programming language
- **OpenAI Swarm**: Framework for multi-agent orchestration
- **PostgreSQL**: Database for storing user and claims data
- **Docker**: Containerization for deployment
- **Flask**: Web server framework

## Database Schema

The system uses the following database tables:

- `users`: Stores user information
- `roles`: Defines user roles and permissions
- `projects`: Tracks projects that claims can be associated with
- `claims`: Stores claim records including submission date, working hours, and status

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional)

### Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Configure database connection:
   Update the database connection parameters in `database.py` if necessary.

### Running Locally

1. Start the chatbot:
   ```
   python main.py
   ```

### Running with Docker

1. Build the Docker image:

   ```
   docker build -t claims-chatbot .
   ```

2. Run the container:
   ```
   docker run -p 5000:5000 claims-chatbot
   ```

## Usage

Once running, the chatbot will prompt for user input. Example interactions:

- Creating a claim: "I need to create a claim for project X"
- Viewing claim details: "Show me details for claim ABC123"
- Viewing user claims: "What claims do I have?"

## Security Note

This project contains API keys in the source code that should be moved to environment variables or a secure secret management system before production use.

## License

[Include license information here]
