import customtkinter  # type: ignore
from tkinter import StringVar


# Initialize the main app window
customtkinter.set_appearance_mode("System")  # Appearance: "Light", "Dark", or "System"
customtkinter.set_default_color_theme("blue")  # You can choose from "blue", "green", "dark-blue"


class ChatView(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)

        # Variables for Select Box and Input Box
        self.select_var = StringVar()
        self.entry_var = StringVar()

        # Scrollable frame for chat messages
        self.chat_frame = customtkinter.CTkScrollableFrame(self, height=450, width=760)
        self.chat_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # Select box for choosing chat option or user
        self.select_box = customtkinter.CTkComboBox(self, values=["User 1", "User 2", "User 3"], variable=self.select_var, width=150, height=40)
        self.select_box.grid(row=1, column=0, padx=5, pady=10, sticky="ew")

        # Input box to type messages
        self.input_box = customtkinter.CTkEntry(self, textvariable=self.entry_var, placeholder_text="Type a message...", width=460, height=40)
        self.input_box.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Send button
        self.send_button = customtkinter.CTkButton(self, text="Send", command=self.send_message, width=80, height=40)
        self.send_button.grid(row=1, column=2, padx=5, pady=10)

        # Configure grid layout to ensure proper expansion
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=0)

    def send_message(self):
        # Get selected user and typed message
        location = self.select_var.get()
        message = self.entry_var.get()

        # Only send if there is a message
        if message:
            self.add_message(message, "outgoing")
            self.add_message(message, "incoming")

            # Clear the input box after sending
            self.entry_var.set("")

    def add_message(self, message, msg_type):
        """ Adds a message to the chat frame with bubble styling. """
        if msg_type == "outgoing":
            bubble_color = "#ADD8E6"  # Light blue for outgoing
            anchor = "e"  # Align right
        else:
            bubble_color = "#90EE90"  # Light green for incoming
            anchor = "w"  # Align left

        # Create a message bubble (Label) inside the scrollable chat frame
        message_label = customtkinter.CTkLabel(self.chat_frame, text=message, fg_color=bubble_color, corner_radius=10, 
                                     width=750, anchor=anchor, justify="left", padx=10, pady=5, text_color="black")

        # Align the message either left or right based on incoming or outgoing
        message_label.grid(sticky=anchor, padx=5, pady=2)


class MyRenting(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame, for example:
        self.label = customtkinter.CTkLabel(self, text="My Renting")
        self.label.grid(row=0, column=0)


class MyItems(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame, for example:
        self.label = customtkinter.CTkLabel(self, text="My Items")
        self.label.grid(row=0, column=0)


class MyTabView(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.add("Chat")
        self.add("My Renting")
        self.add("My Items")

        self.chat_view = ChatView(self.tab("Chat"))
        self.my_renting = MyRenting(self.tab("My Renting"))
        self.my_items = MyItems(self.tab("My Items"))
        
        self.chat_view.grid(row=0, column=0)
        self.my_renting.grid(row=0, column=0)
        self.my_items.grid(row=0, column=0)
        


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("My App")

        self.geometry("800x600")
        # self.maxsize(height=800, width=800)
        # self.minsize(height=800, width=800)

        self.tab_view = MyTabView(master=self, width=780, height=780)
        self.tab_view.grid(row=0, column=0, padx=10, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
