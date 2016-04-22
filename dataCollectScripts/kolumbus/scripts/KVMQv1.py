# Requests Kolumbus SIRI Vehicle Monitoring response and stores it in KVMD.json 

import os, time, requests
from datetime import datetime
import xmltodict, json

url="http://sis.kolumbus.no:90/VMWS/VMService.svc"

while True:
	
	dt = datetime.now()

	xml = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:siri="http://www.kolumbus.no/siri" xmlns:siri1="http://www.siri.org.uk/siri">
   <soapenv:Header/>
   <soapenv:Body>
	  <siri:GetVehicleMonitoring>
		 <ServiceRequestInfo>

			<siri1:RequestTimestamp>%s</siri1:RequestTimestamp>
			<siri1:RequestorRef> testreference </siri1:RequestorRef>
			<!--Optional:-->
			<siri1:MessageIdentifier>?</siri1:MessageIdentifier>
		 </ServiceRequestInfo>
		 <Request version="1.4">
		 	<VehicleMonitoringRequest version="1.4">
		 		<RequestTimestamp>%s</RequestTimestamp>
		 	</VehicleMonitoringRequest>
		  </Request>

	  </siri:GetVehicleMonitoring>
   </soapenv:Body>
</soapenv:Envelope>""" % (dt.isoformat("T"),dt.isoformat("T"))

	headers = {'content-type': 'text/xml', 'SOAPAction': 'GetVehicleMonitoring'}
	
	try:
		response = requests.post(url,data=xml,headers=headers,timeout=5.0)
	except: 
		pass
	else:
		if (not os.path.isfile("KVMD.json")):
			json_file = open("KVMD.json", "w")
			json_file.write("%s" % json.dumps(xmltodict.parse(response.content), indent=2))
			json_file.close()
		else:
			time.sleep(10)
			