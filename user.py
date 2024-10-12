from uagents import Agent, Context, Protocol  # type: ignore
from utils import create_agent
# from models import RegisterRequest, RegisterResponse, AuthRequest, AuthResponse, AddressRequest, AddressResponse, Error


central_protocol = Protocol(name="central_protocol", version="1.0")


@central_protocol.on_interval(period=1)
async def check_agents(context: Context):
    print("Checking agents")


if __name__ == "__main__":
    central_agent: Agent = create_agent(
        "central_agent",
        secret="central_secret",
        storage_initials={"locations": {}},
        protocols=[central_protocol]
    )
    central_agent.run()
