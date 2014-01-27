This repository contains a set of scripts that allow the retrieval of the [United Nations' Treaty Collection](http://treaties.un.org/), and transformation of the retrieved data. Please [open an issue](https://github.com/zmjones/untreaties/issues/new) if you find any errors or would like to suggest a feature. Pull requests are welcome!

### Getting the data

You can clone (see below) or [download](https://github.com/zmjones/untreaties/archive/master.zip) the data contained in this repository or scrape it using `un_data.py`, which requires `pandas`, `requests`, and `beautifulsoup4`. These dependencies are listed in `requirements.txt`. The script will generate `index.csv` along with a folder containing the treaty data itself (`treaties`) and a folder containing declarations made by participants (contained in `declarations`).

```shell
git clone git@github.com:zmjones/untreaties.git
cd untreaties
pip install -r requirements.txt
python un_data.py
```

### Transforming the data

The [R](http://cran.us.r-project.org/) script `utilities.R` contains a number of functions that make working with the raw data easier. You can load these functions by simply sourcing the file. It requires `stringr`, `lubridate`, and `plyr`. The `loadData` function allows the user to load a specific treaty given its chapter and treaty numbers, which are passed as strings. You can optionally expand the column names (if needed). If you choose to expand the column names you can also transform the data into a country-year format, given a start year and an end year (both passed as strings).

```S
source("utilities.R")
loadData(chap = "10", treaty = "2")
loadData(chap = "10", treaty = "2", expand = TRUE)
loadData(chap = "10", treaty = "2", expand = TRUE, panel = TRUE, syear = "1945", eyear = "2013")
```
