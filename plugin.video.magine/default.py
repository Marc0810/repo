#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json
import md5
import hashlib
import time,cookielib
import base64
import datetime
cj = cookielib.CookieJar()

def getUrl(url,data="x",header=[]):
   global cj
   content=""
   debug("URL :::::: "+url)
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   userAgent = 'Coralie/1.7.2-2016081207(SM-G900F; Android; 6.0.1; DeviceId c248c629af1fe0a8c46b95668064c1d2952a9e91d27bccc3c5d584c2f7553a; Token Tvoli/ec9ab8acf27f14cacfefbf1087463fd3aeacdca4; VersionCheck)'
   header.append(('User-Agent', userAgent))
   header.append(('Accept', "*/*"))
   header.append(('Content-Type', "application/json;charset=UTF-8"))
   header.append(('Accept-Encoding', "plain"))
   header.append(('Origin', "https://magine.com"))
   opener.addheaders = header
   try:
      if data!="x" :
         request=urllib2.Request(url)
         cj.add_cookie_header(request)
         content=opener.open(request,data=data).read()
      else:
         content=opener.open(url).read()
   except urllib2.HTTPError as e:
       print e
   opener.close()
   return content







#data="clientId="+ session +"&mk=HTML5&md=PC&userId="+ userid
#content=getUrl("https://magine.com/api/drm/v4/license/widevine",data=data,Authorization=session,userId=userid)

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
debuging=""
# Es geht um Videos
xbmcplugin.setContent(addon_handle, 'movies')
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
defaultBackground = ""
defaultThumb = ""

profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")


user=addon.getSetting("user") 
password=addon.getSetting("password") 

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
  
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',channelid="",times="",ids=0):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&channelid="+str(channelid)+"&times="+str(times)+"&ids="+str(ids)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	liz.setProperty("fanart_image", iconimage)
	#liz.setProperty("fanart_image", defaultBackground)
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok
def addDir(name, url, mode, iconimage, desc="",year="",channelid="",times="",start="",ende="",id_such=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&channelid="+str(channelid)+"&times="+str(times)+"&start="+str(start)+"&ende="+str(ende)+"&id_such="+str(id_such)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)  
  liz.setProperty("fanart_image", iconimage)
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok
def login():
  user=addon.getSetting("user") 
  password=addon.getSetting("password") 
  values = {
      'accessKey' : password,
      'identity' : user
    }
  data = json.dumps(values)  
  try:
    content=getUrl("https://magine.com/api/login/v1/auth/magine",data=data)
    struktur = json.loads(content)
    session=struktur['sessionId']
    userid=struktur['userId']
  except:
    session=-1
    userid=-1
  return session,userid

def selectdate(session,userid,id_such):
   for i in xrange(0, 7):
        Tag=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(i),'%w')         
        datuma=translation(30130 + int(Tag))
        start=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(int(i)),'%Y%m%dT000000Z')
        ende=datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(int(i))+datetime.timedelta(hours=24),'%Y%m%dT000000Z')
        addDir(datuma, "", "mediatek", "", start=start,ende=ende,id_such=id_such)                           
   xbmcplugin.endOfDirectory(addon_handle)
   
