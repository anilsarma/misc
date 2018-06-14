import requests
from bs4 import BeautifulSoup as bs
import cookielib
from  urllib2 import urlopen
import argparse
import getpass
import StringIO
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

def get_session_id(raw_resp):
    soup = bs(raw_resp.text, 'lxml')
    token = soup.find_all('input', {'name':'survey_session_id'})[0]['value']
    return token

def download_file( user, password, outputfilename='rail_data.zip'):
    cj = cookielib.LWPCookieJar()

    payload = {
        'userName': user,      # 21st checkbox
        'password': password,  # first input-field
        }
    url = r'https://www.njtransit.com/mt/mt_servlet.srv?hdnPageAction=MTDevLoginSubmitTo'
    if payload['password'] is None:
        print "password is not set"
        exit(1)

    data = StringIO.StringIO()
    md5_old = None
    if os.path.exists(outputfilename):
        md5_old = md5(outputfilename)

    with requests.session() as s:
        #resp = s.get(url)
        #payload['survey_session_id'] = get_session_id(resp)
        response_post = s.post(url, data=payload)
        #print response_post.text
        soup = bs(response_post.text, 'html.parser')
        good = False
        for i, link in enumerate(soup.findAll('a')):
            _FULLURL = link.get('href')
            if 'mt_servlet.srv?hdnPageAction=MTDevResourceDownloadTo&Category=rail' in _FULLURL:
                print (_FULLURL)
                good = True


        print s.cookies
        if not good:
            print ("we did  get a valid response from the server.")
            exit(-1)

        r = s.get(r'https://www.njtransit.com/mt/mt_servlet.srv?hdnPageAction=MTDevResourceDownloadTo&Category=rail', stream=True)
        #r = s.get(url, stream=True)
        rail = open(outputfilename, "w")
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                data.write(chunk)
                rail.write(chunk)
        rail.close()


    try:
        data.seek(0)
        zip = zipfile.ZipFile(data)
        for x in zip.infolist():
            print x.filename
            c = zip.open(x)
            print c.read(500)
        print ("downloaded ", os.path.abspath(outputfilename))

        md5_new = md5(outputfilename)

        print md5_old, md5_new
        if md5_old != md5_new:
            fp = open("version.txt", "w")
            fp.write( pd.Timestamp('now').strftime("%m/%d/%Y %H:%M:%S"))
    except Exception as e:
        print "not a valid zip file", e
        raise  e
    # <a href="mt_servlet.srv?hdnPageAction=MTDevResourceDownloadTo&Category=rail">Rail Data</a>&nbsp;&nbsp;(Zip format)</font></td>
    # 		</tr>



    #print res


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', help="username.", required=False)
    parser.add_argument('--password', help="password.", required=False)
    parser.add_argument('--output', help="output file.", required=False, default='rail_data.zip')
    args = parser.parse_args()

    if args.user is None:
        args.user = raw_input("njtransit user:")

    if args.password is None:
        args.password = getpass.getpass("njtransit password:")

    download_file( args.user, args.password, args.output)

    exit(0)

