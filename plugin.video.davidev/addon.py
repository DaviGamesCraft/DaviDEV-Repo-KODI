 #!/usr/bin/python
# -*- coding: UTF-8 -*-

##############BIBLIOTECAS A IMPORTAR E DEFINICOES####################


import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,xbmcaddon,HTMLParser,xmltosrt,os,json,sys
from bs4 import BeautifulSoup
 
h = HTMLParser.HTMLParser()

debug = 'true'
versao = '1.0'
addon_id = 'plugin.video.davidev'
selfAddon = xbmcaddon.Addon(id=addon_id)
addonfolder = selfAddon.getAddonInfo('path')
artfolder = addonfolder + '/resources/img/'
fanart = addonfolder + '/fanart.jpg'
Addon = xbmcaddon.Addon(addon_id)

addon_data_dir = os.path.join(xbmc.translatePath("special://userdata/addon_data" ).decode("utf-8"), addon_id)
if not os.path.exists(addon_data_dir):
	os.makedirs(addon_data_dir)

libDir = os.path.join(addonfolder, 'resources', 'lib')
sys.path.insert(0, libDir)
tmpListFile = os.path.join(addonfolder, 'tempList.txt')
import common


################################################## 

#MENUS############################################


def CATEGORIES():
	#addDir('Canais de TV','http://bit.ly/DaviDEV_TV',1,artfolder + 'tv-icon.png')
	#addDir('Filmes (Jorge DeJorge)','http://bit.ly/DaviDEV_Filmes',1,artfolder + 'movie-icon.png')
	#addDir('Todo mundo odeia o Chris','http://bit.ly/DaviDEV_EHC',1,artfolder + 'ehc-icon.jpg')
	#addDir('As visões da Raven','http://bit.ly/DaviDEV_AVS',1,artfolder + 'avs-icon.JPG')

	soup = gethtml("http://pastebin.com/raw/PCzP3AhC");
	for link in soup.find_all('item'):
		nome = str(link.nome.string)
		url = str(link.url.string)
		icone = str(link.icone.string)
		addDir(''+nome,''+url,1,''+icone)
	SetViewThumbnail()
	print 'Menu terminado!'
	
	#addLink("",'',artfolder + '-')  - Esta linha cria um espaço em branco
	

####################################################
#FUNCOES############################################

def SetViewThumbnail():
    skin_used = xbmc.getSkinDir()
    if skin_used == 'skin.confluence':
        xbmc.executebuiltin('Container.SetViewMode(500)')
    elif skin_used == 'skin.aeon.nox':
        xbmc.executebuiltin('Container.SetViewMode(511)') 
    else:
        xbmc.executebuiltin('Container.SetViewMode(500)')

