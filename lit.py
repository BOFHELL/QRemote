import socket, select
import xml.etree.ElementTree as ET

from dict2xml import dict2xml as xmlify
from collections import OrderedDict



###############
## DEFINE APPS 
##############

apps = [{
    'name':'Koodii',
    'displayName':'Kodi',
    'version':'3.0.6',
    'uuid':'AAPN82NZmp3lo',
    'icon_phone':'qtv/mykodi17_phone.png',
    'icon_pad':'yes'
    }]
  #  ,
  #  {
  #  'name':'Youtube',
  #  'displayName':'youtube',
  #  'version':'1.0.6',
  #  'uuid':'yumo3',
  #  'icon_phone':'qtv/mykodi17_phone.png',
  #  'icon_pad':'yes'
  #  }]



def sortchildrenby(parent, attr):
    parent[:] = sorted(parent, key=lambda child: child.get(attr))



def build_apps():
    print("========== SORT ========")
    FIELDS=["name","displayName","version","uuid","icon_phone","icon_pad"]

    
    for app in apps:
        retstr="<item>"
        for f in FIELDS:
            retstr+=("<{}>"+app[f]+"</{}>").format(f,f)
        retstr+="</item>"

    if retstr:
        retstr='<errRtn>success</errRtn>'+retstr
    return retstr


def build_xml(data):
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    header +='<QDocRoot version="1.1">'
    header += data
    header +='</QDocRoot>'

    return header



#############
## cmds:
##  ACK  ListQPKG  GetIcon  Launch  KillAll  GetCurrentUser  Login2  Logout  SetAutoLogin  GetQTVSetting
def sendBack(cmd, con, V=0, ACK_DATA=''):
        V+=1
        root = ET.fromstring(cmd)

        for cmd_xml in root.findall("cmd"):
            cmd_switch=cmd_xml.text
        
        print("=== INSTANCE: {} =====".format(V))
        print("Empfangen {} CMD:>>{}<<".format(V, cmd))
        #print("=============")
        #QDocRoot version="1.1" 
        if cmd_switch=="ListQPKG":         ### WAiT FOR    ACK  
            print("[DEBUG]: ListQPKG ====> cmd: {}".format(cmd))
            #### Check if all fine - > we say allways YES :D and build sending xml, to count and send first
            # Cli -> List -> SRV : ListQPKG | Srv -> size < return bytes xmls -> send xml
            #ACK_SEND_xml= header+xmlify(retc, wrap='QDocRoot', indent="  ",newlines=True)
            #ACK_SEND_xml=header+xmlify(retc, wrap='QDocRoot', indent=None, newlines=False)
            ACK_SEND_xml=build_xml(build_apps())

            #Ack=sort_xml(ACK_SEND_xml)

            print("Konstruckt {}".format(ACK_SEND_xml))
            #reply='<size>{}</size>'.format(len(header+app+footer))
            #reply='<size>{}</size>'.format(len(xml))
            size_data =  '<size>{}</size>'.format(len(ACK_SEND_xml))
            ## 
            # Send Size from APPS XML file
            #size_xml = dicttoxml(size_array, custom_root='QDocRoot', attr_type=False)
            print("D")
            #size_xml = header+xmlify(size_array, wrap='QDocRoot', indent="   ", newlines=True)
            size_xml = build_xml('<size>{}</size>'.format(len(ACK_SEND_xml))) 
            print("D")
            
            #^size_xml=header+'<QDocRoot version="1.1"><size>293</size></QDocRoot>'
            print("SENDE ===> SIZE ARRAY: {}".format(size_xml) )
            
            con.sendall( size_xml )


        if cmd_switch=="ACK":
            print("[DEBUG]: ACK ====> cmd: {}".format(cmd))
            print("SENDE ===> ACK: {}".format(ACK_DATA))
            print(" SENDE LEN: {}".format(len(ACK_DATA)))
            con.sendall( ACK_DATA )

        if cmd_switch=='GetIcon':
            print("[DEBUG]: GetIcon ====> cmd: {}".format(cmd))
            params=[]
            for params_xml in root.findall("param"):
                params.append(params_xml.text)
            #### Check App
            print(" [GetIcon]: params ====> {}".format(params))
            app_uuid=params[0]
            app_icon=params[1]
            print("APPID {} ICON FUER {}".format(app_uuid,app_icon))
            #### abkuerzen  app_uuid, app_icon=list(params)  ??i
            app=(item for item in apps if item["uuid"] == app_uuid).next()
            print("Gefunden APP {}".format(app))
            if app:
                print(" try to get Icon: {}".format(app['icon_'+app_icon]))
                fIcon=open(app['icon_'+app_icon]).read()
                print("opened")
                print("array size")
                fsize_xml = build_xml('<size>{}</size>'.format(len(fIcon))) 
                print(" [GetIcon] SENDE ===> SIZE ARRAY: {}".format(fsize_xml) )
                con.sendall ( fsize_xml )

                ACK_SEND_xml=fIcon


        if cmd_switch=="KillALL":
            print("OKEY, Killing all softly")


        #########################
        ## Handle return request
        ACK = con.recv(2048)
        if ACK:
            #print("[DEBUG]: ACK REV {}".format(ACK))
            #print("====== WILL SEND: ")

            #print(ACK_SEND_xml)

            sendBack(ACK, con, V, ACK_SEND_xml)
        print("=============")



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
                    print "Client (%s, %s) connected" % addr

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
                            #print(" REV ===== {}".format(data))
                            #header='<?xml version="1.0" encoding="UTF-8"?>\n'
                            #header+='<QDocRoot version="1.1"><size>293</size></QDocRoot>'
                            #sock.send(header)

                        # client disconnected, so remove from socket list
                    except:
                        print("Socket error")
                        sock.close()
                        CONNECTION_LIST.remove(sock)
                        continue

        except (KeyboardInterrupt, SystemExit):
            print("Keyboard Interrupt")
            #server_socket.close()
            raise
