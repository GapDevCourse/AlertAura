import os
import gradio as gr
from groq import Groq
from plyer import notification
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Groq Client
client = Groq(
    api_key="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",
)

# MongoDB Manager
class ReminderManager:
    def init(self, db_name="alertaura", collection_name="reminders"):
        try:
            # Connect to MongoDB and select the database and collection
            self.client = MongoClient("mongodb://localhost:27017/")  # Adjust as needed
            self.db = self.client[db_name]  # Use the db_name parameter here
            self.collection = self.db[collection_name]  # Use the collection_name parameter here
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    def add_reminder(self, task, due_date, due_time):
        reminder = {
            "task": task,
            "due_date": due_date,
            "due_time": due_time,
            "created_at": datetime.now(),
        }
        result = self.collection.insert_one(reminder)
        return f"Reminder added with ID: {result.inserted_id}"

    def delete_reminder(self, task, due_date, due_time):
        result = self.collection.delete_one({"task": task, "due_date": due_date, "due_time": due_time})
        return "Reminder deleted" if result.deleted_count > 0 else "No reminder found"

    def get_all_reminders(self):
        reminders = self.collection.find()
        return list(reminders)  # Returns a list of all reminders
# MongoDB Meeting Manager (unchanged)
class Meeting:
    def _init_(self, db_name="alertaura", collection_name="meetings"):
        try:
            self.client = MongoClient("mongodb://localhost:27017/")
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            print("Connected to MongoDB for meetings.")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    def add_meeting(self, title, description, date, time, participants):
        meeting = {
            "title": title,
            "description": description,
            "date": date,
            "time": time,
            "participants": participants,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        try:
            result = self.collection.insert_one(meeting)
            return f"Meeting added with ID: {result.inserted_id}"
        except Exception as e:
            return f"Error adding meeting: {e}"

    def update_meeting(self, meeting_id, updated_data):
        try:
            query = {"_id": ObjectId(meeting_id)}
            updated_data["updated_at"] = datetime.now()
            update = {"$set": updated_data}
            result = self.collection.update_one(query, update)
            return "Meeting updated successfully" if result.matched_count else "Meeting not found"
        except Exception as e:
            return f"Error updating meeting: {e}"

    def get_all_meetings(self):
        try:
            meetings = list(self.collection.find())
            return meetings
        except Exception as e:
            return f"Error retrieving meetings: {e}"

    def delete_meeting(self, meeting_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(meeting_id)})
            return "Meeting deleted successfully" if result.deleted_count else "Meeting not found"
        except Exception as e:
            return f"Error deleting meeting: {e}"

# Link MongoDB Manager
manager = ReminderManager()
# Link MongoDB Manager for Meetings
meeting_manager = Meeting()


# AI Prompt Base
prompt_base = """The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and friendly.
It classifies user input into predefined intents related to reminders or meetings and provides a JSON response.

#REMINDERS
1. set a reminder: This intent is used to set a reminder.
JSON format: 
{{
    "intent": "1",
    "task": "",
    "date": "",
    "time": ""
}}

2. list of reminders: This intent is used to retrieve a list of all reminders.
JSON format: 
{{
    "intent": "2",
    "task": "",
    "date": "",
    "time": ""
}}

3. delete reminder: This intent is used to delete a previously scheduled reminder.
JSON format: 
{{
    "intent": "3",
    "task": "",
    "date": "",
    "time": ""
}}
#MEETINGS
4. schedule meeting: This intent is used to schedule a meeting, allowing you to set a specific time and date, and send reminders or notifications to participants.
JSON format: 
{{
    "intent": "4",
    "task": "",
    "date": "",
    "time": ""
}}

5. list meeting: This intent is used to provide a list of meetings by date and time, allowing you to view scheduled meetings in chronological order.
JSON format: 
{{
    "intent": "5",
    "task": "",
    "date": "",
    "time": ""
}}

6. delete meeting: This intent is used to delete a meeting, removing it from the schedule and notifying any participants of the cancellation.
JSON format: 
{{
    "intent": "6",
    "task": "",
    "date": "",
    "time": ""
}}

7. reschedule meeting: This intent is used to reschedule a meeting, allowing you to change its date, time, or participants while notifying everyone involved of the updated details.
JSON format: 
{{
    "intent": "7",
    "task": "",
    "date": "",
    "time": ""
}}

Human: {user_input}
Make sure you give only the JSON response and nothing else.
"""

def get_groq_response(prompt):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

# Gradio Chatbot Function
def chatgpt_clone(input, history):
    history = history or []
    complete_prompt = prompt_base.format(user_input=input)
    response = get_groq_response(complete_prompt)
    
    try:
        # Parse JSON Response
        intent_data = eval(response)  # You may use json.loads for safer parsing
        intent = intent_data["intent"]
        task = intent_data["task"]
        date = intent_data["date"]
        time = intent_data["time"]
        participants = intent_data.get("participants", "")


        # Map intents to MongoDB functions
        if intent == "1":  # Set Reminder
            result = manager.add_reminder(task, date, time)
        elif intent == "2":  # List Reminders
            reminders = manager.get_all_reminders()
            result = "\n".join([f"- {r['task']} on {r['due_date']} at {r['due_time']}" for r in reminders])
        elif intent == "3":  # Delete Reminder
            result = manager.delete_reminder(task, date, time)
        elif intent == "4":  # Schedule Meeting
            result = meeting_manager.add_meeting(task, task, date, time, participants)
        elif intent == "5":  # List Meetings
            meetings = meeting_manager.get_all_meetings()
            result = "\n".join(
                [f"- {m['title']} on {m['date']} at {m['time']} with {', '.join(m['participants'])}" for m in meetings]
            )
        elif intent == "6":  # Delete Meeting
            result = meeting_manager.delete_meeting(task)
        elif intent == "7":  # Reschedule Meeting
            updated_data = {"date": date, "time": time, "participants": participants.split(", ")}
            result = meeting_manager.update_meeting(task, updated_data)
    
        else:
            result = "Invalid intent received."

    except Exception as e:
        result = f"Error processing request: {str(e)}"

    history.append((input, result))
    return history, history

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# ALERT AURA\n### A Smart Assistant for Reminders and Meetings")
    gr.Markdown("Provide an input to set reminders or schedule meetings. The AI will classify the intent and return a structured JSON response.")

    chatbot = gr.Chatbot(label="Assistant")
    message = gr.Textbox(placeholder="e.g., Set a reminder to do homework by tomorrow evening at 6 PM")
    state = gr.State()
    submit = gr.Button("SEND")

    submit.click(chatgpt_clone, inputs=[message, state], outputs=[chatbot, state])

demo.launch(debug=True)
