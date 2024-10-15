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
from uagents.envelope import Envelope  # type: ignore
from uagents.query import query  # type: ignore
import asyncio
import base64
from io import BytesIO
from PIL import Image, ImageTk
import json

load_dotenv()


def encode_image(image: bytes) -> str:
    return base64.b64encode(image).decode('utf-8')


def decode_image(image: str) -> Any:
    img_bytes = base64.b64decode(image)
    image_file = Image.open(BytesIO(img_bytes))
    image_file.resize((150, 150))
    photo = ImageTk.PhotoImage(image_file)
    return photo


def sync_query(destination: str, message: Any) -> Any:
    async def await_query(address: str, message: Any) -> Any:
        return await query(destination=address, message=message, timeout=240.0)
    loop = asyncio.new_event_loop()
    old_loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    data = asyncio.run(await_query(destination, message))
    asyncio.set_event_loop(old_loop)
    if not isinstance(data, Envelope):
        return None
    return json.loads(data.decode_payload())


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
                    "agents": {},
                    "items": ["wearable", "transport", "electronic", "furniture"]
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
                    "agents": {},
                    "items": ["wearable", "transport", "electronic", "furniture"]
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


@ensure_files
def get_items(file_path: str) -> List[str]:
    with open(file_path, 'r') as file:
        data = load(file)
        return data["items"]


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
            async def register(context: Context) -> None:
                context.logger.info(f"Agent {name} started.")
                context.logger.info(
                    f"Agent address: {agent_data.agent_address}")

                context.logger.info("Running default startup function...")

                context.logger.info("Setting storage initials...")
                if storage_initials:
                    for key, value in storage_initials.items():
                        if context.storage.has(key):
                            context.logger.info(
                                f"Key {key} already exists. Skipping...")
                        else:
                            context.logger.info(f"Setting {key} to {value}")
                            context.storage.set(key, value)
                context.logger.info("Storage initials set.")

                context.logger.info("Default startup function completed.")

            return register
        else:
            @wraps(custom_startup_function)
            async def wrapped_startup(context: Context) -> None:
                context.logger.info(f"Agent {name} started.")
                context.logger.info(
                    f"Agent address: {agent_data.agent_address}")

                context.logger.info("Running custom startup function...")

                context.logger.info("Setting storage initials...")
                if storage_initials:
                    for key, value in storage_initials.items():
                        context.logger.info(f"Setting {key} to {value}")
                        context.storage.set(key, value)
                context.logger.info("Storage initials set.")

                context.logger.info("Executing custom startup function...")
                await custom_startup_function(context)
                context.logger.info("Execution completed.")

                context.logger.info("Custom startup function completed.")

            return wrapped_startup

    def shutdown_wrapper(custom_shutdown_function: Optional[Callable]) -> Callable:
        if not custom_shutdown_function:
            async def unregister(context: Context) -> None:
                context.logger.info("Running default shutdown function...")

                context.logger.info("Removing agent from active ports...")
                remove_agent(name)
                context.logger.info("Agent removed from active ports.")

                context.logger.info("Default shutdown function completed.")
            return unregister
        else:
            @wraps(custom_shutdown_function)
            async def wrapped_shutdown(context: Context) -> None:
                context.logger.info("Running custom shutdown function...")

                context.logger.info("Executing custom shutdown function...")
                await custom_shutdown_function(context)
                context.logger.info("Execution completed.")

                context.logger.info("Removing agent from active ports...")
                remove_agent(name)
                context.logger.info("Agent removed from active ports.")

                context.logger.info("Custom shutdown function completed.")
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
