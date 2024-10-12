from json import load, dump
from dotenv import load_dotenv
from os import getenv, path, makedirs
from pydantic import BaseModel, Field
from typing_extensions import Optional, Dict, Any, Tuple, List, Callable
from random import choice
from string import ascii_letters, digits
from functools import wraps
from uagents import Agent, Context, Bureau, Protocol  # type: ignore
from uagents.setup import fund_agent_if_low  # type: ignore

load_dotenv()


def ensure_files(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        file_path = getenv("AGENT_FILE_PATH")

        if not file_path:
            raise ValueError(
                "`AGENT_FILE_PATH` is not set in environment variables")

        if path.dirname(file_path) and not path.exists(path.dirname(file_path)):
            makedirs(path.dirname(file_path))

        if not path.exists(file_path):
            with open(file_path, 'w') as file:
                dump({
                    "config": {
                        "start_port": 8000,
                        "active_ports": []
                    },
                    "agents": {}
                }, file, indent=4)
                file.truncate()

        if not path.isfile(file_path):
            raise ValueError(f"{file_path} is not a file")

        with open(file_path, 'r+') as file:
            try:
                load(file)
            except Exception as e:
                file.seek(0)
                dump({
                    "config": {
                        "start_port": 8000,
                        "active_ports": []
                    },
                    "agents": {}
                }, file, indent=4)
                file.truncate()

        return func(file_path, *args, **kwargs)
    return wrapper


@ensure_files
def get_port(file_path: str) -> int:
    with open(file_path, 'r+') as file:
        data = load(file)
        port = data["config"]["start_port"]
        while not port or port in data["config"]["active_ports"]:
            port += 1
        data["config"]["active_ports"].append(port)
        file.seek(0)
        dump(data, file, indent=4)
        file.truncate()
    return port


class AgentData(BaseModel):
    name: str
    secret: str = Field(default_factory=lambda: "".join(
        choice(ascii_letters + digits) for _ in range(32)))
    port: int = Field(default_factory=get_port)
    agent_address: Optional[str] = None
    wallet_address: Optional[str] = None


@ensure_files
def create_agent(
    file_path: str,
    name: str,
    secret: Optional[str] = None,
    storage_initials: Optional[Dict[str, Any]] = None,
    protocols: Optional[List[Protocol]] = None,
    custom_startup_function: Optional[Callable] = None,
    custom_shutdown_function: Optional[Callable] = None
) -> Agent:
    
    print("Initializing Agent...")
    
    print("Creating AgentData...")
    agent_data = AgentData(name=name)
    print("AgentData created.")

    print("Setting Agent secret...")
    if secret:
        agent_data.secret = secret
    print("Agent secret set.")

    print("Creating Agent...")
    agent: Agent = Agent(
        name=agent_data.name,
        seed=agent_data.secret,
        port=agent_data.port,
        endpoint=[f"http://127.0.0.1:{agent_data.port}/submit"]
    )
    print("Agent created.")

    print("Funding Agent...")
    fund_agent_if_low(agent.wallet.address())
    print("Agent funded.")

    print("Setting AgentData addresses...")
    agent_data.agent_address = agent.address
    agent_data.wallet_address = str(agent.wallet.address())
    print("AgentData addresses set.")

    def startup_wrapper(custom_startup_function: Optional[Callable]) -> Callable:
        if not custom_startup_function:
            async def register(ctx: Context) -> None:
                ctx.logger.info(f"Agent {name} started.")
                ctx.logger.info(f"Agent address: {agent_data.agent_address}")
                
                ctx.logger.info("Running default startup function...")

                ctx.logger.info("Setting storage initials...")
                if storage_initials:
                    for key, value in storage_initials.items():
                        ctx.logger.info(f"Setting {key} to {value}")
                        ctx.storage.set(key, value)
                ctx.logger.info("Storage initials set.")

                ctx.logger.info("Default startup function completed.")

            return register
        else:
            @wraps(custom_startup_function)
            async def wrapped_startup(ctx: Context) -> None:
                ctx.logger.info(f"Agent {name} started.")
                ctx.logger.info(f"Agent address: {agent_data.agent_address}")

                ctx.logger.info("Running custom startup function...")

                ctx.logger.info("Setting storage initials...")
                if storage_initials:
                    for key, value in storage_initials.items():
                        ctx.logger.info(f"Setting {key} to {value}")
                        ctx.storage.set(key, value)
                ctx.logger.info("Storage initials set.")

                ctx.logger.info("Executing custom startup function...")
                await custom_startup_function(ctx)
                ctx.logger.info("Execution completed.")

                ctx.logger.info("Custom startup function completed.")

            return wrapped_startup

    def shutdown_wrapper(custom_shutdown_function: Optional[Callable]) -> Callable:
        if not custom_shutdown_function:
            async def unregister(ctx: Context) -> None:
                ctx.logger.info("Running default shutdown function...")

                ctx.logger.info("Removing agent from active ports...")
                remove_agent(name)
                ctx.logger.info("Agent removed from active ports.")

                ctx.logger.info("Default shutdown function completed.")
            return unregister
        else:
            @wraps(custom_shutdown_function)
            async def wrapped_shutdown(ctx: Context) -> None:
                ctx.logger.info("Running custom shutdown function...")

                ctx.logger.info("Executing custom shutdown function...")
                await custom_shutdown_function(ctx)
                ctx.logger.info("Execution completed.")

                ctx.logger.info("Removing agent from active ports...")
                remove_agent(name)
                ctx.logger.info("Agent removed from active ports.")

                ctx.logger.info("Custom shutdown function completed.")
            return wrapped_shutdown

    print("Setting startup and shutdown functions...")
    agent.on_event("startup")(startup_wrapper(custom_startup_function))    
    agent.on_event("shutdown")(shutdown_wrapper(custom_shutdown_function))
    print("Startup and shutdown functions set.")

    if protocols:
        print("Including protocols...")
        for protocol in protocols:
            print(f"Including protocol {protocol.name}")
            agent.include(protocol)
        print("Protocols included.")
    else:
        print("No protocols to include.")
        
    print("Agent initialization completed.")

    print("Saving AgentData...")
    with open(file_path, 'r+') as file:
        data = load(file)
        data["agents"][name] = agent_data.model_dump()
        file.seek(0)
        dump(data, file, indent=4)
        file.truncate()
    print("AgentData saved.")

    return agent


@ensure_files
def remove_agent(file_path: str, name: str) -> None:
    with open(file_path, 'r+') as file:
        data = load(file)
        if name not in data["agents"].keys():
            raise ValueError(f"No agent named {name}")
        data["config"]["active_ports"].remove(data["agents"][name]["port"])
        del data["agents"][name]
        file.seek(0)
        dump(data, file, indent=4)
        file.truncate()


@ensure_files
def get_agents(file_path: str, name: str) -> AgentData:
    with open(file_path, 'r') as file:
        data = load(file)
        if name in data["agents"].keys():
            return AgentData.model_validate(data["agents"][name])
    raise ValueError(f"No agent named {name}")
