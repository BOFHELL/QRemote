import socket, select
import xml.etree.ElementTree as ET
import subprocess

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


################################################
## Send Broadcast Packet 4 Autodetect in QRemote
##
########### Listen on   "\x00\x00\x00\x00\x00\x00Cl\x00\x00\x01\x00\x00\x00\x00\x00" -> Answer
#
def send_broadcast():
    print "Sende Broadcast"
    cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    cs.sendto('245ebe0bbb2453650100010000002504ca11c60100000c3139322e3136382e312e3800010669716e617000090a4672\ x69747a2e626f7800280754532d58383200290754532d5838320049085456532d38383200ca', ('255.255.255.255', 8097))
   #"\x24\x5e\xbe\x0b\xbb\x24\x53\x65\x01\x00\x01\x00\x00\x00\x25\x04\xca\x11\xc6\x01\x00\x00\x0c\x31\x39\x32\x2e\x31\x36\x38\x2e\x31\x2e\x38\x00\x01\x06\x69\x71\x6e\x61\x70\x00\x09\x0a\x46\x72\x69\x74\x7a\x2e\x62\x6f\x78\x00\x28\x07\x54\x53\x2d\x58\x38\x32\x00\x29\x07\x54\x53\x2d\x58\x38\x32\x00\x49\x08\x54\x56\x53\x2d\x38\x38\x32\x00\xca" | socat - udp-datagram:255.255.255.255:8097,broadcast


##  >>> "hello".encode("hex")
#'68656c6c6f'


#### snip

#from socket import *
#cs = socket(AF_INET, SOCK_DGRAM)
#cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#cs.sendto('This is a test', ('255.255.255.255', 54545))
##### snip





#############
## cmds:
##  ACK  ListQPKG  GetIcon  Launch  KillAll  GetCurrentUser  Login2  Logout  SetAutoLogin  GetQTVSetting
def sendBack(cmd, con, V=0, ACK_DATA=''):
        V+=1
        root = ET.fromstring(cmd)

        for cmd_xml in root.findall("cmd"):
            cmd_switch=cmd_xml.text
        
        dPrint("=== INSTANCE: {} =====".format(V))
        #QDocRoot version="1.1" 
        if cmd_switch=="ListQPKG":         ### WAiT FOR    ACK  
            dPrint("[DEBUG]: ListQPKG ====> cmd: {}".format(cmd))
            #### Check if all fine - > we say allways YES :D and build sending xml, to count and send first
            # Cli -> List -> SRV : ListQPKG | Srv -> size < return bytes xmls -> send xml
            ACK_SEND_xml=build_xml(build_apps())
            size_data =  '<size>{}</size>'.format(len(ACK_SEND_xml))
            # Send Size from APPS XML file
            size_xml = build_xml('<size>{}</size>'.format(len(ACK_SEND_xml))) 
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
            dPrint("[DEBUG]: ACK ====> cmd: {}".format(cmd))
            dPrint(" SEND LEN: {}".format(len(ACK_DATA)))
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
            #### abkuerzen  app_uuid, app_icon=list(params)  ??i
            app=(item for item in apps if item["uuid"] == app_uuid).next()
            if app:
                dPrint(" try to get Icon: {}".format(app['icon_'+app_icon]))
                fIcon=open(app['icon_'+app_icon]).read()
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

if __name__ == "__main__":

    CONNECTION_LIST = []    # list of socket clients
    RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
    PORT = 9812
         
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    CONNECTION_LIST.append(server_socket)
    

    #######
    ## test
    #######
    #cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #cs.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #msgr="{}\n{}\n{}\n{}".format("$^$ER@@>$^$Se%","192.168.1.6","iQnap","Fritz.Box(TS-X82)")

    #cs.sendto(msgr, ('255.255.255.255', 8097))
    #$^$ER@@>$^$Se%
    #192.168.1.33iqnap   
    #Fritz.box(TS-X82)TS-X82ITVS-882i
    
    
    
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('',8097))

    #m=s.recvfrom(1024)
    #if m[0].encode("hex") == "000000000000436c0000010000000000" :
    #   print "YO"
    #print m[0].encode("hex")
    CONNECTION_LIST.append(s)
    #######

    while True:
        try:
            read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
            
            for sock in read_sockets:
                #New connection
                if sock == server_socket:
                    sockfd, addr = server_socket.accept()
                    CONNECTION_LIST.append(sockfd)
                    dPrint ("Client (%s, %s) connected" % addr)

                #Some incoming message from a client
                else:
                    try:
                        data = sock.recv(RECV_BUFFER)
                        if data.encode("hex") == "000000000000436c0000010000000000" :
                            print "yo"
                            #send_broadcast()
                            #continue
                        # echo back the client message
                        if data:
                            sendBack(data, sock)
                    except:
                        dPrint("Socket error")
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        continue

        except (KeyboardInterrupt, SystemExit):
            dPrint("Keyboard Interrupt")
            #server_socket.close()
            raise
