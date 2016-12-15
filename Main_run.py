#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

################################################################################
# @script name   Taps replace in DCF.zip and test ACLR on single carrier
# @version               v1.2
# @date                  2014-09-16
# @author                Yunpeng
# @draft                   Yunpeng
# 
# @Copyright 2015 Nokia Networks. All rights reserved.
# Modify history:
# 2015-09-24: change result to csv,easyer to analyse
################################################################################


import os
import sys
import shutil 
import time
import datetime
import HTX_class
import def1

from HTX_class import *
from def1 import *

#@@~~~~~~~~~~~~~~~~~~ 预定义参数部分 ~~~~~~~~~~~~~~~~~~~
tapsXls = 'tapsinfo.xlsx'
tapsSheet = "S-Matrix_ID"
scenarioNum = 3
Carrierbandwidth = "5" # Mhz
HOST = "192.168.255.69"
fsvhost = "192.168.1.2"
ftpport = "21"
port_shell = 2323
#aclrReadtimes = "3"
DCFnow = "DCF1"
rootdir = getrootDir()

fmOrigfile = rootdir + "\\FlexiMetros_orig.xml"
fmName = "FlexiMetros.xml"
workdir = rootdir + "\\Temp\\"
DCFdir = rootdir + "\\DCF_orig"
logdir = rootdir + "\\log"
resultdir = rootdir + "\\Results"
origDCFfile = rootdir + "\\DCF_ori.zip"
fm_inDCF = DCFdir + "\\" +fmName
fm_new = workdir + "\\new.xml"
ready_DCFfile = workdir + "\\DCF.zip"

freqplanfile = rootdir + "\\freq_info.xlsx"
freqplan = getfreqplanv1(freqplanfile,"Sheet1")
#==================================================

FHEEconfig = '<SetItUpRequest><Un\
it><CommonName>FHEE</CommonName><UnitInChainId>0</UnitInChainId><Pipe id="0" nominalPower="36.99"><C\
arrier id="0"><Antenna id="0" testModelName="ETM1_1" nominalPower="36.99" scale="0" bw="5" mimoId="-\
1" cellId="1" ></Antenna></Carrier></Pipe><Pipe id="1" nominalPower="36.99"><Carrier id="0"><Antenna\
 id="0" testModelName="ETM1_1" nominalPower="36.99" scale="0" bw="5" mimoId="-1" cellId="1" ></Anten\
na></Carrier></Pipe><RadioSpecific><GSM><DlControlPayloadOffset>0</DlControlPayloadOffset><ExtraNumb\
erOfSlotsToCapture>1</ExtraNumberOfSlotsToCapture></GSM></RadioSpecific></Unit><Connections><SM2Unit\
><DeltaCorrection>202590</DeltaCorrection><SM_MasterPort><IP>192.168.255.16</IP></SM_MasterPort><Sla\
vePort><UnitInChainId>0</UnitInChainId><Id>0</Id><UnitIP>192.168.255.69</UnitIP><FilterIP>192.168.25\
5.70</FilterIP></SlavePort></SM2Unit></Connections></SetItUpRequest>'

doubleband = str(2*int(Carrierbandwidth))
headlinestr = ("S-Matrix,TxAclr,carrierWidth(Mhz),freq(Mhz),TxPower(dbm),Aclr_%sM_lower(db),Aclr_%sM_upper(db),Aclr_%sM_lower(db),Aclr_%sM_upper(db),TxAclr,carrierWidth(Mhz),freq(Mhz),TxPower(dbm),Aclr_%sM_lower(db),Aclr_%sM_upper(db),Aclr_%sM_lower(db),Aclr_%sM_upper(db),TxAclr,carrierWidth(Mhz),freq(Mhz),TxPower(dbm),Aclr_%sM_lower(db),Aclr_%sM_upper(db),Aclr_%sM_lower(db),Aclr_%sM_upper(db)" % (Carrierbandwidth,Carrierbandwidth,doubleband,doubleband,Carrierbandwidth,Carrierbandwidth,doubleband,doubleband,Carrierbandwidth,Carrierbandwidth,doubleband,doubleband))

def logit(text):
    print text + "\n \n"
    of.write(text + "\n \n")

def checkdir(dir,operat):    
    if not checkdirExist(dir):
        os.mkdir(dir)
        logit("folder not exist! create a empty dir: [%s]" % dir)
    else: 
        if operat == "empty" :
            removeFileInFirstDir(dir)
            logit("empty the folder: [%s]" % dir)
        elif operat == "check" :
            logit("folder exist,do nothing: %s " % dir)
    logit("check folder done,OK~: [%s]" % dir)
    
def str2list(str):
    b = str.split("((")
    return b
    
def addahusk(list):
    a = []
    a.append(list)
    return a

csvlineFlag = 1    
headline = headlinestr.split(",")
taplist = gettapsinfo(tapsXls,tapsSheet,scenarioNum)
logname = rootdir + "\\init.txt"
of = open(logname, 'w')    
timestat = maketimestamp()
aclrcsvName = resultdir + "\\" +"ACLR_results_"+ timestat + ".csv"
creatEmptyCSV(aclrcsvName)    
addData2csvline(aclrcsvName,csvlineFlag,headline)
csvlineFlag += 1
   
