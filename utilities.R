require(stringr)
require(lubridate)
require(plyr)
require(reshape2)

createColumns <- function(x, head) {
  if (is.data.frame(x) & ncol(x) == 1) {
    head <- colnames(x)
    x <- x[, 1]
  }
  
  type <- str_extract(x, "[a-zA-Z]+$")
  type <- ifelse(type == "1", "one", type) #I think there is only one instance of this
  atypes <- unique(type[!is.na(type)])
  df <- vector(mode = "list", length(atypes))

  for(i in seq_along(atypes)) {
    check <- grepl(paste0(" ", atypes[i], "$"), x)
    data <- ifelse(check, gsub(" [a-zA-Z]+$", "", x[check]), NA)
    assign(atypes[i], data)
    df[[i]] <- get(atypes[i])
  }

  df <- do.call("cbind", df)
  df <- data.frame(x, df)
  df$x <- ifelse(apply(df, 1, function(x) all(is.na(x[-1]))), x, NA)
  names(df) <- gsub("\\(.*\\)", "", tolower(str_trim(unlist(str_split(head, ",")))))
  return(df)
}

expandColumns <- function(df) {
  date.df <- findDates(df, TRUE)
  other.df <- df[, !(colnames(df) %in% colnames(date.df))]

  if (ncol(date.df) > 1) {
    cols <- vector("list", ncol(date.df))
    cols <- lapply(cols, createColumns(date.df, colnames(date.df)))
    df <- data.frame(nexpand.df, do.call("cbind", cols))
  } else if (ncol(date.df) == 1)
    df <- data.frame(other.df, createColumns(date.df, colnames(date.df)))
  
  colnames(df) <- gsub("\\.", "_", tolower(colnames(df)))
  return(df)
}

loadData <- function(chap, treaty, expand = FALSE, panel = FALSE, ...) {
  df <- read.csv(paste0("./treaties/", chap, "-", treaty, ".csv"),
                 check.names = FALSE, na.string = "")
  if (expand == TRUE & panel == TRUE)
    df <- expandPanel(expandColumns(df), ...)
  else if (expand == TRUE & panel == FALSE)
    df <- expandColumns(df)
  else if (expand == FALSE & panel == TRUE)
    stop("column names must be expanded to use panel expansion.")

  return(df)
}

convertPanel <- function(x, pyear) {
  x <- gsub("Sept", "Sep", x) #date conversion expects 3 letter abbr
  x <- ifelse(year(dmy(x)) <= pyear, 1, 0)
  x[is.na(x)] <- 0
  return(x)
}

expandPanel <- function(df, sdate, edate) {
  df <- do.call("ddply", list(df, "participant", transform, 
                year = call("year", x = seq(ymd(sdate), ymd(edate), "year"))))
  date.df <- findDates(df)
  other.df <- df[, !(colnames(df) %in% colnames(date.df))]
  df <- data.frame(other.df, apply(date.df, 2, function(x) convertPanel(x, df$year)))
  return(df)
}

findDates <- function(df, type = FALSE) {
  if (type)
    re.date <- "[0-9]?{2} [a-zA-Z]?{4} [0-9]{4} [a-zA-Z]+$"
  else
    re.date <- "[0-9]?{2} [a-zA-Z]?{4} [0-9]{4}"
  
  test <- apply(df, 2, function(x) any(grepl(re.date, x)))
  date.df <- data.frame(df[, test])
  colnames(date.df) <- colnames(df)[test]
  return(date.df)
}

searchTreaties <- function(treaty.name, dist.val = .1, trim = TRUE) {
  index.df <- read.csv("index.csv")
  tname <- agrep(treaty.name, index.df$treaty_name, max.distance = dist.val)
  if (length(tname) == 0)
    stop("no matches found")
  else if (length(tname) > 1) {
    message("multiple matches found")
    for(i in 1:length(tname)) {
      if (str_length(tname[i] >= 77))
        print(paste0(strtrim(index.df$treaty_name[tname], 77), "..."))
      else
        print(strtrim(index.df$treaty_name[tname], 77))
    }
    cat("Which treaty would you like to load? ")
    tname <- as.integer(readLines(file("stdin"), 1))
  }
  if (str_length(tname) >= 69)
    message(paste0("loading ", strtrim(index.df$treaty_name[tname], 69), "..."))
  else
    message(paste0("loading ", strtrim(index.df$treaty_name[tname], 69)))
  return(loadData(index.df$chapter_no[tname], index.df$treaty_no[tname]))
}
