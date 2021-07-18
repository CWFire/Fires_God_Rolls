from openpyxl import load_workbook
from os import path, getcwd, getenv
import pydest
import asyncio
from dotenv import load_dotenv

output_header = """title:Fires God Rolls.
description:This is a list I have created to highlight all the "God Rolls" of weapons according to the most used perk percentage on light.gg."""

load_dotenv()

loop = asyncio.get_event_loop()
api_key = getenv("API_KEY")
destiny = pydest.Pydest(api_key, loop)

workbook_path = path.join(getcwd(), "..", "God Rolls.xlsx")
workbook = load_workbook(filename=workbook_path, data_only=True)

output_path = path.join(getcwd(), "..", "generated_God_Rolls.txt")

with open(output_path, "w") as writefile:
    writefile.write(output_header)

current_gun_name = None
current_gun_hash = None
current_gun_rolls_string = ""

perk_hashes_cache = {}

valid_item_types = ["Weapon", "Perk"]


async def get_inventory_item(query: str, item_type: str = None):
    global valid_item_types
    item_type = item_type if item_type in valid_item_types else valid_item_types[0]
    resp = await destiny.api.search_destiny_entities("DestinyInventoryItemDefinition", query[:30])
    results = resp["Response"]["results"]["results"]
    if not results:
        return None
    else:
        dehashed_results = [await destiny.decode_hash(result["hash"], "DestinyInventoryItemDefinition") for result in results]
        valid_results = dehashed_results.copy()
        if len(valid_results) > 1:
            if item_type == "Weapon":
                valid_results = [data for data in valid_results if "traitIds" in data.keys() and "item_type.weapon" in data["traitIds"]]

            elif item_type == "Perk":
                valid_results = [data for data in valid_results if "traitIds" not in data.keys()]

        needy_results = [result for result in valid_results if result["displayProperties"]["name"].lower() == query.lower()]
        if needy_results:
            if item_type == "Weapon":
                power_caps = []
                for result in needy_results:
                    power_caps.append([(await destiny.decode_hash(version["powerCapHash"], "DestinyPowerCapDefinition"))["powerCap"] for version in result["quality"]["versions"]])
                power_caps = [max(caps) for caps in power_caps]
                higher_power_cap = max(power_caps)
                index = power_caps.index(higher_power_cap)
                if higher_power_cap <= 1260:
                    print(f"Item returned from query '{query}' is sunset, consider omitting")
                return needy_results[index]
            else:
                return needy_results[0]
        else:
            if len(valid_results) > 1:
                print(f"Amibiguous results from query '{query}'")
                [print(f"\t{valid_result}") for valid_result in valid_results]
            if len(valid_results) == 0:
                print(f"Failed to find 'good' result for query {query}")
            return valid_results[0] if valid_results else None


async def get_perk_hash(query: str):
    query = query.lower()
    if query in perk_hashes_cache.keys():
        return perk_hashes_cache[query]
    else:
        perk_item = await get_inventory_item(query, "Perk")
        perk_hash = perk_item["hash"]
        perk_hashes_cache[query] = perk_hash
        return perk_hash


for sheet in workbook:
    with open(output_path, "a") as appendfile:
        appendfile.write(f"\n\n\n//{sheet.title}")

    for row in tuple(sheet)[1:]:
        gun = row[0].value
        if gun and str(gun).strip():
            gun_item = loop.run_until_complete(get_inventory_item(gun))
            current_gun_name = gun_item["displayProperties"]["name"]
            current_gun_hash = gun_item["hash"]
            with open(output_path, "a") as appendfile:
                appendfile.write(current_gun_rolls_string)
                appendfile.write(f"\n\n//{current_gun_name}\n//notes:God Roll")
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
    current_gun_rolls_string = ""
