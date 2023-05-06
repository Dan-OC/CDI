import pandas as pd
import os 
import funcs as fn
import time 

#Read data
# input_data_file="Data for Dan v1.xlsx"
# dat=pd.read_excel(os.path.join("data",input_data_file))

print("Reading data")
dat=pd.read_csv(os.path.join("data","dat_sofar.csv"))

#The articles we want have a null CDI and non-null PMID and dates
articles=[x for x in dat[pd.isnull(dat.CDI)].index if (pd.notnull(dat.pmid.loc[x]) and pd.isnull(dat.date.loc[x]))]

print("Starting search for ",str(len(articles))," articles")
counter=0

#Fill in the CDI (in loop for robustness)
for i in articles:

    try: 
        dat.at[i,"CDI"]=fn.calculate_CDI(dat.pmid.loc[i])
        dat.at[i,"date"]=fn.get_article_date(dat.pmid.loc[i])
    except Exception as e:
        print(e)
        continue

    #Save every 100 articles
    if counter%100==0:
        print("Counter:", str(counter),", saving...")
        dat.to_csv("./data/dat_sofar.csv",index=False)
    counter+=1


#Fill in missing dates
for i in dat[(pd.isnull(dat.date)) & (pd.notnull(dat.CDI))].index:
    dat.at[i,"date"]=fn.get_article_date(dat.pmid.loc[i])
    time.sleep(0.1)

#Add in date info 
dat["year"]=[x[0:4] if x==x else pd.NA for x in dat.date ]
dat["month"]=[x[5:7] if x==x else pd.NA for x in dat.date ]
dat["yearmonth"]=dat["year"]+"-"+ dat["month"]

#Save for plotting 
dat.to_csv("./output/dat_toplot.csv",index=False)
