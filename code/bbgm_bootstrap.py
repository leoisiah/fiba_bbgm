# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:50:12 2020

@author: Leo Isiah
"""

import pandas;
import sqlite3;

#%%

conn = sqlite3.connect('bbgm.db');

try:
    tableNames = ["Position", "Team"];
    for tableName in tableNames:
        df = pandas.read_excel("bbgm_init_data.xlsx", sheet_name=tableName);
                          
        for i in range(len(df)):
            try:
                df.iloc[i:i+1].to_sql(tableName, conn, if_exists='append', index=False);
            except:
                pass;
                
finally:    
    conn.commit();
    conn.close();                    