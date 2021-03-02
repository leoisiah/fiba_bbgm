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
    
    conso_stats_temp = pandas.read_sql(sql="select 1 as Constant, * from Consolidated_Stats where TOTMIN >= 36", con=conn);
		
    conso_stats = conso_stats_temp.drop(["StatId", "Competition", "YR", "PlayerId", "TOTMIN"], axis=1)
    print(conso_stats)
    
    coefficients = pandas.read_excel("bbgm_init_data.xlsx", sheet_name="Coefficient", index_col="Attr");
    print(coefficients)       
	
    ratings = conso_stats.dot(coefficients);
  
    conso_simple = conso_stats_temp[["StatId", "Competition", "YR", "PlayerId"]];
    
    conso_simple_ratings = pandas.concat([conso_simple, ratings], axis=1)
    print(conso_simple_ratings);
    conn.execute("DELETE from Raw_Ratings")                            
    conso_simple_ratings.to_sql("Raw_Ratings", conn, if_exists='append', index=False);

                      
finally:    
    conn.commit();
    conn.close();