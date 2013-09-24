This repository contains a set of scripts that allow the retrieval of the [United Nations' Treaty Collection](http://treaties.un.org/), and transformation of the retrieved data. Please [open an issue](https://github.com/zmjones/untreaties/issues/new) if you find any errors or would like to suggest a feature. Pull requests are welcome!

### Getting the data

You can clone (see below) or [download](https://github.com/zmjones/untreaties/archive/master.zip) the data contained in this repository or scrape it using `un_data.py`, which requires `pandas`, `requests`, and `beautifulsoup4`. These dependencies are listed in `requirements.txt`. The script will generate `index.csv` along with a folder containing the treaty data itself (`treaties/`) and a folder containing declarations made by participants (contained in `declarations/`).

	git clone git@github.com:zmjones/untreaties.git
	cd untreaties
	pip install -r requirements.txt
	python un_data.py
	...

### Transforming the data

The [R](http://cran.us.r-project.org/) script `utilities.R` contains a number of functions that make working with the raw data easier. You can load these functions by simply sourcing the file. It requires `stringr`, `lubridate`, and `plyr`.

 - `loadData` loads the data for a specific treaty given its chapter and treaty numbers, which are passed as strings. You can optionally expand the column names (if needed). If you choose to expand the column names you can also transform the data into a country-year format, given a start year and an end year (both passed as strings).

 - `searchTreaties` searches through the `treaty_name` column in `index.csv` using approximate string matching given a maximum distance (internally it uses `agrep`). If multiple matches are found, the user can select the best match from the console. The `trim` option is logical and truncates console output to 80 characters (it is true by default). This function calls `loadData` internally, and allows overloading, so you can pass arguments to `loadData` by passing arguments to `searchTreaties`. Note that you have to name the arguments explicitly (you can't just use argument ordering).

 - `createColumns` takes a character vector of dates (or a dataframe with one column) with a trailing type identifier (a one or two character code) and a name for said column. It returns an expanded version of that column with column dimension equal to the number of unique type identifiers plus one (for the no identifier category).

 - `expandColumns` takes a dataframe that may need to be expanded, passes columns that need to be expanded to `createColumns`, and combines the results.

 - `convertPanel` takes a character vector of dates (of the form `"%d-%b-%Y"`) and a year for comparison and returns a binary variable indicating whether the year of the date that was passed is less than or equal to the comparison year.

 - `expandPanel` takes a dataframe, a start year, and an ending year (both strings), and returns a dataframe with in country-year format with each data column converted into a binary variable.

 - `findDates` takes a dataframe and finds columns which follow the `%d-%b-%Y` date format. Optionally allows for dates with a trailing type identifier.

### Examples

	> source("utilities.R")
    > loadData(chap = "10", treaty = "2")
       Participant   Signature Ratification, Accession(a)
    1      Algeria  4 Aug 1963                10 Sep 1964
    2       Angola        <NA>               9 Jan 1981 a
    3        Benin  8 Oct 1963                25 Aug 1964
    4     Botswana        <NA>              31 Mar 1972 a
    5 Burkina Faso 21 Nov 1963                22 Sep 1964
    6      Burundi  4 Aug 1963               2 Jan 1968 a

    > loadData(chap = "10", treaty = "2", expand = TRUE)
       participant   signature ratification   accession
    1      Algeria  4 Aug 1963  10 Sep 1964        <NA>
    2       Angola        <NA>         <NA> 31 Mar 1972
    3        Benin  8 Oct 1963  25 Aug 1964        <NA>
    4     Botswana        <NA>         <NA> 15 Apr 1976
    5 Burkina Faso 21 Nov 1963  22 Sep 1964        <NA>
    6      Burundi  4 Aug 1963         <NA> 26 Aug 1968

    > loadData(chap = "10", treaty = "2", expand = TRUE, panel = TRUE, syear = "1945", eyear = "2013")
       participant year signature ratification accession
    1      Algeria 1945         0            0         0
    2      Algeria 1946         0            0         0
    3      Algeria 1947         0            0         0
    4      Algeria 1948         0            0         0
    5      Algeria 1949         0            0         0
    6      Algeria 1950         0            0         0
    7      Algeria 1951         0            0         0
    8      Algeria 1952         0            0         0
    9      Algeria 1953         0            0         0
    10     Algeria 1954         0            0         0
    11     Algeria 1955         0            0         0
    12     Algeria 1956         0            0         0
    13     Algeria 1957         0            0         0
    14     Algeria 1958         0            0         0
    15     Algeria 1959         0            0         0
    16     Algeria 1960         0            0         0
    17     Algeria 1961         0            0         0
    18     Algeria 1962         0            0         0
    19     Algeria 1963         1            0         0
    20     Algeria 1964         1            1         0
    21     Algeria 1965         1            1         0
    22     Algeria 1966         1            1         0
    23     Algeria 1967         1            1         0
    24     Algeria 1968         1            1         0
    25     Algeria 1969         1            1         0

    > searchTreaties(treaty.name = "charter of the united nations", dist.val = .1)
    multiple matches found
    [1] "charter of the united nations (deposited in the archives of the government of..."
    [2] "declarations of acceptance of the obligations contained in the charter of the..."
    [3] "amendments to articles 23,27 and 61 of the charter of the united nations, ado..."
    [4] "amendment to article 109 of the charter of the united nations, adopted by the..."
    [5] "amendment to article 61 of the charter of the united nations, adopted by the ..."
    Which treaty would you like to load? 1
                           Participant Ratification
    1                        Argentina  24 Sep 1945
    2                        Australia   1 Nov 1945
    3                          Belarus  24 Oct 1945
    4                          Belgium  27 Dec 1945
    5 Bolivia (Plurinational State of)  14 Nov 1945
    6                           Brazil  21 Sep 1945

	> searchTreaties(treaty.name = "charter of the united nations",
                     expand = TRUE, panel = TRUE, syear = "1945", eyear = "2011")
	multiple matches found
    [1] "charter of the united nations (deposited in the archives of the government of..."
    [2] "declarations of acceptance of the obligations contained in the charter of the..."
    [3] "amendments to articles 23,27 and 61 of the charter of the united nations, ado..."
    [4] "amendment to article 109 of the charter of the united nations, adopted by the..."
    [5] "amendment to article 61 of the charter of the united nations, adopted by the ..."
    Which treaty would you like to load? 1
      participant year ratification
    1   Argentina 1945            1
    2   Argentina 1946            1
    3   Argentina 1947            1
    4   Argentina 1948            1
    5   Argentina 1949            1
    6   Argentina 1950            1
