#!/usr/bin/python

# now pyhon 3 compatable,
import time
import httplib2
import http.client as httplib
import pprint
import hashlib
import os
import pandas as pd

from os import listdir
from os.path import isfile, join, isdir, exists

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from googleapiclient.errors import HttpError

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                        httplib.IncompleteRead, httplib.ImproperConnectionState,
                        httplib.CannotSendRequest, httplib.CannotSendHeader,
                        httplib.ResponseNotReady, httplib.BadStatusLine)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

### Functions

def get_dirs(dir):
    if not exists(dir):
        return list()

    result = [ join(dir,f) for f in listdir(dir) if isdir(join(dir,f)) ]
    return sorted(result)

def get_dirs_relative(dir):
    if not exists(dir):
        return list()

    result = [ f for f in listdir(dir) if isdir(join(dir,f)) ]
    return sorted(result)

def get_files(dir):
    if not exists(dir):
        return list()
    result = [ join(dir,f) for f in listdir(dir) if isfile(join(dir,f)) ]
    return sorted(result)

root="/local_dev/motion"


def get_file_list(service, trashed):
    """Retrieve a list of File resources.
         cribbed directly from the google tutorial

    Args:
        service: Drive API service instance.
    Returns:
         List of File resources.
    """
    result = []
    page_token = None
    while True:
        try:
            param = {}
            param['q'] = 'trashed = %s' % trashed
            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()

            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except Exception as error:
            print( 'An error occurred: %s' % error)
            break
        print ("get_file_list: looping")
    return result


# Copy your credentials from the console
CLIENT_ID = "<>"
CLIENT_SECRET = '<>'
TRASHED = "false"

### Format Conversions
# Google helpfully provides a mechanism to convert Google Drive files into
# formats that can be read by other applications. Uncomment any line to download
# your file(s) in that format.
# NOTE: Forms can't be converted and thus, aren't supported for download yet.
# WARNING: Downloading lots of files in more than 1 format is going to take a long
# damn time. Best to just pick one.

