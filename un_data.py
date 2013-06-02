# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from urllib2 import urlopen
from mechanize import Browser
import pandas as pd
import re, sys, os, unicodedata

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
            name = col[1].get_text(strip = True)
            url = col[1].find("a").get("href")
            record = [chap_list[chap][0], number, name, url]
            df.append(record)
    print("treaty list successfully fetched")
    return df
            
def get_treaties(table_tag, base_url, treaty_list):
    df = []
    for treaty in range(0, len(treaty_list)):
        soup = read_page(base_url + str(treaty_list[treaty][3]))
        table = soup.find(lambda tag:tag.name == "table" and 
                          tag.has_attr("id") and 
                          tag["id"] == table_tag)
        for row in table.findAll("tr")[1:]:
            col = row.findAll("td")
            country = col[0].get_text(strip = True)
            sig = col[1].get_text(strip = True)
            if len(col) == 2:
                adr = "NA"
            elif len(col) == 3:
                adr = col[2].get_text(strip = True)
            else:
                print(str(treaty_list[treaty][0]) + "-" + str(treaty_list[treaty][1]) + 
                      " error        ")
                break
            record = [treaty_list[treaty][0], treaty_list[treaty][1],
                      unicodedata.normalize("NFKD", treaty_list[treaty][2]).encode("ascii", "ignore"), 
                      country, sig, adr]
            df.append(record)
        sys.stdout.write(str(treaty) + " of " + str(len(treaty_list)) + " complete\r")
        sys.stdout.flush()
    return df

base_url = "http://treaties.un.org/pages/"

chap_list_table_tag = "ctl00_ContentPlaceHolder1_dgChapterList"
chap_list = get_chap_list(chap_list_table_tag, base_url)

chap_table_tag = "ctl00_ContentPlaceHolder1_dgSubChapterList"
treaty_list = get_treaty_list(chap_table_tag, base_url, chap_list)
            
treaties_table_tag = "ctl00_ContentPlaceHolder1_tblgrid"
treaty_data = get_treaties(treaties_table_tag, base_url, treaty_list)

treaty_data = pd.DataFrame(treaty_data, columns = ["chapter", "treaty_no", "treaty_name", 
                                                   "country", "sig_date", "adr_date"])

if not os.path.exists("data"):
    os.makedirs("data")

treaty_data.to_csv("./data/un_data.csv", na_rep = "NA", encoding = "utf-8")
