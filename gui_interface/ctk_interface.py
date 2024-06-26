import customtkinter as ctk
import tkinter as tk
import os
import json

from helper_funcs import *

YNAB_ACCESS_TOKEN = None
    

class FrameTokenEntry(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.label_entry = ctk.CTkLabel(master=self, text="Personal Access Token: ")
        self.entry = ctk.CTkEntry(master=self, width=350, height=25, border_width=1, corner_radius=5)

        self.label_entry.grid(row=0, column=0,padx=10)
        self.entry.grid(row=0, column=1)

class FrameAuthentication(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.label_auth_message_1 = ctk.CTkLabel(master=self, font=master.font_h3, text="Please set up your YNAB authentication.")
        self.label_auth_message_2 = ctk.CTkLabel(master=self, font=master.font_h5, text="Currently we are using YNAB Personal Access Tokens for this.\nYour token will be stored in secrets.json in your working directory.")
        self.label_auth_instructions = ctk.CTkLabel(master=self, text="For instructions on how to obtain this, go to\nhttps://api.ynab.com/#:~:text=Sign%20in%20to%20the%20YNAB,to%20get%20an%20access%20token")
        
        self.entry = FrameTokenEntry(self)
        self.button_submit = ctk.CTkButton(master=self, text="Submit", command=self.submit)

        self.label_result = ctk.CTkLabel(master=self, text="")

        self.label_auth_message_1.pack(pady=10)
        self.label_auth_message_2.pack(pady=10)
        self.label_auth_instructions.pack(pady=10)
        self.entry.pack(pady=10)
        self.button_submit.pack(pady=20)

    def submit(self):
        global YNAB_ACCESS_TOKEN
        YNAB_ACCESS_TOKEN = self.entry.entry.get()

        if verify_ynab_access_token(YNAB_ACCESS_TOKEN):
            save_ynab_access_token(YNAB_ACCESS_TOKEN, "secrets.json")
            self.label_result.configure(text="Token verified and saved successfully!", text_color="green")
            self.label_result.pack(pady=10)

            self.master.switch_frame(FrameBudgetDisplay)
        else:
            self.label_result.configure(text="Invalid token. Please try again.", text_color="red")
            self.label_result.pack(pady=10)


class FrameBudgetSelect(ctk.CTkFrame):
    def __init__(self, master, budgets):
        super().__init__(master, fg_color="transparent")

        self.widget_list = []
        self.selected_index = None  # Variable to track the currently selected button index

        for index, budget in enumerate(budgets.values()):
            button = ctk.CTkButton(
                master=self, 
                text=budget, 
                font=master.master.master.font_h5, 
                command=lambda i=index: self.select(i)
            )
            self.widget_list.append(button)
            button.pack(pady=5, ipadx=15)

    def select(self, button_index):
       
        # Deselect previously selected button
        if self.selected_index is not None:
            self.widget_list[self.selected_index].configure(fg_color="#3a7ebf", hover_color="#325882")  # Set color back to default

        # Update selected index and highlight the selected button
        self.selected_index = button_index
        self.widget_list[button_index].configure(fg_color="black", hover_color="black")

        # Check if message needs to be displayed
        self.master.master.display_message()

class FrameBudgetDisplay(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent", width=700, height=500)

        self.budgets = get_budgets(YNAB_ACCESS_TOKEN)
        self.master = master

        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.label_select_start = ctk.CTkLabel(self.grid_frame, text="Select a budget to migrate from.", font=self.master.font_h5)
        self.label_select_end = ctk.CTkLabel(self.grid_frame, text="Select a budget to migrate to.", font=self.master.font_h5)
        self.budget_select_start = FrameBudgetSelect(self.grid_frame, self.budgets)
        self.budget_select_end = FrameBudgetSelect(self.grid_frame, self.budgets)

        self.label_message = ctk.CTkLabel(master=self, text="", font=self.master.font_h5)
        self.button_migrate = ctk.CTkButton(master=self, text="Select Categories", command=self.submit)

        self.label_select_start.grid(column=0, row=0, pady=10, padx=40)
        self.label_select_end.grid(column=1, row=0, pady=10, padx=40)
        self.budget_select_start.grid(column=0, row=1, pady=10, padx=40)
        self.budget_select_end.grid(column=1, row=1, pady=10, padx=40)

        self.grid_frame.pack()
        self.label_message.pack(pady=10)

    def display_message(self):
        if (self.budget_select_start.selected_index != None) and (self.budget_select_end.selected_index != None):
            if self.budget_select_start.selected_index == self.budget_select_end.selected_index:
                self.button_migrate.destroy()
                self.label_message.configure(text="You are trying to migrate within the same budget. This can be easily done in the YNAB web app.")
            else:
                self.label_message.configure(text=f"Migrating from {list(self.budgets.values())[self.budget_select_start.selected_index]} to {list(self.budgets.values())[self.budget_select_end.selected_index]}")
                self.button_migrate.pack()

    def submit(self):
        budget_id_start = list(self.budgets.keys())[self.budget_select_start.selected_index]
        budget_name_start = list(self.budgets.values())[self.budget_select_start.selected_index]
        budget_id_end = list(self.budgets.keys())[self.budget_select_end.selected_index]
        budget_name_end = list(self.budgets.values())[self.budget_select_end.selected_index]

        self.master.switch_frame(FrameCategorySelectWithDropdown, budgets=((budget_id_start, budget_name_start), (budget_id_end, budget_name_end)))


class FrameCategorySelectWithDropdown(ctk.CTkScrollableFrame):
    def __init__(self, master, budgets):
        super().__init__(master, fg_color="transparent")

        self.category_groups = get_categories(YNAB_ACCESS_TOKEN, budgets[0][0])
        self.target_category_groups = get_categories(YNAB_ACCESS_TOKEN, budgets[1][0])

        self.target_categories = {"None":"None"}
        self.target_categories.update(category_groups_to_categories(self.target_category_groups))

        self.dropdown_vars = {}  # Dictionary to hold dropdown variables

        self.create_widgets()

    def create_widgets(self):
        for group_id, group_data in self.category_groups.items(): # Category Group Frames
            group_frame = ctk.CTkFrame(self)
            group_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            group_label = ctk.CTkLabel(group_frame, text=group_data['name'], font=ctk.CTkFont(size=14, weight="bold"))
            group_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            for category_id, category_name in group_data['categories'].items(): # Category Label & Dropdown Frames
                row_frame = ctk.CTkFrame(group_frame)
                row_frame.pack(fill="x", padx=20, pady=2)

                category_label = ctk.CTkLabel(row_frame, text=category_name)
                category_label.pack(side="left", fill="x", expand=True)

                var = tk.StringVar(value="Select target category")
                dropdown = ctk.CTkComboBox(
                    row_frame, 
                    variable=var,
                    values=self.target_categories,
                    width=200,
                )
                dropdown.pack(side="right", padx=10)
                self.dropdown_vars[category_id] = var

        submit_button = ctk.CTkButton(self, text="Submit", command=self.get_selected_migrations)
        submit_button.pack()

    def get_selected_migrations(self):
        selected_migrations = {}
        for category_id, var in self.dropdown_vars.items():
            if var.get() != ("Select target category") and (var.get() != "None"):
                selected_migrations[category_id] = self.target_categories[var.get()]
        print(selected_migrations)
        return selected_migrations


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")

        self.geometry("700x500")
        self.title("YNAB Category Migration")

        # Heading fonts
        self.font_h1 = ctk.CTkFont(size=32, weight="bold")
        self.font_h2 = ctk.CTkFont(size=24, weight="bold")
        self.font_h3 = ctk.CTkFont(size=20, weight="bold")
        self.font_h4 = ctk.CTkFont(size=16, weight="bold")
        self.font_h5 = ctk.CTkFont(size=14, weight="bold")
        self.font_h6 = ctk.CTkFont(size=12, weight="bold")

        self.label_welcome = ctk.CTkLabel(master=self, font=self.font_h1, text="Category Migration for YNAB")
        self.label_welcome.pack(pady=10)

        # Get YNAB API authentication key
        try:
            if os.path.exists("secrets.json"):
                with open("secrets.json", "r") as file:
                    file_dict = json.load(file)
                    if "ynab_access_token" in file_dict:
                        global YNAB_ACCESS_TOKEN
                        YNAB_ACCESS_TOKEN = file_dict['ynab_access_token']
                        if not verify_ynab_access_token(YNAB_ACCESS_TOKEN):
                            raise Exception
                        else:
                            display = FrameBudgetDisplay(self)
                            display.pack_propagate(False)
                            display.pack(pady=20)
                    else:
                        raise Exception
            else:
                raise Exception
        except: # No access token yet.
            FrameAuthentication(self).pack()

    def switch_frame(self, new_frame, **kwargs):
        for widget in self.winfo_children():
            widget.destroy()

        self.label_welcome = ctk.CTkLabel(master=self, font=self.font_h1, text="Category Migration for YNAB")
        self.label_welcome.pack(pady=10)

        display = new_frame(self, **kwargs)
        display.pack(fill="both", expand=True, padx=20, pady=20)


app = App()
app.mainloop()