# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 17:28:39 2020

@author: Leo Isiah
"""

import pandas;
import sqlite3;
import math;
import json;
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
competitionId = 2;
year = 2019;

filename = str(year)+"-"+str((year+1)%100)+".FIBA.json"

teamMap = {};
confMap = {0:0, 1:1, 2:1, 3:0};
divMap = {0:0, 1:3, 2:4, 3:1, 4:2, 5:5, 6:5, 7:2, 8:1, 9:4, 10:3, 11:0}

conn = sqlite3.connect('bbgm.db');

try:  
    teamsSql = pandas.read_sql(sql="""
        select * from Team 
        where Name in
        (
        select Team from Adjusted_Ratings
        where CompetitionId = {competitionId}
        and YR = {year}
        group by Team
        having count(1) >= 10
        )
        order by Rank""".format(competitionId=competitionId, year=year), con=conn);
    
    teamsJson = [];
    
    for i, row in teamsSql.iterrows():           
        teamMap[row["Name"]] = i;
        teamJson = {"tid": i, "cid": confMap[i%4], "did": divMap[i%12], "region": row["IOC3"], "name": row["Name"], "abbrev": row["IOC3"], "imgURL": "https://www.countryflags.io/"+row["IOC2"]+"/shiny/64.png"}
        teamsJson.append(teamJson);
               
    playersSql = pandas.read_sql(sql="""
        select * from Player p, Adjusted_Ratings a
        where p.Id = a.PlayerId
        and a.CompetitionId = {competitionId}
        and a.YR = {year}
        and a.Team in
        (
        select Team from Adjusted_Ratings
        where CompetitionId = {competitionId}
        and YR = {year}
        group by Team
        having count(1) >= 10
        )
        order by a.Team""".format(competitionId=competitionId, year=year), con=conn);
   
    playersJson = [];
    
    for i, row in playersSql.iterrows():           
        playerJson = {"tid": teamMap[row["Team"]], 
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
                      "contract":{"amount":30000,"exp":year+31},}
        playersJson.append(playerJson);

        
        output = {"version":36, "players":playersJson, "teams":teamsJson, 
                  f"gameAttributes": [{"key": "aiTradesFactor", "value": 0}, {"key": "challengeNoTrades", "value": True}, {"key": "draftType", "value": "random"}, {"key": "foulsNeededToFoulOut", "value": 5}, {"key": "maxRosterSize", "value": 19}, {"key": "numSeasonsFutureDraftPicks", "value": 0}, {"key": "quarterLength", "value": 10}]}
        
        outJson = json.dumps(output, indent=4)
        
        with open(filename, "w") as fw:
            fw.write(outJson);
finally:    
    conn.close();
