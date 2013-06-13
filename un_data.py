# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re, sys, os, unicodedata, csv, requests
import pandas as pd

def read_page(url):
    soup = BeautifulSoup(requests.get(url).content)
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

def get_xml(treaty_url):
    soup = read_page(treaty_url)
    xml_link = soup.find(lambda tag:tag.name == "a" and
                         tag.has_attr("id") and
                         tag["id"] == "ctl00_ContentPlaceHolder1_lnkXml")
    xml_link = xml_link["href"]
    soup = read_page("http://treaties.un.org" + str(xml_link))

    return soup

def clean_entry(datum, head = False):
    datum = re.sub("\t|<title>|</title>|<superscript>|</superscript>", "", datum)

    if type(datum) is unicode:
        datum = unicodedata.normalize("NFKD", datum).encode("ascii", "ignore")

    if head:
        datum = re.sub("\d|,", "", datum)

    return datum

def get_normal_table(soup):
    table = soup.find(lambda tag:tag.name == "participants")

    if table is None:
        return None
        
    df = []

    for row in table.findAll("row"):
        data = row.findAll("entry")
        for i in range(0, len(data)):
            data[i] = data[i].get_text(strip = True)
            if i == 0:
                data[i] = clean_entry(data[i], True)
            data[i] = clean_entry(data[i])
        df.append(data)
    
    return df

def get_special_table(soup):
    table = soup.find(lambda tag:tag.name == "specialtables")

    if table is None:
        return None

    df = []

    for row in table.findAll("tableheader"):
        labels = row.findAll("title")
        for i in range(0, len(labels)):
            labels[i] = labels[i].get_text(strip = True)
            if i == 0:
                labels[i] = clean_entry(labels[i], True)
            labels[i] = clean_entry(labels[i])
        df.append(labels)

    for row in table.findAll("row"):
        data = row.findAll("column")
        for i in range(0, len(data)):
            data[i] = data[i].get_text(strip = True)
            data[i] = clean_entry(data[i])
        df.append(data)

    return df

def get_treaties(base_url, treaty_list):
    for treaty in range(0, len(treaty_list)):
        soup = get_xml(str(treaty_list[treaty][3]))

        df = get_normal_table(soup)
        
        if df is None:
            df = get_special_table(soup)

        filename = str(treaty_list[treaty][0]) + "-" + str(treaty_list[treaty][1])

        if not os.path.exists("data"):
            os.makedirs("data")

        df = pd.DataFrame(df)

        if not df.empty: 
            df.ix[:, 0] = df.ix[:, 0].map(lambda x: re.sub("\d|\[|\]|,", "", x))
            df.to_csv("data/" + filename + ".csv", header = False, index = False)

        sys.stdout.write(str(treaty) + " of " + str(len(treaty_list)) + " complete\r")
        sys.stdout.flush()

base_url = "http://treaties.un.org/pages/"

chap_list_table_tag = "ctl00_ContentPlaceHolder1_dgChapterList"
chap_list = get_chap_list(chap_list_table_tag, base_url)

chap_table_tag = "ctl00_ContentPlaceHolder1_dgSubChapterList"
treaty_list = get_treaty_list(chap_table_tag, base_url, chap_list)
            
treaties_table_tag = "ctl00_ContentPlaceHolder1_tblgrid"
get_treaties(base_url, treaty_list)