CONVERT_DOCUMENT = {
    # 'html': 'text/html',
    # 'txt': 'text/'plain',
    # 'rtf': 'application/rtf',
    # 'pdf': 'application/pdf',
    # 'odt': 'application/vnd.oasis.opendocument.text',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}

CONVERT_SPREADSHEET = {
    # 'pdf': 'application/pdf',
    # 'ods': 'application/vnd.oasis.opendocument.spreadsheet',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}

CONVERT_DRAWING = {
    # 'jpeg': 'image/jpeg',
    # 'png': 'image/png',
    'svg': 'image/svg+xml',
    # 'pdf': 'application/pdf',
}

CONVERT_PRESENTATION = {
    # 'pdf': 'application/pdf',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
}

# Ignored mimes
# Folders and Forms aren't supported yet.
IGNORED_MIMES = {
    'application/vnd.google-apps.folder',
    'application/vnd.google-apps.form'
}
# Google Drive file types
gdrive_mimes = {
    'application/vnd.google-apps.document': { 'name': 'Document', 'convert_to': CONVERT_DOCUMENT },
    'application/vnd.google-apps.spreadsheet': { 'name': 'Spreadsheet', 'convert_to': CONVERT_SPREADSHEET },
    'application/vnd.google-apps.drawing': { 'name': 'Drawing', 'convert_to': CONVERT_DRAWING },
    'application/vnd.google-apps.presentation': { 'name': 'Presentation', 'convert_to': CONVERT_PRESENTATION },
}


# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Path to the file to upload
#FILENAME = 'document.txt'
FILENAME = 'movie.mp4'

# Run through the OAuth flow and retrieve credentials
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
authorize_url = flow.step1_get_authorize_url()
#code = raw_input('Enter verification code: ').strip()
storage = Storage('HomeMonitor')
credentials = storage.get()
if credentials is None:
    print ('Go to the following link in your browser: ' + authorize_url)
    code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage.put(credentials)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

# Insert a file
media_body = MediaFileUpload(FILENAME, mimetype='text/plain', resumable=True)
body = {
    'title': 'movie.mp4',
    'description': 'A test document',
    #'mimeType': 'text/plain'
    #'mimeType': 'video/mp4'
    'mimeType': 'video/mpeg4'
}

#file = drive_service.files().insert(body=body, media_body=media_body).execute()
#pprint.pprint(file)
def now():
    return time.strftime("%Y%m%d %H%M%S")


def md5(fname):
    hasher = hashlib.md5()
    blocksize=65536
    afile = open(fname, 'rb')
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()


#print md5("movie.mp4");
# get the folders 
# drive_service.files().
def get_disk_files(service):
    result = []
    page_token = None
    while True:
        try:
            param = {}
            param['q'] = 'trashed = false'
            if page_token:
                param['pageToken'] = page_token
            files = service.files().list(**param).execute()

            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except Exception as error:
            print ('An error occurred: %s' % error)
            break
    print ("%s:get_file_list: looping" % now())
    return result

def build_path(node):
    if node['parents'][0]['isRoot'] == True:
        return node["title"];
    return join(build_path( folders_dict[node["parents"][0]["id"]]), node['title'])

folders = list()
folders_dict = dict()
file_entry = dict()
files = get_disk_files( drive_service )
for file in files:
    if file['mimeType'] == 'application/vnd.google-apps.folder':
        folders.extend([ file ] );
        folders_dict[file["id"]]=file

    #pprint.pprint(file)
    file_entry[file["title"]]=file


full_path = dict();
for entry in files:#folders:
    #pprint.pprint( entry )
    dir = entry['title']
    path = build_path( entry )
    full_path[path]=entry
    #print "PATH=%s" % path



def make_dir( d ):
    s=d.split('/')
    fp = None
    previous = None
    try:
        x = full_path[d]
        print ("found directory %s" % d)
        return
    except:
        tmp = 12# need to create

    for p in s:
        print ("Dir=%s" % fp)
        if fp is not None:
            previous = fp
            fp = fp + "/" + p
        else:
            fp = p
        try:
            e = full_path[fp]
        except:
            body = {
                'title': p,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            try:
                parent = full_path[previous]['id']
                body['parents'] = [{'id': parent }]
            except:
                x=s# dummy don't care

            file = drive_service.files().insert(body=body).execute()
            folders_dict[ file['id']]= file
            path = build_path(file)
            full_path[path] = file

def upload_video(service, parent, file):
    elements = file.split("/");
    name = elements[-1]
    media_body = MediaFileUpload(file, chunksize=-1, mimetype='text/plain', resumable=True)
    #print "upload_video: got here2"
    body = {
        'title': name,
        'description': 'Must Contain the time',
        'mimeType': 'video/mpeg4'
    }
    if parent is not None:
        body['parents'] = [{'id': parent }]

    #print "upload_video: got here3"
    request = service.files().insert(body=body, media_body=media_body)
    response=None
    #print "upload_video: got here"
    retires = 0
    while response is None:
        try:
            print ("%s: Uploading file %s " % (now(), file),)
            status, response = request.next_chunk()
            if 'id' in response:
                #print "%s: file '%s' was successfully uploaded." % (now(), response['title'])
                print ("uploaded %s." % response['title'])
                return response;
            else:
                #print ("The upload failed with an unexpected response: %s" % response)
                print (" failed with an unexpected response: %s" % response)
                return None
        except HttpError as e:
            pprint.pprint(response )
            if e.resp.status in RETRIABLE_STATUS_CODES:
                print( " A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
            else:
                print(" upload_video:some exception %s" % e )
                raise
        except RETRIABLE_EXCEPTIONS:
            print( " A retriable HTTP error %s" % e )
        retires +=1;
        if retires > 10:
            break

    print ("upload_vided: failed")
    return None



def check_dirs(root, d, today, modtime ):

    p=d + "/" + today #join(d,today)
    #print p
    try:
        fp=full_path[p]
    except:
        #print "xx=%s" % p
        print ("need to create %s"% p)
        make_dir(  p )
        fp = full_path[p]

    p = root + "/" + d+ "/movies/" +  today
    files = get_files(p);
    for f in files:
        print ("%s: checking %s " %( now(), f ))
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime ) = os.stat(f)
        if mtime < modtime:
            continue
        elements = f.split("/");
        name = elements[-1]
        parent = fp['id']
        parent_path = build_path( fp );
        path =   elements[-4] + '/' + elements[-2] + '/' + elements[-1]

        try:
            entry = full_path[path]
            if entry is not None:
                m5=md5(f)
                if entry['md5Checksum'] != m5:
                    try:
                        #print "have, need to update %s => %s" % (path, f)
                        print("checksum %s=%s"% (entry['md5Checksum'], md5(f)))
                        #file = drive_service.files().insert(body=body, media_body=media_body).execute()
                        file = upload_video( drive_service, parent, f )
                        #pprint.pprint(file)
                        #exit ("done")
                        if file is None:
                            return False
                        else:
                            m5=md5(f)
                            if m5 ==  file['md5Checksum']:
                                full_path[path] = file
                    except:
                        print ("failed .. try again later ... ")
                        #exit("something failed")
                        return False #sleep_time = 10


        except:
            #print "need to upload %s(%s) => %s" % (name,path, f)
            try:
                #file = drive_service.files().insert(body=body, media_body=media_body).execute()
                file = upload_video( drive_service, parent, f )
                if file is None:
                    return False
                else:
                    m5=md5(f)
                    if m5 ==  file['md5Checksum']:
                        full_path[path] = file
            except:
                print ("failed2 .. try again later ... ")
                #exit("done here 2");
                return False
    return True #time.sleep(sleep_time)



# read config
def read_config():
    global CLIENT_ID
    global CLIENT_SECRET
    config_file = "config.csv"
    if os.path.exiss(config_file):
        df = pd.read_csv(config_file, sep="=", header=None, names=["name", "value"]).set_index("name")
        CLIENT_ID = df.client_id.iloc[-1]
        CLIENT_SECRET = df.client_secret.iloc[-1]
    else:
        raise  Exception("config file config.csv not found")


read_config()
modified_dict = dict()
yesterday = time.strftime("%Y%m%d")
while True:
    dirs = get_dirs_relative( root )
    sleep_time = 60
    today=time.strftime("%Y%m%d")
    dirs = get_dirs_relative( root )

    for d in dirs:
        dates = get_dirs_relative( root + "/" + d + "/movies" );
        dates = list()
        #if today != yesterday:
        #       date.append(yesterday)
        dates.append( today )

        for date in dates:
            print ("date=%s"%date)
            path=root + "/" + d + "/movies"  + "/" + date
            modtime = None
            try:
                modtime = modified_dict[path]
            except:
                modtime = 0
            try:
                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime ) = os.stat(path)
                print ("%s modification time %d <=> %d" % (path, modtime, mtime))
                if (modtime <= mtime):# or (date == today ):
                    if check_dirs(root, d, date, modtime)==False:
                        sleep_time = 10
                    else:
                        modified_dict[path]=mtime
            except:
                modtime = 0

    print ("%s: looping ... sleep %d" % (now(), sleep_time))
    time.sleep(sleep_time)


filelist =get_file_list(drive_service,TRASHED)
exit()

for file in filelist:
    #pprint.pprint(file)
    print ("... Successfully converted and downloaded to %s" % file['title'])
    # is it ignored?
    if file['mimeType'] in IGNORED_MIMES:
        print ("Ignoring %s. Reason: %s in ignore list" % (file['title'], file['mimeType']))
        continue

    # is it a google drive file format?
    if file['mimeType'] in gdrive_mimes.keys():
        print("Found Google Drive %s %s..." % (gdrive_mimes[file['mimeType']]['name'], file['title']))
        for ext, mime in gdrive_mimes[file['mimeType']]['convert_to'].iteritems():
            result = download("%s%s.%s" % (DESTINATION,file['title'],ext), file['modifiedDate'], file['exportLinks'][mime], drive_service)
            if result is not None:
                print("... Successfully converted and downloaded to %s.%s" % (file['title'],ext))
        continue

        # it must be some normal file type. let's download it.
        result = download("%s%s" % (DESTINATION,file['title']), file['modifiedDate'], file['downloadUrl'], drive_service)
        if result is not None:
            print ("Successfully downloaded %s" % file['title'])
                        
