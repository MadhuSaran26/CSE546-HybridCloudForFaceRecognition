import csv
import os
from dotenv import load_dotenv
load_dotenv()

OUTPUT_FILE_DIRECTORY = os.getenv("OUTPUT_FILE_DIRECTORY")
def writeResultToCsv(data, filename):
    if not os.path.exists(OUTPUT_FILE_DIRECTORY):
        os.makedirs(OUTPUT_FILE_DIRECTORY)
    filepath = OUTPUT_FILE_DIRECTORY + '/' + filename
    name = data.get('name', '')
    major = data.get('major', '')
    year = data.get('year', '')
    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, major, year])
