import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

#this is for the matplotlib implementation
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    _HAS_MPL = True
except Exception:
    _HAS_MPL = False

#These are the themes of the GUI
#They use hexadecimals for choosing colors
#It is conventional to use an all uppercase name
BG = "#000000"  #black background
FG = "#2AF76F"  #neon-ish green for text
ACCENT = "#1E8B4D"  #green for fills
SUBTLE = "#3A3A3A"  #dark gray for bars & frames


class App(tk.Tk):
    """Minimal multi-page Tkinter app to switch between frames.
    The routing via a dict of pages is simple and easy to extend.
    """

    def __init__(self):
        super().__init__()
        self.title("Game of Life — Tasks")
        self.configure(bg=BG) #refers to the hexadecimal color option we chose
        self.geometry("920x640")  #used to set the size of our application window -> generic size

        #THIS HERE HAS TO REPLACED WITH THE DATABASE LATER
        self.user_name = "Player"
        self.user_email = ""
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100  #set as a constant value of 100 xp to level up for now
        self.tasks = []  #list of dicts for {name, priority, due_date}

        #defining different font sizes -> lg = large, md = medium, sm = small
        self.font_lg = tkfont.Font(size=18, weight="bold")
        self.font_md = tkfont.Font(size=14)
        self.font_sm = tkfont.Font(size=12)


        #tk.Frame to create the container to hold our widgets
        container = tk.Frame(self, bg=BG) #bg for black background
        #we know we have the three layout managers -> pack, grid, place
        #we are using pack here to literally pack all the widgets into the one window
        #soon we use tk.Raise() -> I will exaplain it when we get there but it is important for this portion
        container.pack(fill="both", expand=True)

        #creating an empty dictionary
        #the intention here is that we can store our page objects and retrieve them later
        #by page object I mean one of the actual functioning pages within the GUI
        self.pages = {}
        #a tuple used to store all of the page classes -> not instances yet
        for Page in (WelcomePage, MenuPage, DashboardPage, AddTaskPage, CalendarPage):
            #parent=container -> the parent widget for this is the container we made earlier
            page = Page(parent=container, app=self)
            self.pages[Page.__name__] = page #store the page instance in the dictionary
            page.grid(row=0, column=0, sticky="nsew") #grid for a two-dimensional table

        self.show("WelcomePage")

    #now we have a method called show
    def show(self, name: str):
        """Show a page by class name.
        Simple and explicit. Avoids magic.
        """
        frame = self.pages[name] #finds the object in the dictionary -> if name = 'MenuPage' it retrieves the menu page
        #tkraise is used to bring the widget we retrieved to the front so that it is visible
        frame.tkraise()
        #hasattr -> means has attribute
        #so if the page object has an attribute on show then it will return True and false is it doesn't
        if hasattr(frame, "on_show"):
            frame.on_show() #if it returns True, it will show

    #this is a helper method intended to keep everything consistent
    #by this I mean any label using make_label will automatically use the same colors and fonts -> keeps it clean and not repetitive
    def make_label(self, parent, text, font=None):
        return tk.Label(parent, text=text, bg=BG, fg=FG, font=font or self.font_md)

    #same helper method idea -> for consistency
    def make_button(self, parent, text, cmd):
        button = tk.Button(parent, text=text, command=cmd, bg=SUBTLE, fg=FG, activebackground=ACCENT,
                        activeforeground="white", relief="flat", padx=12, pady=8)
        return button

    #add xp
    #WE HAVE CONFIG.PY, I BELIEVE THIS SHOULD BE REFERENCED FROM THERE RATHER THAN BEING HERE
    def add_xp(self, amount: int):
        """Grant XP and handle basic level-up logic (very simplified)."""
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1

