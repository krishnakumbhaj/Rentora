from uagents import Agent, Context, Protocol  # type: ignore
from utils import create_agent
from models import LocationRegistrationRequest, LocationRegistrationResponse, LocationUnregistrationRequest, LocationUnregistrationResponse
from utils import get_agents, AgentData
from asyncio import sleep


city_central_link_protocol = Protocol(name="city_central_link_protocol", version="1.0")

@city_central_link_protocol.on_message(model=LocationRegistrationResponse)
async def register_response(ctx: Context, sender: str, response: LocationRegistrationResponse):
    if response.status:
        ctx.logger.info(f"Location {ctx.storage.get('name')} registered")
    else:
        ctx.logger.info(f"Location {ctx.storage.get('name')} already exists")

@city_central_link_protocol.on_message(model=LocationUnregistrationResponse)
async def unregister_response(ctx: Context, sender: str, response: LocationUnregistrationResponse):
    if response.status:
        ctx.logger.info(f"Location {ctx.storage.get('name')} unregistered")
    else:
        ctx.logger.info(f"Location {ctx.storage.get('name')} not found")


city_user_link_protocol = Protocol(name="city_user_link_protocol", version="1.0")




def create_city_agent(name: str, central_agent_address: str) -> Agent:

    async def register(ctx: Context) -> None:
        ctx.logger.info(f"Registering location {name}...")
        await ctx.send(destination=central_agent_address, message=LocationRegistrationRequest(location=name, address=city_agent.address))

    async def unregister(ctx: Context) -> None:
        ctx.logger.info(f"Unregistering location {name}...")
        await ctx.send(destination=central_agent_address, message=LocationUnregistrationRequest(location=name))

    city_agent: Agent = create_agent(
        f"{name}",
        secret=f"{name}_secret",
        storage_initials={"locations": {}, "name": name},
        protocols=[city_central_link_protocol],
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

    city_agent = create_city_agent(city_name, central_agent_address=central_agent_data.agent_address)
    print(f"Starting {city_name} Agent...")
    city_agent.run()
