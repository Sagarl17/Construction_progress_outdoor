import sys
import json
from datetime import date

def compare_dates(date1,date2):
    return (date(int(date1.split("-")[2]), int(date1.split("-")[1]), int(date1.split("-")[0]))-date(int(date2.split("-")[2]), int(date2.split("-")[1]), int(date2.split("-")[0]))).days

filename=sys.argv[1]
today_date=sys.argv[2]
previous_date=sys.argv[3]

progress = json.load(open('./data/external/'+filename+'.json'))
project = json.load(open('./data/analysis/hybrid.json'))
for i in range(len(project)):
    try:
        if len(progress[project[i]["BIM_id"]]["children"])==1:
            if progress[project[i]["BIM_id"]]["progress"]==100 and project[i]["Construction_Finish"]=="" and project[i]["Construction_Start"]!="":
                project[i]["Construction_Finish"]=today_date
                project[i]["Construction_Duration"]=str(abs(compare_dates(today_date,project[i]["Construction_Start"])))+" days"
            elif progress[project[i]["BIM_id"]]["progress"]==100 and len(project[i]["Construction_Start"])=="":
                project[i]["Construction_Start"]=previous_date
                project[i]["Construction_Finish"]=today_date
                project[i]["Construction_Duration"]=str(abs(compare_dates(today_date,previous_date)))+" days"

            elif progress[project[i]["BIM_id"]]["progress"]<100 and progress[project[i]["BIM_id"]]["progress"]>0 and project[i]["Construction_Start"]=="":
                project[i]["Construction_Start"]=today_date

                

        else:
            for k in range(len(progress[project[i]["BIM_id"]]["children"])):
                if progress[project[i]["BIM_id"]]["children"][k]["progress"]==100 and progress[project[i]["BIM_id"]]["children"][k]["name"]== project[i]["stage"] and project[i]["Construction_Finish"]=="" and project[i]["Construction_Start"]!="" :
                    project[i]["Construction_Finish"]=today_date
                    project[i]["Construction_Duration"]=str(abs(compare_dates(today_date,project[i]["Construction_Start"])))+" days"
                elif progress[project[i]["BIM_id"]]["children"][k]["progress"]==100 and project[i]["Construction_Start"]=="" and progress[project[i]["BIM_id"]]["children"][k]["name"]== project[i]["stage"]:
                    project[i]["Construction_Start"]=previous_date
                    project[i]["Construction_Finish"]=today_date
                    project[i]["Construction_Duration"]=str(abs(compare_dates(today_date,previous_date)))+" days"
    
                elif progress[project[i]["BIM_id"]]["children"][k]["progress"]<100 and progress[project[i]["BIM_id"]]["children"][k]["progress"]>0 and project[i]["Construction_Start"]=="" and progress[project[i]["BIM_id"]]["children"][k]["name"]== project[i]["stage"]:
                    project[i]["Construction_Start"]=today_date
                
    except:
        pass






with open('./data/analysis/hybrid.json', 'w') as outfile:
    json.dump(project, outfile)
