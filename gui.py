# class_reminder_clean.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import threading
import time


class ClassReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Reminder")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f8ff")

        # File to store schedule data
        self.schedule_file = "class_schedule.json"

        # Load existing schedule or empty list
        self.schedule = self.load_schedule()

        # Used for reminders
        self.running = True
        self.reminder_thread = None

        # Build GUI and start reminder check
        self.create_widgets()
        self.start_reminder_monitor()

        # Handle window closing properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ────────────── GUI SETUP ────────────── #

    def create_widgets(self):
        # Title
        header = tk.Label(self.root, text="CLASS REMINDER", font=("Arial", 24, "bold"), bg="#4b86b4", fg="white")
        header.pack(fill=tk.X, pady=10)

        # Toolbar with buttons
        toolbar = tk.Frame(self.root, bg="#f0f8ff")
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        button_style = {"font": ("Arial", 10), "bg": "#63a8d4", "fg": "white", "width": 12}

        tk.Button(toolbar, text="Add Class", command=self.add_class, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Edit Class", command=self.edit_class, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Delete Class", command=self.delete_class, **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Set Reminder", command=self.set_reminder, **button_style).pack(side=tk.LEFT, padx=5)


        # Schedule table
        schedule_frame = tk.LabelFrame(self.root, text="Class Schedule", bg="#f0f8ff", font=("Arial", 12))
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("Time", "Class", "Location", "Reminder")
        self.tree = ttk.Treeview(schedule_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status = tk.StringVar()
        status_bar = tk.Label(self.root, textvariable=self.status, anchor="w", bg="#e0e0e0")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.update_schedule_table()
        self.update_status()

    # ────────────── DATA FUNCTIONS ────────────── #

    def load_schedule(self):
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, "r") as f:
                return json.load(f)
        return []

    def save_schedule(self):
        with open(self.schedule_file, "w") as f:
            json.dump(self.schedule, f, indent=2)

    # ────────────── SCHEDULE DISPLAY ────────────── #

    def update_schedule_table(self):
        self.tree.delete(*self.tree.get_children())
        for entry in sorted(self.schedule, key=lambda x: x["time"]):
            self.tree.insert("", tk.END, values=(entry["time"], entry["class"], entry["location"], entry.get("reminder", "No reminder")))

    def update_status(self):
        today = datetime.now().strftime("%A, %B %d")
        count = len(self.schedule)
        self.status.set(f"Today is {today} | {count} classes scheduled")
        self.root.after(60000, self.update_status)

    # ────────────── ADD / EDIT / DELETE ────────────── #

    def add_class(self):
        self.class_form("Add Class")

    def edit_class(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a class to edit.")
            return
        values = self.tree.item(selected[0])["values"]
        self.class_form("Edit Class", values)

    def delete_class(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a class to delete.")
            return
        values = self.tree.item(selected[0])["values"]
        self.schedule = [entry for entry in self.schedule if not (
            entry["time"] == values[0] and entry["class"] == values[1] and entry["location"] == values[2])]
        self.save_schedule()
        self.update_schedule_table()
        self.update_status()
        messagebox.showinfo("Deleted", "Class deleted.")

    def class_form(self, title, values=None):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("350x250")
        win.grab_set()

        labels = ["Class Name", "Time (HH:MM)", "Location", "Reminder (min)"]
        entries = []

        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(win, width=25)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries.append(entry)

        # Prefill values if editing
        if values:
            for i in range(3):
                entries[i].insert(0, values[i])
            if "min" in values[3]:
                entries[3].insert(0, values[3].split()[0])

        def save():
            try:
                class_name = entries[0].get()
                time_str = entries[1].get()
                location = entries[2].get()
                reminder = entries[3].get()
                datetime.strptime(time_str, "%H:%M")  # validate time
            except:
                messagebox.showerror("Error", "Invalid input. Use HH:MM for time.")
                return

            new_entry = {
                "class": class_name,
                "time": time_str,
                "location": location,
                "reminder": f"{reminder} min before" if reminder != "0" else "No reminder"
            }

            if title == "Add Class":
                self.schedule.append(new_entry)
            else:
                for i, entry in enumerate(self.schedule):
                    if entry["time"] == values[0] and entry["class"] == values[1] and entry["location"] == values[2]:
                        self.schedule[i] = new_entry
                        break

            self.save_schedule()
            self.update_schedule_table()
            self.update_status()
            win.destroy()

        tk.Button(win, text="Save", command=save, bg="#63a8d4", fg="white").grid(row=5, columnspan=2, pady=10)

    # ────────────── REMINDER FEATURES ────────────── #

    def set_reminder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a class first.")
            return

        values = self.tree.item(selected[0])["values"]
        minutes = simpledialog.askinteger("Reminder", f"How many minutes before {values[1]}?", minvalue=1, maxvalue=120)
        if minutes:
            for entry in self.schedule:
                if entry["time"] == values[0] and entry["class"] == values[1] and entry["location"] == values[2]:
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
                            self.root.after(0, self.show_reminder, entry)
                            entry["notified"] = now.date().isoformat()
                            self.save_schedule()
                    except:
                        continue
            time.sleep(30)

    def show_reminder(self, entry):
        message = f"Reminder: {entry['class']} starts at {entry['time']}\nLocation: {entry['location']}"
        messagebox.showinfo("Class Reminder", message)

    def on_closing(self):
        self.running = False
        if self.reminder_thread and self.reminder_thread.is_alive():
            self.reminder_thread.join(timeout=1.0)
        self.root.destroy()


# ────────────── RUN THE APP ────────────── #
if __name__ == "__main__":
    root = tk.Tk()
    app = ClassReminderApp(root)
    root.mainloop()
