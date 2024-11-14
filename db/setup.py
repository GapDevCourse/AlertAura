from pymongo import MongoClient
from datetime import datetime

class ReminderManager:
    def __init__(self, db_name="alertaura", collection_name="reminders"):
        self.client = MongoClient("mongodb://localhost:27017/")  # Adjust as needed
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def add_reminder(self, title, description, due_date):
        reminder = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "created_at": datetime.now()
        }
        result = self.collection.insert_one(reminder)
        return f"Reminder added with ID: {result.inserted_id}"

    def update_reminder(self, reminder_id, title=None, description=None, due_date=None):
        update_fields = {}
        if title:
            update_fields["title"] = title
        if description:
            update_fields["description"] = description
        if due_date:
            update_fields["due_date"] = due_date

        result = self.collection.update_one(
            {"_id": reminder_id},
            {"$set": update_fields}
        )
        return "Reminder updated" if result.modified_count > 0 else "No changes made"

    def delete_reminder(self, reminder_id):
        result = self.collection.delete_one({"_id": reminder_id})
        return "Reminder deleted" if result.deleted_count > 0 else "No reminder found"

    def get_all_reminders(self):
        reminders = self.collection.find()
        return list(reminders)  # Returns a list of all reminders

# Example usage
if __name__ == "__main__":
    manager = ReminderManager()
    # Add a reminder
    print(manager.add_reminder("Meeting", "Project meeting with team", "2024-11-15"))
    
    # Update a reminder (use the ID returned above)
    # print(manager.update_reminder(some_id, title="Updated Title"))

    # Delete a reminder
    # print(manager.delete_reminder(some_id))

    # Get all reminders
    # print(manager.get_all_reminders())
