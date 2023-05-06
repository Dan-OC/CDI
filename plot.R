library(tidyverse)
library(ggplot2)
library(lubridate)

dat=read.csv("./dat_sofar3.csv")


dat %>%
    filter(!is.nan(CDI),
           !is.nan(date))%>%
    ggplot(aes(x=CDI,fill="red"))+
    geom_histogram(binwidth=0.05,show.legend = FALSE)+
    labs(x="CDI",y="")+
    theme(text = element_text(size = 20)) +
    ggsave("output/cdi_distribution.png")




dat["year"]=year(dat["date"])




dat %>% 
    filter(!is.nan(CDI),
           !is.nan(date))%>%
    group_by(yearmonth)%>%
    summarize(CDI=mean(CDI))%>%
    arrange(yearmonth)%>%
    ggplot(aes(x=yearmonth,y=CDI))+
    geom_point()+
    labs(x="month",y="Average CDI")+
    theme(text = element_text(size = 20),
    axis.text.x = element_text(angle = 45)) +
    ggsave("output/average_cdi.png")
    




