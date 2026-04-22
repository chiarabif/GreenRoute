# Can otehrs see tis?????

import pandas as pd

# Load the Excel file
df = pd.read_excel("GreenRoute/data/Excel-data.xlsx")


# Show first rows
print(df.head())

# Show column names
print(df.columns)

xls = pd.ExcelFile("GreenRoute/data/Excel-data.xlsx")
print(xls.sheet_names)