def gethtml(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    soup = BeautifulSoup(link, "html.parser")
    return soup

def addon_log(string):
    if debug == 'true':
        xbmc.log("DaviDEV Addon " + versao + ": " + string)

def listar_menu_xml(url):
	addon_log('O proximo menu eh em xml')
	soup = gethtml(url);

	for link in soup.find_all('item'):
		addon_log('Item emcontrado: ' + str(link))
		nome = str(link.nome.string)
		url = str(link.url.string)
		icone = str(link.icone.string)
		addDir(''+nome,''+url,1,''+icone)
		addon_log('Dir adcionada: ' + str(link))

def m3uCategory(url, logos=None):	
	tmpList = []

	page_src = abrir_url(url)
	isxml = 'item'
	if isxml in page_src:
		listar_menu_xml(url)
		return

	list = common.m3u2list(url)

	for channel in list:
		name = channel["display_name"]
		image = channel.get("tvg_logo", "")
		if image == "":
			image = channel.get("logo", "")
		if logos is not None and logos != '' and image is not None and image != '' and not image.startswith('http'):
			image = logos + image
		url = common.GetEncodeString(channel["url"])
		AddDir(name ,url, 3, image, isFolder=False)
		tmpList.append({"url": url.decode("utf-8"), "image": image.decode("utf-8"), "name": name.decode("utf-8")})

	common.SaveList(tmpListFile, tmpList)

def iniciarVideo(name, url, iconimage=None):
	print '--- Rodando "{0}". {1}'.format(name, url)
	listitem = xbmcgui.ListItem(path=url, thumbnailImage=iconimage)
	listitem.setInfo(type="Video", infoLabels={ "Title": name })
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

def obtem_url_dropvideo(url):
	codigo_fonte = abrir_url(url)
	try:
		if not 'dropvideo.com/embed/' in url:
			id_video = re.findall(r'<iframe src="http://www.dropvideo.com/embed/(.*?)/"',codigo_fonte)[0]
			codigo_fonte = abrir_url('http://www.dropvideo.com/embed/%s/' % id_video)
			url_video = re.findall(r'var vurl2 = "(.*?)";',codigo_fonte)[0]
			url_legendas =	re.compile('var vsubtitle = "(.*?)";').findall(codigo_fonte)[0]
		else:
			codigo_fonte = abrir_url(url)
			url_video = re.findall(r'var vurl2 = "(.*?)";',codigo_fonte)[0]
			url_legendas =	re.compile('var vsubtitle = "(.*?)";').findall(codigo_fonte)[0]
	except:
		url_video = '-'
		url_legendas = '-'
	return [url_video,url_legendas]

#def obtem_url_dropvideo(url):
#	codigo_fonte = abrir_url(url)
#	try: url_video = re.compile('var vurl = "(.+?)";').findall(codigo_fonte)[0]
#	except: url_video = '-'
#	try: url_legendas =	re.compile('var vsubtitle = "(.+?)";').findall(codigo_fonte)[0]
#	except: url_legendas = '-'
#	return [url_video,url_legendas]

def obtem_url_vk(url):
	codigo_fonte = abrir_url(url)
	qualidade = []
	urls = []
	try:
		urls_video = re.findall(r'url([0-9]+)=(.*?)&', codigo_fonte)
		for qualidade_ , url_ in urls_video:
			qualidade_ = qualidade_+"p"
			if not qualidade_ in qualidade:
				qualidade.append(qualidade_)
			if not url_ in urls:
				urls.append(url_)
		index = xbmcgui.Dialog().select('Qualidade do vídeo:', qualidade)
		return [urls[index],"-"]
	except:
		return ["-","-"]
def obtem_url_vodlocker(url):
	codigo_fonte = abrir_url(url)
	
	try:
		url_video = re.findall(r'file:."(.*?)"',codigo_fonte)[0]
		return [url_video,"-"]
	except:
		return ["-","-"]
	
def getLocaleString(id):
	return Addon.getLocalizedString(id).encode('utf-8')
	
	
def AddDir(name, url, mode, iconimage, logos="", index=-1, move=0, isFolder=True, background=None):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&logos="+urllib.quote_plus(logos)+"&index="+str(index)+"&move="+str(move)

	liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={ "Title": name})
	listMode = 21 # Lists
	if background != None:
		liz.setProperty('fanart_image', background)
	if mode == 1 or mode == 2:
		items = [(getLocaleString(10008), 'XBMC.RunPlugin({0}?index={1}&mode=22)'.format(sys.argv[0], index)),
		(getLocaleString(10026), 'XBMC.RunPlugin({0}?index={1}&mode=23)'.format(sys.argv[0], index)),
		(getLocaleString(10027), 'XBMC.RunPlugin({0}?index={1}&mode=24)'.format(sys.argv[0], index)),
		(getLocaleString(10028), 'XBMC.RunPlugin({0}?index={1}&mode=25)'.format(sys.argv[0], index))]
		if mode == 2:
			items.append((getLocaleString(10029), 'XBMC.RunPlugin({0}?index={1}&mode=26)'.format(sys.argv[0], index)))
	elif mode == 3:
		liz.setProperty('IsPlayable', 'true')
		liz.addContextMenuItems(items = [('{0}'.format(getLocaleString(10009)), 'XBMC.RunPlugin({0}?url={1}&mode=31&iconimage={2}&name={3})'.format(sys.argv[0], urllib.quote_plus(url), iconimage, name))])
	elif mode == 32:
		liz.setProperty('IsPlayable', 'true')
		items = [(getLocaleString(10010), 'XBMC.RunPlugin({0}?index={1}&mode=33)'.format(sys.argv[0], index)),
		(getLocaleString(10026), 'XBMC.RunPlugin({0}?index={1}&mode=35)'.format(sys.argv[0], index)),
		(getLocaleString(10027), 'XBMC.RunPlugin({0}?index={1}&mode=36)'.format(sys.argv[0], index)),
		(getLocaleString(10028), 'XBMC.RunPlugin({0}?index={1}&mode=37)'.format(sys.argv[0], index))]
		listMode = 38 # Favourits
	if mode == 1 or mode == 2 or mode == 32:
		items += [(getLocaleString(10030), 'XBMC.RunPlugin({0}?index={1}&mode={2}&move=-1)'.format(sys.argv[0], index, listMode)),
		(getLocaleString(10031), 'XBMC.RunPlugin({0}?index={1}&mode={2}&move=1)'.format(sys.argv[0], index, listMode)),
		(getLocaleString(10032), 'XBMC.RunPlugin({0}?index={1}&mode={2}&move=0)'.format(sys.argv[0], index, listMode))]
		liz.addContextMenuItems(items)
		
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder)