#大循环开始
for m in range(scenarioNum):
    
    #@@~~~~~~~~~~~~~~~~~~ prepare work space ~~~~~~~~~~~~~~~~~~~
    checkfileExist(fmOrigfile)
    checkdir(workdir,"empty")
    checkdir(DCFdir,"empty")
    checkdir(logdir,"check")
    checkdir(resultdir,"check")

    unzip_file(origDCFfile,DCFdir)
    time.sleep(2)
    deletefile(fm_inDCF)
    #====================================================

    #@@~~~~~~~~~~~~~~~~~ creat log for every single run time ~~~~~~~~~~~~~~~~~~~
    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time())) 
    logmark = "log_" + timestamp
    currentlogDir = logdir + "\\" +logmark
    os.mkdir(currentlogDir)
    logname = currentlogDir + "\\" + logmark + ".txt"
    of = open(logname, 'w')
    #====================================================

    #@@~~~~~~~~~~~~~~ HTX sync for first time to enable eth ~~~~~~~~~~~~~~~~~~~~~~
    ht = HTX()
    try:
        ht.setUpHtx("FHEE")
        print "select UUT done"
        time.sleep(5)
        print "wair 5s , HTX set-it-up ongoing"
        htxStatus = ht.setItUp(FHEEconfig)
        print "set it up is done!~~"
        if(htxStatus == 0):
            print "\nHtx setup successfully!\n"
    except:
        sys.exit('Exception ocurred in Initialize and Set_it_up HTX!(1)')
    #====================================================
        
    # create xml
    tapsinfo = taplist[m]
    tap2DCFxml(fmOrigfile,tapsinfo,workdir)

    # copy xml to dir
    copyFileto(fm_new,fm_inDCF)
    copyFileto(fm_new,currentlogDir)
    
    # zip file and upload to unit
    zip_dir(DCFdir,ready_DCFfile)
    
    copyFileto(ready_DCFfile,currentlogDir)
    ftp_up(HOST,ftpport,ready_DCFfile)
    logit("ftpup DCF.zip to unit done")
    time.sleep(10)

    #@@~~~~~~~~~~~~~~~ open shell port ~~~~~~~~~~~~~~~~~~~
    try:
        tnsh = telnetlib.Telnet(HOST, port_shell)
        tnsh.read_until("@")
    except IOError:
        logit('Couldn`t connect to shell via telnet.')
        sys.exit('Couldn`t connect to shell!')
    logit("shell connect via telnet done~")
    #====================================================

    tnsh.write("flash -u " + DCFnow + " DCF.zip\n")
    logit("send: flash -u %s DCF.zip" % DCFnow)
    time.sleep(10)

    tnsh.write('Mcu -r 11 6\n')
    logit("send: Mcu -r 11 6")
    time.sleep(52)

    #@@~~~~~~~~~~~~~ HTX setup again after update DCF ~~~~~~~~~~~~~~~~
    try:
        ht.setUpHtx("FHEE")
        print "select UUT"
        time.sleep(5)
        print "wair 5s"
        htxStatus = ht.setItUp(FHEEconfig)
        print "set it up(sync + enalbe IP)"
        if(htxStatus == 0):
            print "\nHtx setup successfully!\n"
    except:
        sys.exit('Exception ocurred in Initialize and Set_it_up HTX!(2)')
    #====================================================
    time.sleep(5)
    fsvPrepare(fsvhost,"5",of)
    time.sleep(1)
    
    addData2csvline(aclrcsvName,csvlineFlag,[str(m+1)])
    #开始小循环,begin B\M\T freq loop
    for n in range(3): 
        txfrequency = freqplan[0][n][0]
        txbandinfo = int(freqplan[1][n][0])
        txcableloss = freqplan[2][n][0]
        channellsit = freqtoChannel(txfrequency,txbandinfo,freqplan[0][n][1],int(freqplan[1][n][1]))
        
        #@@~~~~~~~~~~~~~~~ active TX carrier according to channel ~~~~~~~~~~
        try:
            txonstat = ht.TxOn(channellsit[1],channellsit[0])
            if(txonstat == 0):
                print ("\n active TX carrier successfully!,freq is : %s \n"% txfrequency)
        except:
            sys.exit("\n Exception ocurred in active TX carrier,freq is : %s \n"% txfrequency)
        #==========================================
        time.sleep(3)
        aclrResult = fsvAclr(str(txfrequency),Carrierbandwidth,str(txcableloss),of,"1")
        print aclrResult
        print "\n"
        print aclrResult[1]
        addData2csvline(aclrcsvName,csvlineFlag,aclrResult[1])
        
        #@@~~~~~~~~~~~~~~~ Deactive TX carrier ~~~~~~~~~~
        try:
            txoffstat = ht.TxOff()
            if(txoffstat == 0):
                print ("\n Deactive TX carrier successfully!,freq is : %s \n"% txfrequency)
        except:
            sys.exit("\n Exception ocurred in active TX carrier,freq is : %s \n"% txfrequency)
        #==========================================
        time.sleep(7)
    csvlineFlag += 1
    #@@~~~~~~~~~~~~~~~ open shell port ~~~~~~~~~~~~~~~~~~~
    try:
        tnsh = telnetlib.Telnet(HOST, port_shell)
        tnsh.read_until("@")
    except IOError:
        logit('Couldn`t connect to shell via telnet.')
        sys.exit('Couldn`t connect to shell!')
    logit("shell connect via telnet done~")
    #====================================================
    tnsh.write("Mcu -r 11 6\n")
    logit("ID (%s \ %s) test done, send: Mcu -r 11 6\n" % ((m+1),scenarioNum))
    time.sleep(44)