def mediatek(session,userid,id_such,start,ende):
  debug(".START. "+start)
  debug(".ENDE. "+ende)
  debug(".id_such. "+id_such)
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  content=getUrl("https://magine.com/api/time/v1",header=header)
  struktur = json.loads(content)  
  timestamp=int(struktur["nowUnixtime"])
  content=getUrl("https://magine.com/api/channel/v1/users/"+userid,header=header)  
  struktur = json.loads(content)  
  channelid_arr=[]  
  name_arr=[]
  for element in struktur: 
   channelid_arr.append(element["id"])
   name_arr.append(element["name"])
  senderliste=",".join(channelid_arr)
  
  now = datetime.datetime.utcfromtimestamp(timestamp)
  vontime = now - datetime.timedelta(hours=24)
  bistime = now 
  von=start
  bis=ende
  debug("VON: "+von)
  debug("BIS: "+bis) 
  url="https://magine.com/api/content/v2/timeline/airings?channels="+senderliste+"&from="+von+"&to="+bis
  content=getUrl(url,header=header)  
  struktur_inhalt = json.loads(content)   
  for element in struktur_inhalt:        
    channel=element
    for element in struktur_inhalt[element]:       
        #debug("----"+element["rights"]["recorded"]["available"])    
        if element["rights"]["recorded"]["available"]==True:
           debug("++++-")
           debug(element)
           title=element["title"]
           channel=element["channelId"]
           ids=element["id"]
           bild=element["image"]
           zeitstring=element["start"].split("T")
           start=zeitstring[0]
           zeit=zeitstring[1].split(":")           
           starzeit=zeit[0]+":"+zeit[1]
           id=channelid_arr.index(channel) 
           title=start+" "+starzeit+" "+title+" ( "+name_arr[id]+" )"
           if id_such==channel:
             addLink(title, "", "playvideo", bild, channelid=channel,ids=ids)     
  xbmcplugin.endOfDirectory(addon_handle)

def playvideo(session,userid,channelid,id):
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  newurl="https://magine.com/api/contenturl/v1/channel/"+str(channelid)+"/airing/"+str(id)  
  content=getUrl(newurl,header=header)  
  struktur = json.loads(content)
  newurl="https://magine.com/api/airing/v2/"+str(id)  
  content=getUrl(newurl,header=header)  
  struktur2 = json.loads(content)
  title=struktur2["title"]
  desc=struktur2["description"]
  debug("......")  
  debug(struktur)
  userAgent = "Coralie/1.7.2-2016081207(SM-G900F; Android; 6.0.1; DeviceId c248c629af1fe0a8c46b95668064c1d2952a9e91d27bccc3c5d584c2f7553a; Token Tvoli/ec9ab8acf27f14cacfefbf1087463fd3aeacdca4; VersionCheck)"
  listitem = xbmcgui.ListItem(path=struktur["dash"])        
  debug("List Item gesetzt")      
  pin=addon.getSetting("pin")
  adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.adaptive", "properties": ["enabled"]}}')        
  sstruktur = json.loads(adaptivaddon) 
  is_type=""
  if not "error" in sstruktur.keys() :            
     if sstruktur["result"]["addon"]["enabled"]==True:
        is_type="inputstream.adaptive"
     if is_type=="":
        adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.mpd", "properties": ["enabled"]}}')        
        sstruktur = json.loads(adaptivaddon)           
        if not "error" in sstruktur.keys() :            
           if sstruktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.mpd"                
  if is_type=="":
     dialog = xbmcgui.Dialog()
     nr=dialog.ok("Inputstream", "Inputstream fehlt")
     return "" 
  debug("XXX YYYY")     
  debug(is_type)
  lic_header="|Authorization=Bearer%20"+session+"&UserId=" +userid+"&Magine-ChannelId=" +channelid+"&Magine-Md=PC-Awesomesauce"+"&Magine-ParentalControlPinCode="+pin+"&Magine-Mk=HTML5"+"&Magine-ClientId=c060c1bf-d805-4feb-74d4-d8241e27d836"+"&Magine-ProgramId="+id+"|R{SSM}|"
  listitem.setProperty(is_type+'.license_type', 'com.widevine.alpha')  
  listitem.setProperty(is_type+'.license_key', "https://magine.com/api/drm/v4/license/widevine"+lic_header)
  listitem.setProperty(is_type+'.license_data', base64.b64encode(b'\x08\x01\x12\x10'+'{KID}'+b'\x1A\x05'+'tvoli"'+chr(len('channel.'+channelid+'.'+id))+'channel.'+channelid+'.'+id+'*'+b'\x02'+'SD2'+b'\x00'))
  listitem.setProperty('inputstreamaddon', is_type)  
  listitem.setProperty(is_type+".manifest_type", "mpd")  
  listitem.setInfo( "video", { "Title" : title, "Plot" : desc} )    
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
  
