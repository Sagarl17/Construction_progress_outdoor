import re
import sys
import json
from  datetime import date

project = json.load(open('./data/analysis/hybrid.json'))

filename=sys.argv[1]
today_date=sys.argv[2]

file = open('./reports/'+filename+'.txt','w')

def compare_dates(date1,date2):
    return (date(int(date1.split("-")[2]), int(date1.split("-")[1]), int(date1.split("-")[0]))-date(int(date2.split("-")[2]), int(date2.split("-")[1]), int(date2.split("-")[0]))).days

def finish_check(predecessor,i):
    previous=predecessor

    if type(predecessor) is int:
        project_id=predecessor
        delta=0
    else:
        temp = list(map(int, re.findall(r'\d+', predecessor) ))
        project_id=temp[0]
        try:
            delta=temp[1]
        except:
            delta=0
    object_ids=[]
    for k in range(len(project)):
        if project[k]["Project_id"]==project_id:
            object_ids.append(k)     
    
    for k in object_ids:
        if project[k]["Construction_Finish"]=="":
            predecessor=project[k]["Predecessors"]
            ids=k
            break
    
    if predecessor==previous:
        ids=i
        reason_id=predecessor
    else:
        reason_id,ids=finish_check(predecessor,ids)
    
    return reason_id,ids

def predecessor_check(i,predecessor,total):
    previous=predecessor
    if type(predecessor) is int:
        project_id=predecessor
        delta=0
    else:
        temp = list(map(int, re.findall(r'\d+', predecessor) ))
        project_id=temp[0]
        try:
            delta=temp[1]
        except:
            delta=0
    


    object_ids=[]
    for k in range(len(project)):
        if project[k]["Project_id"]==project_id:
            object_ids.append(k)



    for k in object_ids:
        if "SS" in str(previous):
            try:
                if "+" in previous:
                    if compare_dates(project[k]["Construction_Start"],project[i]["Construction_Start"])<delta:
                        predecessor=project[k]["Predecessors"]
                        break
                else:
                    if compare_dates(project[k]["Construction_Start"],project[i]["Construction_Start"])+delta<0:
                        predecessor=project[k]["Predecessors"]
                        break
            except:
                if project[i]["Construction_Start"]=="":
                    predecessor=previous
                else:
                    predecessor=project[k]["Predecessors"]
                break

        elif "FF" in str(previous):
            try:
                if "+" in previous:
                    if compare_dates(project[k]["Construction_Finish"],project[i]["Construction_Finish"])<delta:
                        predecessor=project[k]["Predecessors"]
                        break
                else:
                    if compare_dates(project[k]["Construction_Finish"],project[i]["Construction_Finish"])+delta<0:
                        predecessor=project[k]["Predecessors"]
                        break
            except:
                if project[i]["Construction_Finish"]=="":
                    predecessor=previous
                else:
                    predecessor=project[k]["Predecessors"]
                break
        elif "SF" in str(previous):
            try:
                if "+" in previous:
                    if compare_dates(project[k]["Construction_Start"],project[i]["Construction_Finish"])<delta:
                        predecessor=project[k]["Predecessors"]
                        break
                else:
                    if compare_dates(project[k]["Construction_Start"],project[i]["Construction_Finish"])+delta<0:
                        predecessor=project[k]["Predecessors"]
                        break 
            except:
                if project[i]["Construction_Finish"]=="":
                    predecessor=previous
                else:
                    predecessor=project[k]["Predecessors"]
                break


        elif "FS" in str(previous):
            try:
                if "+" in previous:
                    if compare_dates(project[i]["Construction_Start"],project[k]["Construction_Finish"])<delta:
                        predecessor=project[k]["Predecessors"]
                        break
                else:
                    if compare_dates(project[i]["Construction_Start"],project[k]["Construction_Finish"])+delta<0:
                        predecessor=project[k]["Predecessors"]
                        break
            except:
                if project[i]["Construction_Start"]=="":
                    predecessor=previous
                else:
                    predecessor=project[k]["Predecessors"]
                break
        
        else:
            try:
                if compare_dates(project[i]["Construction_Start"],project[k]["Construction_Finish"])<0:
                    predecessor=project[k]["Predecessors"]
                    break
            except:
                if project[i]["Construction_Start"]=="":
                    predecessor=previous
                else:
                    predecessor=project[k]["Predecessors"]
                break

    
    
    
    if previous==predecessor:
        reason_id=i
    else:
        try:
            if int((project[k]["Construction_Duration"].split(" days"))[0])>int((project[k]["Project_Duration"].split(" days"))[0]):
                total.append(k)
        except:
            total.append(k)

        reason_id=predecessor_check(k,predecessor,total)

    return reason_id    



