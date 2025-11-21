
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import threading
import time

# ────────────── Main Application Class ────────────── #
class ClassReminder:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Schedule Organizer")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f8ff")

        self.schedule_file = "class_schedule.json"
        self.schedule = self.load_schedule()

        self.running = True
        self.reminder_thread = None

        self.create_widgets()
        self.start_reminder_monitor()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ────────────── GUI SETUP ────────────── #
    def create_widgets(self):
        # Header
        header = tk.Label(self.root, text="CLASS SCHEDULE ORGANIZER", font=("Arial", 24, "bold"), bg="#4b86b4", fg="white")
        header.pack(fill=tk.X, pady=10)

        # Toolbar Buttons
        toolbar = tk.Frame(self.root, bg="#f0f8ff")
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        button_style = {"font": ("Arial", 10), "bg": "#63a8d4", "fg": "white", "width": 14}

        tk.Button(toolbar, text="Add Class", command=self.add_class, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Edit Entry", command=self.edit_class, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Delete Entry", command=self.delete_class, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Set Reminder", command=self.set_reminder, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Add Assignment", command=self.add_assignment, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Add Exam", command=self.add_exam, **button_style).pack(side=tk.LEFT, padx=5)

        # Schedule Table
        schedule_frame = tk.LabelFrame(self.root, text="Schedule", bg="#f0f8ff", font=("Arial", 12))
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("Day", "Time", "Class", "Location", "Type", "Reminder")
        self.tree = ttk.Treeview(schedule_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Status Bar
        self.status = tk.StringVar()
        status_bar = tk.Label(self.root, textvariable=self.status, anchor="w", bg="#e0e0e0")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.update_schedule_table()
        self.update_status()

    # ────────────── Data Handling ────────────── #
    def load_schedule(self):
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, "r") as f:
                return json.load(f)
        return []

    def save_schedule(self):
        with open(self.schedule_file, "w") as f:
            json.dump(self.schedule, f, indent=2)

    def update_schedule_table(self):
        self.tree.delete(*self.tree.get_children())
        for entry in sorted(self.schedule, key=lambda x: x["time"]):
            self.tree.insert("", tk.END, values=(entry["day"], entry["time"], entry["class"], entry["location"], entry["type"], entry.get("reminder", "No reminder")))

    def update_status(self):
        today = datetime.now().strftime("%A, %B %d")
        count = len(self.schedule)
        self.status.set(f"Today is {today} | {count} entries scheduled")
        self.root.after(60000, self.update_status)

    # ────────────── Add / Edit / Delete Entries ────────────── #
    def add_class(self):
        self.class_form("Add Class", entry_type="class")

    def add_assignment(self):
        self.class_form("Add Assignment", entry_type="assignment")

    def add_exam(self):
        self.class_form("Add Exam", entry_type="exam")

    def edit_class(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an entry to edit.")
            return
        values = self.tree.item(selected[0])["values"]
        self.class_form("Edit Entry", values=values, entry_type=values[4])

    def delete_class(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an entry to delete.")
            return
        values = self.tree.item(selected[0])["values"]
        self.schedule = [entry for entry in self.schedule if not (
            entry["day"] == values[0] and entry["time"] == values[1] and entry["class"] == values[2])]
        self.save_schedule()
        self.update_schedule_table()
        self.update_status()
        messagebox.showinfo("Deleted", "Entry deleted.")

    def class_form(self, title, values=None, entry_type="class"):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("400x350")
        win.grab_set()

        labels = ["Day", "Time (HH:MM)", "Class Name", "Location", "Reminder (min)"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(win, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        if values:
            for i in range(5):
                entries[i].insert(0, values[i])

        def save():
            try:
                day = entries[0].get()
                time_str = entries[1].get()
                class_name = entries[2].get()
                location = entries[3].get()
                reminder = entries[4].get()
                datetime.strptime(time_str, "%H:%M")
            except:
                messagebox.showerror("Error", "Invalid input. Ensure time is HH:MM.")
                return

            new_entry = {
                "class": class_name,
                "day": day,
                "time": time_str,
                "location": location,
                "type": entry_type,
                "reminder": f"{reminder} min before" if reminder != "0" else "No reminder"
            }

            if values:
                for i, entry in enumerate(self.schedule):
                    if entry["day"] == values[0] and entry["time"] == values[1] and entry["class"] == values[2]:
                        self.schedule[i] = new_entry
                        break
            else:
                self.schedule.append(new_entry)

            self.save_schedule()
            self.update_schedule_table()
            self.update_status()
            win.destroy()

        tk.Button(win, text="Save", command=save, bg="#63a8d4", fg="white").grid(row=6, columnspan=2, pady=10)

    # ────────────── Reminder System ────────────── #
    def set_reminder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an entry first.")
            return
        values = self.tree.item(selected[0])["values"]
        minutes = simpledialog.askinteger("Reminder", f"How many minutes before {values[2]}?", minvalue=1, maxvalue=120)
        if minutes:
            for entry in self.schedule:
                if entry["day"] == values[0] and entry["time"] == values[1] and entry["class"] == values[2]:
                    entry["reminder"] = f"{minutes} min before"
                    self.save_schedule()
                    self.update_schedule_table()
                    self.update_status()
                    break

    def start_reminder_monitor(self):
        self.reminder_thread = threading.Thread(target=self.reminder_check_loop, daemon=True)
        self.reminder_thread.start()

    def reminder_check_loop(self):
        while self.running:
            now = datetime.now()
            for entry in self.schedule:
                if "min before" in entry.get("reminder", ""):
                    try:
                        minutes = int(entry["reminder"].split()[0])
                        class_time = datetime.strptime(entry["time"], "%H:%M")
                        remind_time = datetime.combine(now.date(), class_time.time()) - timedelta(minutes=minutes)
                        if now >= remind_time and entry.get("notified") != now.date().isoformat():
                            self.root.after(0, lambda e=entry: self.show_reminder(e))
                            entry["notified"] = now.date().isoformat()
                            self.save_schedule()
                    except:
                        continue
            time.sleep(30)

    def show_reminder(self, entry):
        message = f"Reminder: {entry['type'].title()} - {entry['class']} at {entry['time']}\nLocation: {entry['location']}"
        messagebox.showinfo("Reminder", message)

    def on_closing(self):
        self.running = False
        if self.reminder_thread and self.reminder_thread.is_alive():
            self.reminder_thread.join(timeout=1.0)
        self.root.destroy()


# ────────────── Run the App ────────────── #
if __name__ == "__main__":
    root = tk.Tk()
    app = ClassReminder(root)
    root.mainloop()
