#!/usr/bin/env python 
# -*- coding: utf-8 -*-

################################################################################
# @script name   function box library A
# @version               v1.1
# @date                  2014-09-16
# @author                Yunpeng
# @draft                 Yunpeng
# 
# @Copyright 2015 Nokia Networks. All rights reserved.
################################################################################


import os,os.path
import shutil
import re
import linecache
import telnetlib
from xlutils.copy import copy
import xlrd
import xlwt
import time
import zipfile
from ftplib import FTP
import subprocess


def getrootDir():
    homedir = os.getcwd()
    return homedir

def gettapsinfo(xlsxname,sheetname,scenarioNum):
    book = xlrd.open_workbook(xlsxname)
    sheet = book.sheet_by_name(sheetname)
    line = 15
    tapsinfo = [[[None for z in range(2)] for y in range(line)] for x in range(scenarioNum)]
    # x means scenario,y means line,z means 0 or 1
    for x in range(scenarioNum):
        for y in range(line):
            for z in range(2):
                out = sheet.cell_value((y+1),(2*x+z+1))
                if(out != None):
                    #print out
                    tapsinfo[x][y][z] = out
                else:
                    print "read tapsinfo error! +_+"
                    break
    print tapsinfo
    return tapsinfo    
    
def getfreqplanv1(xlsxname,freqsheet):
    book = xlrd.open_workbook(xlsxname)
    sheet = book.sheet_by_name(freqsheet)
    channel_info = [[[None for j in range(2)] for i in range(3)]for x in range(3)]
    # 3 means B\M\T loop
    for i in range(3):
        # 2 means TX\RX info get
        for j in range(2):
            freqout = sheet.cell_value(2+j,(2+3*i))
            bandout = sheet.cell_value(2+j,(4+3*i))
            lossout = sheet.cell_value(2+j,(3+3*i))
            channel_info[0][i][j] = freqout
            channel_info[1][i][j] = bandout
            channel_info[2][i][j] = lossout
    print ("get the freq plan: %s \n\n" % channel_info)
    return channel_info 
    
def deletefile(dfile):  # for single file
    if os.path.isfile(dfile): 
        os.remove(dfile)
    else: 
        print ("the file  order to delete isn't exist: [%s] " % dfile)
        
def zip_dir(dirname,zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        filelist.append(dirname)
    else :
        for root, dirs, files in os.walk(dirname):
            for name in files:
                filelist.append(os.path.join(root, name))
         
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar,arcname)
    zf.close()

def unzip_file(zipfilename, unziptodir):
    if not os.path.exists(unziptodir): os.mkdir(unziptodir, 0777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\','/')
        
        if name.endswith('/'):
            os.mkdir(os.path.join(unziptodir, name))
        else:            
            ext_filename = os.path.join(unziptodir, name)
            ext_dir= os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir) : os.mkdir(ext_dir,0777)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

def maketimestamp():
    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time()))
    return timestamp

def list2strWithComma(list):
    for i in range (len(list)):
        list[i] = str(list[i])
    a = ",".join(list)
    return a    
    
def addData2csvline(origcsv,lineNum,Datalist):
    "new data need be a list"
    s = ''    
    lines = open(origcsv).readlines()
    flag = 0
    for line in lines:
        if flag == (lineNum-1):
            newdata = list2strWithComma(Datalist)
            # print ("newdata is: [%s]~~~~~~~~~~\n" % newdata)
            # print "S is [%s]\n" %s
            # print "Current line is [%s]\n" % line
            line = line.rstrip("\n")
            # print "new line data is [%s]\n" % line
            s += line + "," +newdata + "\n"
            # print "new s is [%s]\n" % s
        else:
            s += line
            # print s + "\n\n"
        flag += 1
    f = open(origcsv,'w')
    f.write(s)
    f.close()

def creatEmptyCSV(name):
    s = "\n\n\n"
    f = open(name,'w')
    f.write(s)
    f.close()
    
def tap2DCFxml(origfile,tapsinfo,outPath):
    lines = open(origfile).readlines()
    s = ''
    num = 0
    for line in lines:
        num += 1
        if line.find('<tap index = "0">') != -1 :
            linefirst = num
        else:
            continue
    flag = 0        
    for line in lines: 
        flag += 1
        if '<delay>' in line:
            print "taps line replace~~ : [" + str(flag) + "]"
            st = linecache.getline(origfile,flag)
            #print "flag is %s" % flag
            #print line
            tap = " "+ str(int(tapsinfo[(flag - linefirst)][0])) + " " + str(int(tapsinfo[(flag - linefirst)][1])) + " "
            s += re.sub(r"\<delay>(.*?)\</delay>","<delay>"+ tap +"</delay>",st)
        else:
            s += line
    f = open(outPath +"\\new.xml",'w')
    f.write(s)
    f.close()
    linecache.clearcache()

