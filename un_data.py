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
        link = col[1].find("a").get("href")
        name = col[2].get_text(strip = True)
        record = [chapter, link, name]
        df.append(record)
    print("chapter list successfully fetched")
    return df

def get_treaty_list(table_tag, base_url, chap_list):
    df = []
    for chap in range(0, len(chap_list)):
        soup = read_page(base_url + str(chap_list[chap][1]))
        table = soup.find(lambda tag:tag.name == "table" and
                          tag.has_attr("id") and 
                          tag["id"] == table_tag)
        for row in table.findAll("tr")[0:]:
            col = row.findAll("td")
            number = col[0].get_text(strip = True)
            number = re.sub(".$", "", str(number))
            name = col[1].get_text(strip = True)
            name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore")
            url = col[1].find("a").get("href")
            record = [chap_list[chap][0], number, name, base_url + str(url)]
            df.append(record)
    index_file = pd.DataFrame(df, columns = ["chapter_no", "treaty_no", "treaty_name", "url"])
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

base_url = "http://treaties.un.org/pages/"

chap_list_table_tag = "ctl00_ContentPlaceHolder1_dgChapterList"
chap_list = get_chap_list(chap_list_table_tag, base_url)

chap_table_tag = "ctl00_ContentPlaceHolder1_dgSubChapterList"
treaty_list = get_treaty_list(chap_table_tag, base_url, chap_list)
            
treaties_table_tag = "ctl00_ContentPlaceHolder1_tblgrid"
get_treaties(treaties_table_tag, base_url, treaty_list)
