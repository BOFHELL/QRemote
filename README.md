# QRemote

QNAP Remote Script 4 Linux Station

Requires
-------
* remotepad from HDStation Package for your ARCH/QNAP

Configure
-------
Just configure the **qnapagent.py** to change the dashboard for your apps.

```html
gnome-session-properties  add
  python qnapagent.py 
  remotepad
 
  'name':'Kodi',
  'displayName':'Kodi',
  'version':'17',
  'uuid':'k0di0wn',
  'icon_phone':'icons/kodi_phone.png',
  'icon_pad':'icons/kodi_pad.png',
  'start':'kodi',   ----- EXE TO RUN
  'stop':'kodi.bin' ----- TASK TO KILL
```

additionaly add LinuxStation IP to fav in qremote, or add mdns/bonjour service for discover qremote service 

thats it
