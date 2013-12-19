rm(list = ls())
source("utilities.R")

treaties <- lapply(list.files("./treaties/"), function(x) {
  split <- unlist(str_split(x, "-", 2))
  split[2] <- gsub("\\.csv", "", split[2])
  print(paste(split[1], split[2]))
})

head(loadData("27", "1"))
head(loadData("27", "1", TRUE))

head(loadData("27", "7"))
head(loadData("27", "7", TRUE))

head(loadData("27", "2"))
head(loadData("27", "2", TRUE))

head(loadData("27", "3"))
head(loadData("27", "3", TRUE))

head(loadData("16", "3"))
head(loadData("16", "3", TRUE))
