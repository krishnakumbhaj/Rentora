import customtkinter  # type: ignore
from tkinter import StringVar
from utils import *
from models import *
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Literal
from tkinter import filedialog


load_dotenv()

# Initialize the main app window
# Appearance: "Light", "Dark", or "System"
customtkinter.set_appearance_mode("System")
# You can choose from "blue", "green", "dark-blue"
customtkinter.set_default_color_theme("blue")


class UserQuery(BaseModel):
    item_category: Literal["wearable", "transport", "electronic", "furniture",
                           "other"] = Field(..., description="The category of the item to query")


class RentView(customtkinter.CTkFrame):
    def __init__(self, master, id, item, user, agent, location, callback, reload, **kwargs):
        super().__init__(master, **kwargs)

        self.item = item
        self.user = user
        self.activation_callback = callback
        self.id = id
        self.reload = reload

        self.agent_address = agent
        self.agent_location = location

        self.image = decode_image(item.image)
        self.image_label = customtkinter.CTkLabel(
            self, image=self.image, text="")
        self.image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display the item name
        self.name_label = customtkinter.CTkLabel(
            self, text=f"Name: {item.name}", font=("Arial", 18, "bold"))

        self.name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")


        if item.period == 1:
            period = "hour"
        elif item.period == 24:
            period = "day"
        elif item.period == 24 * 7:
            period = "week"
        elif item.period == 24 * 30:
            period = "month"
        elif item.period == 24 * 365:
            period = "year"

        # Display the item price
        self.price_label = customtkinter.CTkLabel(
            self, text=f"Price: ₹{item.price:.2f}/{period}", font=("Arial", 14))
        self.price_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Display the item category
        self.category_label = customtkinter.CTkLabel(
            self, text=f"Category: {item.category}", font=("Arial", 14))
        self.category_label.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the item description
        self.description_label = customtkinter.CTkLabel(self, text=f"Description: {
                                                        item.description}", font=("Arial", 12), wraplength=300, justify="left")
        self.description_label.grid(
            row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the user name
        self.user_label = customtkinter.CTkLabel(
            self, text=f"User: {user['name']}", font=("Arial", 14))
        self.user_label.grid(
            row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the user phone
        self.user_phone = customtkinter.CTkLabel(
            self, text=f"Phone No.: {user['phone']}", font=("Arial", 14))
        self.user_phone.grid(
            row=5, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the user email
        self.user_email = customtkinter.CTkLabel(
            self, text=f"Email: {user['email']}", font=("Arial", 14))
        self.user_email.grid(
            row=6, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the user address
        self.user_address = customtkinter.CTkLabel(
            self, text=f"Address: {user['address']['area']}, {user['address']['city']}", font=("Arial", 14))
        self.user_address.grid(
            row=7, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Rent Button
        self.rent_button = customtkinter.CTkButton(
            self, text="Rent Item", command=self.rent)
        self.rent_button.grid(row=8, column=0, columnspan=1, padx=10, pady=10)

        # cancel Button
        self.cancel_button = customtkinter.CTkButton(
            self, text="Cancel", command=self.cancel)
        self.cancel_button.grid(
            row=8, column=1, columnspan=1, padx=10, pady=10)

    def rent(self):
        sync_query(
            destination=self.id, message=HandOverRequest(item=self.item, agent=self.agent_address))
        sync_query(
            destination=self.agent_address, message=RequestedItem(item=self.item))
        request = DeleteRequest(
            name=self.item.name, category=self.item.category, agent_address=self.id)
        sync_query(destination=self.agent_location, message=request)
        print("Item rented successfully")
        self.grid_forget()
        self.reload()

    def cancel(self):
        self.grid_forget()
        self.activation_callback()


class ChatCard(customtkinter.CTkFrame):
    def __init__(self, master, item: Item, id, callback, agent, location, reload, **kwargs):
        super().__init__(master, **kwargs)

        # Item details passed in from the `Item` class
        self.item = item
        self.id = id
        self.activation_callback = callback
        self.agent_location = location
        self.agent_address = agent
        self.reload = reload

        self.image = decode_image(item.image)
        self.image_label = customtkinter.CTkLabel(
            self, image=self.image, text="")
        self.image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display the item name
        self.name_label = customtkinter.CTkLabel(
            self, text=f"Name: {item.name}", font=("Arial", 18, "bold"))
        self.name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")


        if item.period == 1:
            period = "hour"
        elif item.period == 24:
            period = "day"
        elif item.period == 24 * 7:
            period = "week"
        elif item.period == 24 * 30:
            period = "month"
        elif item.period == 24 * 365:
            period = "year"

        # Display the item price
        self.price_label = customtkinter.CTkLabel(
            self, text=f"Price: ₹{item.price:.2f}/{period}", font=("Arial", 14))
        self.price_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Display the item category
        self.category_label = customtkinter.CTkLabel(
            self, text=f"Category: {item.category}", font=("Arial", 14))
        self.category_label.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the item description
        self.description_label = customtkinter.CTkLabel(self, text=f"Description: {
                                                        item.description}", font=("Arial", 12), wraplength=300, justify="left")
        self.description_label.grid(
            row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Rent Button
        self.rent_button = customtkinter.CTkButton(
            self, text="View Item", command=self.retrive)
        self.rent_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def retrive(self):
        data = sync_query(self.id, ItemRequest(name=self.item.name))

        if not data:
            print("Unable to connect to agent")
            return

        if data["status"]:
            item_info = data["content"]
            userinfo = data["content"][1]
            item = Item(**item_info[0])

            self.rent_view = RentView(
                self, self.id, item, userinfo, self.agent_address, self.agent_location, self.activation_callback, self.reload)
            self.rent_view.grid(row=5, column=0)

        else:
            print("Item not found")
            return


class ChatView(customtkinter.CTkFrame):
    def __init__(self, master, agent_address, agent_location, reload, **kwargs):
        super().__init__(master=master, **kwargs)

        model = ChatGoogleGenerativeAI(model="gemini-pro")

        parser = JsonOutputParser(pydantic_object=UserQuery)

        prompt = PromptTemplate(
            template="Parse the user's input into required format.\n{format_instructions}\n{query}",
            input_variables=["query"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()},
        )

        self.last_response = "No previous response"
        self.last_query = "No previous query"

        self.agent_location = agent_location
        self.agent_address = agent_address
        self.reload = reload

        self.chain = prompt | model | parser

        # Variables for Select Box and Input Box
        self.select_var = StringVar()
        self.entry_var = StringVar()

        # Scrollable frame for chat messages
        self.chat_frame = customtkinter.CTkScrollableFrame(
            self, height=450, width=760)
        self.chat_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")

        # Select box for choosing chat option or user
        self.select_box = customtkinter.CTkComboBox(self, values=[
                                                    "User 1", "User 2", "User 3"], variable=self.select_var, width=150, height=40)
        self.select_box.grid(row=1, column=0, padx=5, pady=10, sticky="ew")

        # Input box to type messages
        self.input_box = customtkinter.CTkEntry(
            self, textvariable=self.entry_var, placeholder_text="Type a message...", width=460, height=40)
        self.input_box.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Send button
        self.send_button = customtkinter.CTkButton(
            self, text="Send", command=self.send_message, width=80, height=40)
        self.send_button.grid(row=1, column=2, padx=5, pady=10)

        # Configure grid layout to ensure proper expansion
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=0)

    def send_message(self):
        message = self.entry_var.get()

        # Only send if there is a message
        if message:

            self.add_message(message, "outgoing")

            query = self.chain.invoke({"query": message})

            print(query)

            if query["item_category"] == "other":
                self.add_message(
                    "Sorry, We don't have this type of item in stock.", "incoming")
                return

            # sync_query to the to self.agent_location

            history = f"Last Query: {
                self.last_query}\n Last Response: {self.last_response}"

            data = sync_query(self.agent_location, SearchRequest(
                category=query["item_category"], query=message, history=history))

            print(data)

            if not data:
                self.add_message("Unable to connect to location", "incoming")
                return

            self.add_message(data["response"], "incoming")

            for item in data["items"]:
                self.add_item(item[0], Item.model_validate(item[1]))

            # Clear the input box after sending
            self.last_query = message
            self.last_response = data
            self.entry_var.set("")

    def add_item(self, id, item):
        """ Adds an item to the chat frame with bubble styling. """
        item_card = ChatCard(self.chat_frame, item, id, self.activation_callback,
                             agent=self.agent_address, location=self.agent_location, reload=self.reload)
        item_card.grid(sticky="w", padx=5, pady=2)

    def activation_callback(self):
        self.grid(row=0, column=0)

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


class MyRentingsItem(customtkinter.CTkFrame):
    def __init__(self, master, item: Item, owner, payment_id, agent, location, reload, **kwargs):
        super().__init__(master, **kwargs)

        self.item = item
        self.agent = agent
        self.owner = owner
        self.location = location
        self.reload = reload
        self.payment_id = payment_id

        self.image = decode_image(item.image)
        self.image_label = customtkinter.CTkLabel(
            self, image=self.image, text="")
        self.image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display the item name
        self.name_label = customtkinter.CTkLabel(
            self, text=f"Name: {item.name}", font=("Arial", 18, "bold"))
        self.name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")


        if item.period == 1:
            period = "hour"
        elif item.period == 24:
            period = "day"
        elif item.period == 24 * 7:
            period = "week"
        elif item.period == 24 * 30:
            period = "month"
        elif item.period == 24 * 365:
            period = "year"

        # Display the item price
        self.price_label = customtkinter.CTkLabel(
            self, text=f"Price: ₹{item.price:.2f}/{period}", font=("Arial", 14))
        self.price_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Display the item category
        self.category_label = customtkinter.CTkLabel(
            self, text=f"Category: {item.category}", font=("Arial", 14))
        self.category_label.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the item description
        self.description_label = customtkinter.CTkLabel(self, 
            text=f"Description: {item.description}", font=("Arial", 12), wraplength=300, justify="left")
        self.description_label.grid(
            row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # code entry
        self.code_var = StringVar()
        self.code_entry = customtkinter.CTkEntry(
            self, textvariable=self.code_var, placeholder_text="Enter code...", width=150, height=40)

        self.code_entry.grid(row=4, column=0, padx=5, pady=10)
        # Rent Button
        self.rent_button = customtkinter.CTkButton(
            self, text="Confirm Handover", command=self.handover)
        self.rent_button.grid(row=4, column=1, padx=10, pady=10)

    def handover(self):
        code = self.code_var.get()

        status = sync_query(
            destination=self.owner, message=HandOverEnd(item=self.item, code=code))

        if not status:
            print("Unable to connect to agent")
            return

        if status["status"]:
            status = sync_query(
                destination=self.agent, message=HandOverEndConfirm(item=self.item))

            if not status:
                print("Error: Unable to handover item")
                return

            if status["status"]:

                central_agent_data = get_agents("central_agent")

                print(central_agent_data)

                sync_query(
                    destination=central_agent_data.agent_address, message=PaymentCancel(id=self.payment_id)
                )

                status = sync_query(self.location, AddRequest(item=self.item, agent_address=self.owner))

                if not status:
                    print("Error: Unable to handover item")
                    return
                
                if status["status"]:

                    print("Item handed over successfully")
                    self.grid_forget()
                    self.reload()

                else:
                    print("Error: Unable to handover item")
                    print(status["content"])

            else:
                print("Error: Unable to handover item")
                print(status["content"])

        else:
            print("Error: Unable to handover item")
            print(status["content"])

            return


class MyRenting(customtkinter.CTkFrame):
    def __init__(self, master, agent_address, location, rents, reload, **kwargs):
        super().__init__(master, **kwargs)

        self.agent_address = agent_address

        self.reload = reload

        self.rents = rents

        self.scrollable_frame = customtkinter.CTkScrollableFrame(
            self, height=450, width=760)

        self.scrollable_frame.grid(
            row=0, column=0, columnspan=3, sticky="nsew")

        for i, rent in enumerate(rents):
            rent_view = MyRentingsItem(
                self.scrollable_frame, rent[0], rent[1], rent[2], agent_address, location, reload=reload)
            rent_view.grid(row=i, column=0, padx=10, pady=10)


class ItemCard(customtkinter.CTkFrame):
    def __init__(self, master, item: Item, location, agent, message, reload, **kwargs):
        super().__init__(master, **kwargs)

        # Item details passed in from the `Item` class
        self.item = item
        self.agent_location = location
        self.agent = agent
        self.message = message
        self.reload = reload

        self.image = decode_image(item.image)
        self.image_label = customtkinter.CTkLabel(
            self, image=self.image, text="")
        self.image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display the item name
        self.name_label = customtkinter.CTkLabel(
            self, text=f"Name: {item.name}", font=("Arial", 18, "bold"))
        self.name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")


        if item.period == 1:
            period = "hour"
        elif item.period == 24:
            period = "day"
        elif item.period == 24 * 7:
            period = "week"
        elif item.period == 24 * 30:
            period = "month"
        elif item.period == 24 * 365:
            period = "year"

        # Display the item price
        self.price_label = customtkinter.CTkLabel(
            self, text=f"Price: ₹{item.price:.2f}/{period}", font=("Arial", 14))
        self.price_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Display the item category
        self.category_label = customtkinter.CTkLabel(
            self, text=f"Category: {item.category}", font=("Arial", 14))
        self.category_label.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the item description
        self.description_label = customtkinter.CTkLabel(self, text=f"Description: {
                                                        item.description}", font=("Arial", 12), wraplength=300, justify="left")
        self.description_label.grid(
            row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Rent Button
        self.rent_button = customtkinter.CTkButton(
            self, text="Delete Item", command=self.delete_item)
        self.rent_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def delete_item(self):

        request = DeleteRequest(
            name=self.item.name, category=self.item.category, agent_address=self.agent)

        status = sync_query(
            destination=self.agent_location, message=request)

        if not status:
            self.message.configure(text="Unable to connect to location")
            print("unable to connect to location")
            return

        if status["status"]:
            status = sync_query(
                destination=self.agent, message=request)

            if not status:
                self.message.configure(
                    text="Error: Unable to delete item from agent")
                print(status["content"])
                return

            if status["status"]:
                self.message.configure(text="Item deleted successfully.")
                # print(status["content"])
                self.grid_forget()
                self.reload()

            else:
                self.message.configure(
                    text="Error: Unable to delete item from agent.")
                print(status["content"])

        else:
            self.message.configure(
                text="Error: Unable to delete item from city")
            print(status["content"])

            return


class ItemList(customtkinter.CTkFrame):
    def __init__(self, master, items, agent, location, message, reload, **kwargs):
        super().__init__(master, **kwargs)

        self.items = items
        self.agent = agent
        self.agent_location = location
        self.message = message
        self.reload = reload

        # Create a list of `ItemCard` widgets for each item
        for i, item in enumerate(items):
            item_card = ItemCard(
                self, item, location=self.agent_location, agent=self.agent, message=self.message, reload=reload)
            item_card.grid(row=i, column=0, padx=10, pady=10)


class NavigationBar(customtkinter.CTkFrame):
    def __init__(self, master, heading, callback_text, callback, **kwargs):
        super().__init__(master, **kwargs)

        self.heading_label = customtkinter.CTkLabel(
            self, text=heading, font=("Arial", 18, "bold"))
        self.heading_label.grid(row=0, column=0, padx=10, pady=10)

        self.callback_button = customtkinter.CTkButton(
            self, text=callback_text, command=callback)
        self.callback_button.grid(row=0, column=1, padx=10, pady=10)


class AddItem(customtkinter.CTkFrame):
    def __init__(self, master, agent_address, location, callback, reload, **kwargs):
        super().__init__(master, **kwargs)

        self.agent_address = agent_address
        self.agent_location = location
        self.callback = callback
        self.reload = reload

        self.navbar = NavigationBar(self, "Add Item", "Submit", self.submit)
        self.navbar.grid(row=0, column=0)

        # add widgets onto the frame, for example:
        self.item_name_var = StringVar()
        self.item_price_var = StringVar()
        self.item_period_var = StringVar()
        self.item_image_var = StringVar()
        self.item_category_var = StringVar()
        self.item_description_var = StringVar()

        self.item_name_label = customtkinter.CTkLabel(
            self, text="Item Name", width=20, height=40)
        self.item_name_label.grid(row=1, column=0, padx=5, pady=10)

        self.item_name_entry = customtkinter.CTkEntry(
            self, textvariable=self.item_name_var, placeholder_text="Enter item name...", width=150, height=40)
        self.item_name_entry.grid(row=1, column=1, padx=5, pady=10)

        self.item_price_label = customtkinter.CTkLabel(
            self, text="Item Price", width=20, height=40)
        self.item_price_label.grid(row=2, column=0, padx=5, pady=10)

        self.item_price_entry = customtkinter.CTkEntry(
            self, textvariable=self.item_price_var, placeholder_text="Enter item price...", width=150, height=40)
        self.item_price_entry.grid(row=2, column=1, padx=5, pady=10)

        self.item_period_label = customtkinter.CTkLabel(
            self, text="Payment Frequency", width=20, height=40)
        self.item_period_label.grid(row=3, column=0, padx=5, pady=10)

        self.item_period_entry = customtkinter.CTkComboBox(
            self, values=["hourly", "daily", "weekly", "monthly", "yearly"], variable=self.item_period_var, width=150, height=40)
        self.item_period_entry.grid(row=3, column=1, padx=5, pady=10)

        self.item_image_label = customtkinter.CTkLabel(
            self, text="Item Image", width=20, height=40)
        self.item_image_label.grid(row=4, column=0, padx=5, pady=10)

        self.item_image_button = customtkinter.CTkButton(
            self, text="Select Image", command=self.select_image, width=150, height=40)
        self.item_image_button.grid(row=4, column=1, padx=5, pady=10)

        self.item_category_label = customtkinter.CTkLabel(
            self, text="Item Category", width=20, height=40)

        self.item_category_label.grid(row=5, column=0, padx=5, pady=10)

        self.item_category_entry = customtkinter.CTkComboBox(
            self, values=["wearable", "transport", "electronic", "furniture", "other"], variable=self.item_category_var, width=150, height=40)
        self.item_category_entry.grid(row=5, column=1, padx=5, pady=10)

        self.item_description_label = customtkinter.CTkLabel(
            self, text="Item Description", width=20, height=40)
        self.item_description_label.grid(row=6, column=0, padx=5, pady=10)

        self.item_description_entry = customtkinter.CTkEntry(
            self, textvariable=self.item_description_var, placeholder_text="Enter item description...", width=150, height=40)
        self.item_description_entry.grid(row=6, column=1, padx=5, pady=10)

        self.message = customtkinter.CTkLabel(
            self, text="", width=150, height=40)
        self.message.grid(row=7, column=1, padx=5, pady=10)

        self.submit_button = customtkinter.CTkButton(
            self, text="Submit", command=self.submit, width=80, height=40)
        self.submit_button.grid(row=8, column=1, padx=5, pady=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;")]
        )
        if file_path:
            self.item_image_var.set(file_path)

    def submit(self):
        item_name = self.item_name_var.get()
        item_price = self.item_price_var.get()
        item_period = self.item_period_var.get()
        item_image = self.item_image_var.get()
        item_category = self.item_category_var.get()
        item_description = self.item_description_var.get()

        if not item_name:
            self.message.configure(text="Item name is required")
            return

        if not item_price:
            self.message.configure(text="Item price is required")
            return
        else:
            try:
                float(item_price)
            except ValueError:
                self.message.configure(text="Invalid price")
                return

        if not item_period:
            self.message.configure(text="Item period is required")
            return
        else:
            if item_period not in ["hourly", "daily", "weekly", "monthly", "yearly"]:
                self.message.configure(text="Invalid period")
                return

        if not item_image:
            self.message.configure(text="Item image is required")
            return

        if not item_category:
            self.message.configure(text="Item category is required")
            return
        else:
            if item_category not in ["wearable", "transport", "electronic", "furniture", "other"]:
                self.message.configure(text="Invalid category")
                return

        if not item_description:
            self.message.configure(text="Item description is required")
            return

        with open(item_image, 'rb') as f:
            image = f.read()
            encoded_image = encode_image(image=image)

        self.callback()

        if item_period == "hourly":
            payment_period = 1
        elif item_period == "daily":
            payment_period = 24
        elif item_period == "weekly":
            payment_period = 24 * 7
        elif item_period == "monthly":
            payment_period = 24 * 30
        elif item_period == "yearly":
            payment_period = 24 * 365

        item = Item(name=item_name, price=float(item_price), period=payment_period,
                    image=encoded_image, category=item_category, description=item_description)

        status = sync_query(
            destination=self.agent_location, message=AddRequest(item=item, agent_address=self.agent_address))

        if not status:
            self.message.configure(text="Unable to connect to agent")
            return

        if status["status"]:
            status = sync_query(
                destination=self.agent_address, message=item)

            if not status:
                self.message.configure(
                    text="Error: Unable to add item to agent")
                return

            if status["status"]:
                status = sync_query(
                    destination=self.agent_address, message=ItemRequest(name=None))

                if not status:
                    self.message.configure(
                        text="Error: Unable to add item to agent")
                    return

                if status["status"]:
                    items = []
                    for item in status["content"]:
                        items.append(Item(**item))

                    self.callback(True, items)
                    self.reload()

                else:
                    self.callback(False, "Unable to fetch new items.")

            else:
                self.message.configure(
                    text="Error: Unable to add item to agent")
                return

        else:
            self.message.configure(text="Error: Unable to add item to city")
            return


class RequestedItemView(customtkinter.CTkFrame):
    def __init__(self, master, item: Item, code, **kwargs):
        super().__init__(master, **kwargs)

        self.item = item

        self.image = decode_image(item.image)
        self.image_label = customtkinter.CTkLabel(
            self, image=self.image, text="")

        self.image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display the item name
        self.name_label = customtkinter.CTkLabel(
            self, text=f"Name: {item.name}", font=("Arial", 18, "bold"))

        self.name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")


        if item.period == 1:
            period = "hour"
        elif item.period == 24:
            period = "day"
        elif item.period == 24 * 7:
            period = "week"
        elif item.period == 24 * 30:
            period = "month"
        elif item.period == 24 * 365:
            period = "year"

        # Display the item price
        self.price_label = customtkinter.CTkLabel(
            self, text=f"Price: ₹{item.price:.2f}/{period}", font=("Arial", 14))
        self.price_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Display the item category
        self.category_label = customtkinter.CTkLabel(
            self, text=f"Category: {item.category}", font=("Arial", 14))

        self.category_label.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the item description
        self.description_label = customtkinter.CTkLabel(self, text=f"Description: {
                                                        item.description}", font=("Arial", 12), wraplength=300, justify="left")
        self.description_label.grid(
            row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.code_label = customtkinter.CTkLabel(
            self, text=f"Code: {code}", font=("Arial", 14))

        self.code_label.grid(row=4, column=0, columnspan=2,
                             padx=10, pady=5, sticky="w")


class MyItems(customtkinter.CTkFrame):
    def __init__(self, master, agent_address, location, items, message, reload, **kwargs):
        super().__init__(master, **kwargs)

        self.agent_address = agent_address
        self.agent_location = location
        self.message = message
        self.reload = reload

        self.list_navbar = NavigationBar(
            self, "My Items 1", "Add Item", self.add_item)
        self.list_navbar.grid(row=0, column=0)

        self.add_navbar = NavigationBar(
            self, "My Items 2", "Cancel", self.cancel_add)

        # add widgets onto the frame, for example:
        self.item_list = ItemList(
            self, items, self.agent_address, self.agent_location, self.message, reload=reload)
        self.item_list.grid(row=1, column=0)

    def add_item(self):

        self.list_navbar.grid_forget()
        self.add_navbar.grid(row=0, column=0)

        self.item_list.grid_forget()
        self.add_item_view = AddItem(
            self, self.agent_address, self.agent_location, self.cancel_add, reload=self.reload)
        self.add_item_view.grid(row=1, column=0)

    def cancel_add(self, status=False, items=None):
        self.add_navbar.grid_forget()
        self.add_item_view.grid_forget()

        self.list_navbar.grid(row=0, column=0)

        if status:
            self.item_list = ItemList(
                self, items, self.agent_address, self.agent_location, self.message, reload=self.reload)

        self.item_list.grid(row=1, column=0)


class HandOverItem(customtkinter.CTkFrame):
    def __init__(self, master, item, address, id, reload, **kwargs):
        super().__init__(master, **kwargs)

        self.item = item
        self.address = address
        self.id = id
        self.reload = reload

        self.image = decode_image(item.image)
        self.image_label = customtkinter.CTkLabel(
            self, image=self.image, text="")
        self.image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display the item name
        self.name_label = customtkinter.CTkLabel(
            self, text=f"Name: {item.name}", font=("Arial", 18, "bold"))
        self.name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")


        if item.period == 1:
            period = "hour"
        elif item.period == 24:
            period = "day"
        elif item.period == 24 * 7:
            period = "week"
        elif item.period == 24 * 30:
            period = "month"
        elif item.period == 24 * 365:
            period = "year"

        # Display the item price
        self.price_label = customtkinter.CTkLabel(
            self, text=f"Price: ₹{item.price:.2f}/{period}", font=("Arial", 14))
        self.price_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Display the item category
        self.category_label = customtkinter.CTkLabel(
            self, text=f"Category: {item.category}", font=("Arial", 14))
        self.category_label.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the item description
        self.description_label = customtkinter.CTkLabel(self, text=f"Description: {item.description}", font=("Arial", 12), wraplength=300, justify="left")
        self.description_label.grid(
            row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.code = StringVar()

        self.address_input = customtkinter.CTkEntry(
            self, textvariable=self.code, placeholder_text="Enter code...", width=150, height=40)
        self.address_input.grid(
            row=4, column=0, columnspan=2, padx=10, pady=10)

        self.handover_button = customtkinter.CTkButton(
            self, text="Hand Over", command=self.handover)

        self.handover_button.grid(
            row=5, column=0, columnspan=2, padx=10, pady=10)

    def handover(self):
        code = self.code.get()

        if not code:
            print("Code is required")
            return
        
        
        
        to_wallet = sync_query(destination=self.address, message=WalletRequest(any=None))["content"]
        amount = self.item.price
        frequency = self.item.period

        central_agent_data = get_agents("central_agent")

        payment_request = PaymentRequest(
            from_address=self.id,
            to_address=to_wallet,
            amount=amount,
            frequency=frequency
        )

        payment_response = sync_query(destination=central_agent_data.agent_address, message=payment_request)["content"]


        sync_query(
            destination=self.address, message=RentConfirmRequest(item=self.item, code=code, agent=self.id, payment_id=payment_response))
        sync_query(
            destination=self.id, message=handOverConfirm(item=self.item))

        self.grid_forget()
        self.reload()

class Rented_Item(customtkinter.CTkFrame):
    def __init__(self, master, item, code, **kwargs):
        super().__init__(master, **kwargs)

        self.item = item
        self.code = code

        self.image = decode_image(item.image)
        self.image_label = customtkinter.CTkLabel(
            self, image=self.image, text="")
        self.image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display the item name
        self.name_label = customtkinter.CTkLabel(
            self, text=f"Name: {item.name}", font=("Arial", 18, "bold"))
        self.name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    

        if item.period == 1:
            period = "hour"
        elif item.period == 24:
            period = "day"
        elif item.period == 24 * 7:
            period = "week"
        elif item.period == 24 * 30:
            period = "month"
        elif item.period == 24 * 365:
            period = "year"

        # Display the item price
        self.price_label = customtkinter.CTkLabel(
            self, text=f"Price: ₹{item.price:.2f}/{period}", font=("Arial", 14))
        self.price_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Display the item category
        self.category_label = customtkinter.CTkLabel(
            self, text=f"Category: {item.category}", font=("Arial", 14))
        self.category_label.grid(
            row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display the item description
        self.description_label = customtkinter.CTkLabel(self, text=f"Description: {
                                                        item.description}", font=("Arial", 12), wraplength=300, justify="left")
        self.description_label.grid(
            row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.address_label = customtkinter.CTkLabel(
            self, text=f"Code: {code}", font=("Arial", 14))
        self.address_label.grid(
            row=4, column=0, columnspan=2, padx=10, pady=5, sticky="w")


class RentedView(customtkinter.CTkFrame):
    def __init__(self, master, rented, reload, **kwargs):
        super().__init__(master, **kwargs)

        # reload button
        self.reload_button = customtkinter.CTkButton(
            self, text="Reload", command=reload)
        self.reload_button.grid(row=0, column=0, padx=10, pady=10)

        self.view = customtkinter.CTkScrollableFrame(
            self, height=450, width=760)
        self.view.grid(row=1, column=0)

        for i, item in enumerate(rented):
            item_card = Rented_Item(self.view, item[0], item[1])
            item_card.grid(row=i, column=0, padx=10, pady=10)


class RequestedView(customtkinter.CTkFrame):
    def __init__(self, master, requested, reload, **kwargs):
        super().__init__(master, **kwargs)

        # reload button
        self.reload_button = customtkinter.CTkButton(
            self, text="Reload", command=reload)
        self.reload_button.grid(row=0, column=0, padx=10, pady=10)

        self.view = customtkinter.CTkScrollableFrame(
            self, height=450, width=760)
        self.view.grid(row=1, column=0)

        for i, item in enumerate(requested):
            item_card = RequestedItemView(self.view, item[0], item[1])
            item_card.grid(row=i, column=0, padx=10, pady=10)


class HandOverView(customtkinter.CTkFrame):
    def __init__(self, master, handover, id, reload, **kwargs):
        super().__init__(master, **kwargs)

        self.view = customtkinter.CTkScrollableFrame(
            self, height=450, width=760)
        self.view.grid(row=0, column=0)

        for i, item in enumerate(handover):
            item_card = HandOverItem(self.view, item[0], item[1], id, reload)
            item_card.grid(row=i, column=0, padx=10, pady=10)


class MyTabView(customtkinter.CTkTabview):
    def __init__(self, master, agent_address, agent_location, rents, items, requested, handover, rented, message, reload, **kwargs):
        super().__init__(master, **kwargs)

        self.add("Chat")
        self.add("My Renting")
        self.add("My Items")
        self.add("Rented")
        self.add("Requested")
        self.add("Hand Over")

        self.message = message

        self.chat_view = ChatView(
            self.tab("Chat"), agent_address, agent_location, reload=reload)
        self.my_renting = MyRenting(
            self.tab("My Renting"), agent_address, agent_location, rents=rents, reload=reload)
        self.my_items = MyItems(self.tab("My Items"),
                                agent_address, agent_location, items=items, message=self.message, reload=reload)
        self.rended_view = RentedView(self.tab("Rented"), rented, reload=reload)
        self.requested_view = RequestedView(self.tab("Requested"), requested, reload=reload)
        self.handover_view = HandOverView(
            self.tab("Hand Over"), handover, agent_address, reload=reload)

        self.chat_view.grid(row=0, column=0)
        self.my_renting.grid(row=0, column=0)
        self.my_items.grid(row=0, column=0)
        self.rended_view.grid(row=0, column=0)
        self.requested_view.grid(row=0, column=0)
        self.handover_view.grid(row=0, column=0)


class LoginView(customtkinter.CTkFrame):
    def __init__(self, master, callback, **kwargs):
        super().__init__(master=master, **kwargs)

        self.callback = callback

        # Variables for username
        self.username_var = StringVar()

        # Username label and entry box
        self.username_label = customtkinter.CTkLabel(
            self, text="Username", width=20, height=40)
        self.username_label.grid(row=0, column=0, padx=5, pady=10)

        self.username_entry = customtkinter.CTkEntry(
            self, textvariable=self.username_var, placeholder_text="Enter your username...", width=150, height=40)
        self.username_entry.grid(row=0, column=1, padx=5, pady=10)

        # Login button
        self.login_button = customtkinter.CTkButton(
            self, text="Login", command=self.authenticate, width=80, height=40)
        self.login_button.grid(row=2, column=1, padx=5, pady=10)

        # Message label
        self.message = customtkinter.CTkLabel(
            self, text="", width=150, height=40)
        self.message.grid(row=3, column=1, padx=5, pady=10)

        # Configure grid layout to ensure proper expansion
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

    def authenticate(self):
        self.login_button.grid_forget()

        username = self.username_var.get()
        if not username:
            self.message.configure(text="ID is required")
            self.login_button.grid(row=2, column=1, padx=5, pady=10)
            return

        central_agent_data = get_agents("central_agent")

        print(central_agent_data)
        status = sync_query(
            destination=central_agent_data.agent_address, message=AgentRequest(id=username))

        if not status:
            self.message.configure(text="Unable to connect to central agent")
            self.login_button.grid(row=2, column=1, padx=5, pady=10)
            return

        if status["status"]:
            # Proceed with the callback on success
            self.callback(status["content"])
            return

        else:
            self.message.configure(text="User not found")
            self.login_button.grid(row=2, column=1, padx=5, pady=10)
            return


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("My App")

        self.geometry("1000x800")
        # self.maxsize(height=800, width=800)
        # self.minsize(height=800, width=800)

        self.login_view = LoginView(
            master=self, width=780, height=780, callback=self.login_callback)

        self.login_view.grid(row=0, column=0, padx=10, pady=10)
        # self.tab_view.grid(row=0, column=0, padx=10, pady=10)

    def login_callback(self, agent_info):
        self.agent_address = agent_info["agent"]
        self.agent_location = agent_info["location"]
        self.load_app()

    def reload_app(self):
        self.tab_view.grid_forget()
        self.load_app()

    def load_app(self):

        while True:
            response = sync_query(
                destination=self.agent_address, message=DataRequest(data=None))
            if not response:
                continue
            items = []
            rents = []
            rented = []
            requested = []
            handover = []

            for item in response["content"]["items"]:
                items.append(Item(**item))

            for rent in response["content"]["rents"]:
                rents.append((Item(**rent[0]), rent[1], rent[2]))

            for rent in response["content"]["rented"]:
                rented.append((Item(**rent[0]), rent[1]))

            for rent in response["content"]["requested"]:
                requested.append((Item(**rent[0]), rent[1]))

            for rent in response["content"]["handover"]:
                handover.append((Item(**rent[0]), rent[1]))

            break

        # Message label
        self.message = customtkinter.CTkLabel(
            self, text="", width=150, height=40)
        self.message.grid(row=0, column=0, padx=5, pady=10)

        self.tab_view = MyTabView(master=self, width=780, height=780, agent_address=self.agent_address,
                                  agent_location=self.agent_location, rents=rents, items=items, rented=rented, requested=requested, handover=handover, message=self.message, reload=self.reload_app)
        self.tab_view.grid(row=1, column=0, padx=10, pady=10)
        self.login_view.grid_forget()


if __name__ == "__main__":
    app = App()
    app.mainloop()
