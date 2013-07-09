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


def get_chap_list(table_tag, base_url):
    """
    parses the list of all UN treaty chapters
    """
    soup = read_page(base_url + "ParticipationStatus.aspx")
    table = soup.find(lambda tag:tag.name == "table" and 
                                tag.has_attr("id") and 
                                tag["id"] == table_tag)
    df = []
    for row in table.find_all("tr")[0:]:
        col = row.find_all("td")
        chapter = col[0].get_text(strip = True)
        link = base_url + col[1].find("a").get("href")
        name = col[2].get_text(strip = True).lower()
        record = [chapter, link, name]
        df.append(record)
    print("chapter list successfully fetched")
    return df


def get_treaty_list(table_tag, base_url, chap_list):
    """
    gets list of all treaties and writes index file
    """
    df = []
    for chap in range(len(chap_list)):
        soup = read_page(str(chap_list[chap][1]))
        table = soup.find(lambda tag:tag.name == "table" and
                          tag.has_attr("id") and 
                          tag["id"] == table_tag)
        for row in table.find_all("tr")[0:]:
            col = row.find_all("td")
            number = col[0].get_text(strip = True)
            number = re.sub(".$", "", str(number))
            name = clean_entry(re.sub(r"\xc2|\xa0", "", col[1].get_text(strip = True))).lower()
            url = base_url + col[1].find("a").get("href")
            record = [chap_list[chap][0], number, name, url, chap_list[chap][1], chap_list[chap][2]]
            df.append(record)
    index_file = pd.DataFrame(df, columns = ["chapter_no", "treaty_no", 
                                             "treaty_name", "url", "chapter_url", "chapter_name"])
    index_file.to_csv("index.csv", index = False, encoding = "utf-8")
    print("treaty list successfully fetched")
    return df


def get_xml(treaty_url):
    """
    finds the XML link on a treaty page
    """
    soup = read_page(treaty_url)
    xml_link = soup.find(lambda tag:tag.name == "a" and
                         tag.has_attr("id") and
                         tag["id"] == "ctl00_ContentPlaceHolder1_lnkXml")
    xml_link = xml_link["href"]
    return read_page("http://treaties.un.org" + str(xml_link))


def clean_entry(datum, head=False):
    """
    removes cruft from data entry
    """
    datum = re.compile(r"<[^<]*?/?>|\t|\r|\n|\f|\[|\]").sub("", datum)
    datum = re.sub(r"\s+|\xc2|\xa0", " ", datum)
    if head:
        datum = re.sub("\d|,", "", datum)
    return datum.strip()


def get_normal_table(soup):
    """
    fetches data from the typical UN treaty page
    """
    table = soup.find(lambda tag:tag.name == "participants")
    if table is None:
        return None
    df = []
    for row in table.find_all("row"):
        data = row.find_all("entry")
        for i in range(len(data)):
            data[i] = clean_entry(data[i].get_text(strip = True))
            if i == 0:
                data[i] = clean_entry(data[i], True)
        df.append(data)
    return df


def get_special_table(soup):
    """
    function that fetches special cases that the normal function fails at
    """
    table = soup.find(lambda tag:tag.name == "specialtables")
    if table is None:
        return None
    df = []
    for row in table.find_all("tableheader"):
        labels = row.find_all("title")
        for i in range(len(labels)):
            labels[i] = labels[i].get_text(strip = True)
            if i == 0:
                labels[i] = clean_entry(labels[i], True)
            labels[i] = clean_entry(labels[i])
        df.append(labels)
    for row in table.find_all("row"):
        data = row.find_all("column")
        for i in range(len(data)):
            data[i] = clean_entry(data[i].get_text(strip = True))
        df.append(data)
    return df


def get_declarations(soup, treaty_id):
    """
    fetches any reservations that countries register for a particular treaty
    """
    table = soup.find(lambda tag:tag.name == "declarations")
    if table is not None:
        for row in table.find_all("declaration"):
            name = clean_entry(row.find("participant").get_text(strip = True).lower(), True)
            text = row.find_all(lambda tag:tag.name == "text" and 
                               tag.has_attr("type") and tag["type"] == "para")
            if os.path.exists("declarations/" + treaty_id + ".txt"):
                os.remove("declarations/" + treaty_id + ".txt")
            with open("declarations/" + treaty_id + ".txt", "a+") as f:
                f.writelines("#" + name.encode("utf-8") + "\n")
                for entry in text:
                    entry = clean_entry(entry.get_text(strip = True))
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
    treaty_list = get_treaty_list(chap_table_tag, base_url, chap_list)
    get_treaties(base_url, treaty_list)
