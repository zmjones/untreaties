require(stringr)
require(reshape2)
require(countrycode)

nameConvert <- function(df) {
  df$cowcode <- countrycode(df$Participant, "country.name", "cown", warn = TRUE)
  #to-do: find out which countries don't parse correctly, add exceptions
  return(df)
}

createColumns <- function(x, head) {
  type <- str_extract(x, "[a-zA-Z]+$")
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

df <- read.csv("./data/27-15.csv", check.names = FALSE, na.string = "")

createColumns(df[, 3], colnames(df)[3])




