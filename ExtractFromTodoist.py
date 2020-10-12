#print("Initialising")

# Import packages
#import sys
import os
import logging
import configparser
#import ctypes

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

# # Get environment variables
# token1 = os.getenv("Token1")
# if token1 == None:
#     my_main_exception.handle_exception("Missing environment variables!")

# Declare variables


##################################################
# Functions
##################################################


##################################################
# Main
##################################################


# if switch1:
#     pass

#my_general_class.finalise_app(is_app_end=True)