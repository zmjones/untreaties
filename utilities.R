nameConvert <- function(df) {
  require(countrycode)
  df$cowcode <- countrycode(df$Participant, "country.name", "cown", warn = TRUE)
  #to-do: find out which countries don't parse correctly, add exceptions
  return(df)
}

createColumns <- function(x, head) {
  require(stringr)
  type <- str_extract(x, "[a-zA-Z]?{2}$")
  head <- gsub("\\.", " ", head)
  type <- ifelse(type == "A", "A ", type) #a bit of a hack
  text <- str_extract(head, paste0("[a-zA-Z]* ", type))
  text <- substr(text, 0, nchar(text) - (nchar(type) + 1))
  data <- gsub(" [a-zA-Z]?{2}$", "", x)

  df <- cbind(type, text, data)
  df <- apply(df, 2, function(x) ifelse(x == "", NA, x))
  df <- as.data.frame(df)

  cols <- unique(df$text[!is.na(df$text)])

  for(i in seq_along(cols))
    df[cols[i]] <- ifelse(df$text == cols[i], df$data, NA)

  df <- df[, !names(df) %in% c("type", "text", "data")]
  return(df)
}

require(RCurl)
df <- read.csv(text = getURL("https://raw.github.com/zmjones/untreaties/master/data/10-10.csv"))

createColumns(df[, 3], colnames(df)[3])

