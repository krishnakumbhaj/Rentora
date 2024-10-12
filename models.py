from uagents import Model # type: ignore
from typing import Optional, List, Any

class LocationRequest(Model):
    location: Optional[str]

class Response(Model):
    status: bool
    content: Any

class LocationRegistrationRequest(Model):
    location: str
    address: str

class LocationRegistrationResponse(Model):
    status: bool
    message: str

class LocationUnregistrationRequest(Model):
    location: str

class LocationUnregistrationResponse(Model):
    status: bool
    message: str