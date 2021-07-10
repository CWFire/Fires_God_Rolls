from openpyxl import load_workbook
from os import path, getcwd

workbook_path = path.join(getcwd(), "..", "God Rolls.xlsx",)

workbook = load_workbook(filename=workbook_path, data_only=True)
for sheet in workbook:
    print(sheet["A1"].value)

