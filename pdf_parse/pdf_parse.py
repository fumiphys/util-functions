# -*- coding: utf-8 -*-
import glob
import re
import subprocess


if __name__ == '__main__':
    filelist = glob.glob("*.pdf")
    for filename in filelist:
        try:
            result = subprocess.check_output(["pdfinfo", filename])
        except Exception:
            print(str(filename) + "    " + "\"" + "cannot parse" + "\"")
            continue
        result = str(result).split("\\n")
        for line in result:
            line = re.sub("Title:[ ]*", "Title:", line)
            values = line.split(":")
            if values[0] == "b'Title" and len(values) > 1:
                print(str(filename) + "    " + "\"" + str(values[1]) + "\"")
