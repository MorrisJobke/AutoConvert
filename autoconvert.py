#!/usr/bin/env python
#
# Copyright (C) Morris Jobke 2010 <morris.jobke@googlemail.com>
# 
# AutoConvert is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# GMailNotify is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import pyinotify
import ConfigParser
import time

class EventHandler(pyinotify.ProcessEvent):
	def __init__(self, file):
		''' initiates EventHandler with file where to write changes '''
		pyinotify.ProcessEvent.__init__(self)
		self.file = file

	def process_IN_CLOSE_WRITE(self, event):
		''' event handler for close file after writing event - append path '''
		print 'close:\t', event.pathname
		self.fileAppend(event.pathname)
				
	def process_IN_DELETE(self, event):
		''' event handler for delete event - removes entries'''
		print 'delete:\t', event.pathname
		self.fileDeletePath(event.pathname)
		
	def fileAppend(self, path):
		''' append line with current unixtimestamp and given path '''
		self.fileDeletePath(path)
		fileHandler = open(self.file, 'a')
		fileHandler.write(str(time.time()) + '\t' + path + '\n')
		fileHandler.close()
	
	def fileDeletePath(self, path):
		''' deletes all lines with given path '''
		tmp = []
		fileHandler = open(self.file, 'r')
		while True:
			line = fileHandler.readline()
			if line == '':
				break
			if not line.split('\t')[1][:-1] == path:
				tmp.append(line)
		fileHandler.close()
		fileHandler = open(self.file, 'w')
		fileHandler.writelines(tmp)
		fileHandler.close()
     
# parse config file
config = ConfigParser.ConfigParser()
config.read('settings.conf')

# settings
watchingMask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE   
watchingDir = config.get('Main', 'watchingDirectory')
fooFile = config.get('Main', 'fooFile')

# initialise
watchManager = pyinotify.WatchManager()
handler = EventHandler(fooFile)
notifier = pyinotify.Notifier(watchManager, handler)
watchManager.add_watch(watchingDir, watchingMask)
notifier.loop()
