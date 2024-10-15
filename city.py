from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from uagents import Agent, Context, Protocol  # type: ignore
from utils import create_agent
from models import *
from utils import get_agents, AgentData
from random import choice
from string import digits
from typing import Dict
from dotenv import load_dotenv
load_dotenv()

chain: Any = None


class RelatedItems(BaseModel):
    user_id: str
    name: str
    price: str
    description: str


class ResponseData(BaseModel):
    response: str = Field(description="Answer to the user query in string format")
    items: List[RelatedItems] = Field(description="Related items to the user query in format of list of RelatedItems")


def create_data(all_data: Dict):

    print(all_data)

    final_data = []

    for user, items in all_data.items():
        for name, item in items.items():
            if item["period"] == 1:
                rate = "hour"
            elif item["period"] == 24:
                rate = "day"
            elif item["period"] == 24 * 7:
                rate = "week"
            elif item["period"] == 24 * 30:
                rate = "month"
            elif item["period"] == 24 * 365:
                rate = "year"
            final_data.append(RelatedItems(user_id=user, name=name, price=f"{item["price"]}/{rate}", description=item["description"]))

    return final_data


city_central_link_protocol = Protocol(
    name="city_central_link_protocol", version="1.0")


item_management_protocol = Protocol(
    name="item_management_protocol", version="1.0")


search_protocol = Protocol(
    name="search_protocol", version="1.0")


@search_protocol.on_query(model=SearchRequest, replies={SearchResponse})
async def search(context: Context, sender: str, request: SearchRequest):
    items = context.storage.get("items")
    data = create_data(items[request.category])
    global chain

    response = chain.invoke(
        {"query": request.query, "history": request.history, "data": data})
    
    related_items = []
    
    for item in response["items"]:
        if item["user_id"] in items[request.category]:
            if item["name"] in items[request.category][item["user_id"]]:
                related_items.append((item["user_id"], Item(**items[request.category][item["user_id"]][item["name"]])))      

    await context.send(destination=sender, message=SearchResponse(response=response["response"], items=related_items))


@item_management_protocol.on_query(model=AddRequest, replies={Response})
async def add_item(context: Context, sender: str, request: AddRequest):
    items = context.storage.get("items")
    if request.agent_address not in items[request.item.category]:
        items[request.item.category][request.agent_address] = {}
    items[request.item.category][request.agent_address][request.item.name] = request.item.model_dump()
    context.storage.set("items", items)
    await context.send(destination=sender, message=Response(status=True, content="Item added"))


@item_management_protocol.on_query(model=DeleteRequest, replies={Response})
async def delete_item(context: Context, sender: str, request: DeleteRequest):
    items = context.storage.get("items")
    if request.agent_address in items[request.category]:
        if request.name in items[request.category][request.agent_address]:
            items[request.category][request.agent_address].pop(request.name)
            context.storage.set("items", items)
            await context.send(destination=sender, message=Response(status=True, content="Item deleted"))
            return
        else:
            await context.send(destination=sender, message=Response(status=False, content="Item not found"))
    else:
        await context.send(destination=sender, message=Response(status=False, content="User not found"))


@city_central_link_protocol.on_message(model=LocationRegistrationResponse)
async def register_response(context: Context, sender: str, response: LocationRegistrationResponse):
    if response.status:
        context.logger.info(f"Location registered successfully")
        items: Dict[str, Dict] = {}
        for item in response.items:
            items[item] = {}
        context.storage.set("items", items)
    else:
        context.logger.info(f"Location already exists")


city_user_link_protocol = Protocol(
    name="city_user_link_protocol", version="1.0")


@city_user_link_protocol.on_message(model=User, replies={UserID})
async def receive_user(context: Context, sender: str, user: User):
    if not user.id:
        users = context.storage.get("users")
        while True:
            new_id = "".join(choice(digits) for _ in range(10))
            if new_id not in users:
                break
        user.id = new_id
        users[user.id] = sender
        context.storage.set("users", users)
        context.logger.info(f"User {user.name} registered with ID {user.id}")
    await context.send(destination=sender, message=UserID(id=user.id))


def create_city_agent(name: str, central_agent_address: str) -> Agent:

    global chain
    model = ChatGoogleGenerativeAI(model="gemini-pro")

    parser = JsonOutputParser(pydantic_object=ResponseData)

    prompt = PromptTemplate(
        template="Answer the user query in required format.\nFormat Instruction: {format_instructions}\nPrevious Conversation: {history}\nAvailable Data: {data}\nQuery: {query}\n\n DO NOT USE ANY IMAGINARY DATA(ONLY USE THE DATA PROVIDED IN THE AVAILABLE DATA)\n\nONLY RETURN IN THE FORMAT MENTIONED IN THE FORMAT INSTRUCTION",
        input_variables=["query", "history", "data"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    
    async def register(context: Context) -> None:


        context.logger.info(f"Registering location {name}...")


        await context.send(destination=central_agent_address, message=LocationRegistrationRequest(location=name, address=city_agent.address))

    async def unregister(context: Context) -> None:
        context.logger.info(f"Unregistering location {name}...")
        await context.send(destination=central_agent_address, message=LocationUnregistrationRequest(location=name))

    city_agent: Agent = create_agent(
        f"{name}",
        secret=f"{name}_secret",
        storage_initials={"users": {}, "items": {}},
        protocols=[city_central_link_protocol, city_user_link_protocol,
                   item_management_protocol, search_protocol],
        custom_startup_function=register,
        custom_shutdown_function=unregister
    )

    return city_agent


if __name__ == "__main__":
    city_name = input("Enter city name: ")
    central_agent_data: AgentData = get_agents("central_agent")

    if not central_agent_data.agent_address:
        print("Central agent not found. Exiting...")
        exit(1)

    city_agent = create_city_agent(
        city_name, central_agent_address=central_agent_data.agent_address)
    print(f"Starting {city_name} Agent...")
    city_agent.run()
