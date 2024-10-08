import os
import subprocess
import pandas as pd
import zipfile
from io import StringIO
import sqlite3


def make_db(zip_file, outputfile, outputzipfile):
    with zipfile.ZipFile(zip_file, 'r', zipfile.ZIP_DEFLATED) as archive:
        print ("Content of archive downloaded\n", archive.printdir())
        print ("creating SQL Lite database ", outputfile)
        df = pd.read_csv('station_codes.txt');
        with sqlite3.connect(outputfile) as conn:
            df.to_sql('station_codes', conn, if_exists="replace", index=False )
            for x in archive.namelist():
                #print x
                f=archive.open(x)    
                contents=f.read()
                f.close()
                s = StringIO.StringIO(contents)
                df = pd.read_csv(s)
                name = os.path.splitext(x)[0]
                print ("\twriting {} {} records".format(x, df.shape[0]))
                df.to_sql(name, conn, if_exists="replace", index=False )
                #print df.shape
                #break
    
    
    with zipfile.ZipFile(outputzipfile, 'w') as archive:
        print ("writing to archive ",  os.path.basename(outputzipfile))
        archive.write(outputfile, os.path.basename(outputfile), zipfile.ZIP_DEFLATED)
        archive.write("version.txt", "version.txt", zipfile.ZIP_DEFLATED)
        
    with zipfile.ZipFile(outputzipfile) as archive:
            print (archive.printdir())
    os.remove(outputfile)

def system(cmd):
    print("running system command ", cmd )
    ret = os.system(cmd)
    print("running system command ", cmd , "result", ret)
    if ret !=0:
       raise Exception("command cmd failed code={}".format(ret))
  
if __name__ == "__main__":
    os.system("git pull ")
    os.system("python get_transit_data.py")
    result = subprocess.check_output(['git', 'status'])
    try:
        result = result.decode("utf-8")
    except:
        pass
    tokens = result.split("\n")
    #make_db(r'rail_data.zip', "rail_data.db", "rail_data_db.zip" )
    #tokens.append('modified: rail_data.zip')
    for t in tokens:
        if 'rail_data.zip' in t:
            if 'modified:' in t:
                print ("rail_data.zip modified ")
                print ("making the sql files ... ")
                make_db(r'rail_data.zip', "rail_data.db", "rail_data_db.zip" )
                
                system("git add rail_data.zip version.txt rail_data_db.zip")
                system("git commit -m 'auto commit {}'".format( pd.Timestamp('now')))
                os.system("git push")
                break
