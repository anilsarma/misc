import requests
from bs4 import BeautifulSoup as bs
try:
    import cookielib
except:
    from http import cookiejar as cookielib

try:
    from  urllib2 import urlopen
except:
    pass
import argparse
import getpass
try:
    import StringIO
except:
    from io import StringIO
try:
    import raw_input as input
except:
    pass
import zipfile
import os
import hashlib
import pandas as pd

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def now():
    return pd.Timestamp('now')


def download_file( user, password, outputfilename='rail_data.zip'):
    cj = cookielib.LWPCookieJar()

    # payload for submit to the website.
    payload = {
        'userName': user,      # 21st checkbox
        'password': password,  # first input-field
        }
    url = r'https://www.njtransit.com/mt/mt_servlet.srv?hdnPageAction=MTDevLoginSubmitTo'
    if payload['password'] is None:
        print ("password is not set")
        exit(1)

    data = StringIO()
    md5_old = None
    if os.path.exists(outputfilename):
        md5_old = md5(outputfilename)

    with requests.session() as s:
        print (now(), "logging into ", url)
        response_post = s.post(url, data=payload)
        #print response_post.text
        soup = bs(response_post.text, 'html.parser')
        print (now(), "received response")
        good = False
        # go through the anchors in the page and find the one we want.
        for i, link in enumerate(soup.findAll('a')):
            _FULLURL = link.get('href')
            if 'mt_servlet.srv?hdnPageAction=MTDevResourceDownloadTo&Category=rail' in _FULLURL:
                #print now(), (_FULLURL)
                print (now(), "found the download link")
                good = True

        print (now(), "cookies", s.cookies)
        if not good:
            print ("we did not get a valid response from the server or the server has changed.")
            exit(-1)

        print (now(), "starting download of rail data")
        r = s.get(r'https://www.njtransit.com/mt/mt_servlet.srv?hdnPageAction=MTDevResourceDownloadTo&Category=rail', stream=True)
        print (now(), "writing to ", os.path.abspath(outputfilename))
        rail = open(outputfilename, "w")
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                data.write(chunk)
                rail.write(chunk)
        rail.close()
        print (now(), "download complete, size:", data.len, "(bytes)")


    try:
        data.seek(0)
        zip = zipfile.ZipFile(data)
        for x in zip.infolist():
            print (now(), "\tchecking archive ", x.filename)
            c = zip.open(x)
            c.read(500)
        print (now(), ("checking complete ", os.path.abspath(outputfilename)))

        # check the previous mdf file.
        md5_new = md5(outputfilename)
        print (now(), "checksum old/new", md5_old, md5_new)
        if md5_old != md5_new:
            str = pd.Timestamp('now').strftime("%m/%d/%Y %H:%M:%S")
            print ( now(), "checksum changed, updating version.txt to:", str)

            fp = open("version.txt", "w")
            fp.write( str)
            fp.close()
            
        else:
            print (now(), "checksum unchanged")
    except Exception as e:
        print( "not a valid zip file", e)
        raise  e


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', help="username.", required=False)
    parser.add_argument('--password', help="password.", required=False)
    parser.add_argument('--output', help="output file.", required=False, default='rail_data.zip')
    args = parser.parse_args()

    # we should move this to the user home directory
    login_files = [ x for x in [ "login.preferences", ".login", os.path.join( os.path.expanduser("~"), ".njt", "login.preferences") ] if os.path.exists(x ) ]
    #print login_files

    if login_files: #os.path.exists(".login"):
        login_filename = login_files[0]
        print ("using ", login_filename)
        # user,password
        # <username>,<password>
        df = pd.read_csv(login_filename, sep='=', header=None, names=['field', 'value'])
        #print df
        #print df.columns
        if 'value' in df.columns:            
            #print "good"
            dfx = df
            df = df.set_index('field').T.reset_index()
            #print "NULL", pd.isnull(dfx.value).all()
            if dfx.shape[0]>0:
                if pd.isnull(dfx.value).all():
                    df = pd.read_csv('.login') # old style file
            #print df

        if not df.empty:
            #print df
            if args.user is None:
                args.user = df.iloc[0].user
            if args.password is None:
                args.password = df.iloc[0].password

    if args.user is None:
        args.user = input("njtransit user:")

    if args.password is None:
        args.password = getpass.getpass("njtransit password:")

    r = download_file( args.user, args.password, args.output)

    exit(0)

