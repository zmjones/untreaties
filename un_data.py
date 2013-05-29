from bs4 import BeautifulSoup
from urllib2 import urlopen
from mechanize import Browser
import pandas as pd

mech = Browser()

def ReadPage(url):
    page = mech.open(url)
    html = page.read()
    soup = BeautifulSoup(html.decode("utf-8", "ignore"))
    return soup

def ParseTable(soup):
    table = soup.find(lambda tag: tag.name == "table" and tag.has_key("id") 
                  and tag["id"] == "ctl00_ContentPlaceHolder1_tblgrid")

    df = []

    for row in table.findAll("tr")[1:]:
        col = row.findAll("td")
        country = col[0].get_text(strip = True)
        sig_date = col[1].get_text(strip = True)
        asr_date = col[2].get_text(strip = True)
        record = [country, sig_date, asr_date]
        df.append(record)

    return df

#UN International Covenant on Civil and Political Rights
cpr_url = "http://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=IV-4&chapter=4&lang=en"

soup = ReadPage(cpr_url)
cpr_df = ParseTable(soup)
cpr_df = pd.DataFrame(cpr_df, columns = ["country", "sig_date", "asr_date"])
cpr_df.to_csv("./data/cpr_un_data.csv", na_rep = "NA")

#UN Convention against Torture and Other Cruel, Inhuman or Degrading Treatment or Punishment
cat_url = "http://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=IV-9&chapter=4&lang=en"

soup = ReadPage(cat_url)
cat_df = ParseTable(soup)
cat_df = pd.DataFrame(cat_df, columns = ["country", "sig_date", "asr_date"])
cat_df.to_csv("./data/cat_un_data.csv", na_rep = "NA")

