from smart_open import smart_open
def generateResultsUsingMapping():
    mappingDict = load_file_as_dict()
    correctCount = 0
    totalCount = len(mappingDict)
    for key, value in mappingDict.items():
        videoNameKey = key.split('.')[0] + '.csv'
        for line in smart_open('s3://image-classification-output/' + videoNameKey, 'rb'):
            line_str = line.decode('utf-8').strip()
            line = line_str.split(",")
            print(line)
            if value['major'] == line[1] and value['year'] == line[2]:
                correctCount += 1
    percent = (correctCount / totalCount)*100
    print(percent)


def load_file_as_dict(file_path='/Users/diyabiju/Documents/GitHub/CSE546-FaceRecognition/mapping'):
    data_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            video_name = parts[0]
            info = parts[1].split(',')
            data_dict[video_name] = {'major': info[0], 'year': info[1]}
    return data_dict

generateResultsUsingMapping()