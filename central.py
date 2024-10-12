from uagents import Agent, Context, Protocol  # type: ignore
from utils import create_agent
from models import LocationRequest, Response, LocationRegistrationRequest, LocationRegistrationResponse, LocationUnregistrationRequest, LocationUnregistrationResponse
from typing import Dict

user_central_link_protocol = Protocol(
    name="user_central_link_protocol", version="1.0")


@user_central_link_protocol.on_message(model=LocationRequest, replies={Response})
async def get_location(context: Context, sender: str, request: LocationRequest):
    locations: Dict[str, str] = context.storage.get("locations")

    if request.location:
        if request.location in locations.keys():
            context.logger.info(f"Location {request.location} found")
            await context.send(destination=sender, message=Response(status=True, content=locations[request.location]))
        else:
            context.logger.info(f"Location {request.location} not found")
            await context.send(destination=sender, message=Response(status=False, content=f"Location {request.location} not found"))
    else:
        context.logger.info(f"Listing all locations")
        await context.send(destination=sender, message=Response(status=True, content=list(locations.keys())))


city_central_link_protocol = Protocol(
    name="city_central_link_protocol", version="1.0")


@city_central_link_protocol.on_message(model=LocationRegistrationRequest, replies={LocationRegistrationResponse})
async def set_location(context: Context, sender: str, request: LocationRegistrationRequest):
    locations: Dict[str, str] = context.storage.get("locations")
    if request.location in locations.keys():
        context.logger.info(f"Location {request.location} already exists")
        await context.send(destination=sender, message=LocationRegistrationResponse(status=False, message=f"Location {request.location} already exists"))
    else:
        locations[request.location] = request.address
        context.storage.set("locations", locations)
        context.logger.info(f"Location {request.location} registered")
        await context.send(destination=sender, message=LocationRegistrationResponse(status=True, message=f"Location {request.location} registered"))


@city_central_link_protocol.on_message(model=LocationUnregistrationRequest, replies={LocationUnregistrationResponse})
async def remove_location(context: Context, sender: str, request: LocationUnregistrationRequest):
    locations: Dict[str, str] = context.storage.get("locations")
    if request.location in locations.keys():
        del locations[request.location]
        context.storage.set("locations", locations)
        context.logger.info(f"Location {request.location} unregistered")
        await context.send(destination=sender, message=LocationUnregistrationResponse(status=True, message=f"Location {request.location} unregistered"))
    else:
        context.logger.info(f"Location {request.location} not found")
        await context.send(destination=sender, message=LocationUnregistrationResponse(status=False, message=f"Location {request.location} not found"))

central_agent: Agent = create_agent(
    "central_agent",
    secret="central_secret",
    storage_initials={"locations": {}},
    protocols=[user_central_link_protocol, city_central_link_protocol]
)

if __name__ == "__main__":
    print("Starting Central Agent...")
    central_agent.run()
