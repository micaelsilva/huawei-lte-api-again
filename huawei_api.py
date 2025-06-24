import hashlib
import xml.etree.ElementTree as ET
from base64 import b64encode
import json
import datetime

import requests

import xml_parse
from xml_parse import xml_findall, parse_xml, parsing_childs, create_xml
import enums.errors
import enums.sms
import enums.net

class Client:
	def __init__(
			self,
			ip="192.168.1.1",
			user=None,
			password=None):
		self.ip = ip
		self.user = user
		self.password = password
		self.s = requests.Session()
		self.s.timeout = 3
		r = self.s.get(f"http://{self.ip}/api/webserver/SesTokInfo")
		
		self.sessID = next((x.text for x in xml_findall(r.text, './SesInfo')))
		self.token = next((x.text for x in xml_findall(r.text, './TokInfo')))

		self.tokens = []
		self.s.headers.update({"Cookie": self.sessID})
		if user and password:
			self.login()

	@staticmethod
	def sha256sum(msg):
		return hashlib.sha256(msg.encode()).hexdigest()

	def login(self):
		r = self._request_post_get("user/state-login", "get")
		state_login = self.xml_to_dict(r.text)
		
		if state_login['State'] != '-1':
			return True
		
		if state_login['password_type'] == '4':
			hashed_pwd = self.sha256sum(self.password)
			str_passwd = self.sha256sum(self.user + b64encode(hashed_pwd.encode()).decode() + self.token)

		xml_request = create_xml({
			"Username": self.user,
			"Password": b64encode(str_passwd.encode()).decode(),
			"password_type": state_login["password_type"]
		})

		r = self._request_post_get("user/login", "post", data=xml_request, headers={"__RequestVerificationToken": self.token})

		self.sessID = next((f"{i.name}={i.value}" for i in self.s.cookies))
		
		self.s.headers.update({"Cookie": self.sessID})
		self.tokens = r.headers['__RequestVerificationToken'].split("#")[:-1]		
						
	def _request_post_get(self, endpoint, method="post", headers=None, data=None):
		if method == "post":
			try:
				token = {"__RequestVerificationToken": self.tokens.pop(0)}
			except IndexError:
				token = {"__RequestVerificationToken": headers["__RequestVerificationToken"]}
			if not headers:
				headers = token
			else:
				if "__RequestVerificationToken" in headers:
					headers.update(token)
		return self.s.request(method, f"http://{self.ip}/api/{endpoint}", headers=headers, data=data)

	@staticmethod
	def process_error(xml):
		x = next((x.text for x in xml.findall("./code")))
		raise Exception(enums.errors.ResponseCodeEnum(int(x)))

	def xml_to_dict(self, xml):
		lista = {}
		xml = parse_xml(xml)
		if xml.tag == "error":
			self.process_error(xml)
		for child in xml:
			lista.update(parsing_childs(child))
		return lista
	
	def _run(self, request):
		try:
			out = self.xml_to_dict(request.text)
			return out
		except Exception as a:
			print(a)
	
	def network(self):
		return self._run(self._request_post_get("net/network", "get"))
	
	def net_mode(self):
		net_modes =  self._run(self._request_post_get("net/net-mode", "get"))
		net_modes.update({
			"NetworkMode": enums.net.NetworkModeEnum(net_modes["NetworkMode"]),
			"NetworkBand": enums.net.NetworkBandEnum(
				int("0x" + net_modes["NetworkBand"], 16)),
			"LTEBand": enums.net.LTEBandEnum(
				int("0x" + net_modes["LTEBand"], 16))
		})
		return net_modes
	
	def current_plmn(self):
		return self._run(self._request_post_get("net/current-plmn", "get"))
		
	def status(self):
		return self._run(self._request_post_get("monitoring/status", "get"))
	
	def get_sms(self):
		return self._run(self._request_post_get("sms/sms-list", data=create_xml({
			'PageIndex': "1",
      'ReadCount': "6",
      'BoxType': enums.sms.BoxTypeEnum.LOCAL_INBOX.value,
      'SortType': "0",
      'Ascending': "0",
      'UnreadPreferred': "1"
		})))
		#sms/sms-list
		#sms/get-cbsnewslist
	
	def send_sms(self, number, msg):
		return self._run(self._request_post_get("sms/send-sms", data=create_xml({
		'Index': "-1",
      'Phones': {"Phone": number},
      'Sca': "",
      'Content': msg,
      'Length': len(msg),
      'Reserved': enums.sms.TextModeEnum.EIGHT_BIT.value,
      'Date': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') 
		})))
