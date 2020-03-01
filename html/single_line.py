import os
import re
data = None
def make_string(file):
    with open (file, "r") as myfile:
        data=myfile.readlines()

    data = " ".join(data)
    data = data.replace("\n", " ")
    data = data.replace("\\", "")

    data = data.replace("\"", "\\\"")
    data = re.sub("\s+", " ", data)

    data = re.sub(">\s+<", "><", data)
    return data

#print(data)

import glob, os
dir =r"C:\Users\Anil Sarma\git\electronics\arduino\esp_base\www2"
dir_files = []
for root, dirs, files in os.walk(dir):
    for file in files:
        dir_files.append(os.path.join(root, file))

on = []
h = open('html_pages.h', "w")
h.write("#ifndef __INDEX_HTML_H__\n#define __INDEX_HTML_H__\n")
for file in dir_files:
    orig_name = os.path.relpath(file, dir)
    name = os.path.relpath(file, dir).replace("/", "_")
    name = name.replace("\\", "_dir")
    name = name.replace("-", "_dash")
    name = name.replace(".", "_dot")
    s = make_string(file)
    h.write("const char* {}=\"{}\";\n".format(name, s));

    #print(orig_name, "=", name)
    on.append("server.on(\"{}\", handle_{});".format(orig_name, name))

    print("void handle_{}() ".format(name))
    print("{")
    print("  server.send(200, \"text/plain\", {});".format(name))
    print("}")
h.write("#endif\n")
h.close()


for o in on:
    print(o)