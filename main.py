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

def create_claim(user_id, project_id, days_worked, hours_worked_per_day):
  """Create a claim for a user based on the user_id, project_id, days_worked, and hours_worked_per_day
  Takes as input arguments in the format '{"user_id":"1","project_id":"2","days_worked":"3","hours_worked_per_day":"4"}'
  """
  total_working_hours = float(days_worked) * float(hours_worked_per_day)
  claim_id = str(uuid.uuid4())
  conn = database.get_postgres_connection()
  cursor = conn.cursor()
  cursor.execute('INSERT INTO claims (claim_id, user_id, project_id, submitted_date, total_working_hours, claim_status) VALUES (%s, %s, %s, %s, %s, %s)',
                 (claim_id, user_id, project_id, datetime.datetime.now(), total_working_hours, "PENDING"))
  conn.commit()
  cursor.close()
  conn.close()
  return "Claim created successfully"
# sdk
def get_user_claim(user_id):
  """Return claim information for a user based on the user_id 
  Takes as input arguments in the format '{"user_id":"1"}'
  """
  conn = database.get_postgres_connection()
  cursor = conn.cursor()
  cursor.execute('SELECT * FROM claims WHERE user_id = %s;', (user_id,))
  result = cursor.fetchall()
  cursor.close()
  conn.close()
  return result
    
def get_claim_details(claim_id):
  """return claim details for a claim based on the claim_id 
  Takes as input arguments in the format '{"claim_id":"1"}'
  """
  conn = database.get_postgres_connection()
  cursor = conn.cursor()
  cursor.execute('SELECT * FROM claims WHERE claim_id = %s;', (claim_id,))
  result = cursor.fetchone()
  cursor.close()
  conn.close()
  return result

claims_agent = Agent(
    name="Claim Agent",
    description="""You are a claim agent that handles all actions related to claims.
    If the user want to get a claim details, ask user clarifying questions until you know whether or not it is a get claim by user_id or get claim by claim_id request. 
    Once you know, call the appropriate transfer function. Either ask clarifying questions, or call one of your functions, every time.
    You must ask for the projectID, days worked, hours worked per day, and userID (get from the browser) to create a claim in one message.
    If the user asks you to email them, you must ask them for email address in one message.""",
    functions=[create_claim, get_user_claim, get_claim_details],
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""You are to triage a users request, and call a tool to transfer to the right intent.
    Once you are ready to transfer to the right intent, call the tool to transfer to the right intent.
    You dont need to know specifics, just the topic of the request.
    If the user request is about a claim, transfer to the Claim Agent.
    When you need more information to triage the request to an agent, ask a direct question without explaining why you're asking it.
    *Remember: Do not share your thought process with the user! Do not make unreasonable assumptions on behalf of user.""",
)

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

    response = client.run(
        agent=triage_agent,
        messages=[{"role": "user", "content": user_input}],
        stream=False
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