# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:50:12 2020

@author: Leo Isiah
"""

from selenium import webdriver;
#from selenium.webdriver.firefox.options import Options
#from msedge.selenium_tools import Edge, EdgeOptions;
import pandas;
import sqlite3;

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

worldCompetitionStatsUrl = "banana";

if int(latestWorldCup.text) > int(latestOlympic.text): 
    worldCompetitionStatsUrl = baseUrl + latestWorldCup["value"].replace("rosters", "stats") + "/" + latestWorldCup.text
else:
    worldCompetitionStatsUrl = baseUrl + latestOlympic["value"].replace("rosters", "stats") + "/" + latestOlympic.text

nba1StatsUrl = baseUrl + "/nba/stats/" + str(year-2)
nba2StatsUrl = baseUrl + "/nba/stats/" + str(year-1)
dLg1StatsUrl = baseUrl + "/dleague/stats/" + str(year-2)
dLg2StatsUrl = baseUrl + "/dleague/stats/" + str(year-1)

statUrls = [worldCompetitionStatsUrl, nba1StatsUrl, nba2StatsUrl, dLg1StatsUrl, dLg2StatsUrl]

req = requests.get(baseUrl + "/international/league/1/Euroleague/players")
soup = BeautifulSoup(req.content, 'html.parser')

tempUrl2 = baseUrl + soup.find("label", string="Season:").find_next("select").select("option[value$='"+str(year-1)+"']")[0]['value']
req = requests.get(tempUrl2)
soup = BeautifulSoup(req.content, 'html.parser')

statUrls.extend([baseUrl + m['value'].rsplit("/",1)[0].replace("players", "stats") + "/" + str(year-1) for m in soup.find("label", string="League:").find_next("select").select("option")])

conn = sqlite3.connect('bbgm.db');

try:
    for url in statUrls :
        try:
            
            browser = 0;
        
            url_add_path_1s = ["Per_36", "Misc_Stats", "Advanced_Stats"]
            #url_add_path_1s = ["Per_36", "Misc_Stats"]    
            url_add_path_2 = "/All/player/All/asc/"    
            
            splitted = url.split("/");
            
            competitionYear = int(splitted[-1]);
            
            if splitted[3]=="national":
                competitionName = splitted[6];
            if splitted[3]=="international":
                competitionName = splitted[6];    
                url_add_path_2 = "/All/All/player/All/asc/";
            if splitted[3]=="nba":
                competitionName = "NBA";
            if splitted[3]=="dleague":
                competitionName = "DLeague";
            
            cursor = conn.cursor();
            cursor.execute("SELECT COUNT(1) from Per_36 where Competition = '{comp}' and YR = {compYR}".format(comp=competitionName, compYR=competitionYear));
            count  = cursor.fetchone()[0]
            if count > 0:
                print("SKIPPED " + competitionName + " " + str(competitionYear))
                continue;
            
            browser =  webdriver.PhantomJS(service_args=['--load-images=no'])
            
            page = 1;
            stop = False;
            
            while stop==False:
            
                for url_add_path_1 in url_add_path_1s:
                    
                    fullUrl = url+"/"+url_add_path_1+url_add_path_2+str(page);
                    
                    print(fullUrl+ " Start")
                    
                    html = "";
                    df = "";
                    
                    #browser =  webdriver.PhantomJS(service_args=['--load-images=no'])
                    browser.get(fullUrl);
                    browser.execute_script("""
                    $(".scoreboard").remove();
                                           """);            

                    browser.execute_script("""
                    $(".tablesaw").find("thead tr th:nth-child(1)").text("StatId");
                                           """);
                                           
                    browser.execute_script("""                                   
                    $(".tablesaw").find("thead tr th:nth-child(2)").text("PlayerId");
                                           """);            
                                           
                    browser.execute_script("""
                    $(".tablesaw").find("tbody tr").each(function() {
                            $(this).find("td:nth-child(2)").text($(this).find("td:nth-child(2) a").attr("href").split("/").slice(-1)[0]);   
                    });                       
                                           """);
                                           
                    browser.execute_script("""
                    $(".tablesaw").find("td").filter(function(){ return $(this).text() == '-';}).text("0");
                                           """);

                    html = browser.page_source;
                    #browser.quit();
                    
                    df = pandas.read_html(html)[0];
                    
                    df["Competition"] = competitionName;
                    df["YR"] = competitionYear;            
                    
                    df.drop('eDiff', inplace=True, axis=1, errors="ignore");
                    df.drop('Team', inplace=True, axis=1, errors="ignore");
                    df.drop('Pos', inplace=True, axis=1, errors="ignore");
                    
                    df.to_sql(url_add_path_1, conn, if_exists='append', index=False);                
                    
                    if len(df)<100:
                        stop = True;
                        
                    print(fullUrl+ " End")                
                        
                page = page+1;    
        except Exception as e:
            print(e)
            pass;
        finally:
            if browser != 0:
                browser.quit();        
finally:
    conn.commit();
    conn.close();                    


