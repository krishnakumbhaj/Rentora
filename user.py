from uagents import Agent, Context, Protocol  # type: ignore
from utils import create_agent, AgentData, get_agents
from models import *
from rich.prompt import Prompt
from random import choice
from string import ascii_letters, digits
from typing import Dict


wallet = None
wallet_address = None

user_registration_protocol = Protocol(
    name="user_registration_protocol", version="1.0")



requested_protocol = Protocol(
    name="requested_protocol", version="1.0")

@requested_protocol.on_query(model=RequestedItem, replies={Response})
async def add_item(context: Context, sender: str, item: RequestedItem):
    requested = context.storage.get("requested")
    requested.append((item.item.model_dump(), ''.join(choice(digits) for _ in range(4))))
    context.storage.set("requested", requested)
    await context.send(destination=sender, message=Response(status=True, content="Item added"))



rent_protocol = Protocol(
    name="rent_protocol", version="1.0")

@rent_protocol.on_query(model=RentConfirmRequest, replies={Response})
async def get_rdents(context: Context, sender: str, request: RentConfirmRequest):
    requested = context.storage.get("requested")
    rents = context.storage.get("rents")
    
    for item in requested:
        if item[0]["name"] == request.item.name:
            if item[1] != request.code:
                await context.send(destination=sender, message=Response(status=False, content="Invalid code"))
                return
            requested.remove(item)
            rents.append((item[0], request.agent, request.payment_id))
            context.storage.set("requested", requested)
            context.storage.set("rents", rents)
            await context.send(destination=sender, message=Response(status=True, content="Item rented"))
            return
        
    await context.send(destination=sender, message=Response(status=False, content="Item not found"))

payment_protocol = Protocol(
    name="payment_protocol", version="1.0")

@payment_protocol.on_query(model=TransactionRequest, replies={Response})
async def get_payment(context: Context, sender: str, request: TransactionRequest):
    global wallet
    transaction = context.ledger.send_tokens(
        request.to_address, request.amount, "atestfet", wallet
    )
    await context.send(destination=sender, message=Response(status=True, content=transaction.tx_hash))

handover_protocol = Protocol(
    name="handover_protocol", version="1.0")



@handover_protocol.on_query(model=HandOverRequest, replies={Response})
async def get_rents(context: Context, sender: str, request: HandOverRequest):
    handover = context.storage.get("handover")
    handover.append((request.item.model_dump(), request.agent))
    context.storage.set("handover", handover)
    items = context.storage.get("items")
    items.remove(request.item.model_dump())
    context.storage.set("items", items)
    await context.send(destination=sender, message=Response(status=True, content="Item rented"))


@handover_protocol.on_query(model=handOverConfirm, replies={Response})
async def get_ren__ts(context: Context, sender: str, request: handOverConfirm):
    handover = context.storage.get("handover")
    rented = context.storage.get("rented")
    
    for item in handover:
        if item[0]["name"] == request.item.name:
            handover.remove(item)
            rented.append((item[0], "".join(choice(digits) for _ in range(4))))
            context.storage.set("handover", handover)
            context.storage.set("rented", rented)
            await context.send(destination=sender, message=Response(status=True, content="Item rented"))
            return
        
    await context.send(destination=sender, message=Response(status=False, content="Item not found"))


@handover_protocol.on_query(model=HandOverEndConfirm, replies={Response})
async def get______rents(context: Context, sender: str, request: HandOverEndConfirm):
    rents = context.storage.get("rents")
    for item in rents:
        if item[0]["name"] == request.item.name:
            rents.remove(item)
            context.storage.set("rents", rents)
            await context.send(destination=sender, message=Response(status=True, content="Item returned"))
            return
    await context.send(destination=sender, message=Response(status=False, content="Item not found"))


@handover_protocol.on_query(model=HandOverEnd, replies={Response})
async def ge___t_rentss(context: Context, sender: str, request: HandOverEnd):
    rented = context.storage.get("rented")
    for item in rented:
        if item[0]["name"] == request.item.name:
            if item[1] != request.code:
                await context.send(destination=sender, message=Response(status=False, content="Invalid code"))
                return
            rented.remove(item)
            context.storage.set("rented", rented)
            items = context.storage.get("items")
            items.append(item[0])
            context.storage.set("items", items)
            await context.send(destination=sender, message=Response(status=True, content="Item returned"))
            return
    await context.send(destination=sender, message=Response(status=False, content="Item not found"))



@user_registration_protocol.on_message(model=LocationList, replies={LocationRequest})
async def create_userinfo(context: Context, sender: str, request: LocationList):

    print("Enter your details:")
    name = input("Enter your name: ")
    phone = input("Enter your phone number: ")
    email = input("Enter your email: ")

    print("Enter your address:")
    area = input("Enter your area: ")
    city = Prompt.ask("Enter your city", choices=request.locations)

    userinfo = User(
        id=None,
        name=name,
        phone=phone,
        email=email,
        address=Address(
            area=area,
            city=city
        ),
        items=[],
        rents=[]
    )

    context.storage.set("userinfo", userinfo.model_dump())
    context.logger.info(f"User information saved")
    await context.send(destination=sender, message=LocationRequest(location=city))


