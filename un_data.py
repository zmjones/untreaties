# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib2 import urlopen
from mechanize import Browser
import re, sys, os, unicodedata, csv
from datetime import datetime
import pandas as pd

def read_page(url):
    mech = Browser()
    page = mech.open(url)
    html = page.read()
    soup = BeautifulSoup(html.decode("utf-8", "ignore"))
    return soup

def get_chap_list(table_tag, base_url):
    soup = read_page(base_url + "ParticipationStatus.aspx")
    table = soup.find(lambda tag:tag.name == "table" and 
                                tag.has_attr("id") and 
                                tag["id"] == table_tag)
    df = []
    for row in table.findAll("tr")[0:]:
        col = row.findAll("td")
        chapter = col[0].get_text(strip = True)
        link = base_url + col[1].find("a").get("href")
        name = col[2].get_text(strip = True)
        record = [chapter, link, name]
        df.append(record)
    print("chapter list successfully fetched")
    return df

def get_treaty_list(table_tag, base_url, chap_list):
    df = []
    for chap in range(0, len(chap_list)):
        soup = read_page(str(chap_list[chap][1]))
        table = soup.find(lambda tag:tag.name == "table" and
                          tag.has_attr("id") and 
                          tag["id"] == table_tag)
        for row in table.findAll("tr")[0:]:
            col = row.findAll("td")
            number = col[0].get_text(strip = True)
            number = re.sub(".$", "", str(number))
            name = col[1].get_text(strip = True)
            name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore")
            url = base_url + col[1].find("a").get("href")
            record = [chap_list[chap][0], number, name, url, chap_list[chap][1], chap_list[chap][2]]
            df.append(record)
    index_file = pd.DataFrame(df, columns = ["chapter_no", "treaty_no", 
                                             "treaty_name", "url", "chap_url", "chap_name"])
    index_file.to_csv("index.csv", index = False, encoding = "utf-8")
    print("treaty list successfully fetched")
    return df            

def get_treaties(table_tag, base_url, treaty_list):
    for treaty in range(0, len(treaty_list)):
        soup = read_page(str(treaty_list[treaty][3]))
        table = soup.find(lambda tag:tag.name == "table" and 
                          tag.has_attr("id") and 
                          tag["id"] == table_tag)
        df = []
        for row in table.findAll("tr"):
            data = row.findAll("td")
            for i in range(0, len(data)):
                data[i] = data[i].get_text(strip = True)
                if i == 0:
                    data[i] = re.sub("\d|,", "", data[i])
                data[i] = re.sub("\t", "", data[i])
                data[i] = unicodedata.normalize("NFKD", data[i]).encode("ascii", "ignore")
            df.append(data)
        filename = str(treaty_list[treaty][0]) + "-" + str(treaty_list[treaty][1])
        if not os.path.exists("data"):
            os.makedirs("data")
        pd.DataFrame(df).to_csv("data/" + filename + ".csv", header = False, index = False)
        sys.stdout.write(str(treaty) + " of " + str(len(treaty_list)) + " complete\r")
        sys.stdout.flush()

def htmlize_treaty_list(treaty_list):
    f = open('index.html', 'w')
    data_url = "https://raw.github.com/zmjones/untreaties/master/data/"
    f.write("""<html lang="en"><head><title></title></head><body><h1><center>U.N. Treaty Data</center></h1>""")
    f.write("""<link rel="stylesheet" href="style.css" type="text/css"/>""")
    f.write("""<p>This page contains all United Nations tready data listed at 
               <a href="http://treaties.un.org/pages/ParticipationStatus.aspx">treaties.un.org</a>.
                The chapter and treaty links return you to the UN treaty or chapter page and the "CSV"
                link downloads the treaty data. Utilities to clean and transform the data further, as 
                well as the scripts that scraped this data can be found at
                <a href="http://github.com/zmjones/untreaties">http://github.com/zmjones/untreaties</a></p>""")
    f.write("""<table border="1" class="padded-table">""")
    for i in range(0, len(treaty_list)):
        if i == 0:
            f.write("""<tr><th>chapter no.</th><th>chapter name</th><th>treaty no.</th>
                       <th>treaty name</th><th>data</th></tr>""")
        chap =  str(treaty_list[i][0])
        treaty = str(treaty_list[i][1])
        url = data_url + chap + "-" + treaty + ".csv"
        f.write("<tr>")
        f.write("<td>" + treaty_list[i][0] + "</td>")
        f.write("<td><a href = \"" + treaty_list[i][4] + "\">" + treaty_list[i][5] + "</a></td>")
        f.write("<td>" + treaty_list[i][1] + "</td>")
        f.write("<td><a href = \"" + treaty_list[i][3] + "\">" + treaty_list[i][2] + "</a></td>")
        f.write("<td><a href = \"" + url + "\">csv</a></td>")
        f.write("</tr>")
    f.write("</table></body></html>")

base_url = "http://treaties.un.org/pages/"

chap_list_table_tag = "ctl00_ContentPlaceHolder1_dgChapterList"
chap_list = get_chap_list(chap_list_table_tag, base_url)

chap_table_tag = "ctl00_ContentPlaceHolder1_dgSubChapterList"
treaty_list = get_treaty_list(chap_table_tag, base_url, chap_list)
            
treaties_table_tag = "ctl00_ContentPlaceHolder1_tblgrid"
get_treaties(treaties_table_tag, base_url, treaty_list)

htmlize_treaty_list(treaty_list)
