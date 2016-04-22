from IPython.display import SVG, display
import os, csv, time

def c2p (lat,lon):
	x1 = 5.492680
	y1 = 59.038151
	x2 = 5.791032
	y2 = 58.794293
	qvx = 1193/(x2-x1)
	qvy = 1881/(y1-y2)
	dx = lon-x1
	dy = y1-lat
	rx = int(dx*qvx)
	ry = int(dy*qvy)
	return (rx,ry)

f=open("stops.csv")
o=open("StavangerRegionMap.svg","r")
n=open("StavangerRegionBS.svg","w")
nth_byte = os.path.getsize("StavangerRegionMap.svg")-7
n.write(o.read(nth_byte))

for row in csv.reader(f):
	x,y=c2p(float(row[0]),float(row[1]))
	if x >= 6 and y >=6 and x <= 1193-6 and y <= 1881-6: # are x,y inside the defined map?
		ids = row[2]+","+row[3]
		markerstring = """<circle id="%s" cx="%s" cy="%s" fill="rgb(100, 0, 250)" r="6" opacity="0.9"/><circle cx="%s" cy="%s" fill="rgb(255, 255, 255)" r="3" opacity="0.8"/>"""%(ids,x,y,x,y)
		# "id" is free to define and contains both bus stop number and description, comma delimited
		# "type" and "name" are not standard SVG <circle> attributes and can explode some browsers rendering engine
		# r is of int type, <circle> does not take float arguments for it
		# print(markerstring)
		n.write(markerstring)
	else:
		pass

n.write(o.read())
time.sleep(10) # Allow the new created file to settle a little while
print ("READY >")

SVG(filename="StavangerRegionBS.svg")