def mainmenu(session,userid):
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))  
  content=getUrl("https://magine.com/api/your-tv/v1/sections",header=header)  
  struktur = json.loads(content) 

  
  
  for element in struktur["sections"][0]["sectionItems"][0]["subsection"]["items"]: 
        element=element["airing"]
        debug (element)
        bild=element["image"] 
        kanal_name=element["channel"]["name"]
        kanal_id=element["channel"]["id"]
        zeit=element["id"]        
        senung_name=element["title"]
        addLink(kanal_name +" - "+senung_name , str(zeit), "playlive", bild, channelid=str(kanal_id))
  xbmcplugin.endOfDirectory(addon_handle)

def listchannels(session,userid):
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  content=getUrl("https://magine.com/api/time/v1",header=header)
  struktur = json.loads(content)  
  timestamp=int(struktur["nowUnixtime"])
  content=getUrl("https://magine.com/api/channel/v1/users/"+userid,header=header)  
  struktur = json.loads(content)  
  channelid_arr=[]  
  name_arr=[]
  for element in struktur: 
   channelid_arr.append(element["id"])
   name_arr.append(element["name"])
  senderliste=",".join(channelid_arr)
  
  now = datetime.datetime.utcfromtimestamp(timestamp)
  vontime = now - datetime.timedelta(hours=24)
  bistime = now 
  von=vontime.strftime("%Y%m%dT%H%M00Z")
  bis=bistime.strftime("%Y%m%dT%H%M00Z")
  debug("VON: "+von)
  debug("BIS: "+bis) 
  url="https://magine.com/api/content/v2/timeline/airings?channels="+senderliste+"&from="+von+"&to="+bis
  content=getUrl(url,header=header)  
  struktur_inhalt = json.loads(content)   
  for element1 in struktur_inhalt:        
    channel=element1
    channela=0
    for element in struktur_inhalt[element1]:      
      if element["rights"]["recorded"]["available"]==True:
            channel=element["channelId"]
            id=channelid_arr.index(channel)    
            channela=1 
            break
    if channela==1:            
      debug("BILD :"+"http://images.tvoli.com/channel-logos/"+str(channel) +".png?width=128&height=128")
      addDir(name_arr[id], "", "selectdate", "http://images.tvoli.com/channel-logos/"+str(channel) +".png?width=128&height=128", channelid=str(channel))                   
  xbmcplugin.endOfDirectory(addon_handle)     
                
def playlive(url,session,userid,channelid):      
  header=[]
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))
  times=url
  debug("Playlive")
  playlist = xbmc.PlayList(1)
  playlist.clear() 
  item,title,next,dauer=leseclips(times,session,userid,channelid)
  playlist.add(title, item)  
  debug("NEXT :"+ str(next))  
  xbmc.Player().play(playlist)
  time.sleep(3)
  while xbmc.Player().isPlaying():  
    dauer=dauer-300
    if dauer<0:
      dauer=1
    time.sleep(dauer)
    dauer=0
    try:
        item,title,next,dauer=leseclips(next,session,userid,channelid)  
    except:
         pass
    playlist.add(title, item) 
  
  
