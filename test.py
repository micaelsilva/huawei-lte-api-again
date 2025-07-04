import json

import huawei_api
from enums.net import NetworkModeEnum, NetworkBandEnum, LTEBandEnum

if __name__ == "__main__":
	e = huawei_api.Client(
		ip="192.168.1.1",
		user="admin",
		password="admin")
	#print(e.set_net_mode(
	#	networkmode=NetworkModeEnum.MODE_4G_ONLY))
	#print(e.net_mode())
	#print(json.dumps(e.status(), indent=2))
	print(json.dumps(e.profiles(), indent=2))
	#print(e.register())
	#e.get_sms()
	#e.send_sms("8000", "Teste")