# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:50:12 2020

@author: Leo Isiah
"""

import pandas;
import sqlite3;
#%%
def setMax(df):
    if(df["TOTMIN"]<48):
        return 45;
    return 95;
#%%

conn = sqlite3.connect('bbgm.db');

try:
    
    conso_stats_temp = pandas.read_sql(sql="select 1 as Constant, * from Consolidated_Stats where TOTMIN >=36", con=conn);
    conso_stats = conso_stats_temp.drop(["Team", "TOTMIN"], axis=1)
    print(conso_stats)
    
    coefficients = pandas.read_excel("bbgm_init_data.xlsx", sheet_name="Coefficient", index_col="Attr");
    print(coefficients)
    
    ratings = conso_stats.dot(coefficients);
  
    conso_simple = conso_stats_temp[['PlayerId','Team', 'CompetitionId', 'YR']];
    
    conso_simple_ratings = pandas.concat([conso_simple, ratings], axis=1)
    print(conso_simple_ratings);
    
    conso_simple_ratings.to_sql("Raw_Ratings", conn, if_exists='append', index=False);

                      
finally:    
    conn.commit();
    conn.close();