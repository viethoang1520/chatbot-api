import datetime
import uuid
from flask import Flask, Response, request
from flask_cors import CORS
from swarm import Swarm, Agent
import database
import json
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)
CORS(app)

client = Swarm()

database.get_postgres_connection()

# sdk

# TESTED
def get_user_claims(context_variables):
  """Return claim information for a user based on the user_id in the context variables.
  Please format the response as:
  Request ID:...
  Duration: start_date - end_date (keep the "-")
  Total hours:...
  Project ID:...
  Submitted date:... 
  Status:...
  """
  user_id = context_variables["user_id"]
  conn = database.get_postgres_connection()
  cursor = conn.cursor()
  cursor.execute('SELECT request_id, start_date, end_date, total_hours, project_id, submitted_date, claim_status FROM claims WHERE user_id = %s;', (user_id,))
  result = cursor.fetchall()
  context_variables["user_claims"] = result
  cursor.close()
  conn.close()
  return result
    

def get_claim_details(request_id):
  """ Return claim details for a claim based on the request_id, format the response as:
      Claim ID:...
      Date: ...
      Working hours: ...
  """
  conn = database.get_postgres_connection()
  cursor = conn.cursor()
  cursor.execute('SELECT claim_id, date, working_hours FROM claim_details WHERE request_id = %s AND status = %s;', (request_id, 1))
  result = cursor.fetchall()
  cursor.close()
  conn.close()
  return result

claims_agent = Agent(
    name="Claim Agent",
    description="""You are a claim agent that handles all actions related to claims.
    If the user want to get their claim details, ask user clarifying questions until you know which claim id they want to get details for,
    get the request_id by fetching the context_variables["user_claims"] and then call the appropriate function.
    Once you know, call the appropriate transfer function. Either ask clarifying questions, or call one of your functions, every time.
    """,
    # If the user asks you to email them, you must ask them for email address in one message.
    functions=[get_user_claims, get_claim_details],
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""You are to triage a users request, and call a tool to transfer to the right intent.
    Once you are ready to transfer to the right intent, call the tool to transfer to the right intent.
    When you need more information to triage the request to an agent, ask a direct question without explaining why you're asking it.
    *Remember: Do not share your thought process with the user! Do not make unreasonable assumptions on behalf of user.""",
)
    # You dont need to know specifics, just the topic of the request.
    # If the user request is about a claim, transfer to the Claim Agent.

def transfer_to_claim():
    return claims_agent

def transfer_back_to_triage():
    return triage_agent

triage_agent.functions.append(transfer_to_claim)
claims_agent.functions.append(transfer_back_to_triage)

# API endpoint for get response
@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json()
    user_input = data.get("message")
    user_id = data.get("user_id")
    role_id = data.get("role_id")
    context_variables = {"user_id": user_id, "role_id": role_id}

    response = client.run(
        agent=triage_agent,
        messages=[{"role": "user", "content": user_input}],
        stream=False,
        context_variables=context_variables
    )
    
    # Get only the last assistant message
    last_message = None
    for message in response.messages:
        if message["role"] == "assistant":
            last_message = {
                "sender": message["sender"],
                "content": message["content"],
            }
    
    return Response(
        json.dumps(last_message), 
        mimetype="application/json"
    )

@app.route("/", methods=["GET"])
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)