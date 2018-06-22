import os
import subprocess
import pandas as pd

os.system("git pull ")
os.system("python get_transit_data.py")
result = subprocess.check_output(['git', 'status'])
tokens = result.split("\n")

for t in tokens:
     if 'rail_data.zip' in t:
          if 'modified:' in t:
             print "rail_data.zip modified "
             os.system("git add rail_data.zip version.txt")
             os.system("git commit -m 'auto commit {}'".format( pd.Timestamp('now')))
             os.system("git push")
             break
