# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:50:12 2020

@author: Leo Isiah
"""

#from selenium import webdriver;
#from selenium.webdriver.chrome.options import Options;
from msedge.selenium_tools import Edge, EdgeOptions;
import pandas;
import sqlite3;
import dateutil;

#%%
def getBirthDate(df):
    try:
        return dateutil.parser.parse(df["Birth Date"]);
    except:
        return None;

#%%
def getHeight(df):
    try:
        splitted = df["HT"].split("-");
        return 12*int(splitted[0]) + int(splitted[1]);
    except:
        return None;

#%%
options = EdgeOptions()
options.use_chromium = True
options.add_argument("headless")
options.add_argument("disable-gpu")

browser = Edge(options=options)
conn = sqlite3.connect('bbgm.db');

try:
    url = "https://basketball.realgm.com/national/tournament/2/FIBA-World-Cup/214/rosters";
    url = "https://basketball.realgm.com/national/tournament/6/FIBA-Asia-Cup/174/rosters"
    url = "https://basketball.realgm.com/national/tournament/4/FIBA-AfroBasket/175/rosters"
    url = "https://basketball.realgm.com/national/tournament/5/FIBA-AmeriCup/176/rosters"
    url = "https://basketball.realgm.com/national/tournament/7/EuroBasket/162/rosters"
           
    print(url + " Start")
    
    browser.get(url);
    browser.execute_script("""
    $(".tablesaw").find("thead tr").each(function() {	
    	tr = $(this);	
    	tr.prepend("<th>Id</th>");		
    	tr.append("<th>Nationality2</th>");		
    	tr.append("<th>College</th>");			
    });
                           """);
                           
    browser.execute_script("""
    $(".tablesaw").find("tbody tr").each(function() {	
    	tr = $(this);	
    	tr.prepend("<td></td>");
    	tr.append("<td></td>");
    	tr.append("<td></td>");
    
    	tr.find("td:eq(0)").text(tr.find("td:eq(1) a").attr("href").split("/").slice(-1)[0]);	
    	tr.find("td:eq(10)").text(tr.find("td:eq(7) a[href*='ncaa']").text());		
    	tr.find("td:eq(9)").text(tr.find("td:eq(8) a:eq(1)").text());
    	tr.find("td:eq(8)").text(tr.find("td:eq(8) a:eq(0)").text());			
    });
                           """);
    
    html = browser.page_source;
    
    dfs = pandas.read_html(html, parse_dates=True, na_values=["-"]);
    
    for df in dfs:                    
        df["Birth Date"] = df.apply(getBirthDate, axis=1);
        df["HT"] = df.apply(getHeight, axis=1);
        #df.to_sql("Player", conn, if_exists='append', index=False);
        for i in range(len(df)):
            try:
                df.iloc[i:i+1].to_sql("Player", conn, if_exists='append', index=False);
            except:
                pass
                    
    print(url + " End")                
                
finally:
    browser.quit();
    conn.commit();
    conn.close();                    