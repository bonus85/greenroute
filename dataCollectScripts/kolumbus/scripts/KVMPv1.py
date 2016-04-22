# Kolumbus SIRI Vehicle Monitoring parse KVMD.json and store it in Cassandra
# KVMD.json acts as a lock file for KVMQ so it will be deleted after loading data 

import os, time
from datetime import datetime
import json

while True:
	
	if (not os.path.isfile("KVMD.json")):
		time.sleep(10)
	
	else:
	
		try:
			json_file = open("KVMD.json", "r")
	
			dt = datetime.now()
	
			while True:
			
				c=json_file.read(1)
			
				if c == '[':						
				
					while True:						

						aopen = 0
						aclosed = 0
						a4json = ""

						while True:

							c = json_file.read(1)
							if c ==',': c = json_file.read(1)
							if c == ']': break
							a4json += str(c)
							if c == '{': aopen += 1
							if c == '}': aclosed += 1
							if aopen == aclosed:
								if aopen != 0: break

						print a4json						# Cassandra loading comes here
					
						if c == ']': break
					
					if c == ']': break
		
			json_file.close()
			os.remove("KVMD.json")
	
		except: pass
