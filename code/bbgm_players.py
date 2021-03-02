# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:50:12 2020

@author: Leo Isiah
"""

from selenium import webdriver;
#from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.chrome.options import Options;
#from msedge.selenium_tools import Edge, EdgeOptions;
import pandas;
import sqlite3;
import dateutil;

import requests;
from bs4 import BeautifulSoup;

# edit this
year = 2013

baseUrl = "https://basketball.realgm.com"

req = requests.get(baseUrl + "/national/tournament/2/FIBA-World-Cup/214/rosters")
soup = BeautifulSoup(req.content, 'html.parser')
latestWorldCup = [m for m in soup.find("label", string="Year:").find_next("select").select("option") if int(m.text) < year][0]

req = requests.get(baseUrl + "/national/tournament/1/Olympic-Games/157/rosters")
soup = BeautifulSoup(req.content, 'html.parser')
latestOlympic = [m for m in soup.find("label", string="Year:").find_next("select").select("option") if int(m.text) < year][0]

worldCompetitionRostersUrl = "banana";

if int(latestWorldCup.text) > int(latestOlympic.text): 
    worldCompetitionRostersUrl = baseUrl + latestWorldCup["value"]
else:
    worldCompetitionRostersUrl = baseUrl + latestOlympic["value"]

nba1RosterUrl = baseUrl + "/nba/players/" + str(year-2)
nba2RosterUrl = baseUrl + "/nba/players/" + str(year-1)
dLg1RosterUrl = baseUrl + "/dleague/players/" + str(year-2)
dLg2RosterUrl = baseUrl + "/dleague/players/" + str(year-1)

rosterUrls = [worldCompetitionRostersUrl, nba1RosterUrl, nba2RosterUrl, dLg1RosterUrl, dLg2RosterUrl]

req = requests.get(baseUrl + "/international/league/1/Euroleague/players")
soup = BeautifulSoup(req.content, 'html.parser')

tempUrl2 = baseUrl + soup.find("label", string="Season:").find_next("select").select("option[value$='"+str(year-1)+"']")[0]['value']
req = requests.get(tempUrl2)
soup = BeautifulSoup(req.content, 'html.parser')

rosterUrls.extend([baseUrl + m['value'] + "/" + str(year-1) for m in soup.find("label", string="League:").find_next("select").select("option")])
rosterUrls = ["https://basketball.realgm.com/international/league/85/Premier-Basketball-League/players/78/2012"]
#%%
def getBirthDate(df):
    try:
        return dateutil.parser.parse(df["Birth Date"]);
    except:
        return None;

#%%
def getHeight(df):
    try:
        splittedTemp = df["HT"].split("-");
        return 12*int(splittedTemp[0]) + int(splittedTemp[1]);
    except:
        return None;

#%%
def getBirthDateFromDraftStatus(df):
    try:
        text = df["Draft Status"];
        age = 22;
        if "Pick" in text:
            age = 20;
        return "Jan 1, " + str(int(text[0:4])-age);
    except:
        return None;

#%%
def getBirthDateFromNBADraftStatus(df):
    try:
        text = df["NBA Draft Status"];
        age = 22;
        if "Pick" in text:
            age = 20;
        return "Jan 1, " + str(int(text[0:4])-age);
    except:
        return None;
        
#%%
def getBirthDateFromAge(df):
    try:
        age = df["Age"];
        return "Jan 1, " + str(year-1-age);
    except:
        return None;
        
conn = sqlite3.connect('bbgm.db');

try:        
    for url in rosterUrls :
        browser =  webdriver.PhantomJS(service_args=['--load-images=no'])
               
        print(url + " Start")
        splitted = url.split("/");                 
        
        browser.get(url);
        browser.execute_script("""
        $(".tablesaw").find("thead tr").each(function() {    
            tr = $(this);                    
            tr.prepend("<th>Id</th><th>College</th><th>Nationality2</th>");                
        });
                               """);
                               
        browser.execute_script("""
        $(".tablesaw").find("tbody tr").each(function() {    
            tr = $(this);    
            tr.prepend("<td></td>");
            tr.prepend("<td></td>");
            tr.prepend("<td></td>");            
        
            tr.find("td:eq(0)").text(tr.find("a[href*='/player/']").attr("href").split("/").slice(-1)[0]);            
            tr.find("td:eq(1)").text(tr.find("a[href*='/ncaa']").text());        
            tr.find("td:eq(2)").text(tr.find("a[href*='/nationality/']:eq(1)").text());
            nat_link = tr.find("a[href*='/nationality/']:eq(0)");
            nat_link.closest("td").html(nat_link.text())
        });
                               """);                          
                               
        html = browser.page_source;
        
        dfs = pandas.read_html(html, parse_dates=True, na_values=["-"]);

        cols = ["Id", "Player", "Pos", "HT", "WT", "Birth City", "Birth Date", "Nationality", "Nationality2", "NationalTeam", "College"];
        
        for df in dfs:                    
            
            if 'Draft Status' in df.columns:
                df["Birth Date"] = df.apply(getBirthDateFromDraftStatus, axis=1);

            if 'NBA Draft Status' in df.columns:
                df["Birth Date"] = df.apply(getBirthDateFromNBADraftStatus, axis=1);

                
            if 'Age' in df.columns:
                df["Birth Date"] = df.apply(getBirthDateFromAge, axis=1);        
            
            df["Birth Date"] = df.apply(getBirthDate, axis=1);
            df["HT"] = df.apply(getHeight, axis=1);
            
            if splitted[3]=="national":
                nationalTeam = (df["Nationality"].append(df["Nationality2"])).value_counts().keys()[0];
                print(nationalTeam);
                cursor = conn.cursor();
                cursor.execute("SELECT COUNT(1) from Player where NationalTeam = '{tm}'".format(tm=nationalTeam));
                count  = cursor.fetchone()[0]

                if count == 0:
                    df["NationalTeam"] = nationalTeam;
                else:
                    print("SKIPPING " + nationalTeam);
                             
            for i in range(len(df)):
                try:
                    df.iloc[i:i+1].filter(cols).to_sql("Player", conn, if_exists='append', index=False);
                except:            
                    pass
            
            conn.execute("delete from Player where NationalTeam is not null and NationalTeam<>Nationality and NationalTeam<>Nationality2")
            conn.execute("update Player set Nationality = 'Puerto Rico', Nationality2 = NULL where Nationality = 'Puerto Rico' and Nationality2 = 'United States' ")                
            conn.execute("update Player set Nationality = 'Puerto Rico', Nationality2 = NULL where Nationality = 'United States' and Nationality2 = 'Puerto Rico' ")                
            conn.execute("update Player set NationalTeam = 'Puerto Rico' where Nationality = 'Puerto Rico' and Nationality2 is NULL and NationalTeam is not NULL ")
            
        conn.execute("UPDATE Player set Pos = 'GF' where Pos = 'G-F' ")
        conn.execute("UPDATE Player set Pos = 'FC' where Pos = 'F-C' ")
        conn.execute("UPDATE Player set Pos = 'GF' where Pos = 'F-G' ")
        conn.execute("UPDATE Player set Pos = 'FC' where Pos = 'C-F' ")

        browser.quit();		
        print(url + " End")                
                    
finally:    
    conn.commit();
    conn.close();                    