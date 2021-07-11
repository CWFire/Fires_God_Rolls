from openpyxl import load_workbook
from os import path, getcwd, getenv
import pydest
import asyncio
from dotenv import load_dotenv

output_header = """title:Fires God Rolls.
description:This is a list I have created to highlight all the "God Rolls" of weapons according to the most used perk percentage on light.gg."""

load_dotenv()

loop = asyncio.get_event_loop()
api_key = getenv("API_KEY", loop)
destiny = pydest.Pydest(api_key)

workbook_path = path.join(getcwd(), "..", "God Rolls.xlsx")
workbook = load_workbook(filename=workbook_path, data_only=True)

output_path = path.join(getcwd(), "..", "generated_God_Rolls.txt")

with open(output_path, "w") as writefile:
    writefile.write(output_header)

current_gun_name = None
current_gun_hash = None
current_gun_rolls_string = ""

perk_hashes_cache = {}


async def get_inventory_item_hash(query: str):
    resp = await destiny.api.search_destiny_entities("DestinyInventoryItemDefinition", query[:30])
    results = resp["Response"]["results"]["results"]
    return results[0]["hash"] if results else None


async def get_perk_hash(query: str):
    query = query.lower()
    if query in perk_hashes_cache.keys():
        return perk_hashes_cache[query]
    else:
        perk_hash = await get_inventory_item_hash(query)
        perk_hashes_cache[query] = perk_hash
        return perk_hash

for sheet in workbook:
    with open(output_path, "a") as appendfile:
        appendfile.write(f"\n\n//{sheet.title}")
        current_gun_rolls_string = ""

    for row in tuple(sheet)[1:]:
        gun = row[0].value
        if gun and str(gun).strip():
            current_gun_name = gun
            with open(output_path, "a") as appendfile:
                appendfile.write(current_gun_rolls_string)
                appendfile.write(f"\n\n//{current_gun_name}\n//notes:God Roll")
            current_gun_hash = loop.run_until_complete(get_inventory_item_hash(gun))
            current_gun_rolls_string = ""

        perk_names = [cell.value for cell in row[1:5] if cell.value]
        perk_hashes_str = str([loop.run_until_complete(get_perk_hash(perk_name)) for perk_name in perk_names if perk_name and perk_name != "*"])[1:-1].replace(" ", "")

        if not perk_hashes_str:
            if "*" in "".join(perk_names):
                perks_str = "&perks=*"
            else:
                continue
        else:
            perks_str = f"&perks={perk_hashes_str}"

        note = row[5].value

        current_gun_rolls_string += f"\ndimwishlist:item={current_gun_hash}{perks_str}{f' #notes:{note}' if note else ''}"

    with open(output_path, "a") as appendfile:
        appendfile.write(current_gun_rolls_string)
