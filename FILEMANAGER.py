import os
import re

def file_exists(file):
	if (os.path.exists(file)):
		return True
	else:
		return False

def create_if_not_exists(file):
	#"last_depot.txt"
	#"remote_info.txt"
	if(not file_exists(file)):
		open(file, "w").close()
	
#def create_always(file):
#	open(file, "w").close()
	
def read_file_list(file):
	res = []
	if(file_exists(file)):
		f = open(file, "r")
		for line in f:
			res.append(line[:-1])
		f.close()
	return res

def read_file_dictionary(file, dictionary):
	if(file_exists(file)):
		f = open(file, "r")
		for line in f:
			if (re.search(":", line)):
				idx = line.index(":")
				var = line[:idx]
				if (var in dictionary):
					dictionary[var] = line[idx+1:-1]
		f.close()
	else:
		write_file_dictionary(file, dictionary)

def write_file_list(file, list):
	f = open(file, "w")
	for i in range(len(list)):
		f.write(list[i] + "\n")
	f.close()

def write_file_dictionary(file, dictionary):
	f = open(file, "w")
	for k in dictionary.keys():
		f.write(k + ":" + str(dictionary[k]) + "\n")
	f.close()

def write_file(file, body):
	f = open(file, "w")
	f.write(body)
	f.close()
#-----------------------------------------------------------	
def read_depot():
	res = []
	f = open("last_depot.txt", "r")
	for line in f:
		res.append(line.replace("\n",""))
	f.close()
	return res

def write_depot(depot):
	f = open("last_depot.txt", "w")
	for i in range(0, len(depot)):
		f.write(depot[i] + "\n")
	f.close()

def read_info(depot, env):
	f = open("remote_info.txt", "r")
	for line in f:
		line = line.replace("\n","")
		if(re.match(depot, line)):
			env["valk"] = line[line.index(":")+1:]
			if (env["valk"] != ""):
				if(os.path.exists(env["valk"] + "\\cookie.txt")):
					sf = open(env["valk"] + "\\cookie.txt", "r")
					for sline in sf:
						if(re.match("changelist_" + depot, sline)):
							env["changelist"] = int(sline[sline.index(":")+1:-1])
						if(re.match("projectid_" + depot, sline)):
							env["projectId"] = sline[sline.index(":")+1:-1]
						if(re.match("projectname_" + depot, sline)):
							pass
						if(re.match("field_to_" + depot, sline)):
							env["fieldTo"] = sline[sline.index(":")+1:-1]
						if(re.match("field_cc_" + depot, sline)):
							env["fieldCc"] = sline[sline.index(":")+1:-1]
					sf.close()
				else:
					open(env["valk"] + "\\cookie.txt", "w").close()
			else:
				print "Information ot stored: set 'location of Valk' first"
	f.close()

def write_info(depot, env):
	if(os.path.exists("remote_info.txt")):
		internal = {}
		f = open("remote_info.txt", "r")
		for line in f:
			line = line.replace("\n","")
			ind = line.index(":")
			internal[line[0:ind]] = line[ind+1:]
		f.close()
		internal[depot] = env["valk"]
		f = open("remote_info.txt", "w")
		for key in internal.keys():
			f.write(key + ":" + internal[key] + "\n")
		f.close()
		
		if(os.path.exists(env["valk"] + "\\cookie.txt")):
			f = open(env["valk"] + "\\cookie.txt", "w")
			f.write("changelist_" + depot + ":" + str(env["changelist"]) + "\n")
			f.write("projectid_" + depot + ":" + env["projectId"] + "\n")
			f.write("projectname_" + depot + ":\n")
			f.write("field_to_" + depot + ":" + env["fieldTo"] + "\n")
			f.write("field_cc_" + depot + ":" + env["fieldCc"] + "\n")
			f.close()

def add_remote_info(env):
	t = env["workspace"] + ":" + env["valk"] + "\n"
	f = open("remote_info.txt", "r")
	for line in f:
		if(not re.match(env["workspace"], line)):
			t += line
	f.close()
	f = open("remote_info.txt", "w")
	f.write(t)
	f.close()

def read_remote_info2(workspace):
	res = {}
	res["valk"] = ""
	res["changelist"] = ""
	res["projectId"] = ""
	f = open("remote_info.txt", "r")
	for line in f:
		if(re.match(workspace, line)):
			res["valk"] = line[line.index(":")+1:-1]
			if(os.path.exists(res["valk"] + "\\cookie.txt")):
				sf = open(res["valk"] + "\\cookie.txt", "r")
				for sline in sf:
					if(re.match("changelist_" + workspace, sline)):
						res["changelist"] = sline[sline.index(":")+1:-1]
					if(re.match("projectid_" + workspace, sline)):
						res["projectId"] = sline[sline.index(":")+1:-1]
				sf.close()
			break
	f.close()
	return res

def	add_last_branches(branch):
	branches = read_branches()
	t = branch + "\n"
	for i in range(0, len(branches)):
		if(branch != branches[i]):
			t += branches[i] + "\n"
	f = open("last_branches.txt", "w")
	f.write(t)
	f.close()

