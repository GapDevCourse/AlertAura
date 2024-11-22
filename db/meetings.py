from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

class Meeting:
    def __init__(self, db_name="alertaura", collection_name="meetings"):
        try:
            self.client = MongoClient("mongodb://localhost:27017/")
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            print("Connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    # Add a new meeting
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
            print(f"Meeting added with ID: {result.inserted_id}")
        except Exception as e:
            print(f"Error adding meeting: {e}")

    # Update an existing meeting
    def update_meeting(self, meeting_id, updated_data):
        try:
            query = {"_id": ObjectId(meeting_id)}
            updated_data["updated_at"] = datetime.now()
            update = {"$set": updated_data}
            result = self.collection.update_one(query, update)
            if result.matched_count:
                print("Meeting updated successfully")
            else:
                print("Meeting not found")
        except Exception as e:
            print(f"Error updating meeting: {e}")

    # Get all meetings
    def get_all_meetings(self):
        try:
            meetings = list(self.collection.find())
            return meetings
        except Exception as e:
            print(f"Error retrieving meetings: {e}")
            return []

    # Schedule a new meeting (Alias for add_meeting)
    def schedule_meeting(self, title, description, date, time, participants):
        self.add_meeting(title, description, date, time, participants)

    # List a specific meeting by ID
    def list_meeting(self, meeting_id):
        try:
            meeting = self.collection.find_one({"_id": ObjectId(meeting_id)})
            if meeting:
                return meeting
            else:
                print("Meeting not found")
        except Exception as e:
            print(f"Error retrieving meeting: {e}")

    # Delete a meeting by ID
    def delete_meeting(self, meeting_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(meeting_id)})
            if result.deleted_count:
                print("Meeting deleted successfully")
            else:
                print("Meeting not found")
        except Exception as e:
            print(f"Error deleting meeting: {e}")

    # Reschedule an existing meeting
    def reschedule_meeting(self, meeting_id, new_date, new_time):
        updated_data = {"date": new_date, "time": new_time}
        self.update_meeting(meeting_id, updated_data)


# Example usage
if __name__ == "__main__":
    manager = Meeting()

    # Adding a meeting
    manager.add_meeting(
        title="Project Discussion",
        description="Discussion about the new project",
        date="2024-11-20",
        time="15:00",
        participants=["manogna@example.com", "tejaswi@example.com"]
    )

    # Getting all meetings
    meetings = manager.get_all_meetings()
    print(meetings)

    # Updating a meeting
    if meetings:
        meeting_id = str(meetings[0]['_id'])
        manager.update_meeting(meeting_id, {"title": "Updated Project Discussion"})

    # Deleting a meeting
    if meetings:
        manager.delete_meeting(meeting_id)
