import pydest
import asyncio
from os import getenv
from dotenv import load_dotenv

load_dotenv()

loop = asyncio.get_event_loop()

api_key = getenv("API_KEY")

destiny = pydest.Pydest(api_key, loop)
resp = loop.run_until_complete(destiny.api.search_destiny_entities("DestinyInventoryItemDefinition", "Crown Splitter"))
results = resp["Response"]["results"]["results"]
hashes = [result["hash"] for result in results]
dehashed = [loop.run_until_complete(destiny.decode_hash(itemhash, "DestinyInventoryItemDefinition")) for itemhash in hashes]


# we can differentiate between weapons / perks / shaders using the decoded items' property 'traidIds'
# weapons have item_type.weapon in traitIds
# perks do not have property traitIds

