import os

# Settings file to get the path
# The folder csvfiles and its files were deleted from the git to save our personal/scholar data
# If you wanna use this bot to get information about your School/University you must create your own files using your token and edit the moodleapi package to fit your own purposes.
PATH_EVENTS = os.path.abspath('bot').split('bot')[0] + "csvfiles\events.csv"
PATH_ASSIGNMENTS = os.path.abspath('bot').split('bot')[0] + "csvfiles\\assignments.csv"
PATH_CLASSES = os.path.abspath('bot').split('bot')[0] + "csvfiles\liveclasses.csv"
PATH_TOKENS = os.path.abspath('bot').split('bot')[0] + "csvfiles\\tokens.csv"

allowed_channels = []