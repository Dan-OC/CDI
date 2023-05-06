import requests
import pandas as pd 
import json
import numpy as np 
import re 
from datetime import datetime


"""
These functions are useful for interacting with EuropePMC and are utilized in scripts for projects pertaining to that 

Extensive use of the EPMC API is employed - more information can be found here:
https://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf

The CDI is a measure of the consolation/disruptiveness of a paper and is explained in 
Park et. al., Nature 613, 138-144 (2023)

"""
def get_article_date(pmid):
    return get_details_on_pmid(pmid)["resultList"]["result"][0]["firstPublicationDate"]

def get_details_on_pmid(pmid):
    #Search EPMC for a specific pmid and return all details found for it 
    link="https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{}&resultType=core&format=json".format(int(pmid))
    response=requests.get(link)
    return json.loads(response.text)


def get_references_of(pmid,**kwargs):

    #First get the source 
    if "source" in kwargs:
        source=kwargs.get("source")
    else:
        source=get_details_on_pmid(pmid)["resultList"]["result"][0]["source"]

    #Second get article date 
    if "date" in kwargs:
        date=datetime.strptime(kwargs.get("datecutoff"),"%Y-%m-%d")
    else:
        date=datetime.strptime(get_details_on_pmid(pmid)["resultList"]["result"][0]["firstPublicationDate"],"%Y-%m-%d")

    #The time index of the CD
    years_cutoff=5

    #Form link and get response
    link="https://www.ebi.ac.uk/europepmc/webservices/rest/{}/{}/references?&format=json".format(source,int(pmid))
    response=requests.get(link)

    #If the request was successful (200) but returned no results:
    if "errCode" in json.loads(response.text).keys(): 
        Warning(print(json.loads(response.text)["errMsg"]))
        return np.nan
    
    #Otherwise, check for hits and return within date range
    if json.loads(response.text)["hitCount"]!=0: #if there's a hit
        return [x for x in json.loads(response.text)["referenceList"]["reference"] if x["pubYear"]<= date.year+years_cutoff]
    else:
        return np.nan
        
    
def get_citations_to(pmid,**kwargs):
    
    #First get the source 
    if "source" in kwargs:
        source=kwargs.get("source")
    else:
        source=get_details_on_pmid(pmid)["resultList"]["result"][0]["source"]
    
    #Second get article date 
    if "date" in kwargs:
        date=datetime.strptime(kwargs.get("datecutoff"),"%Y-%m-%d")
    else:
        date=datetime.strptime(get_details_on_pmid(pmid)["resultList"]["result"][0]["firstPublicationDate"],"%Y-%m-%d")

    #The t index of the CD
    years_cutoff=5

    #Form link and get response
    link="https://www.ebi.ac.uk/europepmc/webservices/rest/{}/{}/citations?&format=json".format(source,int(pmid))
    response=requests.get(link)
    
    #If the request was successful (200) but returned no results:
    if "errCode" in json.loads(response.text).keys(): 
        Warning(print(json.loads(response.text)["errMsg"]))
        return np.nan
    
    #Otherwise, check for hits and return 
    if json.loads(response.text)["hitCount"]!=0: #if there's a hit
        return [x for x in json.loads(response.text)["citationList"]["citation"] if x["pubYear"]<= date.year+years_cutoff]
    else:
        return np.nan
    
    
def calculate_CDI(pmid):
    
    #Given a PMID, calculate the consolidating-disruptive index (CDI)
    #This involves getting info on the references of, and citations to, the input PMID 
    
    try: #Get the references OF the focal pmid
        refs=get_references_of(pmid)
        ref_ids=[x["id"] for x in refs if "id" in x.keys()]
    except Exception as e: #If it doesn't work for some reason (data missing)
        return np.nan #Then we can't calculate CDI
    
    try: #Get the references TO the focal pmid
        cited_by=get_citations_to(pmid)
        cite_ids=[x["id"] for x in refs if "id" in x.keys()]
    except Exception as e: #If it doesn't work for some reason (data missing)
        return np.nan #Then we can't calculate CDI
    
    #The CDI is calculated over all papers that reference the focus
    CDI=[]
    
    #Keep numeric PMIDs only (ie remove preprints etc)
    cite_ids=[x for x in cite_ids if re.match("^\d",x)]
    ref_ids= [x for x in ref_ids  if re.match("^\d",x)]
    
    #For each article that points to the focus
    for cite_article in cite_ids:
        
        #Get the references of this paper 
        subrefs=get_references_of(cite_article)
        
        if subrefs!=subrefs: #If we can't get references for this article 
            continue #Skip it
        
        reference_ids=[x["id"] for x in subrefs if "id" in x.keys()]
        
        #Keep only those references that are also referenced by the focal (original input) article
        sub_refs=[x for x in reference_ids if x in ref_ids]
    
        if sub_refs: #if there are references in common
            b=1
        else: #Otherwise, this must be 0
            b=0
            
        f=1 #This follows, as cite_article must also cite focal article 
    
        #Keep a tally of the CDI score        
        CDI.append(-2*f*b+f) #See paper for explanation 
    
    CDI=np.round(np.mean(CDI),2)
    
    return CDI 
    

