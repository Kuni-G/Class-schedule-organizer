schedule = []  # List to store class schedules
def display_menu():
    print("\n--- Class Schedule Organizer ---")
    print("1. Add a Class")
    print("2. View Schedule")
    print("3. Exit")
def add_class():
    subject = input("Enter subject name: ")
    day = input("Enter day (e.g., Monday): ")
    start_time = input("Enter start time (e.g., 09:00 AM): ")
    end_time = input("Enter end time (e.g., 10:30 AM): ")
    schedule.append({
        "subject": subject,
        "day": day,
        "start": start_time,
        "end": end_time})
    print("Class added successfully!")

def view_schedule():
    if not schedule:
        print("No classes in your schedule yet.")
    else:
        print("\n--- Your Class Schedule ---")
        for idx, entry in enumerate(schedule, start=1):
            print(f"{idx}. {entry['subject']} - {entry['day']} {entry['start']} to {entry['end']}")

# Main program loop
while True:
    display_menu()
    choice = input("Choose an option (1-3): ")

    if choice == "1":
        add_class()
    elif choice == "2":
        view_schedule()
    elif choice == "3":
        print("Goodbye!")
        break
    else:
        print("Invalid choice. Please select 1, 2, or 3.")
