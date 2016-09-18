data <- read.csv("~/Projects/data.csv")
x <- data[,1]
y <- data[,2]
jet.colors <-
  colorRampPalette(c("#00007F", "blue", "#007FFF", "cyan",
                     "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))

d <- structure(list(X=x,Y=y, .Names= c("X", "Y"), class = " data.frame ", row.names=c(NA, 20L)))
require(MASS)
dens <- kde2d(d$X, d$Y) 
filled.contour(dens, color=jet.colors)
