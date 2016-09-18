import json
import csv
import requests

class jsonGetter(object):
	def __init__(self,firebaseName):
		self.json_data = requests.get(firebaseName)
		print("got data")
		if self.json_data.status_code != 200:
			#raise .
			print("Error: bad request")
		self.json_data = self.json_data.json()
	def getData(self):
		pass
		# ( -> { <id> : { "time": time, "x":x, "x":y  }})
		timePeriods = [key for key in self.json_data]
		latestFootage = sorted(timePeriods,key=str.lower)[0]
		#for timePeriod in self.json_data:
		subDict = self.json_data[latestFootage]
		for frameName in subDict:
			frame = json.loads(subDict[frameName])
			for entityId in frame:
				yield frame[entityId]


def firebaseToCsv(csvFileName, firebaseName):
    with open(csvFileName, 'w') as csvFile: 
        writer = csv.DictWriter(csvFile, fieldnames = ['x','y'],lineterminator = '\n')
        getter = jsonGetter(firebaseName)
        writer.writeheader()
        for event in getter.getData():
            try:
                xValue = event['x']
                yValue = event['y']
            except KeyError:
                xValue = event['width']
                yValue = event['height']
            csvData = {'x': xValue,'y': yValue}
            print (event)
            writer.writerow(csvData)

firebaseToCsv("/mnt/projects/c9dfa99e-7d58-11e6-a1ae-9bb94fbfab7e/myCsv.csv","https://mithack2016-a7c0c.firebaseio.com/.json")
