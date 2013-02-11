#!/usr/bin/env python

import sys,json

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

FILE_ERROR=0
OPTION_ERROR=1
OTHER_ERROR=2
DEBUG = False
legal_options = {"formats":["-xml","-json"],"debug":["--debug"]}
error_array = ["Invalid file extension - expects '<filename>.arff'","Invalid option - expects '-json' or '-xml'.","The file format is invalid."]
errors = open("stderr","w")
error_log = []
line_count = 0


def build_output(schema,outfile,opts):
	JSON = ("-json" in opts)
	if JSON:
		output_json(schema, outfile)
	else:
		output_xml(schema,outfile)

def build_nodes(data, name):
	# Recurse through data and build DOM tree.
	output=[]
	parent = ET.Element(name)
	if(isinstance(data,list)):
		console("list")
		for item in data:
			if(name=="values"):
				tagname="value"
			elif(name=="attributes"):
				tagname="attribute"
			elif(name=="data"): 
				tagname = "entry"
			else:
				tagname = name
			output.append(build_nodes(item,name=tagname))
	elif(isinstance(data,dict)):
		for attr in data:
			output.append(build_nodes(data[attr],name=attr))
	if (len(output)>0):
		for entry in output:
			t = ET.ElementTree(entry)
			t.write(errors)
		parent.extend(tuple(output))
	else:
		parent.text=data
	return parent
	

def output_xml(schema,outfile):
	root = build_nodes(schema,'dataset')
	if not (root):
		console("root was null and I don't know why.")
	roottree = ET.ElementTree(root)
	roottree.write(outfile)


def exit_with_errors():
	"""docstring for exit_with_errors"""
	for error in error_log:
		console("Error at " + error['line_num']+":")
		console(error["message"])
		console(error["details"])
	sys.exit()

def get_filenames(args):
	"""docstring for get_filenames"""
	filenames = []
	for arg in args:
		if not arg[0]=='-':
			if has_valid_extension(arg):
				filenames.append(arg)
			else:
				log_error(0,FILE_ERROR, "Please check the file extension and try again.")
				exit_with_errors()
	return filenames

def get_options(args):
	"""docstring for get_options"""
	options = []
	for arg in args:
		if  arg[0]=='-':
			for option in legal_options:
				if(is_legal(option, arg)):
					options.append(arg)
	return options

def has_valid_extension(path):
	"""docstring for has_valid_extension"""
	filename = name_from_path(path)
	parts = filename.split(".")
	if(len(parts)<1):
		return False
	elif(parts[len(parts)-1]=="arff"):
		return True
	else:
		return False

def is_legal(option, arg):
	return arg in legal_options[option]
	"""docstring for is_legal"""

def console(msg):
	errors.write(str(msg))
	errors.write("\n")

def log_error(line_num,error_index, details):
	"""docstring for log_error"""
	this_error = {"line_num":line_num,"message":error_array,"details":details}
	error_log.append(this_error)

def name_from_path(path):
	"""docstring for name_from_path"""
	result = path
	substr = path.split("/")
	if(len(substr)>0):
		return substr[len(substr)-1]
	return result

def output_json(schema,outfile):
	outfile.write(json.dumps(schema))

def process(filename, opts):
	readdata = False
	handle = filename.split(".")[0] 
	if "-json" in opts:
		handle = handle + ".json"
	else:
		handle = handle + ".xml"
	if "--debug" in opts:
		DEBUG = True
	infile = open(filename,'r')
	outfile = open(handle,'w')
	schema = {"relation":"","attributes":[],"data":[]}
	for line in infile:
		if(line[0]=="%"):
			continue
		elif(line[0]=="@"):
			args = line.split()
			if (args[0]=="@relation"):
				schema["relation"]=args[1]
			elif(args[0]=="@attribute"):
				values = "".join(args[2:])
				if(values[0]=="{"):
					values = values[1:len(values)-1]
					values = values.split(",")
				schema["attributes"].append({"name":args[1],"values":values})
			elif(args[0]=="@data"):
				readdata=True
		elif(readdata):
			schema["data"].append(line.strip())
	if(DEBUG):
		show_schema(schema)
	names = []
	data = []
	attrs = schema["attributes"]
	for attr in attrs:
		names.append(attr["name"])
	for row in schema["data"]:
		row = row.split(",")
		entry = {}
		for name in names:
			entry[name] = row[names.index(name)]
		data.append(entry)
	schema["data"] = data
	build_output(schema,outfile,opts)

def show_schema(schema):
	"""debug"""
	for field in schema:
		console(field, schema[field])

def main():
	args = sys.argv[1:]
	file_args = get_filenames(args)
	opts = get_options(args)
	for filename in file_args:
		process(filename, opts)

main()