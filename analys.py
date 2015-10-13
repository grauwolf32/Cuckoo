import simplejson as json
import requests
import argparse
import logging
import os
import sys
import time
import shutil
import errno

def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: 
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def main():
    print 'Starting analys...'
    bad_ext = ""
    report_dir = "/media/ruslan/Transcend/MalwareRep"
    file_list = open("files.txt","r")
    task_list = []
    for file_ in file_list:
        file_ = file_[0:-1]
        (dirName,fileName) = os.path.split(file_)
        (fileBaseName,fileExtension) = os.path.splitext(fileName)
        if fileExtension == "":
            task_id = send_task(file_)
            if task_id != -1:
                task_list.append([fileName,dirName,task_id])
        else:
            if (bad_ext.find(fileExtension) != -1):
               continue
            else:
                task_id = send_task(file_)
                if task_id != -1:
                    task_list.append([fileName,dirName,task_id])

    while len(task_list) > 0 :
        task_list = [x for x in task_list if not save_report(x[0],str(report_dir) + str(x[1]),x[2]) ]
        print str(len(task_list)) + " files left to analys..."
        time.sleep(15)
   
    return


def save_report(fileName,dirName,task_id):
    REST_URL = 'http://localhost:8090/tasks/report/' + str(task_id) + '/html'
    CUCKOO_DIR = '/home/ruslan/Desktop/cuckoo/storage/analyses/'
    (fileBaseName,fileExtension) = os.path.splitext(fileName)
    r = requests.get(REST_URL)
    if r.status_code == 200 :
        dir_path = str(dirName) +'/' + str(fileBaseName)+'_'+fileExtension[1:]+'/'
        try:
            copyanything(CUCKOO_DIR+str(task_id),dir_path)
        except:
            dir_path = str(dirName) +'/' + str(fileBaseName)+'_'+str(task_id)+'/'
            try:
                copyanything(CUCKOO_DIR+str(task_id),dir_path)
            except:
                pass
        return True
    return False
    
def send_task(filename):
    REST_URL = 'http://localhost:8090/tasks/create/file'
    with open(str(filename),'rb') as sample:
        multipart_file = {"file": (filename,sample)}
        r = requests.post(REST_URL,files=multipart_file)
    
    json_decoder = json.JSONDecoder()
    try: 
        task_id = json_decoder.decode(r.text)["task_id"]
    except:
        task_id = -1
    return task_id

if __name__ == "__main__":
    main()