def copyFileto(sourcefile,targetfile): 
    shutil.copy(sourcefile,targetfile)        

def ftp_up(host,port,filename): 
    ftp=FTP() 
    ftp.set_debuglevel(2)
    ftp.connect(host,port) 
    ftp.login('','') 
    bufsize = 1024 
    file_handler = open(filename,'rb') 
    ftp.storbinary('STOR %s' % os.path.basename(filename),file_handler,bufsize) 
    ftp.set_debuglevel(0) 
    file_handler.close() 
    ftp.quit() 
    print "ftp up OK" 
    
def removeFileInFirstDir(targetDir): 
    for file in os.listdir(targetDir): 
        targetFile = os.path.join(targetDir,  file) 
        if os.path.isfile(targetFile): 
            os.remove(targetFile)
            
def checkdirExist(dir):
    a = os.path.exists(dir)
    return a 
    
def checkfileExist(file):
    a = os.path.isfile(file)
    return a

def build_Matrix(x,y,ele = 0):
	N=[]
	F=[]
	for i in range(x):
		for j in range(y):
			F.append(ele)
		N.append(F)
		F=[]
	return N
    
def fsvPrepare(fsvip,bandwidth,of,port = 5025):
    'make FSV ready in LTE mode'
    dict_SupportBands = {'1.4':'1_40', '3':'3_00', '5':'5_00','10':'10_00','15':'15_00','20':'20_00'}
    band = dict_SupportBands[bandwidth]
    fsvPre = ["*RST","INIT:CONT OFF","SYST:DISP:UPD ON","INST LTE","CONF:DL:BW BW"+band,"POW:AUTO2 ON"]
    global fsvtn
    fsvtn = telnetlib.Telnet(fsvip, port)
    for i in range(0,len(fsvPre)):
        fsvtn.write(fsvPre[i] + "\n")
        time.sleep(2)
        print("==> SEND : %s " % fsvPre[i])
        of.write('[FsvPrepare] ==> SEND : %s \r\n' % str(fsvPre[i]) )
    print 'FSV is prepared in LTE mode!'
    of.write('[FsvPrepare] FSV is prepared in LTE mode!')
    
def fsvAclr(freq,carrierband,cableloss,of,testtimes='3',testgap='3'):
    'input necessary parameter and query aclr value'
    aclrRusults = build_Matrix(int(testtimes)+1,8)
    aclrpre = ["CALC2:FEED 'SPEC:ACP'","FREQ:CENT "+freq+"MHz","DISP:TRAC:Y:RLEV:OFFS "+cableloss]
        
    for i in range(0,len(aclrpre)):
        fsvtn.write(aclrpre[i] + "\n")
        time.sleep(2)
        print("==> SEND : %s " % aclrpre[i])
        of.write('[FsvAclr] ==> SEND : %s \r\n' % str(aclrpre[i]) )
    doubleband = str(2*int(carrierband))
    aclrRusults[0] = ["TxAclr","carrierWidth(Mhz)","freq(Mhz)","TxPower(dbm)","Aclr_"+carrierband+"M_lower(db)","Aclr_"+carrierband+"M_upper(db)","Aclr_"+doubleband+"M_lower(db)","Aclr_"+doubleband+"M_upper(db)"]
    for i in range(1,int(testtimes)+1):
        print("query ACLR and save results for (%s/%s) time." % (i,testtimes))
        fsvtn.write("INIT;*WAI\n") # execute test for one time
        of.write("[FsvAclr]    ==> SEND : INIT;*WAI ,execute test for one time \r\n")
        time.sleep(2)
        fsvtn.write("CALC1:MARK:FUNC:POW:RES?\n") # ask for aclr result
        of.write("[FsvAclr]    ==> SEND : CALC1:MARK:FUNC:POW:RES? ,ask for aclr result \r\n \r\n")
        time.sleep(1)
        temp = fsvtn.read_very_eager()
        aclrRusults[i][1] = carrierband
        aclrRusults[i][2] = freq
        data = temp.split(',')
        for j in range(5):
            aclrRusults[i][j+3] = data[j]
            
        of.write('[FsvAclr] ACLR test result for %s time : \r\n Out Power is: %s\r\n  ACLR_%sM_lower is:%s\r\n  ACLR_%sM_upper is:%s\r\n  ACLR_%sM_lower is:%s\r\n  ACLR_%sM_upper is:%s\r\n' % ((i),str(aclrRusults[i][3]),carrierband,str(aclrRusults[i][4]),carrierband,str(aclrRusults[i][5]),carrierband,str(aclrRusults[i][6]),carrierband,str(aclrRusults[i][7]) ) )
            
        if aclrRusults[i] == [0]*8:
            print "==== get aclr result error!! ===="
            of.write("[FsvAclr] === data list is all 0,get aclr result error!! \r\n")
            break
        time.sleep(int(testgap))
    return aclrRusults

