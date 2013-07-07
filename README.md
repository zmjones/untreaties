A set of scripts that allows the retrieval of the [United Nations' Treaty Collection](http://treaties.un.org/), and transformation of the retrieved data.

### Getting the data

You can clone or download the data contained in this repository or scrape it using `un_data.py`, which requires `pandas`, `requests`, and '`beautifulsoup4`. The script with generate a `index.csv` along with a folder containing the treaty data itself (`treaties/`) and a folder containing declarations made by participants (contained in `declarations/`).

### Transforming the data

The `R` script `utilities.R` contains a number of functions that make working with the raw data easier. You can load these functions by simply sourcing the file.

 - `loadData` loads the data for a specific treaty given its chapter and treaty numbers, which are passed as strings. You can optionally expand the column names (if needed). If you choose to expand the column names you can also transform the data into a country-year format, given a start date and an end date (both passed as strings in a day-month-year format).

 - `searchTreaties` searches through the `treaty_name` column in `index.csv` using approximate string matching given a maximum distance (internally it uses `agrep`). If multiple matches are found, the user can select the best match from the console. The `trim` option is logical and truncates console output to 80 characters (it is true by default).

 - `createColumns` takes a character vector of dates (or a dataframe with one column) with a trailing type identifier (a one or two character code) and a name for said column. It returns an expanded version of that column with column dimension equal to the number of unique type identifiers + 1.

 - `expandColumns` takes a dataframe that may need to be expanded, passes columns that need to be expanded to `createColumns`, and combines the results.

 - `convertPanel` takes a character vector of dates (of the form "%d-%b-%Y") and a year for comparison and returns a binary variable indicating whether the year of the date that was passed is less than or equal to the comparison year.

 - `expandPanel` takes a dataframe, a starting, and an ending date, and returns a dataframe with `nrow(df) * (year(eyear) - year(syear))` rows, i.e. a country-year format.

 - `findDates` takes a dataframe and finds columns which follow the "%d-%b-%Y" date format. Optionally allows for dates with a trailing type identifier.
 


