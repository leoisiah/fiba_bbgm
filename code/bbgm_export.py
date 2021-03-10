# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 17:28:39 2020

@author: Leo Isiah
"""

import pandas;
import sqlite3;
import math;
import json;

# edit this
year = 2021

#%%
def adjustRating(x):
    return min(max(round(x),0),100);

#%%
def computeWeight(ht, wt):
    if(math.isnan(wt)):
        return round(2.7*ht);
    return round(wt);

#%%
def computeBirthLoc(city, country):
    if(city is None):
        return country;
    return city+", "+country;

#%%
def computeCollege(college):
    if(college is None):
        return "";
    return college;

#%%
def generateJson(conn):
    
    filename = str(year-1)+"-"+str((year)%100)+".FIBA.json"
    
    teamMap = {};
	
    teamsSql = pandas.read_sql(sql="""
        select * from Team where Name in (select NationalTeam2 from Output)
        order by Rank""", con=conn);
    
    teamsJson = [];

    numTeams = 0;
		
    for i, row in teamsSql.iterrows():           
        teamMap[row["Name"]] = i;
        teamJson = {"tid": i, "cid": 0, "did": 0, "region": row["ISO3"], "name": row["Name"], "abbrev": row["ISO3"], "imgURL": "https://www.countryflags.io/"+row["ISO2"]+"/shiny/64.png", "pop": 10, }
        teamsJson.append(teamJson);
        numTeams = numTeams + 1;
		
    playersSql = pandas.read_sql(sql="""
        select * from Output
        order by NationalTeam2""", con=conn);
   
    playersJson = [];
    
    for i, row in playersSql.iterrows():           
        playerJson = {"tid": teamMap[row["NationalTeam2"]], 
                      "name": row["Player"], 
                      "ratings": [{"diq": adjustRating(row["dIQ"]), 
                                   "dnk": adjustRating(row["Dnk"]), 
                                   "drb": adjustRating(row["Drb"]), 
                                   "endu": adjustRating(row["End"]), 
                                   "fg": adjustRating(row["2Pt"]), 
                                   "ft": adjustRating(row["FT"]), 
                                   "hgt": adjustRating(row["Hgt"]), 
                                   "ins": adjustRating(row["Ins"]), 
                                   "jmp": adjustRating(row["Jmp"]), 
                                   "oiq": adjustRating(row["oIQ"]), 
                                   "pss": adjustRating(row["Pss"]), 
                                   "reb": adjustRating(row["Reb"]), 
                                   "spd": adjustRating(row["Spd"]), 
                                   "stre": adjustRating(row["Str"]), 
                                   "tp": adjustRating(row["3Pt"])}], 
                      "pos": row["Pos"], 
                      "hgt": row["HT"], 
                      "weight": computeWeight(row["HT"], row["WT"]), 
                      "born": {"year": int(row["Birth Date"][0:4]), "loc": computeBirthLoc(row["Birth City"], row["Nationality"])}, 
                      "college": computeCollege(row["College"]),
                      }
        playersJson.append(playerJson);		            
		
    output = {"version":36, "startingSeason":year, "players":playersJson, "teams":teamsJson, 
              "gameAttributes": [{"key": "numDraftRounds", "value": 1}, {"key": "homeCourtAdvantage", "value": 0}, {"key": "numGames", "value": numTeams-1}, {"key": "aiTradesFactor", "value": 0}, {"key": "challengeNoTrades", "value": True}, {"key": "draftType", "value": "noLotteryReverse"}, {"key": "foulsNeededToFoulOut", "value": 5}, {"key": "minRosterSize", "value": 8}, {"key": "maxRosterSize", "value": 12}, {"key": "numSeasonsFutureDraftPicks", "value": 0}, {"key": "quarterLength", "value": 10}, {"key": "maxContract", "value": 6000}, {"key": "minPayroll", "value": 0}, {"key": "defaultStadiumCapacity", "value": 50000}, {"key": "numGamesPlayoffSeries", "value": [1,1,1,1,1]}, {"key": "confs", "value": [{"cid": 0, "name": "Conference"}]}, {"key": "divs", "value": [{"did": 0, "cid": 0, "name": "Division"}]}, ]}


        
			  
    outJson = json.dumps(output, indent=4)
        
    with open(filename, "w") as fw:
        fw.write(outJson);
			
    print("OUTPUT: "+filename);    

    
#%%   
conn = sqlite3.connect('bbgm.db');

try:  
    generateJson(conn);    
finally:    
    conn.close();
