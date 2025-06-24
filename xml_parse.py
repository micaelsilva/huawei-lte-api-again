import xml.etree.ElementTree as ET
import json

import enums

def parse_xml(text):
	try:
		root = ET.fromstring(text)
	except Exception:
		raise Exception("Cannot be parsed")
	else:
		return root

def xml_findall(text, path):
	root = parse_xml(text)
	return root.findall(path)

def create_element(root, item):
	for k, v in item.items():
		b = ET.SubElement(root, k)
		if isinstance(v, (int, str)):
			b.text = str(v)
		else:
			pass

def create_xml(items):
	root = ET.Element('request')
	for k, v in items.items():
		b = ET.SubElement(root, k)
		if isinstance(v, (int, str)):
			b.text = str(v)
		else:
			create_element(b, v)
	return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(root, encoding="unicode")

def process_error(xml):
	x = next((x.text for x in xml.findall("./code")))
	raise Exception(enums.ResponseCodeEnum(int(x)))

def parsing_childs(elm):
	if len(elm) > 0:
		child_text = {}
		for sub in elm:
			par = parsing_childs(sub)
			if isinstance(child_text, list):
			  child_text.append(par)
			elif list(par.keys())[0] in child_text:
			  a = list(par.keys())[0]
			  child_text = [child_text[a]]
			  child_text.append(list(par.values())[0])
			else:
			  
			  child_text.update(par)
		return {elm.tag: child_text}
	else:
		return {elm.tag: elm.text}

def xml_to_dict(xml):
	lista = {}
	xml = parse_xml(xml)
	if xml.tag == "error":
		process_error(xml)
	for child in xml:
		lista.update(parsing_childs(child))
	return lista

