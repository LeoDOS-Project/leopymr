#! /usr/bin/env Rscript

data = read.table('data/result.dat', header=T)
#data

data.rand = data[data$BENCH=="random",]
data.rand.los = data.rand[data.rand$PLACEMENT=="los",]
data.rand.center = data.rand[data.rand$PLACEMENT=="center",]

data.bi = data[data$BENCH=="bipartite",]
data.bi.los = data.bi[data.bi$PLACEMENT=="los",]
data.bi.center = data.bi[data.bi$PLACEMENT=="center",]

png("plots/sim.png")

plot(data.rand.los$ITER,data.rand.los$VAL,ylim=c(0,1),type='n',ylab="Time (s)",xlab="Iteration")
lines(data.rand.los$ITER,data.rand.los$VAL,col="red")
points(data.rand.los$ITER,data.rand.los$VAL,col="red")
lines(data.rand.center$ITER,data.rand.center$VAL,col="pink")
points(data.rand.center$ITER,data.rand.center$VAL,col="pink")
lines(data.bi.los$ITER,data.bi.los$VAL,col="blue")
points(data.bi.los$ITER,data.bi.los$VAL,col="blue")
lines(data.bi.center$ITER,data.bi.center$VAL,col="cyan")
points(data.bi.center$ITER,data.bi.center$VAL,col="cyan")
legend("bottomright",legend=c("RANDOM LOS","RANDOM CENTER","BIPART LOS","BIPART CENTER"),col=c("red","pink","blue","cyan"),lt=1)
dev.off()
