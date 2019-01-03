import sqlite3
import pandas as pd
#Name of Excel xlsx file. SQLite database will have the same name and extension .db
filename="output/Pokedex"
con = sqlite3.connect(filename+".db")
wb = pd.read_excel(filename+'.xlsx',sheet_name=None)
for sheet in wb:
    wb[sheet].to_sql(sheet, con, index=False, if_exists="replace")
con.commit()
con.close()
