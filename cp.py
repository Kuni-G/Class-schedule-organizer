from datetime import datetime, timedelta

def validate_class_input(day, time_str, class_name):
    """
    Validates class input fields.
    Returns True if all required fields are present and time_str is in a valid format.
    """
    if not all([day, time_str, class_name]):
        return False, "Day, Time, and Class Name are required!"
    
    try:
        # Attempt to parse time to ensure it's in a valid HH:MM format
        datetime.strptime(time_str, "%H:%M").time()
        return True, ""
    except ValueError:
        return False, "Time must be in HH:MM format (e.g., 09:00 or 14:30)."

def validate_assignment_input(class_name, assignment_name, due_date_str):
    """
    Validates assignment input fields.
    Returns True if all required fields are present and due_date_str is in a valid format.
    """
    if not all([class_name, assignment_name, due_date_str]):
        return False, "Class, Assignment, and Due Date are required!"
    
    try:
        # Attempt to parse date to ensure it's in a valid YYYY-MM-DD format
        datetime.strptime(due_date_str, "%Y-%m-%d").date()
        return True, ""
    except ValueError:
        return False, "Due Date must be in YYYY-MM-DD format (e.g., 2025-12-31)."


def validate_exam_input(class_name, exam_name, date_str):
    """
    Validates exam input fields.
    Returns True if all required fields are present and date_str is in a valid format.
    """
    if not all([class_name, exam_name, date_str]):
        return False, "Class, Exam, and Date are required!"
    
    try:
        # Attempt to parse date to ensure it's in a valid YYYY-MM-DD format
        datetime.strptime(date_str, "%Y-%m-%d").date()
        return True, ""
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format (e.g., 2025-12-31)."


def validate_reminder_input(reminder_text, date_str):
    """
    Validates reminder input fields.
    Returns True if all required fields are present and date_str is in a valid format.
    """
    if not all([reminder_text, date_str]):
        return False, "Reminder text and date are required!"
    
    try:
        # Attempt to parse date to ensure it's in a valid YYYY-MM-DD format
        datetime.strptime(date_str, "%Y-%m-%d").date()
        return True, ""
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format (e.g., 2025-12-31)."

def check_for_time_conflict(existing_schedule, new_day, new_time_str):
    """
    Checks if adding a new class creates a time conflict with existing classes.
    Assumes classes are typically 1 hour long for simple conflict detection.
    
    Inputs:
    - existing_schedule (dict): The current schedule data.
    - new_day (str): The day for the new class (e.g., "Monday").
    - new_time_str (str): The start time for the new class in "HH:MM" format.
    
    Outputs:
    - (bool): True if a conflict exists, False otherwise.
    - (str): A message describing the conflict, or an empty string if no conflict.
    """
    if new_day not in existing_schedule:
        return False, "" # No classes on this day yet, so no conflict

    try:
        new_start_time = datetime.strptime(new_time_str, "%H:%M").time()
        # For simple conflict, assume each class takes 1 hour.
        # This can be made more sophisticated by adding class duration.
        new_end_time = (datetime.combine(datetime.min, new_start_time) + timedelta(hours=1)).time()
    except ValueError:
        # If time format is invalid, let the input validation handle it first.
        # This function assumes valid time_str after initial validation.
        return False, ""

    for class_info in existing_schedule[new_day]:
        existing_time_str = class_info.get('time')
        if not existing_time_str:
            continue # Skip if no time info

        try:
            existing_start_time = datetime.strptime(existing_time_str, "%H:%M").time()
            existing_end_time = (datetime.combine(datetime.min, existing_start_time) + timedelta(hours=1)).time()

            # Check for overlap:
            # (new_start < existing_end) AND (new_end > existing_start)
            if (new_start_time < existing_end_time and new_end_time > existing_start_time):
                return True, f"Conflict: {class_info['class_name']} is scheduled from {format_time_display(existing_time_str)} on {new_day}."
        except ValueError:
            continue # Skip if existing time format is invalid

    return False, "" # No conflict found

def format_time_display(time_str):
    """
    Formats a time string from "HH:MM" to "HH:MM AM/PM".
    """
    try:
        dt_obj = datetime.strptime(time_str, "%H:%M")
        return dt_obj.strftime("%I:%M %p")
    except ValueError:
        return time_str # Return as is if format is invalid

def format_date_display(date_str):
    """
    Formats a date string from "YYYY-MM-DD" to "Month Day, Year".
    """
    try:
        dt_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        return dt_obj.strftime("%B %d, %Y")
    except ValueError:
        return date_str # Return as is if format is invalid

def get_upcoming_reminders(reminders):
    """
    Filters reminders to show only upcoming ones (today or in the future)
    and sorts them by date.
    """
    today = datetime.now().date()
    upcoming = []
    for reminder in reminders:
        try:
            reminder_date = datetime.strptime(reminder['date'], "%Y-%m-%d").date()
            if reminder_date >= today:
                upcoming.append(reminder)
        except ValueError:
            continue # Skip reminders with invalid date format
    return sorted(upcoming, key=lambda x: x['date'])
