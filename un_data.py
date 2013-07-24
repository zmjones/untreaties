# -*- coding: utf-8 -*-

import re
import sys
import os
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

def read_page(url):
    """
    downloads the page, sleeps for 60 seconds if this fails
    """
    try:
        html = requests.get(url).content
    except:
        print "sleeping..."
        time.sleep(60)
        html = requests.get(url).content
    return BeautifulSoup(html)


def read_table(url, table_tag):
    """
    then parses the specified html table
    """
    soup = read_page(url)
    return soup.find(lambda tag:tag.name == "table" and 
                            tag.has_attr("id") and 
                            tag["id"] == table_tag)

def get_chap_list(table_tag, base_url):
    """
    parses the list of all UN treaty chapters
    """
    table = read_table(base_url + "ParticipationStatus.aspx", table_tag)
    return [[td.get_text(strip=True)
             if td.find("a") is None 
             else base_url + td.find("a")["href"] 
             for td in tr.find_all("td")] 
             for tr in table.find_all("tr")]


def get_treaty_list(table_tag, base_url, chap_list):
    """
    gets list of all treaties and writes index file
    """
    df = []
    for chap in range(len(chap_list)):
        table = read_table(chap_list[chap][1], table_tag)
        for row in table.find_all("tr")[0:]:
            col = row.find_all("td")
            number = re.sub("\\.$", "", col[0].get_text(strip=True))
            name = clean(re.sub(r"\xc2|\xa0", "", col[1].get_text(strip=True)))
            url = base_url + col[1].find("a").get("href")
            df.append([chap_list[chap][0], number, name, url, 
                       chap_list[chap][1], chap_list[chap][2]])
    cols = ["chapter_no", "treaty_no", "treaty_name", "url", "chapter_url", "chapter_name"]
    pd.DataFrame(df, columns = cols).to_csv("index.csv", index=False, encoding="utf-8")
    return df


def clean(s, head=False):
    """
    removes cruft from data entry
    """
    s = re.compile(r"<[^<]*?/?>|\t|\r|\n|\f|\[|\]").sub("", s)
    s = re.sub(r"\s+|\xc2|\xa0", " ", s)
    if head:
        s = re.sub("\d|,", "", s)
    return s.strip()


def get_xml(treaty_url):
    """
    finds the XML link on a treaty page
    """
    soup = read_page(treaty_url)
    xml_link = soup.find(lambda tag:tag.name == "a" and
                         tag.has_attr("id") and
                         tag["id"] == "ctl00_ContentPlaceHolder1_lnkXml")
    return read_page("http://treaties.un.org" + str(xml_link["href"]))


def get_normal_table(soup):
    """
    fetches data from the typical UN treaty page
    """
    table = soup.find(lambda tag:tag.name == "participants")
    if table is None:
        return None
    return [[clean(td.get_text(strip=True))
             if td.find("a") is None 
             else base_url + td.find("a")["href"] 
             for td in tr.find_all("entry")] 
             for tr in table.find_all("row")]


def get_special_table(soup):
    """
    function that fetches special cases that the normal function fails at
    """
    table = soup.find(lambda tag:tag.name == "specialtables")
    if table is None:
        return None
    header = [[clean(td.get_text(strip=True), True)
               for td in tr.find_all("title")] 
               for tr in table.find_all("tableheader")]
    data = [[clean(td.get_text(strip=True))
             if td.find("a") is None 
             else base_url + td.find("a")["href"] 
             for td in tr.find_all("column")] 
             for tr in table.find_all("row")]
    return header + data


def get_declarations(soup, treaty_id):
    """
    fetches any reservations that countries register for a particular treaty
    """
    table = soup.find(lambda tag:tag.name == "declarations")
    if table is not None:
        for row in table.find_all("declaration"):
            name = clean(row.find("participant").get_text(strip=True), True)
            text = row.find_all(lambda tag:tag.name == "text" and 
                                       tag.has_attr("type") and 
                                       tag["type"] == "para")
            with open("declarations/" + treaty_id + ".txt", "a+") as f:
                f.writelines("#" + name.encode("utf-8") + "\n")
                for entry in text:
                    entry = clean(entry.get_text(strip=True))
                    f.writelines(entry.encode("utf-8"))
                f.writelines("\n\n")
            f.close()


def get_treaties(base_url, treaty_list):
    """
    fetches all treaty data and writes it to file
    """
    for treaty in range(len(treaty_list)):
        soup = get_xml(str(treaty_list[treaty][3]))
        df = get_normal_table(soup)
        if df is None:
            df = get_special_table(soup)
        treaty_id = str(treaty_list[treaty][0]) + "-" + str(treaty_list[treaty][1])
        treaty_id = re.sub("\.", "-", treaty_id)
        if not os.path.exists("declarations"):
            os.makedirs("declarations")
        if os.path.exists("declarations/" + treaty_id + ".txt"):
            os.remove("declarations/" + treaty_id + ".txt")
        get_declarations(soup, treaty_id)
        if not os.path.exists("treaties"):
            os.makedirs("treaties")
        df = pd.DataFrame(df)
        if not df.empty: 
            df.ix[:, 0] = df.ix[:, 0].map(lambda x: re.sub("\d|,", "", x))
            df.to_csv("treaties/" + treaty_id + ".csv", header = False, index = False, encoding = "utf-8")
        sys.stdout.write(str(treaty) + " of " + str(len(treaty_list)) + " complete\r")
        sys.stdout.flush()


base_url = "http://treaties.un.org/pages/"
chap_list_table_tag = "ctl00_ContentPlaceHolder1_dgChapterList"
chap_table_tag = "ctl00_ContentPlaceHolder1_dgSubChapterList"

if __name__ == "__main__":
    chap_list = get_chap_list(chap_list_table_tag, base_url)
    print("chapter list successfully fetched")
    treaty_list = get_treaty_list(chap_table_tag, base_url, chap_list)
    print("treaty list successfully fetched")
    get_treaties(base_url, treaty_list)
