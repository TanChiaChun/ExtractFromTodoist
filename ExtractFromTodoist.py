print("Initialising")

# Import packages
#import sys
import os
import logging
import configparser
#import ctypes
import requests
import csv
import win32com.client as win32

# Import classes
import MyClasses
import MyExceptions

# Initialise
PROJECT_NAME = "ExtractFromTodoist"
CURRENT_DIRECTORY = os.getcwd()
LOG_END = "\n-------------------------"
os.makedirs("app_data", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Initialise class
my_logger_class = MyClasses.MyLogger(PROJECT_NAME)
my_logger = my_logger_class.my_logger
my_main_exception = MyExceptions.MainException(PROJECT_NAME, my_logger, LOG_END)
my_general_class = MyClasses.AppGeneral(PROJECT_NAME, my_logger, LOG_END)
my_config_class = MyClasses.MyConfig(PROJECT_NAME, my_logger)
my_config = my_config_class.my_config

# Initialise config
if not os.path.isfile("config.ini"):
    my_config_class.create_file_specific()
    msg_box_res = my_config_class.create_file()
    if msg_box_res == 2: # 1 for IDOK, 2 for IDCANCEL
        my_general_class.finalise_app(is_app_end=False)
my_logger.info("Reading config file")
my_config.read("config.ini")
try:
    outlook_email_switch = my_general_class.parse_boolean_string(my_config["Outlook"]["email_enable"] )
    email_personal_work = my_config["Outlook"]["email_personal_work"]
    my_config_class.configure_logger()
except KeyError:
    my_main_exception.handle_exception("Config file error!")

# Get environment variables
if email_personal_work == "Personal":
    email_to = os.getenv("Email_Personal")
elif email_personal_work == "Work":
    email_to = os.getenv("Email_Work")
todoist_token = os.getenv("Todoist_Token")
if email_to == None or todoist_token == None:
    my_main_exception.handle_exception("Missing environment variables!")

# Declare variables
projects_url = "https://api.todoist.com/rest/v1/projects"
tasks_url = "https://api.todoist.com/rest/v1/tasks"
dest_csv = r"data\Projects.csv"
tasks_list = [ ["Project", "Section", "Task", "DoDate", "DueDate", "StartDate", "Priority", "Description", "SubTasks", "ID", "Parent"] ]
temp_list_start = []
temp_list_description = []
temp_list_append = []
key_startdate = "[S]"
key_description = "[D]"
section_dict = {}
priority_dict = {
    1: "4-Low",
    2: "3-Medium",
    3: "2-High",
    4: "1-Critical"
}

##################################################
# Functions
##################################################
# Function to search 2d index of value from list, raise exception if value not found
def get_2d_index(pList, pValue):
    for i, row in enumerate(pList):
        try:
            return i, row.index(pValue)
        except ValueError:
            pass
    raise Exception

# Function process sub-task and add info to correct main task
def parse_subtask(pList, pValue, pIndex, pTask):
    i = get_2d_index(pList, pValue)[0]
    pList[i][pIndex] = str.split(pTask, ']')[1]

# Function to append sub-task to main task
def append_subtask(pList, pValue, pTask):
    i = get_2d_index(pList, pValue)[0]
    if pList[i][8] == '': # 8 for
        pList[i][8] = pTask
    elif pList[i][8] != '':
        pList[i][8] += "|" + pTask

# Function to parse task content to name and DueDate 
def parse_task_content(pContent):
    str_split = str.split(pContent, '|')
    due = ""
    if len(str_split) == 2:
        due = str_split[1]
    return [str_split[0], due]

# Function to parse DueDate
def get_task_due(pDue):
    if pDue != None:
        return pDue.get("date")
    return ""

# Function to change parent ID to boolean
def parse_task_parent(pParent):
    if pParent == None:
        return "Yes"
    return "No"

##################################################
# Main
##################################################
# Extract projects
my_logger.info("Extracting from Todoist")
try:
    projects = requests.get(projects_url, headers={"Authorization": "Bearer %s" % todoist_token}).json()
except requests.exceptions.ConnectionError:
    my_main_exception.handle_exception("Error connecting to Todoist!")
my_logger.info("Obtained %d projects", len(projects) )

# Loop projects for sections and tasks
my_logger.info("Extracting tasks")
tasks_counter = 0
for project in projects:
    my_logger.debug("Reading project [%s]", project["name"] )

    tasks = requests.get(tasks_url, params={"project_id": project["id"]}, headers={"Authorization": "Bearer %s" % todoist_token}).json()
    for task in tasks:
        my_logger.debug("--Reading task [%s]", task["content"])

        # For StartDate sub-task
        if task["content"].startswith(key_startdate):
            try:
                parse_subtask(tasks_list, task["parent_id"], 5, task["content"] ) # 5 for StartDate
            except:
                temp_list_start.append(task) # Add to temp list if value not found yet, i.e. data not in sequence from raw
            continue

        # For description sub-task
        if task["content"].startswith(key_description):
            try:
                parse_subtask(tasks_list, task["parent_id"], 7, task["content"] ) # 7 for description
            except:
                temp_list_description.append(task) # Add to temp list if value not found yet, i.e. data not in sequence from raw
            continue

        # For normal sub-task
        if task.get("parent_id") != None:
            try:
                append_subtask(tasks_list, task["parent_id"], task["content"])
            except:
                temp_list_append.append(task) # Add to temp list if value not found yet, i.e. data not in sequence from raw

        # Get section ID
        section_id = task["section_id"]
        if section_id != 0 and section_dict.get(section_id) == None:
            section_dict[section_id] = requests.get("https://api.todoist.com/rest/v1/sections/" + str(section_id), headers={"Authorization": "Bearer %s" % todoist_token}).json()["name"]
        
        task_split = parse_task_content(task["content"] )
        tasks_list.append( [ project["name"], section_dict.get(section_id), task_split[0], get_task_due( task.get("due") ), task_split[1], "", priority_dict[ task["priority"] ], "", "", task["id"], parse_task_parent( task.get("parent_id") ) ] )
        tasks_counter += 1
        if tasks_counter % 10 == 0:
            my_logger.info("Extracting: %d tasks completed", tasks_counter)
my_logger.info("Obtained %d tasks", tasks_counter)

# Catch up tasks in temp lists
for row in temp_list_start:
    parse_subtask(tasks_list, row["parent_id"], 5, row["content"] )
for row in temp_list_description:
    parse_subtask(tasks_list, row["parent_id"], 7, row["content"] )
for row in temp_list_append:
    append_subtask(tasks_list, row["parent_id"], row["content"])

# Write to csv
my_logger.info("Writing to csv")
with open(dest_csv, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(tasks_list)
my_logger.info("Complete writing to %s\%s", CURRENT_DIRECTORY, dest_csv)

if outlook_email_switch:
    # Initialise Outlook application
    try:
        outlook_app = win32.Dispatch("Outlook.Application")
        outlook_namespace = outlook_app.GetNameSpace("MAPI")
    except:
        my_main_exception.handle_exception("Outlook application error!")
    
    try:
        # Send email with attachment
        my_logger.info("Drafting email")
        outlook_mail = outlook_app.CreateItem(0)
        outlook_mail.To = email_to
        outlook_mail.Subject = "Projects"
        my_logger.info("Attaching csv")
        outlook_mail.Attachments.Add(CURRENT_DIRECTORY + "\\" + dest_csv)
        outlook_mail.Send()
        my_logger.info("Email sent to %s", email_to)
    except:
        my_main_exception.handle_exception("Error sending email!")

my_general_class.finalise_app(is_app_end=True)