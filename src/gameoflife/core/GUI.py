from config import Task, TaskStatus
from game import User, Player, TaskManager
import database
import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont

# this is for the matplotlib implementation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

#These are the themes of the GUI
#We used tk instead of ttk for this exact reason! because we wanted these specific colors!
BG = "#000000"  # black background
FG = "#2AF76F"  # neon-ish green for text
ACCENT = "#1E8B4D"  # green for fills
SUBTLE = "#3A3A3A"  # dark gray for bars & frames


class App(tk.Tk):
    def __init__(self):
        #initialize the parent class and make the root window
        super().__init__()
        self.title("Game of Life — Tasks")
        self.configure(bg=BG)
        self.geometry("920x640")

        #initialize the database on startup. overlooked this and caused a headache
        database.init_db()

        #these values are initialized to None originally, and will be populated after the user logs in
        self.task_manager = None
        self.current_user = None
        self.current_player = None

        #defining different font sizes
        self.font_lg = tkfont.Font(size=18, weight="bold")
        self.font_md = tkfont.Font(size=14)
        self.font_sm = tkfont.Font(size=12)

        #tk.Frame to create the container to hold our widgets
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)

        self.pages = {}
        # a tuple used to store all of the page classes
        for Page in (WelcomePage, MenuPage, DashboardPage, AddTaskPage, CalendarPage):
            #initialize the page -> pass 'container' as the parent
            page = Page(parent=container, app=self)
            self.pages[Page.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show("WelcomePage")

    def show(self, name: str):
        #retreieve the page object from the dictionary
        frame = self.pages[name]
        #we use tkraise() to bring the retrieved object to the front of the scren
        frame.tkraise()
        #hasattr -> has attribute -> used to reload a users data
        if hasattr(frame, "on_show"):
            frame.on_show()

    # helper methods for consistency and ease
    def make_label(self, parent, text, font=None):
        return tk.Label(parent, text=text, bg=BG, fg=FG, font=font or self.font_md)

    def make_button(self, parent, text, cmd):
        button = tk.Button(parent, text=text, command=cmd, bg=SUBTLE, fg=FG, activebackground=ACCENT,
                           activeforeground="white", relief="flat", padx=12, pady=8)
        return button


class WelcomePage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app

        app.make_label(self, "WELCOME TO THE", font=app.font_lg).pack(pady=(40, 0))
        app.make_label(self, "GAME OF LIFE!", font=app.font_lg).pack(pady=(0, 30))

        app.make_label(self, "ENTER YOUR USERNAME:", font=app.font_sm).pack()
        self.name_var = tk.StringVar(value="")
        tk.Entry(self, textvariable=self.name_var, bg=SUBTLE, fg=FG, insertbackground=FG).pack(ipadx=80, ipady=6,
                                                                                               pady=6)

        app.make_label(self, "ENTER YOUR EMAIL (optional):", font=app.font_sm).pack(pady=(12, 0))
        self.email_var = tk.StringVar(value="")
        tk.Entry(self, textvariable=self.email_var, bg=SUBTLE, fg=FG, insertbackground=FG).pack(ipadx=80, ipady=6,
                                                                                                pady=6)

        app.make_button(self, "BEGIN", self._begin).pack(pady=24)

    def _begin(self):
        #this gets the entered string from StringVar
        #then strips it from any additional whitespace which is important becasue we dont care about spaces in a username
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()

        if not name: #if no username is entered
            #then error message and terminate the function
            messagebox.showwarning("Input Error", "Please enter a username.")
            return

        #query the database to see if the username already exists
        user_data = database.get_user_by_username(name)

        if user_data: #if the user is found
            #id is stored at index 0, so extract it
            user_id = user_data[0]
            #then get username at index 1 and email at index 2
            user_obj = User(user_data[1], user_data[2])
            print(f"Loaded User: {user_obj}")
        else: #otherwise create a new user
            user_obj = User(name, email)
            #save the new user into the databse
            user_id = database.insert_user(user_obj)
            print(f"Created New User ID: {user_id}")

        self.app.current_user = user_obj

        #retreive the stats from the user
        player_data = database.get_player_by_user_id(user_id)

        if player_data:
            p_obj = Player(user_obj) #this is the empty player object linked to the user
            #all of these are the indicies we want to retrieve
            #ex. ID, username, email, XP, level, etc.
            p_obj.id = player_data[0]
            p_obj.xp = player_data[2]
            p_obj.level = player_data[3]
            p_obj.tasks_completed = player_data[4]
            p_obj.tasks_failed = player_data[5]
            p_obj.current_streak = player_data[6]
            p_obj.longest_streak = player_data[7]
            p_obj.tasks_completed_early = player_data[8]
            p_obj.critical_tasks_completed = player_data[9]
            p_obj.previous_rank = player_data[10]
            print("Loaded existing player stats.")
        else: #othewise we create a defualt player
            player_id = database.insert_player(user_id)
            p_obj = Player(user_obj)
            p_obj.id = player_id
            print("Created new player stats.")

        self.app.current_player = p_obj

        #initialize task manager
        #p_obj: the loaded in player object
        #p_obj.id: used as a save file
        self.app.task_manager = TaskManager(p_obj, user_id, p_obj.id)

        #loads the active tasks from the database into the task manager
        db_tasks = database.get_tasks_by_user(user_id)
        for t in db_tasks:
            #We removed OVERDUE and FAILED from before, so we only check for active or completed
            #if active, add it to the task manager list
            if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                self.app.task_manager.active_tasks.append(t)
            #if the task is completed leave it be
            elif t.status == TaskStatus.COMPLETED:
                self.app.task_manager.completed_tasks.append(t)

        self.app.show("MenuPage")


class MenuPage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app

        app.make_label(self, "GAME OF LIFE", font=app.font_lg).pack(pady=(24, 6))
        self.welcome = app.make_label(self, "WELCOME BACK, USER!", font=app.font_sm)
        self.welcome.pack(pady=(0, 24))

        app.make_button(self, "MAIN DASHBOARD", lambda: app.show("DashboardPage")).pack(pady=6)
        app.make_button(self, "MANAGE TASKS", lambda: app.show("AddTaskPage")).pack(pady=6)
        app.make_button(self, "VIEW CALENDAR", lambda: app.show("CalendarPage")).pack(pady=6)

    def on_show(self):
        if self.app.current_user:
            self.welcome.config(text=f"WELCOME BACK, {self.app.current_user.username.upper()}!")


class DashboardPage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app

        # header using large font
        app.make_label(self, "MAIN DASHBOARD", font=app.font_lg).pack(pady=(24, 20))

        row = tk.Frame(self, bg=BG)
        row.pack(pady=8)
        app.make_label(row, "PLAYER", font=app.font_sm).pack(side="left", padx=(0, 12))

        self.name_box = tk.Label(row, text="NAME", bg=SUBTLE, fg=FG, font=app.font_sm, width=20, anchor="w", padx=8)
        self.name_box.pack(side="left")

        app.make_label(self, "XP", font=app.font_sm).pack(pady=(20, 6))
        self.xp_bar = ProgressBar(self, width=420, height=18, bg_color=SUBTLE, fill_color=ACCENT)
        self.xp_bar.pack()
        self.xp_details = app.make_label(self, "0 / 100", font=tkfont.Font(size=10))
        self.xp_details.pack()

        self.level_text = app.make_label(self, "LEVEL 1", font=app.font_sm)
        self.level_text.pack(pady=(20, 6))
        self.rank_text = app.make_label(self, "Rank: None", font=tkfont.Font(size=10))
        self.rank_text.pack()

        tk.Frame(self, height=16, bg=BG).pack()
        app.make_button(self, "BACK TO MENU", lambda: app.show("MenuPage")).pack(pady=8)

    def on_show(self):
        #this is our solution to our task manager crashing
        #it ensures that the game engine is running properly
        if self.app.current_user and self.app.task_manager:
            p = self.app.task_manager.player
            self.name_box.config(text=self.app.current_user.username)

            #calculate the xp progress and update the bar
            progress_pct = p.get_progress_to_next_level()
            self.xp_bar.set_ratio(progress_pct / 100.0)

            #update the labels to show the updated stats
            self.xp_details.config(text=f"{p.xp} Total XP")
            self.level_text.config(text=f"LEVEL {p.level}")
            self.rank_text.config(text=f"Rank: {p.get_rank()} | Streak: {p.current_streak}")


class AddTaskPage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app
        #used to keep track of which task object corresponds to a specific list selection
        self.displayed_tasks = []

        app.make_label(self, "TASK MANAGER", font=app.font_lg).grid(row=0, column=0, columnspan=4, pady=(24, 16))

        #add task
        app.make_label(self, "ADD TASK:", font=app.font_sm).grid(row=1, column=0, sticky="w", padx=20)
        self.task_name = tk.StringVar()
        tk.Entry(self, textvariable=self.task_name, bg=SUBTLE, fg=FG, insertbackground=FG, width=28).grid(row=1,
                                                                                                          column=1,
                                                                                                          sticky="w")

        #priority options
        app.make_label(self, "PRIORITY", font=app.font_sm).grid(row=2, column=0, sticky="w", padx=20, pady=(8, 0))
        self.priority = tk.StringVar(value="medium")
        # Note: Mapping display strings to config strings lowercase
        tk.OptionMenu(self, self.priority, "low", "medium", "high", "critical").grid(row=2, column=1, sticky="w",
                                                                                     pady=(8, 0))

        #due date entry
        app.make_label(self, "DUE DATE", font=app.font_sm).grid(row=1, column=2, sticky="w", padx=(40, 0))
        self.due_date = tk.StringVar()
        tk.Entry(self, textvariable=self.due_date, bg=SUBTLE, fg=FG, insertbackground=FG, width=18).grid(row=1,
                                                                                                         column=3,
                                                                                                         sticky="w")
        app.make_label(self, "Format: YYYY-MM-DD", font=app.font_sm).grid(row=2, column=2, columnspan=2, sticky="w",
                                                                          padx=(40, 0))

        #buttons
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=12, sticky="w", padx=20)

        app.make_button(btn_frame, "ADD TASK", self._add_task).pack(side="left", padx=(0, 10))
        #complete task button
        app.make_button(btn_frame, "COMPLETE SELECTED", self._complete_task).pack(side="left", padx=(0, 10))
        app.make_button(btn_frame, "BACK TO MENU", lambda: app.show("MenuPage")).pack(side="left")

        #active tasks list
        app.make_label(self, "ACTIVE TASKS", font=app.font_sm).grid(row=4, column=0, columnspan=2, sticky="w", padx=20,
                                                                    pady=(12, 4))
        self.listbox = tk.Listbox(self, width=80, height=8, bg=SUBTLE, fg=FG, font=("Consolas", 10))
        self.listbox.grid(row=5, column=0, columnspan=4, sticky="w", padx=20)


        app.make_label(self, "CHART: TASKS BY PRIORITY", font=app.font_sm).grid(row=6, column=0, columnspan=2,
                                                                                    sticky="w", padx=20, pady=(14, 4))
        self.fig = Figure(figsize=(4.6, 2.4), facecolor=BG)
        self.ax = self.fig.add_subplot(111)
        #these are the plot colors
        self.ax.set_facecolor(BG)
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=2, padx=20, sticky="w")

    def _add_task(self):
        name = self.task_name.get().strip()
        if not name:
            return

        #parse date string to datetime object
        d_str = self.due_date.get().strip()
        d_obj = None
        if d_str:
            try:
                d_obj = datetime.datetime.strptime(d_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Date Error", "Invalid Date Format. Use YYYY-MM-DD")
                return

        #create our task object
        new_task = Task(title=name, priority=self.priority.get(), due_date=d_obj)

        #send it to the task manager
        self.app.task_manager.add_task(new_task)

        self._refresh_list()
        self._refresh_chart()

        self.task_name.set("")
        self.due_date.set("")

    def _complete_task(self):
        #this is the logic behind when a user clicks the complete task button
        #index of the selected item
        selection = self.listbox.curselection()
        if not selection:#dont do anything if nothing is selected
            return

        index = selection[0] #from the tuple we made, extract the index
        #this if statement makes sure our UI index actually corresponds to a task
        if index < len(self.displayed_tasks):
            task_to_complete = self.displayed_tasks[index]

            #then it returns a dictionary about what just happened
            result = self.app.task_manager.complete_task(task_to_complete)

            #shows rewards, ranks up if needed
            msg = f"Task Completed!\nXP Earned: {result['xp_earned']}"
            if result['rank_changed']:
                msg += f"\nRANK UP! You are now a {result['new_rank']}!"
            messagebox.showinfo("Victory", msg)
            #then it refreshes the lists and the charts
            self._refresh_list()
            self._refresh_chart()

    def on_show(self):
        #all this does is ensure that everything is refreshed upon a task being added
        self._refresh_list()
        self._refresh_chart()

    def _refresh_list(self):
        #delete from index 0 to the very last index
        self.listbox.delete(0, tk.END)
        #reset the list to be empty
        self.displayed_tasks = []

        if self.app.task_manager: #make sure everything running properly
            tasks = self.app.task_manager.get_active_tasks()
            self.displayed_tasks = tasks  #store objects to match listbox index

            for t in tasks:
                d_text = t.due_date.strftime("%Y-%m-%d") if t.due_date else "No Due Date"
                #makes sure the columns are roughly aligned -> looks much better than before
                self.listbox.insert(tk.END, f"{t.title:<30} | {t.priority.upper():<10} | {d_text}")

    def _refresh_chart(self):
        if not self.app.task_manager:
            return
        #clears all the previous bars
        self.ax.clear()
        counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for t in self.app.task_manager.active_tasks:
            if t.priority in counts:
                counts[t.priority] += 1

        labels = list(counts.keys())
        values = [counts[k] for k in labels]

        bars = self.ax.bar(labels, values, color=ACCENT)
        self.ax.set_title("Active Tasks by Priority", color='white')
        self.canvas.draw()


# class CalendarPage(tk.Frame):
#     def __init__(self, parent, app: App):
#         super().__init__(parent, bg=BG)
#         self.app = app
#         app.make_label(self, "CALENDAR (COMING SOON)", font=app.font_lg).pack(pady=(24, 12))
#         app.make_label(
#             self,
#             "This page will show a calendar view and scheduled tasks.",
#             font=app.font_sm,
#         ).pack(pady=6)
#         app.make_button(self, "BACK TO MENU", lambda: app.show("MenuPage")).pack(pady=

# --- ADD THIS IMPORT AT THE TOP OF GUI.PY ---
from tkcalendar import Calendar


class CalendarPage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app

        # 1. Header
        app.make_label(self, "CALENDAR & SCHEDULE", font=app.font_lg).pack(pady=(20, 10))

        # 2. The Calendar Widget
        # CRITICAL FIX: date_pattern='yyyy-mm-dd' prevents the "jumping month" bug
        # and ensures standard string comparison for tasks.
        self.cal = Calendar(
            self,
            selectmode='day',
            date_pattern='yyyy-mm-dd',  # <--- THIS FIXES THE GLITCH
            background=BG,
            foreground=FG,
            headersbackground=SUBTLE,
            headersforeground=FG,
            bordercolor=SUBTLE,
            normalbackground=BG,
            normalforeground="white",
            weekendbackground=BG,
            weekendforeground="white",
            selectbackground=ACCENT,
            selectforeground='white',
            cursor="hand2"
        )
        self.cal.pack(pady=10, padx=20, fill="both", expand=True)

        # Bind the "Click" event
        self.cal.bind("<<CalendarSelected>>", self._on_day_selected)

        # 3. Task Details Section
        details_frame = tk.Frame(self, bg=BG)
        details_frame.pack(fill="both", expand=True, padx=20, pady=10)

        app.make_label(details_frame, "TASKS FOR SELECTED DATE:", font=app.font_sm).pack(anchor="w")

        self.details_list = tk.Listbox(details_frame, bg=SUBTLE, fg=FG, height=5, font=("Consolas", 10), relief="flat")
        self.details_list.pack(fill="x", pady=5)

        app.make_button(self, "BACK TO MENU", lambda: app.show("MenuPage")).pack(pady=10)

    def on_show(self):
        """Refreshes events (dots) whenever the page is opened."""
        self.cal.calevent_remove("all")  # Clear old dots

        if self.app.task_manager:
            for task in self.app.task_manager.active_tasks:
                if task.due_date:
                    # We strip the time and keep only the date component
                    # task.due_date is a datetime object, so we need .date()
                    d_date = task.due_date.date()

                    self.cal.calevent_create(
                        d_date,
                        "Task Due",
                        "task_due"
                    )

        # Color the dots GREEN
        self.cal.tag_config("task_due", background=ACCENT, foreground='white')

        # Trigger the selection logic immediately for the current day
        # so the list isn't empty when you first open the page
        self._on_day_selected(None)

    def _on_day_selected(self, event):
        """Updates the listbox when a day is clicked."""
        self.details_list.delete(0, tk.END)

        # Get the selected date as a string (Format: YYYY-MM-DD)
        selected_date_str = self.cal.get_date()

        found_any = False
        if self.app.task_manager:
            for task in self.app.task_manager.active_tasks:
                if task.due_date:
                    # Convert the task's datetime object to the same string format
                    task_date_str = task.due_date.strftime("%Y-%m-%d")

                    # Compare strings
                    if task_date_str == selected_date_str:
                        # Add to list
                        self.details_list.insert(tk.END, f"• {task.title} ({task.priority.upper()})")
                        found_any = True

        if not found_any:
            self.details_list.insert(tk.END, "(No tasks due on this day)")






class ProgressBar(tk.Frame):
    def __init__(self, parent, width=300, height=16, bg_color=SUBTLE, fill_color=ACCENT):
        super().__init__(parent, bg=BG)
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.canvas = tk.Canvas(self, width=width, height=height, highlightthickness=0, bg=BG)
        self.canvas.pack()
        self.canvas.create_rectangle(0, 0, width, height, fill=bg_color, width=0)
        self.fill_id = self.canvas.create_rectangle(0, 0, 0, height, fill=fill_color, width=0)

    def set_ratio(self, ratio: float):
        ratio = max(0.0, min(1.0, ratio))
        self.canvas.coords(self.fill_id, 0, 0, int(self.width * ratio), self.height)


if __name__ == "__main__":
    app = App()
    app.mainloop()