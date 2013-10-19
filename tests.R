source("utilities.R")

treaties <- lapply(list.files("./treaties/"), function(x) {
  split <- unlist(str_split(x, "-", 2))
  split[2] <- gsub("\\.csv", "", split[2])
  print(paste(split[1], split[2]))
  if (x != "8-5.csv") #haven't figured out how to parse this one yet
    loadData(split[1], split[2], TRUE)
})

df <- loadData("8", "5")
