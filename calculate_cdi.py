import pandas as pd
import os 
import funcs as fn
import time 

#Read data
input_data_file="Data for Dan v1.xlsx"
# dat=pd.read_excel(os.path.join("data",input_data_file))

# dat=pd.read_csv(os.path.join("data","dat_sofar.csv"))


dat=pd.read_csv(os.path.join("dat_sofar.csv"))


# dat.CDI.iloc[3900:4768]=dat2.CDI.iloc[3900:4768]

n=3000





i=4760
#Fill in the CDI (in loop for robustness)
# for i in dat.index:
# for i in range(i,dat.shape[0]):
for i in [ x for x in dat[pd.isnull(dat.CDI)].sample(n).index if pd.notnull(dat.pmid.loc[x])]:
    dat.at[i,"CDI"]=fn.calculate_CDI(dat.pmid.loc[i])
    dat.at[i,"date"]=fn.get_article_date(dat.pmid.loc[i])
    
#Fill in missing dates
for i in dat[(pd.isnull(dat.date)) & (pd.notnull(dat.CDI))].index:
    dat.at[i,"date"]=fn.get_article_date(dat.pmid.loc[i])
    time.sleep(0.1)



for i in dat.index: 
    dat.at[i,"year"]=[x[0:4] for x in ]


dat["year"]=[x[0:4] if x==x else pd.NA for x in dat.date ]
dat["month"]=[x[5:7] if x==x else pd.NA for x in dat.date ]
dat["yearmonth"]=dat["year"]+"-"+ dat["month"]


dat.to_csv("./dat_sofar3.csv")


sum(pd.isna(dat[0:6000].CDI))
sum(pd.isna(dat[0:6000].pmid))




#By a map:    
dat["CDI"]=dat.pmid.map(fn.calculate_CDI)


#Get info from this PMID
dat_test=dat.iloc[0:10]

pmid=dat_test.pmid.iloc[5]

get_details_on_pmid(pmid)
