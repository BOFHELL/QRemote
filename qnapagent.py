import socket, select
import xml.etree.ElementTree as ET
import subprocess
#import os

from dict2xml import dict2xml as xmlify
from collections import OrderedDict



###############
## DEFINE APPS 
## Icon Size:
##  phone:  256x256
##  pad:    350x350
##  tv:     380x380
##############


apps = [{
    'name':'Kodi',
    'displayName':'Kodi',
    'version':'17',
    'uuid':'k0di0wn',
    'icon_phone':'icons/kodi_phone.png',
    'icon_pad':'yes',
    'start':'kodi',
    'stop':'kodi.bin'
    },
    {
    'name':'Chrome',
    'displayName':'Chrome',
    'version':'12',
    'uuid':'ch0me',
    'icon_phone':'icons/chrome_phone.png',
    'icon_pad':'yes',
    'start':'google-chrome-stable',
    'stop':'chrome'
    }]



def dPrint(msg):
    DEBUG=False
    if DEBUG:
        print(msg)


def build_apps():
    dPrint("========== SORT ========")
    FIELDS=["name","displayName","version","uuid","icon_phone","icon_pad"]
    retstr=''
    
    for app in apps:
        retstr+="<item>"
        for f in FIELDS:
            retstr+=("<{}>"+app[f]+"</{}>").format(f,f)
        retstr+="</item>"

    if retstr:
        retstr='<errRtn>success</errRtn>'+retstr
    return retstr


def build_xml(data):
    ret_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    ret_xml +='<QDocRoot version="1.1">'
    ret_xml += data
    ret_xml +='</QDocRoot>'

    return ret_xml



#############
## cmds:
##  ACK  ListQPKG  GetIcon  Launch  KillAll  GetCurrentUser  Login2  Logout  SetAutoLogin  GetQTVSetting
def sendBack(cmd, con, V=0, ACK_DATA=''):
        V+=1
        root = ET.fromstring(cmd)

        for cmd_xml in root.findall("cmd"):
            cmd_switch=cmd_xml.text
        
        dPrint("=== INSTANCE: {} =====".format(V))
        dPrint("Empfangen {} CMD:>>{}<<".format(V, cmd))
        #dPrint("=============")
        #QDocRoot version="1.1" 
        if cmd_switch=="ListQPKG":         ### WAiT FOR    ACK  
            dPrint("[DEBUG]: ListQPKG ====> cmd: {}".format(cmd))
            #### Check if all fine - > we say allways YES :D and build sending xml, to count and send first
            # Cli -> List -> SRV : ListQPKG | Srv -> size < return bytes xmls -> send xml
            ACK_SEND_xml=build_xml(build_apps())

            dPrint("Konstruckt {}".format(ACK_SEND_xml))
            
            size_data =  '<size>{}</size>'.format(len(ACK_SEND_xml))
            ## 
            # Send Size from APPS XML file
            size_xml = build_xml('<size>{}</size>'.format(len(ACK_SEND_xml))) 
            
            #^size_xml=header+'<QDocRoot version="1.1"><size>293</size></QDocRoot>'
            dPrint("SENDE ===> SIZE ARRAY: {}".format(size_xml) )
            
            con.sendall( size_xml )

        #############
        ## Launch App
        if cmd_switch=="Launch":
            dPrint("[DEBUG]: Launch ====> cmd: {}".format(cmd))
            params=[]
            for params_xml in root.findall("param"):
                params.append(params_xml.text)
            #### Check App
            dPrint(" [Launch]: params ====> {}".format(params))
            app_name=params[0]
            #### abkuerzen  app_uuid, app_icon=list(params)  ??i
            app=(item for item in apps if item["name"] == app_name).next()
            if app:
                startp=app['start']
                dPrint(" [LAuNCh]: start ===== cmd: {}".format(startp))
                subprocess.Popen(startp)

        #######
        ## ACK 
        if cmd_switch=="ACK":
            #dPrint("[DEBUG]: ACK ====> cmd: {}".format(cmd))
            #dPrint("SENDE ===> ACK: {}".format(ACK_DATA))
            #dPrint(" SENDE LEN: {}".format(len(ACK_DATA)))
            con.sendall( ACK_DATA )

        ###################
        ## GetIcon for App
        if cmd_switch=='GetIcon':
            dPrint("[DEBUG]: GetIcon ====> cmd: {}".format(cmd))
            params=[]
            for params_xml in root.findall("param"):
                params.append(params_xml.text)
            #### Check App
            dPrint(" [GetIcon]: params ====> {}".format(params))
            app_uuid=params[0]
            app_icon=params[1]
            dPrint("APPID {} ICON FUER {}".format(app_uuid,app_icon))
            #### abkuerzen  app_uuid, app_icon=list(params)  ??i
            app=(item for item in apps if item["uuid"] == app_uuid).next()
            dPrint("Gefunden APP {}".format(app))
            if app:
                dPrint(" try to get Icon: {}".format(app['icon_'+app_icon]))
                fIcon=open(app['icon_'+app_icon]).read()
                dPrint("opened")
                dPrint("array size")
                fsize_xml = build_xml('<size>{}</size>'.format(len(fIcon))) 
                dPrint(" [GetIcon] SENDE ===> SIZE ARRAY: {}".format(fsize_xml) )
                con.sendall ( fsize_xml )

                ACK_SEND_xml=fIcon

        ###########################
        ## KillAll -> run STOP cmd
        if cmd_switch=="KillAll":
            dPrint("[DEBUG]: KillAll ====> cmd: {}".format(cmd))
            for item in apps:
                subprocess.call(['killall', '-3', item["stop"]])


        #########################
        ## Handle return request
        ACK = con.recv(2048)
        if ACK:
            #dPrint("[DEBUG]: ACK REV {}".format(ACK))
            #dPrint("====== WILL SEND: ")

            #dPrint(ACK_SEND_xml)

            sendBack(ACK, con, V, ACK_SEND_xml)
        dPrint("=============")



if __name__ == "__main__":

    CONNECTION_LIST = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 9812
         
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
     
    while True:
        try:
            # Get the list sockets which are ready to be read through select
            read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
            
            for sock in read_sockets:
                #New connection
                if sock == server_socket:
                    # Handle the case in which there is a new connection recieved through server_socket
                    sockfd, addr = server_socket.accept()
                    CONNECTION_LIST.append(sockfd)
                    dPrint ("Client (%s, %s) connected" % addr)

                #Some incoming message from a client
                else:
                    try:
                        #In Windows, sometimes when a TCP program closes abruptly,
                        # a "Connection reset by peer" exception will be thrown
                        data = sock.recv(RECV_BUFFER)
                        # echo back the client message
                        if data:
                            #root = ET.fromstring(data)
                            #for cmd_xml in root.findall("cmd"):
                            #    cmd=cmd_xml.text
                            #sendBack(cmd, sock)
                            sendBack(data, sock)
                            #dPrint(" REV ===== {}".format(data))
                            #header='<?xml version="1.0" encoding="UTF-8"?>\n'
                            #header+='<QDocRoot version="1.1"><size>293</size></QDocRoot>'
                            #sock.send(header)

                        # client disconnected, so remove from socket list
                    except:
                        dPrint("Socket error")
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        continue

        except (KeyboardInterrupt, SystemExit):
            dPrint("Keyboard Interrupt")
            #server_socket.close()
            raise
