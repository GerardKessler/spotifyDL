# -*- coding: utf-8 -*-
# Copyright (C) 2021 Gera Késsler <gera.kessler@gmail.com>
# This file is covered by the GNU General Public License.
# This software uses code of FFMpeg. licensed under the LGPLv2.1

import wx
from threading import Thread
import subprocess
from time import sleep
import os
from json import load, loads
import gui
import globalPluginHandler
from urllib import request

import api
from scriptHandler import script
from ui import message, browseableMessage
import globalVars

MAIN_PATH= os.path.dirname(__file__)
MPEG_PATH= os.path.join(MAIN_PATH, 'bin', 'ffmpeg.exe')
SPOT_PATH= os.path.join(MAIN_PATH, 'bin', 'spotdl.exe')
with request.urlopen('https://api.github.com/repos/spotDL/spotify-downloader/releases') as query:
	content= loads(query.read().decode())
EXE_URL= content[0]['assets'][3]['browser_download_url']

def getSeconds(time):
	try:
		time= time.split(':')
		time= [int(t) for t in time]
	except ValueError:
		# Translators: Texto del raise ValueError
		raise ValueError('El formato de la cadena no es válido')
	if len(time) == 2:
		return time[0] * 60 + time[1]
	elif len(time) == 3:
		return time[0] * 3600 + time[1] * 60 + time[2]
	else:
		return None

def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls

@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__()
		self.percent= 0

	def __call__(self, block_num, block_size, total_size):
		readsofar= block_num * block_size
		if total_size > 0:
			percent= readsofar * 1e2 / total_size
			percent_format= int(percent*1)
			if percent_format <= (self.percent+10): return
			self.percent= percent_format
			# Translators: Palabra porciento posterior al número de porcentaje
			message('{} porciento').format(percent_format)

	def filesDownload(self):
		connection_error= _('Error en la conexión. Por favor compruebe su conexión a internet y vuelva a intentarlo en unos minutos')
		modal= wx.MessageDialog(None, _('Es necesario descargar el archivo ejecutable de spotify-downloader. ¿Quieres hacerlo ahora?'), _('Importante:'), wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
		if modal.ShowModal() == wx.ID_YES:
			os.makedirs(os.path.join(MAIN_PATH, 'bin'))
			request.urlretrieve(EXE_URL, os.path.join(MAIN_PATH, 'bin', 'spotdl.exe'), reporthook= self.__call__)
			subprocess.Popen('{} --download-ffmpeg'.format(SPOT_PATH), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
			gui.messageBox('🙌. Ejecutables descargados  correctamente', 'spotifyDL:', wx.OK)

	@script(
		category= 'spotifyDL',
		# Translators: Descripción del elemento en el diálogo gestos de entrada
		description= 'Activa el cuadro de descarga de spotifyDL'
	)
	def script_guiOpen(self, gesture):
		if not os.path.isdir(os.path.join(MAIN_PATH, 'bin')):
			Thread(target= self.filesDownload, daemon= True).start()
			return
		download_dialog= DownloadDialog(gui.mainFrame)
		gui.mainFrame.prePopup()
		download_dialog.Show()


class DownloadDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title= 'SpotifyDL', style=wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP)
		
		self.static_text= wx.StaticText(self, label='Pega el link  de una canción, lista de reproducción o álbum y pulsa intro para iniciar la descarga')
		
		self.text_ctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.text_ctrl.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.static_text, 0, wx.ALL, 10)
		main_sizer.Add(self.text_ctrl, 0, wx.EXPAND|wx.ALL, 10)
		
		self.SetSizerAndFit(main_sizer)
		self.CenterOnParent()
		
	def on_key_down(self, event):
		key_code= event.GetKeyCode()
		if key_code == wx.WXK_ESCAPE:
			self.Close()
		elif key_code == wx.WXK_RETURN or key_code == wx.WXK_NUMPAD_ENTER:
			self.startDownload()
		else:
			event.Skip()

	def startDownload(self):
		if not os.path.isdir(os.path.join(os.environ['USERPROFILE'], 'spotifyDL')): os.makedirs(os.path.join(os.environ['USERPROFILE'], 'spotifyDL'))
		url_in= self.text_ctrl.GetValue()
		self.Destroy()
		command= '{} --output {} {}'.format(SPOT_PATH, os.path.join(os.environ['USERPROFILE'], 'spotifyDL'), url_in)
		Thread(target=self.newProcess, args=(command, True), daemon=True).start()

	def newProcess(self, command, notification):
		try:
			process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
		except:
			message('Error en la descarga')
			return
		if notification:
			gui.messageBox('Proceso iniciado. En la descarga de listas de reproducción el proceso puede demorarse un buen tiempo. paciencia... 😉', 'spotifyDL:', wx.OK)
		process.wait()
		if notification:
			gui.messageBox('Descarga finalizada. Los archivos se guardan en {}\\spotifyDL'.format(os.environ['USERPROFILE']), 'spotifyDL:', wx.OK)