def days_ago(num_days):
    #Return a yyyy-mm-dd string that is num_days days ago
    return datetime.strftime(datetime.today()-timedelta(days=num_days), "%Y-%m-%d")  



# def get_article_info_from_pmid(pmid):
#     return process_data(read_xml(query_epmc_for_pmid(pmid).text))
    
# def query_epmc_for_pmid(pmid):
    
#     #Function to get results from European PMC using sensible default values 
    
#     #Form the link
#     link="https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{}&resultType=core".format(int(pmid))
#     return requests.get(link)


# def get_nests(child,id):
    
#     #Get the info contained in nested child nodes 
#     tagnames=[]
#     tagvals=[]
#     order=[]
    
#     for z,gchild in enumerate(list(child)): #Iterate over the grandchildren
#         for i in gchild.iter(): #And the nodes within
            
#             if type(i.text)!=type(None): #Filter out junk
#                 if i.text.strip()!="": #If this tag has something included
            
#                     tagnames.append(i.tag) #Store tag name
#                     tagvals.append(i.text) #value
#                     order.append(z) #and the "order" - the group to which this tag belongs
    
#     #Then for each group
#     ret=pd.DataFrame()
#     for ordy in pd.unique(order):
        
#         #Get the relevant columns and values only
#         cols=[x for x,y in zip(tagnames,order) if y==ordy ]
#         vals=[x for x,y in zip(tagvals,order) if y==ordy ]
        
#         #Form a dictionary to pair them up
#         ret_dict={}
#         for colname in pd.unique(cols):
#             ret_dict[colname]=[y for x,y in zip(cols,vals) if x==colname]
        
#         #Sometimes there are multiple values per key. Join them up here
#         for key,val in ret_dict.items():
#             if len(val)>1:
#                 ret_dict[key]=["; ".join(val)]
        
#         #Convert dictionary to dataframe and append
#         ret_=pd.DataFrame.from_dict(data=ret_dict)
#         # ret=ret.append(ret_,ignore_index=True)
#         ret = pd.concat([ret,ret_],ignore_index=True)
    
#     #For some reason, journalInfo is stored differently, so implement this fix
#     if child.tag=="journalInfo":
#         ret=ret.bfill().iloc[0].to_frame().transpose()
        
#     #Add the ID column for linking purposes 
#     ret["id"]=id

#     return ret


# def read_xml(xml_string):
    
#     #Get root of XML tree
#     tree=ET.ElementTree(ET.fromstring(xml_string))
#     root=tree.getroot()

#     #Get the nextcursormark here
#     cursor=[i.text for i in root.iter("nextCursorMark")]
#     if cursor==[]:
#         cursor=np.nan
        
#     #Create an overall frame for unnested children 
#     dat=pd.DataFrame()
    
#     #Keep a running list of the variable names with nested nodes - these will be concatenated later 
#     frames_with_children=[]
    
#     #Iterate over all papers
#     for i,paper in enumerate(root.iter('result')):
#         # print(i)
        
#         #Get the child nodes (ie the columns)
#         for child in list(paper): 
#             #If this child is nested (ie it also has children eg authorList)
#             if list(child)!=[]:
                
#                 #Then parse those separately
#                 output=get_nests(child,id=list(paper)[0].text)  
                
