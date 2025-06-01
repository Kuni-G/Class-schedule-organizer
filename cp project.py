import json
import os
class Database:
    def __init__(self, filename="schedule.json"): # Corrected: __init__
        self.filename = filename
        self.schedule_data = self._load_schedule()
    def _load_schedule(self):
        """Loads the schedule data from the JSON file."""
        if os.path.isabs(self.filename):
            file_path = self.filename
        else:
            # Construct the absolute path to the file within the project directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, self.filename)
        if not os.path.exists(file_path):
            return []  # Return an empty list if the file doesn't exist yet
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {self.filename}. Starting with an empty schedule.")
            return []
        except Exception as e:
            print(f"Error loading schedule: {e}")
            return []

    def _save_schedule(self):
        """Saves the current schedule data to the JSON file."""
        if os.path.isabs(self.filename):
            file_path = self.filename
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, self.filename)
        try:
            with open(file_path, 'w') as f:
                json.dump(self.schedule_data, f, indent=4) # indent for pretty-printing
        except Exception as e:
            print(f"Error saving schedule: {e}")
    def get_all_entries(self):
        """Returns all schedule entries."""
        return self.schedule_data
    def add_entry(self, entry):
        """
        Adds a new class entry to the schedule.
        'entry' should be a dictionary like:
        {"name": "Math", "day": "Monday", "time": "10:00", "type": "class"}
        Consider adding a unique ID to each entry if you plan to update/delete specific entries.
        """
        self.schedule_data.append(entry)
        self._save_schedule()
        print(f"Added entry: {entry}")
    def update_entry(self, old_entry, new_entry):
        """
        Updates an existing entry. This assumes you can uniquely identify old_entry.
        A better approach for update/delete would be to use a unique ID for each entry.
        For simplicity, this example will try to match all fields.
        """
        try:
            index = self.schedule_data.index(old_entry)
            self.schedule_data[index] = new_entry
            self._save_schedule()
            print(f"Updated entry from {old_entry} to {new_entry}")
            return True
        except ValueError:
            print(f"Entry {old_entry} not found for update.")
            return False
    def delete_entry(self, entry_to_delete):
        """
        Deletes a specific entry from the schedule.
        Similar to update, this might need a unique ID for robust deletion.
        """
        initial_length = len(self.schedule_data)
        self.schedule_data = [entry for entry in self.schedule_data if entry != entry_to_delete]
        if len(self.schedule_data) < initial_length:
            self._save_schedule()
            print(f"Deleted entry: {entry_to_delete}")
            return True
        else:
            print(f"Entry {entry_to_delete} not found for deletion.")
            return False
    # Example of how you might fetch entries based on a criteria
    def get_entries_by_day(self, day):
        """Returns all entries for a specific day."""
        return [entry for entry in self.schedule_data if entry.get("day") == day]
# For Example
if __name__ == "__main__": 
    db = Database()
    # Clear existing data for fresh testing
    db.schedule_data = []
    db._save_schedule()
    print("Initial schedule:", db.get_all_entries())
# Add some entries
    db.add_entry({"name": "Math", "day": "Monday", "time": "10:00", "type": "class"})
    db.add_entry({"name": "History", "day": "Wednesday", "time": "14:00", "type": "class"})
    db.add_entry({"name": "Project Meeting", "day": "Friday", "time": "09:00", "type": "meeting"})
    db.add_entry({"name": "Physics", "day": "Monday", "time": "11:00", "type": "class"})
    print("\nSchedule after adding entries:", db.get_all_entries())
    # Get entries for a specific day
    print("\nEntries for Monday:", db.get_entries_by_day("Monday"))

    # Update an entry
    old_math = {"name": "Math", "day": "Monday", "time": "10:00", "type": "class"}
    new_math = {"name": "Advanced Math", "day": "Monday", "time": "10:00", "type": "class"}
    db.update_entry(old_math, new_math)
    print("\nSchedule after updating Math:", db.get_all_entries())
    # Try to update an entry that doesn't exist
    db.update_entry({"name": "Nonexistent", "day": "Sunday", "time": "12:00", "type": "class"}, {"name": "New Nonexistent", "day": "Sunday", "time": "12:00", "type": "class"})
    # Delete an entry
    db.delete_entry({"name": "Project Meeting", "day": "Friday", "time": "09:00", "type": "meeting"})
    print("\nSchedule after deleting Project Meeting:", db.get_all_entries())
    # Demonstrate loading from file on a new instance
    print("\nLoading with a new DB instance:")
    db_reloaded = Database()
    print("Reloaded schedule:", db_reloaded.get_all_entries())
    # Add an assignment (example of different type of entry)
    db_reloaded.add_entry({"name": "English Essay", "due_date": "2025-06-15", "type": "assignment"})
    print("\nSchedule after adding assignment:", db_reloaded.get_all_entries())