def obtem_url_picasa(url):
	itags = {5:'Baixa Qualidade, 240p, FLV, 400x240',
		17:'Baixa Qualidade, 144p, 3GP, 0x0',
		18:'Media Qualidade, 480p, MP4, 480x360',
		59:'Media Qualidade, 360p, MP4, 480x360',
		22:'Alta Qualidade, 720p, MP4, 1280x720',
		34:'Media Qualidade, 360p, FLV, 640x360',
		35:'Standard Definition, 480p, FLV, 854x480',
		36:'Baixa Qualidade, 240p, 3GP, 0x0',
		37:'Alta Qualidade, 1080p, MP4, 1920x1080',
		38:'Original Definition, MP4, 4096x3072',
		43:'Media Qualidade, 360p, WebM, 640x360',
		44:'Standard Definition, 480p, WebM, 854x480',
		45:'Alta Qualidade, 720p, WebM, 1280x720',
		46:'Alta Qualidade, 1080p, WebM, 1280x720',
		82:'Media Qualidade 3D, 360p, MP4, 640x360',
		84:'Alta Qualidade 3D, 720p, MP4, 1280x720',
		100:'Media Qualidade 3D, 360p, WebM, 640x360',
		102:'Alta Qualidade 3D, 720p, WebM, 1280x720'}
	codigo_fonte_player = abrir_url(url)
	#try:
	itags_ = []
	id_video = re.findall(r'FlashVars="plugins=plugins1/proxy.swf&proxy.link=https://picasaweb.google.com/lh/photo/(.*?)&skin=newtubedark.zip&proxy.reloader=false"',codigo_fonte_player)[0]
	itag37 = "http://redirector.googlevideo.com/videoplayback?id=" + id_video + "&itag=37&source=picasa&cmo=sensitive_content=yes&ip=0.0.0.0&ipbits=0&expire=1397243357&sparams=id%2Citag%2Csource%2Cip%2Cipbits%2Cexpire&signature=CA66CBBEF3510DDF0054366A11222FABBD77B0F6.56EF5482EFC67CB051B0A5F67AFFF28A599C92E4&key=lh1"
	url_video_picasa = 'https://picasaweb.google.com/lh/photo/%s' % id_video
	redirectors = re.findall(r'"(http://redirector.googlevideo.com/videoplayback.*?)"',abrir_url(url_video_picasa))
	for redirector in redirectors:
		itag = re.findall(r'&itag=([0-9]+?)&',redirector)[0]
		itag = itags[int(itag)]
		itags_.append(itag)
		
	#redirect = urllib2.unquote(re.findall(r"!'(.*?)'",abrir_url(url_video_picasa))[0])
	index = xbmcgui.Dialog().select('Qualidade do vídeo:', itags_)
	return [redirectors[index],"-"]
	#except:
	#	return ["-","-"]

