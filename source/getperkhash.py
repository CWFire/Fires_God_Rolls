import pydest
import asyncio
from os import getenv
from dotenv import load_dotenv

load_dotenv()

loop = asyncio.get_event_loop()

api_key = getenv("API_KEY", loop)

destiny = pydest.Pydest(api_key)
resp = loop.run_until_complete(destiny.api.search_destiny_entities("DestinyInventoryItemDefinition", "vision of confluence (timelost)"))
perkhash = resp["Response"]["results"]["results"][0]["hash"]

