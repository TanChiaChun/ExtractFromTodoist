#print("Initialising")

# Import packages
#import sys
import os
import logging
import configparser
#import ctypes
import requests
import csv

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
    #switch1 = my_general_class.parse_boolean_string(my_config["Heading1"]["switch1"] )
    #var1 = my_config["Heading1"]["var1"]
    my_config_class.configure_logger()
except KeyError:
    my_main_exception.handle_exception("Config file error!")

# Get environment variables
todoist_token = os.getenv("Todoist_Token")
if todoist_token == None:
    my_main_exception.handle_exception("Missing environment variables!")

# Declare variables
projects_url = "https://api.todoist.com/rest/v1/projects"
tasks_url = "https://api.todoist.com/rest/v1/tasks"
dest_csv = r"data\Tasks_Full.csv"
tasks_list = [ ["Project", "Section", "Task", "StartDate", "DueDate", "Priority", "Parent"] ]
section_dict = {}
priority_dict = {
    1: "Low",
    2: "Medium",
    3: "High",
    4: "Critical"
}

##################################################
# Functions
##################################################
def parse_task_content(pContent):
    str_split = str.split(pContent, '|')
    due = ""
    if len(str_split) == 2:
        due = str_split[1]
    return [str_split[0], due]

def get_task_due(pDue):
    if pDue != None:
        return pDue.get("date")
    return ""

def parse_task_parent(pParent):
    if pParent != None:
        return "No"
    return "Yes"

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
        section_id = task["section_id"]
        if section_id != 0 and section_dict.get(section_id) == None:
            section_dict[section_id] = requests.get("https://api.todoist.com/rest/v1/sections/" + str(section_id), headers={"Authorization": "Bearer %s" % todoist_token}).json()["name"]
        task_split = parse_task_content(task["content"] )
        tasks_list.append( [ project["name"], section_dict.get(section_id), task_split[0], get_task_due( task.get("due") ), task_split[1], priority_dict[ task["priority"] ], parse_task_parent( task.get("parent_id") ) ] )
        tasks_counter += 1
my_logger.info("Obtained %d tasks", tasks_counter)

# Write to csv
my_logger.info("Writing to csv")
with open(dest_csv, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(tasks_list)
my_logger.info("Complete writing to %s\%s", CURRENT_DIRECTORY, dest_csv)

# if switch1:
#     pass

#my_general_class.finalise_app(is_app_end=True)