#Task Started Late



for i in range(len(project)):
    predecessors=[]
    if project[i]["Construction_Start"]!="":
        total=[]
        if compare_dates(project[i]["Project_Start"],project[i]["Construction_Start"])<0:
            predecessor=project[i]["Predecessors"]
            reason_id=predecessor_check(i,predecessor,total)
            total=set(total)
            if i==reason_id:
                file.write("%s started late due to self"%(project[i]["BIM_id"]))
            else:
                file.write("%s started late due to :"%(project[i]["BIM_id"]))



#Task Started Early



for i in range(len(project)):
    predecessors=[]
    if project[i]["Construction_Start"]!="":
        if compare_dates(project[i]["Project_Start"],project[i]["Construction_Start"])>0:
            file.write("%s started early"%(project[i]["BIM_id"]))




#Task Finished Late



for i in range(len(project)):
    predecessors=[]
    if project[i]["Construction_Finish"]!="":
        total=[]
        if compare_dates(project[i]["Project_Finish"],project[i]["Construction_Finish"])<0:
            predecessor=project[i]["Predecessors"]
            reason_id=predecessor_check(i,predecessor,total)
            total=set(total)
            if i==reason_id:
                file.write("%s finished late due to self"%(project[i]["BIM_id"]))
            else:
                file.write("%s finished late due to :"%(project[i]["BIM_id"]))
                for t in total:
                    file.write(project[t]["BIM_id"])
        

 

#Task Finished Early


for i in range(len(project)):
    if project[i]["Construction_Finish"]!="":
        if compare_dates(project[i]["Project_Finish"],project[i]["Construction_Finish"])>0:
            file.write("%s finished early"%(project[i]["BIM_id"]))



#Task Taking Long




for i in range(len(project)):
    if project[i]["Construction_Start"]!="" and project[i]["Construction_Finish"]=="":
        duration= compare_dates(today_date,project[i]["Construction_Start"])
        if duration>int((project[i]["Project_Duration"].split(" days"))[0]):
            file.write("%s is taking too long"%(project[i]["BIM_id"]))




#Task Being Delayed 





for i in range(len(project)):
    total=[]
    if compare_dates(today_date,project[i]["Project_Start"])>0:
        if project[i]["Construction_Start"]=="":
            predecessor=project[i]["Predecessors"]
            reason_id,k=finish_check(predecessor,i)
            file.write("%s being delayed due to %s"%(project[i]["BIM_id"],project[k]["BIM_id"]))
            



#Compensated by task



for i in range(len(project)):
    if project[i]["Construction_Duration"]!="":
        if int((project[i]["Construction_Duration"].split(" days"))[0])<int((project[i]["Project_Duration"].split(" days"))[0]):
            com=int((project[i]["Project_Duration"].split(" days"))[0])-int((project[i]["Construction_Duration"].split(" days"))[0])
            if compare_dates(project[i]["Construction_Start"],project[i]["Project_Start"])>0:
                file.write("%s compensated delay by %s days"%(project[i]["BIM_id"],com))


#Check if predecessor isnt complete:


for i in range(len(project)):
    if project[i]["Construction_Duration"]!="":
        predecessors=project[i]["Predecessors"]
        reason_id,k=finish_check(predecessor,i)
        file.write("%s is complete despite its predecessor %s not being complete"%(project[i]["BIM_id"],project[k]["BIM_id"]))
        
file.close()