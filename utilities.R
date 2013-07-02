rm(list = ls())

require(stringr)
require(reshape2)
require(countrycode)

nameConvert <- function(df, drop = FALSE) {    
  df$cowcode <- countrycode(df$participant, "country.name", "cown")
  if (any(df$participant == "Serbia")) {
    message("Serbia is not listed by COW, assigning GW code.")
    df$cowcode[df$participant == "Serbia"] <- 340
  }
  
  no.ccode <- c("European Union", "Niue", "Cook Islands")
  if (any(df$participant %in% no.ccode) & drop == TRUE)
    df <- df[!is.na(df$cowcode), ]
  else
    message("Some observations do not have country codes.")

  return(df)
}

createColumns <- function(x, head) {
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
  test <- apply(df[, -1], 2, function(x) any(grepl(" [a-zA-Z]+$", x)))
  cols <- vector("list", length(test))

  for(i in 1:length(test)) {
    if (test[i])
      cols[[i]] <- createColumns(df[, colnames(df) %in% names(test[i])], names(test[i]))
    else
      cols[[i]] <- df[, colnames(df) %in% names(test[i])]
  }

  df <- data.frame("participant" = df[, 1], do.call("cbind", cols))
  colnames(df) <- gsub("\\.", "_", colnames(df))
  return(df)
}

df <- read.csv("./data/27-15.csv", check.names = FALSE, na.string = "")
df <- expandColumns(df)
df <- nameConvert(df)
