# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:50:12 2020

@author: Leo Isiah
"""

from msedge.selenium_tools import Edge, EdgeOptions;
import pandas;
import sqlite3;

options = EdgeOptions()
options.use_chromium = True
options.add_argument("headless")
options.add_argument("disable-gpu")

browser = Edge(options=options)
conn = sqlite3.connect('bbgm.db');

try:
    url = "https://basketball.realgm.com/national/tournament/2/FIBA-World-Cup/214/stats/2019";
    url = "https://basketball.realgm.com/national/tournament/6/FIBA-Asia-Cup/174/stats/2017"
    url = "https://basketball.realgm.com/national/tournament/4/FIBA-AfroBasket/175/stats/2017"
    url = "https://basketball.realgm.com/national/tournament/5/FIBA-AmeriCup/176/stats/2017"
    url = "https://basketball.realgm.com/national/tournament/7/EuroBasket/162/stats/2017"
    url_add_path_1s = ["Per_36", "Misc_Stats", "Advanced_Stats"]
    url_add_path_2 = "/All/player/All/asc/"
    
    
    splitted = url.split("/")
    competitionId = int(splitted[5]);
    competitionName = splitted[6];
    competitionYear = int(splitted[9]);
    
    competitionDf = pandas.DataFrame({'Id': [competitionId], 'Name': [competitionName]});
    try:
        competitionDf.to_sql("Competition", conn, if_exists='append', index=False);
    except:
        pass;
        
    page = 1;
    stop = False;
    
    while stop==False:
    
        for url_add_path_1 in url_add_path_1s:
            
            fullUrl = url+"/"+url_add_path_1+url_add_path_2+str(page);
            
            print(fullUrl+ " Start")
            
            browser.get(fullUrl);
            browser.execute_script("""
            $(".tablesaw").find("thead tr th:nth-child(1)").text("PlayerId");
                                   """);
                                   
            browser.execute_script("""
            $(".tablesaw").find("tbody tr").each(function() {
                    $(this).find("td:nth-child(1)").text($(this).find("td:nth-child(2) a").attr("href").split("/").slice(-1)[0]);   
            });                       
                                   """);
            
            html = browser.page_source;
            
            df = pandas.read_html(html)[0];
            
            df["CompetitionId"] = competitionId;
            df["YR"] = competitionYear;            
            
            for i in range(len(df)):
                try:
                    df.iloc[i:i+1].to_sql(url_add_path_1, conn, if_exists='append', index=False);
                except:
                    pass;
                
            
            if len(df)<100:
                stop = True;
                
            print(fullUrl+ " End")                
                
        page = page+1;            
    
finally:
    browser.quit();
    conn.commit();
    conn.close();                    


