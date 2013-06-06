nameConvert <- function(df) {
  require(countrycode)
  df$cowcode <- countrycode(df$Participant, "country.name", "cown")
  print("Serbia was not matched.") #unknown if there are other mis-matches
  return(df)
}

multipleField <- function(x) {
  require(stringr)
  x <- ifelse(str_trim(x) == "", NA, str_trim(x))
  if(any(grepl(" [a-z]$", x)) == TRUE)
    return(data.frame("type" = str_trim(str_extract(x, " [a-z]$")),
                      "date" = ifelse(grepl(" [a-z]$", x), str_replace(x, " [a-z]$", ""), x)))
  else
    return(x)
}

cleanMultipleField <- function(df) {
  print("renaming the columns is suggested!")
  df <- apply(df, 2, multipleField)
  require(plyr)
  df <- lapply(df, function(x) if(is.vector(x)) return(x) else return(data.frame(t(ldply(x)))[-1, ]))
  df <- do.call("cbind", df)
  return(df)
}