def player(name,url,iconimage):
	
	google = r'.*?;usp=embed_googleplus.*?'
	picasa = r'src="(.*?filmesonlinebr.*?/player/.*?)"'
	vk = r'src="(.*?vk.*?/video.*?)"'
	nvideo = r'src="(.*?nowvideo.*?/embed.*?)"'
	dropvideo = r'src="(.*?dropvideo.*?/embed.*?)"'
	vodlocker = r'src="(.*?vodlocker.*?/embed.*?)"'
	firedrive = r'src="(.*?firedrive.*?/embed/.*?)"'
	
	mensagemprogresso = xbmcgui.DialogProgress()
	mensagemprogresso.create('DaviDEV Addon', 'Procurando players...','Se importa em aguardar?')
	mensagemprogresso.update(13)
	links = []
	hosts = []
	matriz = []
	codigo_fonte = abrir_url(url)
	#try: url_video = re.findall(r'<iframe src="(.*?)" width="738" height="400" frameborder="0"></iframe></li>',codigo_fonte)[0]
	############################<iframe src="(.*?)" width="738" height="400" frameborder="0"></iframe></li>
	#except: return
	
	try:
		links.append(re.findall(picasa, codigo_fonte)[0])
		hosts.append('Picasa')
	except:
		pass
	
	try:
		links.append(re.findall(google, codigo_fonte)[0])
		hosts.append('Google Drive')
	except:
		pass
	
	try:
		links.append(re.findall(vk, codigo_fonte)[0])
		hosts.append('Vk')
	except:
		pass
	
	try:
		links.append(re.findall(nvideo, codigo_fonte)[0])
		hosts.append('Nowvideo - Sem suporte')
	except:
		pass
	
	try:
		links.append(re.findall(dropvideo, codigo_fonte)[0])
		hosts.append('Dropvideo')
	except:
		pass
	
	try:
		links.append(re.findall(vodlocker, codigo_fonte)[0])
		hosts.append('Vodlocker')
	except:
		pass

	
	if not hosts:
		return
	
	index = xbmcgui.Dialog().select('Selecione um dos hosts suportados :', hosts)
	
	if index == -1:
		return
	
	url_video = links[index]
	mensagemprogresso.update(66)
	
	print 'Player url: %s' % url_video
	if 'google' in url_video:
		iniciarVideo(name,'plugin://plugin.video.gdrive?mode=streamURL&amp;url=' + url,iconimage)
		return
	elif 'dropvideo.com/embed' in url_video:
		matriz = obtem_url_dropvideo(url_video) 
	elif 'filmesonlinebr.info/player' in url_video:
		matriz = obtem_url_picasa(url_video)
	elif 'vk.com/video_ext' in url_video:
		matriz = obtem_url_vk(url_video)
	elif 'vodlocker.com' in url_video:
		matriz = obtem_url_vodlocker(url_video)
	else:
		print "Falha: " + str(url_video)
	print matriz
	url = matriz[0]
	print url
	if url=='-': return
	legendas = matriz[1]
	print "Url do gdrive: " + str(url_video)
	print "Legendas: " + str(legendas)
	
	mensagemprogresso.update(100)
	mensagemprogresso.close()
	
	listitem = xbmcgui.ListItem() # name, iconImage="DefaultVideo.png", thumbnailImage="DefaultVideo.png"
	listitem.setPath(url)
	listitem.setProperty('mimetype','video/mp4')
	listitem.setProperty('IsPlayable', 'true')
	#try:
	xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	xbmcPlayer.play(url)
	if legendas != '-':
		if 'timedtext' in legendas:
			#legenda = xmltosrt.convert(legendas)
			#try:
				import os.path
				sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
				sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
				sub_file_xml = open(sfile_xml,'w')
				sub_file_xml.write(urllib2.urlopen(legendas).read())
				sub_file_xml.close()
				print "Sfile.srt : " + sfile_xml
				xmltosrt.main(sfile_xml)
				xbmcPlayer.setSubtitles(sfile)
			#except:
			#	pass
		else:
			xbmcPlayer.setSubtitles(legendas)

def abrir_url(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def addLink(name,url,iconimage):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', fanart)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok

def addDir(name,url,mode,iconimage,pasta=True,total=1):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', fanart)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)
	return ok

############################################################################################################
#                                               GET PARAMS                                                 #
############################################################################################################
              
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

      
params=get_params()
url=None
name=None
mode=None
iconimage=None


try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

try:        
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass


print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Iconimage: "+str(iconimage)




###############################################################################################################
#                                                   MODOS                                                     #
###############################################################################################################


if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()

elif mode==1:
	print ""
	m3uCategory(url)
elif mode == 3 or mode == 32:
	if 'google' in url:
		player(name, url, iconimage)
	else:
		iniciarVideo(name, url, iconimage)

xbmcplugin.endOfDirectory(int(sys.argv[1]))