@user_registration_protocol.on_message(model=LocationAddress, replies={User})
async def register_user(context: Context, sender: str, request: LocationAddress):
    context.logger.info(f"Location address found")
    userinfo: User = User.model_validate(context.storage.get("userinfo"))
    context.storage.set("location", request.address)
    await context.send(destination=request.address, message=userinfo)


@user_registration_protocol.on_message(model=UserID, replies={UserLocationLink})
async def activate_user(context: Context, sender: str, request: UserID):
    context.logger.info(f"User activated")
    userinfo: User = User.model_validate(context.storage.get("userinfo"))
    userinfo.id = request.id
    context.storage.set("userinfo", userinfo.model_dump())
    context.logger.info(f"{userinfo.name} activated with ID: {request.id}")
    central_agent_data: AgentData = get_agents("central_agent")
    await context.send(destination=central_agent_data.agent_address, message=UserLocationLink(id=request.id, location=context.storage.get("location")))


@user_registration_protocol.on_message(model=Response)
async def activate_user_finish(context: Context, sender: str, request: Response):
    if request.status:
        context.logger.info(f"User activated")
    else:
        context.logger.info(f"User already activated")


item_management_protocol = Protocol(
    name="item_management_protocol", version="1.0")


@item_management_protocol.on_query(model=Item, replies={Response})
async def add_i_tem(context: Context, sender: str, item: Item):
    items = context.storage.get("items")
    items.append(item.model_dump())
    context.storage.set("items", items)
    await context.send(destination=sender, message=Response(status=True, content="Item added"))


@item_management_protocol.on_query(model=DeleteRequest, replies={Response})
async def delete_item(context: Context, sender: str, request: DeleteRequest):
    items = context.storage.get("items")
    for item in items:
        if item["name"] == request.name:
            items.remove(item)
            context.storage.set("items", items)
            await context.send(destination=sender, message=Response(status=True, content="Item deleted"))
            return
    await context.send(destination=sender, message=Response(status=False, content="Item not found"))


user_application_link_protocol = Protocol(
    name="user_application_link_protocol", version="1.0")


@user_application_link_protocol.on_query(model=WalletRequest, replies={Response})
async def get_wallet(context: Context, sender: str, request: WalletRequest):
    global wallet_address
    await context.send(destination=sender, message=Response(status=True, content=wallet_address))


@user_application_link_protocol.on_query(model=ItemRequest, replies={Response})
async def get_items(context: Context, sender: str, request: ItemRequest):
    items = context.storage.get("items")
    userinfo = context.storage.get("userinfo")

    if request.name:
        for item in items:
            if item["name"] == request.name:
                await context.send(destination=sender, message=Response(status=True, content=(item, userinfo)))
                return
        await context.send(destination=sender, message=Response(status=False, content="Item not found"))
    else:
        await context.send(destination=sender, message=Response(status=True, content=items))


@user_application_link_protocol.on_query(model=DataRequest, replies={Response})
async def ge__t_rents(context: Context, sender: str, request: DataRequest):
    rents = context.storage.get("rents")
    items = context.storage.get("items")
    rented = context.storage.get("rented")
    handover = context.storage.get("handover")
    requested = context.storage.get("requested")
    
    response = {
        "rents": rents,
        "items": items,
        "rented": rented,
        "handover": handover,
        "requested": requested
    }

    await context.send(destination=sender, message=Response(status=True, content=response))



def create_user_agent(code: str, central_agent_address: str) -> Agent:

    async def register(context: Context) -> None:
        if context.storage.has("userinfo"):
            userinfo: User = User.model_validate(
                context.storage.get("userinfo"))
            # context.storage.set("wallet", )
            context.logger.info(f"Connecting to location: {userinfo.address.city}...")
            await context.send(destination=central_agent_address, message=LocationRequest(location=userinfo.address.city))
        else:
            context.logger.info("User information not found")
            await context.send(destination=central_agent_address, message=LocationRequest(location=None))

    async def unregister(context: Context) -> None:
        context.logger.info(f"Unregistering user")
        # await context.send(destination=central_agent_address, message=LocationUnregistrationRequest(location=name))

    city_agent: Agent = create_agent(
        f"{code}",
        secret=f"{code}_secret",
        storage_initials={"items": [], "rents": [], "requested": [], "rented": [], "handover": []},
        protocols=[user_registration_protocol, user_application_link_protocol, item_management_protocol, requested_protocol, rent_protocol, handover_protocol, payment_protocol],
        custom_startup_function=register,
        custom_shutdown_function=unregister
    )

    global wallet_address, wallet
    wallet = city_agent.wallet
    wallet_address = str(city_agent.wallet.address())

    return city_agent


if __name__ == "__main__":
    central_agent_data: AgentData = get_agents("central_agent")

    if not central_agent_data.agent_address:
        print("Central agent not found. Exiting...")
        exit(1)

    # "".join(choice(ascii_letters + digits) for _ in range(32))
    code = input("Enter the user code: ")

    city_agent = create_user_agent(
        code, central_agent_address=central_agent_data.agent_address)
    print("Starting User Agent...")
    city_agent.run()
