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