#FROM THIS POINT ON IS THE IMPLEMENTATION OF THE ACTUAL INTERFACES OF EACH PAGE
#note it takes in parameter tk.Frame
#note we use our helper method make_label
class WelcomePage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app

        app.make_label(self, "WELCOME TO THE", font=app.font_lg).pack(pady=(40, 0))
        app.make_label(self, "GAME OF LIFE!", font=app.font_lg).pack(pady=(0, 30))

        app.make_label(self, "ENTER YOUR NAME:", font=app.font_sm).pack()
        self.name_var = tk.StringVar(value="")
        tk.Entry(self, textvariable=self.name_var, bg=SUBTLE, fg=FG, insertbackground=FG).pack(ipadx=80, ipady=6, pady=6)

        app.make_label(self, "ENTER YOUR EMAIL:", font=app.font_sm).pack(pady=(12, 0))
        self.email_var = tk.StringVar(value="")
        tk.Entry(self, textvariable=self.email_var, bg=SUBTLE, fg=FG, insertbackground=FG).pack(ipadx=80, ipady=6, pady=6)

        app.make_button(self, "BEGIN", self._begin).pack(pady=24)

    def _begin(self):
        #note we defined name_var in WelcomePage
        #will retrieve the text input by the user and strips it to remove possible whitespace
        #if the user doesn't input anything it will use Player as default
        name = self.name_var.get().strip() or "Player"
        email = self.email_var.get().strip()
        self.app.user_name = name
        self.app.user_email = email
        self.app.show("MenuPage")


class MenuPage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app

        app.make_label(self, "GAME OF LIFE", font=app.font_lg).pack(pady=(24, 6))
        self.welcome = app.make_label(self, "WELCOME BACK, USER!", font=app.font_sm)
        self.welcome.pack(pady=(0, 24))

        app.make_button(self, "MAIN DASHBOARD", lambda: app.show("DashboardPage")).pack(pady=6)
        app.make_button(self, "ADD TASKS", lambda: app.show("AddTaskPage")).pack(pady=6)
        app.make_button(self, "VIEW CALENDAR", lambda: app.show("CalendarPage")).pack(pady=6)

    def on_show(self):
        self.welcome.config(text=f"WELCOME BACK, {self.app.user_name.upper()}!")


class DashboardPage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app

        #header using large font
        app.make_label(self, "MAIN DASHBOARD", font=app.font_lg).pack(pady=(24, 20))

        #
        row = tk.Frame(self, bg=BG)
        row.pack(pady=8)
        app.make_label(row, "PLAYER", font=app.font_sm).pack(side="left", padx=(0, 12))
        #defining name_box
        self.name_box = tk.Label(row, text="NAME", bg=SUBTLE, fg=FG, font=app.font_sm, width=20, anchor="w", padx=8)
        self.name_box.pack(side="left")

        #used for our XP bar
        app.make_label(self, "XP", font=app.font_sm).pack(pady=(20, 6))
        #Tkinter has a widget ProgressBar which is perfect for what we need
        self.xp_bar = ProgressBar(self, width=420, height=18, bg_color=SUBTLE, fill_color=ACCENT)
        self.xp_bar.pack()

        #level bar -> same idea as the xp bar
        self.level_text = app.make_label(self, "LEVEL 1", font=app.font_sm)
        self.level_text.pack(pady=(20, 6))
        self.lv_bar = ProgressBar(self, width=420, height=18, bg_color=SUBTLE, fill_color=ACCENT)
        self.lv_bar.pack()

        tk.Frame(self, height=16, bg=BG).pack()
        #we use lambda here so we dont have to define a function to show menupage
        app.make_button(self, "BACK TO MENU", lambda: app.show("MenuPage")).pack(pady=8)

    def on_show(self):
        self.name_box.config(text=self.app.user_name)
        # XP progress is xp / xp_to_next
        xp_ratio = max(0.0, min(1.0, self.app.xp / float(self.app.xp_to_next)))
        self.xp_bar.set_ratio(xp_ratio)

        # Level progress here is fake/simple (same as XP bar) to show the visual per wireframe.
        self.level_text.config(text=f"LEVEL {self.app.level}")
        self.lv_bar.set_ratio(xp_ratio)


