import simplejson as json
import requests
import argparse
import logging
import os
import sys
import time
import shutil
import errno

def get_info(start_dir):
    report_dir = []
    report_data = []
    find_report_dirs(start_dir,report_dir)
    for dir_ in report_dir:
        json_report = os.path.join(dir_,'report.json')
        json_data = open(json_report)
        data = json.load(json_data)
        #Here i get a number of signatures
        try:
            number_of_signatures = len(data['signatures'])
        except:
            print 'Error, can not number of signatures'
            number_of_signatures = 0

        #Compute max and average severity of those signatures
        try:
            max_severity = 0
            avg_severity = 0
            for signature in data['signatures']:
                severity = signature['severity']
                if max_severity < severity:
                    max_severity = severity
                avg_severity += severity
            if number_of_signatures != 0:
                avg_severity = float(avg_severity) / float(number_of_signatures)
        except:
            print 'Error, can not get average severity'
            avg_severity = 0
            max_severity = 0

        #Here i get a number of mutexes, registry keys and files used by programm
        try:
            number_of_mutexes = len(data["behavior"]["summary"]["mutexes"])
            number_of_regkeys = len(data["behavior"]["summary"]["keys"])
            number_of_files   = len(data["behavior"]["summary"]["files"])
        except:
            print 'Error, can not get behavioral summary'
            number_of_mutexes = 0
            number_of_regkeys = 0
            number_of_files = 0

        #Analys of behavioral analys: number of processes, total amount of calls
        try:
            total_function_calls = 0
            num_of_processes = len(data["behavior"]["processes"])
            for proc in data["behavior"]["processes"]:
                total_function_calls += len(proc["calls"])
        except:
            print 'Error, can not get process calls'
            total_function_calls = 0
            num_of_processes = 0

        #Analys of network activity
        try:
            total_network_connects = 0
            total_network_connects += len(data["network"]["tcp"])
            total_network_connects += len(data["network"]["http"])
            total_network_connects += len(data["network"]["smtp"])
            total_network_connects += len(data["network"]["hosts"])
            total_network_connects += len(data["network"]["dns"])
            total_network_connects += len(data["network"]["udp"])
            total_network_connects += len(data["network"]["irc"])
            total_network_connects += len(data["network"]["icmp"])
            total_network_connects += len(data["network"]["domains"])

            conn_tcp = len(data["network"]["tcp"])
            conn_http =  len(data["network"]["http"])
            conn_domains = len(data["network"]["domains"])
            conn_hosts =  len(data["network"]["hosts"])
        except:
            print 'Error, can not get network stat'
            total_network_connects = 0
            conn_tcp = 0
            conn_http = 0
            conn_domains = 0
            conn_hosts = 0
        #Deration of analys
        try:
            duration = data["info"]["duration"]
        except:
            print 'Error, can not get duration'
            duration = 0
        #Path (need to be added to result
        try:
            targ_path = str(data["target"]["file"]["path"])
        except:
            targ_path = "./"
        #Save result
        report_data.append([number_of_signatures,max_severity,avg_severity,number_of_mutexes,number_of_regkeys,number_of_files,\
        num_of_processes,total_function_calls,total_network_connects,conn_tcp,conn_http,conn_domains,conn_hosts,duration,targ_path])

    return report_data


def find_report_dirs(start_dir,found_dir):
    for name in os.listdir(start_dir):
        full_path = os.path.join(start_dir,name)
        if name == 'reports':
            if os.path.isdir(full_path):
                found_dir.append(full_path)
                continue
        if not os.path.islink(full_path) and os.path.isdir(full_path):
            find_report_dirs(full_path,found_dir)

def main():
    start_dir = '/media/ruslan/Transcend/MalwrReports/'
    data = get_info(start_dir)
    report_csv = open('report_new.csv','w')
    report_csv.write('Number of signatures,Max severity,Average severity,Mutexes,Registry keys,Files,\
        Processes,Function calls,Network connections,TCP,HTTP,Domains,Hosts,Duration,Target Path\n')
    for item in data:
        line = ''
        for i in xrange(0,len(item)-1):
           line += str(item[i])
           line += ','
        line += str(item[len(item)-1])+'\n'
        report_csv.write(line)
    return

if __name__ == "__main__":
    main()