#                 #Check if we have a list for this type of tag
#                 try:
#                     exec("framelist_"+ child.tag)
#                 except NameError: #if we don't - create one
#                     exec("framelist_"+ child.tag + " = []")
#                     frames_with_children.append("framelist_"+ child.tag)
                
#                 #Then store output in the unique list
#                 exec("framelist_" + child.tag + ".append(output)") 
            
#             else: #If the node is childless, store info here 
#                 try:
#                     dat.at[i,child.tag]=child.text
#                 except ValueError: #This indicates the column is the wrong type - happens if the data hitherto is different type
#                     dat[child.tag]=dat[child.tag].astype(object) #Convert to object (so we can mix types)
#                     dat.at[i,child.tag]=child.text #Then insert the data 
                    
#     #Put all the frames in a handy dictionary
#     framedict=dict()
#     framedict["fulldat"]=dat

#     for frame in frames_with_children:
#         exec("framedict['" + frame.split("_")[1]+"']=pd.concat("+frame+")")            
    
#     #Add in nextcursormark 
#     framedict["cursorMark"]=cursor
    
#     return framedict


# def process_data(dat_all):
    
#     dat_full=dat_all["fulldat"]
    
#     #If we have grants info, get it
#     if ("grantsList") in dat_all.keys():
#         dat_grants=dat_all["grantsList"].reset_index(drop=True)
#     else: #If we don't, define an empty(ish) dataframe
#         dat_grants=pd.DataFrame(data={"grantId":""},index=[0])
    
#     #Same for journal info
#     if ("journalInfo") in dat_all.keys():
#         dat_journs=dat_all["journalInfo"].reset_index(drop=True)
#     else: #If we don't, define an empty(ish) dataframe
#         dat_journs=pd.DataFrame(data={"id":""},index=[0])


#     #Preallocate
#     dat_full["printPublicationDate"]=""
#     dat_full["journalIssueId"]=""
#     dat_full["ESSN"]=""
#     dat_full["ISSN"]=""
#     dat_full["journal_name"]=""


#     for id in pd.unique(dat_full.id):
        
#         ind=dat_full[dat_full.id==id].index[0]

#         #If this paper id is in the grant info dataframe
#         if id in dat_grants.id.values: 
#             #Save the results
#             dat_full.at[ind,"grants"]="; ".join([ x for x in dat_grants[dat_grants.id==id].grantId if (x!="") and (x==x)])

#         #If this paper id is in the grant info dataframe
#         if id in dat_journs.id.values: 
#             #Save the results
#             dat_full.at[ind,"journal_name"]="; ".join([ x for x in dat_journs[dat_journs.id==id].title if (x!="") and (x==x)])
#             dat_full.at[ind,"ISSN"]="; ".join([ x for x in dat_journs[dat_journs.id==id].ISSN if (x!="") and (x==x)])
#             dat_full.at[ind,"ESSN"]="; ".join([ x for x in dat_journs[dat_journs.id==id].ESSN if (x!="") and (x==x)])
#             dat_full.at[ind,"journalIssueId"]="; ".join([ x for x in dat_journs[dat_journs.id==id].journalIssueId if (x!="") and (x==x)])
#             dat_full.at[ind,"printPublicationDate"]="; ".join([ x for x in dat_journs[dat_journs.id==id].printPublicationDate if (x!="") and (x==x)])
#     return dat_full




# def query_epmc(date_from,date_to,resultType="core",pagesize="100",res_format="json",sorttype="P_PDATE_D desc",nextcursormark="*"):
    
#     #Function to get results from European PMC using sensible default values 
    
#     #Form the link
#     link="https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=FIRST_PDATE%3A%5B{}%20TO%20{}%5D%20%26%20GRANT_AGENCY%3A%22BRITISH%20HEART%20FOUNDATION%22&resultType={}&cursorMark={}&pageSize={}&format={}&sort={}".format(date_from,date_to,resultType,nextcursormark,pagesize,res_format,sorttype.replace(" ","%20"))    
#     return requests.get(link)
   

# # def read_archive():
# #     # return pd.read_csv(output_file)
# #     return pd.read_excel(output_file)


# def highlight_rows(row):
#     #Nicked from the net
#     value = row.loc['new']
#     if value == True:
#         colour = '#e7f20a' #Yellow
#     else:
#         colour = '#ffffff'
#     return ['background-color: {}'.format(colour) for r in row]
