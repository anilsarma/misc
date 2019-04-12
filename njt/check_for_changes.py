import os
import subprocess
import pandas as pd
import zipfile, StringIO
import sqlite3
import argparse



def make_db(zip_file, outputfile, outputzipfile):
    with zipfile.ZipFile(zip_file, 'r', zipfile.ZIP_DEFLATED) as archive:
        print "Content of archive downloaded\n", archive.printdir()
        print "creating SQL Lite database ", outputfile
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
                print "\twriting {} {} records".format(x, df.shape[0])
                df.to_sql(name, conn, if_exists="replace", index=False )
                #print df.shape
                #break
    
    
    with zipfile.ZipFile(outputzipfile, 'w') as archive:
        print "writing to archive ",  os.path.basename(outputzipfile)
        archive.write(outputfile, os.path.basename(outputfile), zipfile.ZIP_DEFLATED)
        archive.write("version.txt", "version.txt", zipfile.ZIP_DEFLATED)
        
    with zipfile.ZipFile(outputzipfile) as archive:
            print archive.printdir()
    os.remove(outputfile)

def system(cmd):
    print("running system command ", cmd )
    ret = os.system(cmd)
    print("running system command ", cmd , "result", ret)
    if ret !=0:
       raise Exception("command cmd failed code={}".format(ret))
  
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--make', help="rail/bus", required=False, default=None)
    parser.add_argument('--type', help="rail/bus", required=False, default='rail')
    args = parser.parse_args()


    zip_file = "{}_data.zip".format(args.type)
    db_file = "{}_data_db.zip".format(args.type)
    if( args.make is not None) :
        print(zip_file)
        make_db(zip_file, "{}_data.db".format(args.type), db_file)
        exit(0)

    os.system("git pull ")
    os.system("python get_transit_data.py --type {} --output {}".format(args.type, zip_file))
    result = subprocess.check_output(['git', 'status'])
    tokens = result.split("\n")
    #make_db(r'rail_data.zip', "rail_data.db", "rail_data_db.zip" )
    #tokens.append('modified: rail_data.zip')
    for t in tokens:
        if zip_file in t:
            if 'modified:' in t:
                print "{} modified ".format (zip_file)
                print "making the sql files ... "
                make_db(zip_file, "{}_data.db".format(args.type), db_file )
                
                system("git add  version.txt {} {} ".format(zip_file, db_file ))
                system("git commit -m 'auto commit {}'".format( pd.Timestamp('now')))
                os.system("git push")
                break
