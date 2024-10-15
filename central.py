from uagents import Agent, Context, Protocol  # type: ignore
from utils import create_agent, get_items
from models import *
from typing import Dict
from random import randint
from uagents.network import wait_for_tx_to_complete # type: ignore
from utils import sync_query
from uagents.envelope import Envelope  # type: ignore
from uagents.query import query  # type: ignore
import json

payment_protocol = Protocol(
    name="payment_protocol", version="1.0")


@payment_protocol.on_query(model=PaymentCancel, replies={Response})
async def cancel_payment(context: Context, sender: str, request: PaymentCancel):
    print(f'{request=}')
    payments = context.storage.get("payments")
    if request.id in payments.keys():
        del payments[request.id]
        context.storage.set("payments", payments)
        print(f"Payment cancelled {payments}")
        await context.send(destination=sender, message=Response(status=True, content="Payment cancelled"))
    else:
        await context.send(destination=sender, message=Response(status=False, content="Payment not found"))


@payment_protocol.on_query(model=PaymentRequest, replies={Response})
async def get_payment(context: Context, sender: str, request: PaymentRequest):
    items = context.storage.get("payments")

    payment_id = randint(1000, 9999)
    items[payment_id] = {
        "from": request.from_address,
        "to": request.to_address,
        "amount": request.amount,
        "repeat": 60 * request.frequency,
        "remaining": 0
    }

    context.storage.set("payments", items)
    await context.send(destination=sender, message=Response(status=True, content=payment_id))


@payment_protocol.on_interval(period=60)
async def check_payments(context: Context):
    payments = context.storage.get("payments")
    for payment in payments.values():
        if payment["remaining"] == 0:
            data = await query(destination=payment["from"], message=TransactionRequest(to_address=payment["to"], amount=payment["amount"]), timeout=240.0)
            if not isinstance(data, Envelope):
                continue
            transaction = json.loads(data.decode_payload())["content"]
            tx_resp = await wait_for_tx_to_complete(transaction, context.ledger)
            coin_received = tx_resp.events["coin_received"]
            if (
                coin_received["receiver"] == payment["to"]
                and coin_received["amount"] == f"{payment["amount"]}atestfet"
            ):
                context.logger.info(f"Transaction was successful: {coin_received}")
            else:
                context.logger.info(f"Transaction failed: {coin_received}")

        payment["remaining"] -= 1


user_central_link_protocol = Protocol(
    name="user_central_link_protocol", version="1.0")


@user_central_link_protocol.on_message(model=LocationRequest, replies={LocationAddress, LocationList})
async def get_location_by_message(context: Context, sender: str, request: LocationRequest):
    locations: Dict[str, str] = context.storage.get("locations")

    if request.location:
        if request.location in locations.keys():
            context.logger.info(f"Location {request.location} found")
            await context.send(destination=sender, message=LocationAddress(address=locations[request.location], status=True))
        else:
            context.logger.info(f"Location {request.location} not found")
            await context.send(destination=sender, message=LocationAddress(address="Location not found", status=False))
    else:
        context.logger.info(f"Listing all locations")
        await context.send(destination=sender, message=LocationList(locations=list(locations.keys())))


@user_central_link_protocol.on_query(model=AgentRequest, replies={Response})
async def get_location_by_query(context: Context, sender: str, request: AgentRequest):
    print("Querying...")
    users: Dict[str, str] = context.storage.get("users")
    if request.id in users.keys():
        print("User found")
        await context.send(destination=sender, message=Response(status=True, content=users[request.id]))
    else:
        print("User not found")
        await context.send(destination=sender, message=Response(status=False, content="User not found"))


@user_central_link_protocol.on_message(model=UserLocationLink, replies={Response})
async def activate_user(context: Context, sender: str, request: UserLocationLink):
    users: Dict[str, Dict] = context.storage.get("users")
    if request.id in users.keys():
        await context.send(destination=sender, message=Response(status=False, content="User already activated"))
    else:
        users[request.id] = {"agent": sender, "location": request.location}
        context.storage.set("users", users)
        await context.send(destination=sender, message=Response(status=True, content="User activated"))

city_central_link_protocol = Protocol(
    name="city_central_link_protocol", version="1.0")


@city_central_link_protocol.on_message(model=LocationRegistrationRequest, replies={LocationRegistrationResponse})
async def set_location(context: Context, sender: str, request: LocationRegistrationRequest):
    locations: Dict[str, str] = context.storage.get("locations")
    if request.location in locations.keys():
        context.logger.info(f"Location {request.location} already exists")
        await context.send(destination=sender, message=LocationRegistrationResponse(status=False, items=context.storage.get("items")))
    else:
        locations[request.location] = request.address
        context.storage.set("locations", locations)
        context.logger.info(f"Location {request.location} registered")
        await context.send(destination=sender, message=LocationRegistrationResponse(status=True, items=context.storage.get("items")))


@city_central_link_protocol.on_message(model=LocationUnregistrationRequest, replies={LocationUnregistrationResponse})
async def remove_location(context: Context, sender: str, request: LocationUnregistrationRequest):
    locations: Dict[str, str] = context.storage.get("locations")
    if request.location in locations.keys():
        del locations[request.location]
        context.storage.set("locations", locations)
        context.logger.info(f"Location {request.location} unregistered")
    else:
        context.logger.info(f"Location {request.location} not found")

central_agent: Agent = create_agent(
    "central_agent",
    secret="central_secret",
    storage_initials={"locations": {}, "users": {}, "items": get_items(), "payments": {}},
    protocols=[user_central_link_protocol, city_central_link_protocol, payment_protocol]
)

if __name__ == "__main__":
    print("Starting Central Agent...")
    central_agent.run()