def leseclips(url,session,userid,channelid):  

  debug("leseclips")
  times=url
  path=str(times)[0:5]
  header=[]    
  header.append (("Authorization","Bearer "+session))
  header.append (("UserId",userid))  
  
  content=getUrl("https://magine.com/api/time/v1",header=header)
  struktur = json.loads(content)  
  timestamp=int(struktur["nowUnixtime"])
  
  content=getUrl("https://magine.com/api/airing/v2/"+times,header=header)
  struktur= json.loads(content) 
  debug(struktur)
  title=struktur["title"]
  stop=struktur["stopUnixtime"]
  desc=struktur["description"]
  dauer=stop-timestamp
  
  debug("dauer :"+str(dauer))
  debug("Git file")
  content=getUrl("https://magine.com/api/contenturl/v1/channel/"+ channelid +"/airing/"+times,header=header)
  struktur= json.loads(content) 
  dash_file=struktur["dash"]
  debug(struktur)
  listitem = xbmcgui.ListItem(path=dash_file)        
  debug("List Item gesetzt")      
  pin=addon.getSetting("pin") 
  adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.adaptive", "properties": ["enabled"]}}')        
  sstruktur = json.loads(adaptivaddon) 
  is_type=""
  if not "error" in sstruktur.keys() :            
     if sstruktur["result"]["addon"]["enabled"]==True:
        is_type="inputstream.adaptive"
  if is_type=="":
     adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.mpd", "properties": ["enabled"]}}')        
     sstruktur = json.loads(adaptivaddon)           
     if not "error" in sstruktur.keys() :            
        if sstruktur["result"]["addon"]["enabled"]==True:
          is_type="inputstream.mpd"                
  if is_type=="":
      dialog = xbmcgui.Dialog()
      nr=dialog.ok("Inputstream", "Inputstream fehlt")
      return "" 
  lic_header="|Authorization=Bearer%20"+session+"&UserId=" +userid+"&Magine-ChannelId=" +channelid+"&Magine-Md=PC-Awesomesauce"+"&Magine-ParentalControlPinCode="+pin+"&Magine-Mk=HTML5"+"&Magine-ClientId=c060c1bf-d805-4feb-74d4-d8241e27d836"+"&Magine-ProgramId="+times+"|R{SSM}|"
  listitem.setProperty(is_type+'.license_type', 'com.widevine.alpha')
  listitem.setProperty(is_type+'.license_key', "https://magine.com/api/drm/v4/license/widevine"+lic_header)
  listitem.setProperty(is_type+'.license_data', base64.b64encode(b'\x08\x01\x12\x10'+'{KID}'+b'\x1A\x05'+'tvoli"'+chr(len('channel.'+channelid+'.'+times))+'channel.'+channelid+'.'+times+'*'+b'\x02'+'SD2'+b'\x00'))
  listitem.setProperty('inputstreamaddon', is_type)   
  listitem.setProperty(is_type+".manifest_type", "mpd")  
  listitem.setInfo( "video", { "Title" : title, "Plot" : desc} )   
  debug("ADDDD")      
  return listitem,dash_file,str(path)+str(stop),dauer

  
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
  
    


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
channelid = urllib.unquote_plus(params.get('channelid', ''))
ids = urllib.unquote_plus(params.get('ids', ''))
times = urllib.unquote_plus(params.get('times', ''))
showName = urllib.unquote_plus(params.get('showName', ''))
start = urllib.unquote_plus(params.get('start', ''))
ende = urllib.unquote_plus(params.get('ende', ''))
id_such= urllib.unquote_plus(params.get('id_such', ''))
hideShowName = urllib.unquote_plus(params.get('hideshowname', '')) == 'True'
nextPage = urllib.unquote_plus(params.get('nextpage', '')) == 'True'
einsLike = urllib.unquote_plus(params.get('einslike', '')) == 'True'    

session,userid=login()
# Haupt Menu Anzeigen      
if mode is '':
    if session==-1:
          dialog = xbmcgui.Dialog()
          nr=dialog.ok("User/Password", "Bitte Korrekten User und Password in Einstellungen hinterlegen") 
    else:          
        addDir(translation(30104) , url="-", mode="mainmenu", iconimage="")    
        addDir("Mediatek" , url="-", mode="listchannels", iconimage="") 
    addDir(translation(30103), translation(30102), 'Settings', "")         
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
if mode == 'playlive':
          playlive(url,session,userid,channelid)     
if mode == 'mainmenu':
          mainmenu(session,userid)      
if mode == 'listchannels':
          listchannels(session,userid)   
if mode == 'listchannel':
          listchannel(session,userid,channelid)    
if mode == 'selectdate':
           selectdate(session,userid,channelid)
if mode == 'playvideo':
          playvideo(session,userid,channelid,ids)    
if mode == 'mediatek':
          mediatek(session,userid,id_such,start,ende)         
if mode == 'Settings':
          addon.openSettings()          