class AddTaskPage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app

        app.make_label(self, "TASK DETAILS", font=app.font_lg).grid(row=0, column=0, columnspan=4, pady=(24, 16))

        #add task
        app.make_label(self, "ADD TASK:", font=app.font_sm).grid(row=1, column=0, sticky="w", padx=20)
        #StringVar() so that we can use the widgets for string data
        self.task_name = tk.StringVar()
        tk.Entry(self, textvariable=self.task_name, bg=SUBTLE, fg=FG, insertbackground=FG, width=28).grid(row=1, column=1, sticky="w")

        #priority options
        app.make_label(self, "PRIORITY", font=app.font_sm).grid(row=2, column=0, sticky="w", padx=20, pady=(8, 0))
        self.priority = tk.StringVar(value="Low")
        tk.OptionMenu(self, self.priority, "Low", "Medium", "High", "Critical").grid(row=2, column=1, sticky="w", pady=(8, 0))

        #due date entry
        app.make_label(self, "DUE DATE", font=app.font_sm).grid(row=1, column=2, sticky="w", padx=(40, 0))
        self.due_date = tk.StringVar()
        tk.Entry(self, textvariable=self.due_date, bg=SUBTLE, fg=FG, insertbackground=FG, width=18).grid(row=1, column=3, sticky="w")
        app.make_label(self, "Format suggestion: YYYY-MM-DD", font=app.font_sm).grid(row=2, column=2, columnspan=2, sticky="w", padx=(40, 0))

        #add button
        app.make_button(self, "ADD", self._add_task).grid(row=3, column=1, sticky="w", pady=12)
        app.make_button(self, "BACK TO MENU", lambda: app.show("MenuPage")).grid(row=3, column=0, sticky="w", padx=20, pady=12)
        
        #active tasks list
        app.make_label(self, "ACTIVE TASKS", font=app.font_sm).grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=(12, 4))
        self.listbox = tk.Listbox(self, width=60, height=8, bg=SUBTLE, fg=FG)
        self.listbox.grid(row=5, column=0, columnspan=2, sticky="w", padx=20)

        #None of this is from the notebooks or what we learned in class
        #It uses matplotlib to display a graph for the tasks we have idk if I really like it
        if _HAS_MPL:
            app.make_label(self, "CHART: TASKS BY PRIORITY", font=app.font_sm).grid(row=6, column=0, columnspan=2, sticky="w", padx=20, pady=(14, 4))
            self.fig = Figure(figsize=(4.6, 2.4))
            self.ax = self.fig.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=2, padx=20, sticky="w")


        #used to configure the padding for the grid
        for col in range(4):
            self.grid_columnconfigure(col, pad=8)

    def _add_task(self):
        name = self.task_name.get().strip()
        if not name:
            return
        item = {
            "name": name,
            "priority": self.priority.get(),
            "due": self.due_date.get().strip(),
        }
        self.app.tasks.append(item)
        #FAKE TO SEE THE BARS MOVE, WE HAVE TO IMPLEMENT THIS WITH THE REST OF OUR TABLES
        self.app.add_xp(10)
        self._refresh_list()
        if _HAS_MPL: #for the matplotlib integration
            self._refresh_chart()
        self.task_name.set("")
        self.due_date.set("")

    def on_show(self):
        self._refresh_list()
        if _HAS_MPL:
            self._refresh_chart()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for t in self.app.tasks:
            self.listbox.insert(tk.END, f"{t['name']}  |  {t['priority']}  |  {t['due']}")

    def _refresh_chart(self):
        #simple bar chart with counts per priority.
        self.ax.clear()
        counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for t in self.app.tasks:
            if t["priority"] in counts:
                counts[t["priority"]] += 1
        labels = list(counts.keys())
        values = [counts[k] for k in labels]
        self.ax.bar(labels, values)  #no custom colors just to keep it simple
        self.ax.set_ylim(0, max(values + [1]))
        self.ax.set_title("Tasks by Priority")
        self.canvas.draw()


class CalendarPage(tk.Frame):
    def __init__(self, parent, app: App):
        super().__init__(parent, bg=BG)
        self.app = app
        app.make_label(self, "CALENDAR (COMING SOON)", font=app.font_lg).pack(pady=(24, 12))
        #placeholder text to make it obvious where the calendar would go for future integration
        app.make_label(
            self,
            "This page will show a calendar view and scheduled tasks.",
            font=app.font_sm,
        ).pack(pady=6)
        app.make_button(self, "BACK TO MENU", lambda: app.show("MenuPage")).pack(pady=16)


class ProgressBar(tk.Frame):
    """A tiny, canvas-based progress bar used for XP/Level.
    Canvas is a very common primitive in Tkinter intros. Simple and dependency-free.
    """

    def __init__(self, parent, width=300, height=16, bg_color=SUBTLE, fill_color=ACCENT):
        super().__init__(parent, bg=BG)
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fill_color = fill_color
        #using canvas lets us draw what we wnat it to look like -> idk if I like this I have to explore other options
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
