from uagents import Model  # type: ignore
from typing import Optional, Any, List, Tuple


class LocationRequest(Model):
    location: Optional[str]


class LocationList(Model):
    locations: List[str]


class LocationAddress(Model):
    address: str
    status: bool


class Item(Model):
    name: str
    price: float
    period: int
    image: str
    category: str
    description: str


class ItemRequest(Model):
    name: Optional[str]



class AddRequest(Model):
    item: Item
    agent_address: str


class DeleteRequest(Model):
    name: str
    category: str
    agent_address: str


class RentRequest(Model):
    name: Optional[str]


class Address(Model):
    area: str
    city: str


class User(Model):
    id: Optional[str]
    name: str
    phone: str
    email: str
    address: Address


class UserID(Model):
    id: str

class UserRegistrationRequest(Model):
    address: str
    items: List[Item]


class UserRegistrationResponse(Model):
    status: bool
    message: str


class Response(Model):
    status: bool
    content: Any


class LocationRegistrationRequest(Model):
    location: str
    address: str


class LocationRegistrationResponse(Model):
    status: bool
    items: List[str]


class LocationUnregistrationRequest(Model):
    location: str


class LocationUnregistrationResponse(Model):
    status: bool
    message: str


class AgentRequest(Model):
    id: str


class UserLocationLink(Model):
    id: str
    location: str


class SearchRequest(Model):
    category: str
    query: str
    history: str

class SearchResponse(Model):
    items: List[Tuple[str, Item]]
    response: str

class RequestedItem(Model):
    item: Item


class HandOverRequest(Model):
    item: Item
    agent: str
    

class DataRequest(Model):
    data: Any


class RentConfirmRequest(Model):
    item: Item
    code: str
    agent: str
    payment_id: str

class handOverConfirm(Model):
    item: Item

class HandOverEnd(Model):
    item: Item
    code: str

class HandOverEndConfirm(Model):
    item: Item

class WalletRequest(Model):
    any: Any


class PaymentRequest(Model):
    from_address: str
    to_address: str
    amount: float
    frequency: int


class PaymentCancel(Model):
    id: str


class TransactionRequest(Model):
    to_address: str
    amount: float