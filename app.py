
import customtkinter as ctk
from tkinter import filedialog, Menu
from PIL import Image, ImageTk
import json
import os
import shutil
import uuid

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Shelf Mapper")
        self.geometry("1200x700")

        # Set color scheme
        ctk.set_appearance_mode("Light")  # Force light mode
        ctk.set_default_color_theme("blue")

        # Create main frame
        main_frame = ctk.CTkFrame(self, fg_color="#f0f2f5")
        main_frame.pack(fill="both", expand=True)

        # --- Top Bar ---
        top_bar = ctk.CTkFrame(main_frame, fg_color="#ffffff", height=60)
        top_bar.pack(fill="x", side="top")

        self.location_title = ctk.CTkLabel(top_bar, text="", font=("Arial", 24, "bold"))
        self.location_title.pack(side="left", padx=20, pady=10)

        self.add_item_button_top = ctk.CTkButton(top_bar, text="+ Add Item", command=self.add_item, width=120)
        self.add_item_button_top.pack(side="right", padx=20, pady=10)
        self.add_item_button_top.configure(state="disabled")

        # Create two panels
        self.locations_panel = ctk.CTkFrame(main_frame, width=280, fg_color="#ffffff")
        self.locations_panel.pack(side="left", fill="y", expand=False, pady=(0,10), padx=(10,5))

        self.items_panel = ctk.CTkFrame(main_frame, fg_color="#f0f2f5")
        self.items_panel.pack(side="right", fill="both", expand=True, pady=(0,10), padx=(5,10))

        # --- Locations Panel ---
        locations_label = ctk.CTkLabel(self.locations_panel, text="Shelf Mapper", font=("Arial", 20, "bold"))
        locations_label.pack(pady=20, padx=20, anchor="w")

        self.locations_list = ctk.CTkScrollableFrame(self.locations_panel, fg_color="#ffffff")
        self.locations_list.pack(fill="both", expand=True, padx=5, pady=5)

        add_location_frame = ctk.CTkFrame(self.locations_panel, fg_color="#ffffff")
        add_location_frame.pack(fill="x", pady=10, padx=10)

        self.add_location_button = ctk.CTkButton(add_location_frame, text="Add Location", command=self.add_location)
        self.add_location_button.pack(fill="x")

        # --- Items Panel ---
        self.items_list_frame = ctk.CTkScrollableFrame(self.items_panel, fg_color="#f0f2f5")
        self.items_list_frame.pack(fill="both", expand=True)

        # --- Empty State --- 
        self.empty_frame = ctk.CTkFrame(self.items_panel, fg_color="#ffffff")
        empty_label = ctk.CTkLabel(self.empty_frame, text="This location is empty", font=("Arial", 18))
        empty_label.pack(pady=(20, 5))
        empty_sublabel = ctk.CTkLabel(self.empty_frame, text="Add a new item to get started.", font=("Arial", 12), text_color="#888888")
        empty_sublabel.pack(pady=5)
        add_item_button_empty = ctk.CTkButton(self.empty_frame, text="+ Add Item", command=self.add_item)
        add_item_button_empty.pack(pady=20)

        # --- Data ---
        self.data = self.load_data()
        self.current_location = None
        self.populate_locations()
        self.show_empty_state()

    def load_data(self):
        if os.path.exists("data.json") and os.path.getsize("data.json") > 0:
            with open("data.json", "r") as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open("data.json", "w") as f:
            json.dump(self.data, f, indent=4)

    def populate_locations(self):
        for widget in self.locations_list.winfo_children():
            widget.destroy()

        for location in self.data.keys():
            self.create_location_widget(location)

    def create_location_widget(self, location):
        location_frame = ctk.CTkFrame(self.locations_list, fg_color="transparent")
        location_frame.pack(fill="x", pady=2, padx=10)

        btn = ctk.CTkButton(location_frame, text=location, command=lambda loc=location: self.select_location(loc), fg_color="transparent", text_color="#000000", hover_color="#f0f2f5", anchor="w")
        btn.pack(side="left", fill="x", expand=True)

        options_button = ctk.CTkButton(location_frame, text="...", width=30, fg_color="transparent", text_color="#000000", hover_color="#f0f2f5", font=("Arial", 16, "bold"), command=lambda loc=location, event=None: self.show_location_options(loc, event))
        options_button.pack(side="right")

    def show_location_options(self, location, event):
        menu = Menu(self, tearoff=0, bg="#ffffff", fg="#000000", activebackground="#e6f0ff", activeforeground="#000000", relief="flat", bd=5)
        menu.add_command(label="Edit", command=lambda: self.edit_location(location))
        menu.add_command(label="Delete", command=lambda: self.confirm_delete_location(location))
        menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def edit_location(self, old_name):
        dialog = ctk.CTkInputDialog(text="Enter new location name:", title="Edit Location")
        new_name = dialog.get_input()
        if new_name and new_name != old_name:
            self.data[new_name] = self.data.pop(old_name)
            self.save_data()
            self.populate_locations()
            if self.current_location == old_name:
                self.select_location(new_name)

    def confirm_delete_location(self, location):
        self.show_delete_confirmation("Are you sure?", f"This will permanently delete the location '{location}' and all its items.", lambda: self.delete_location(location))

    def delete_location(self, location):
        del self.data[location]
        self.save_data()
        self.populate_locations()
        if self.current_location == location:
            self.current_location = None
            self.location_title.configure(text="")
            self.add_item_button_top.configure(state="disabled")
            self.show_empty_state()

    def select_location(self, location):
        self.current_location = location
        self.location_title.configure(text=location)
        self.add_item_button_top.configure(state="normal")
        self.populate_items()

    def add_location(self):
        dialog = ctk.CTkInputDialog(text="Enter location name:", title="Add Location")
        location_name = dialog.get_input()
        if location_name:
            if location_name not in self.data:
                self.data[location_name] = []
                self.save_data()
                self.populate_locations()
                self.select_location(location_name)

    def populate_items(self):
        for widget in self.items_list_frame.winfo_children():
            widget.destroy()

        if self.current_location and self.data[self.current_location]:
            self.hide_empty_state()
            for i, item in enumerate(self.data[self.current_location]):
                self.create_item_widget(item, i)
        else:
            self.show_empty_state()

    def show_empty_state(self):
        self.items_list_frame.pack_forget()
        self.empty_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def hide_empty_state(self):
        self.empty_frame.pack_forget()
        self.items_list_frame.pack(fill="both", expand=True)

    def create_item_widget(self, item, index):
        item_frame = ctk.CTkFrame(self.items_list_frame, fg_color="#ffffff", corner_radius=10)
        item_frame.grid(row=index // 3, column=index % 3, padx=10, pady=10, sticky="nsew")
        self.items_list_frame.grid_columnconfigure(index % 3, weight=1)

        

        # --- Content ---
        top_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10,0))

        item_name_label = ctk.CTkLabel(top_frame, text=item["name"], font=("Arial", 16, "bold"))
        item_name_label.pack(side="left", anchor="w")

        options_button = ctk.CTkButton(top_frame, text="...", width=30, fg_color="transparent", text_color="#000000", hover_color="#f0f2f5", font=("Arial", 16, "bold"), command=lambda i=item, event=None: self.show_item_options(i, event))
        options_button.pack(side="right")

        id_label = ctk.CTkLabel(item_frame, text=f"ID: {item['id']}", font=("Arial", 10), text_color="#888888")
        id_label.pack(anchor="w", padx=10)

        img_label_frame = ctk.CTkFrame(item_frame, fg_color="#e0e0e0", height=200)
        img_label_frame.pack(fill="x", padx=10, pady=10)
        img_label_frame.pack_propagate(False)

        img_label = ctk.CTkLabel(img_label_frame, text="")
        img_label.pack(expand=True, fill="both")

        def add_image_to_item():
            image_path = filedialog.askopenfilename(title="Select Image", filetypes=(("Image Files", "*.png *.jpg *.jpeg"),))
            if image_path:
                new_image_path = os.path.join("images", os.path.basename(image_path))
                shutil.copy(image_path, new_image_path)
                item["image_path"] = new_image_path
                self.save_data()
                self.update_item_image(img_label, new_image_path)

        img_label.bind("<Button-1>", lambda e: add_image_to_item())

        if item.get("image_path") and os.path.exists(item["image_path"]):
            self.update_item_image(img_label, item["image_path"])
        else:
            img_label.configure(text="600x400") # Placeholder text

        checkbox_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=10, pady=10)

        available_var = ctk.StringVar(value="Available" if item.get("available") else "Not Available")

        def on_check(value):
            item["available"] = (value == "Available")
            self.save_data()

        available_check = ctk.CTkRadioButton(checkbox_frame, text="Available", variable=available_var, value="Available", command=lambda: on_check("Available"))
        available_check.pack(side="left")

        not_available_check = ctk.CTkRadioButton(checkbox_frame, text="Not Available", variable=available_var, value="Not Available", command=lambda: on_check("Not Available"))
        not_available_check.pack(side="left", padx=10)

    def show_item_options(self, item, event):
        menu = Menu(self, tearoff=0, bg="#ffffff", fg="#000000", activebackground="#e6f0ff", activeforeground="#000000", relief="flat", bd=5)
        menu.add_command(label="Edit", command=lambda: self.edit_item(item))
        menu.add_command(label="Delete", command=lambda: self.confirm_delete_item(item))
        menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def edit_item(self, item):
        dialog = ctk.CTkInputDialog(text="Enter new item name:", title="Edit Item")
        new_name = dialog.get_input()
        if new_name:
            item["name"] = new_name
            self.save_data()
            self.populate_items()

    def confirm_delete_item(self, item):
        self.show_delete_confirmation("Are you sure?", f"This will permanently delete the item '{item['name']}'.", lambda: self.delete_item(item))

    def delete_item(self, item_to_delete):
        if self.current_location:
            if item_to_delete.get("image_path") and os.path.exists(item_to_delete["image_path"]):
                os.remove(item_to_delete["image_path"])

            self.data[self.current_location] = [item for item in self.data[self.current_location] if item["id"] != item_to_delete["id"]]
            self.save_data()
            self.populate_items()

    def update_item_image(self, img_label, image_path):
        try:
            img = Image.open(image_path)
            img.thumbnail((600, 400))
            photo = ImageTk.PhotoImage(img)
            img_label.configure(image=photo, text="")
            img_label.image = photo
        except Exception as e:
            print(f"Error loading image: {e}")
            img_label.configure(text="Image Error")

    def add_item(self):
        if not self.current_location:
            return

        dialog = ctk.CTkInputDialog(text="Enter item name:", title="Add Item")
        item_name = dialog.get_input()
        if item_name:
            new_item = {"id": str(uuid.uuid4())[:8], "name": item_name, "available": True, "image_path": ""}
            self.data[self.current_location].append(new_item)
            self.save_data()
            self.populate_items()

    def show_delete_confirmation(self, title, message, command):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()

        dialog.lift()
        dialog.attributes("-topmost", True)

        main_frame = ctk.CTkFrame(dialog, fg_color="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(main_frame, text=title, font=("Arial", 18, "bold"))
        title_label.pack(pady=(10,5))

        message_label = ctk.CTkLabel(main_frame, text=message, wraplength=360)
        message_label.pack(pady=10)

        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        def on_confirm():
            command()
            dialog.destroy()

        cancel_button = ctk.CTkButton(button_frame, text="No, cancel", command=dialog.destroy, fg_color="#e0e0e0", text_color="#000000", hover_color="#c0c0c0")
        cancel_button.pack(side="left", padx=10)

        confirm_button = ctk.CTkButton(button_frame, text="Yes, I'm sure", command=on_confirm, fg_color="#ff4d4d", hover_color="#cc0000")
        confirm_button.pack(side="right", padx=10)

        # Animate the dialog
        dialog.attributes("-alpha", 0.0)
        dialog.after(50, lambda: dialog.attributes("-alpha", 1.0))

    def animate_slide_in(self, widget, start_y, end_y):
        pos_y = start_y
        def step():
            nonlocal pos_y
            if pos_y > end_y:
                pos_y -= 5
                widget.place(y=pos_y)
                self.after(10, step)
            else:
                widget.place(y=end_y)
        step()

if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")
    app = App()
    app.mainloop()
