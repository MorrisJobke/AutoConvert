#!/usr/bin/env python
#
# Copyright (C) Morris Jobke 2010 <morris.jobke@googlemail.com>
# 
# AutoConvert is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# AutoConvert is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import pyinotify
import ConfigParser
import time
import os

import exceptions

class FileIsDirException(exceptions.Exception):
	def __init__(self):
		return
	
	def __str__(self):
		print '', 'file is an directory'

class EventHandler(pyinotify.ProcessEvent):
	def __init__(self, fileHandler):
		''' initializes EventHandler '''
		pyinotify.ProcessEvent.__init__(self)
		self.filehandler = fileHandler
		self.filehandler.clearFile()

	def process_IN_CLOSE_WRITE(self, event):
		''' event handler for close file after writing event - append path '''
		print 'close:\t', event.pathname
		self.filehandler.appendPath(event.pathname)
				
	def process_IN_DELETE(self, event):
		''' event handler for delete event - removes entries'''
		print 'delete:\t', event.pathname
		self.fileHandler.clearFile(event.pathname)

class FileHandler():
	def __init__(self, file):
		''' initializes FileHandler with given file and create this if not exists '''
		self.file = file
		if not os.path.exists(self.file):
			fh = open(self.file, 'w')
			fh.close()
		elif os.path.isdir(self.file):
			raise FileIsDirException()
		
	def appendPath(self, path):
		''' append a line with current unixtimestamp and given path '''
		self.clearFile(path)
		fh = open(self.file, 'a')
		fh.write(str(time.time()) + '\t' + path + '\n')
		fh.close()
		
	def clearFile(self, path=None):
		''' deletes all lines with given path or non-existant path '''
		tmp = []
		fh = open(self.file, 'r')
		for line in fh:
			tmpPath = line.split('\t')[1][:-1]
			if not tmpPath == path and os.path.exists(tmpPath):
				tmp.append(line)
		fh.close()
		fh = open(self.file, 'w')
		fh.writelines(tmp)
		fh.close()		

if __name__ == '__main__':
	#####################
	# parse config file #
	#####################
	config = ConfigParser.ConfigParser()
	if os.path.exists('settings.conf'):
		config.read('settings.conf')
		
		#################
		# load settings #
		#################
		watchingMask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE   
		watchingDir = config.get('Main', 'watchingDirectory')
		fooFile = config.get('Main', 'fooFile')
	else:
		###############
		# set default #
		###############
		watchingDir = '/home'
		fooFile = '/tmp/fooFile'
	try:
		fh = FileHandler(fooFile)
	except FileIsDirException:
		print 'Error: fooFile is directory - please adjust settings.conf'
		# TODO fh doesn't exists
	except Exception, e:
		raise e
    
    ##############
    # initialize #
	##############
	watchManager = pyinotify.WatchManager()
	handler = EventHandler(fh)
	notifier = pyinotify.Notifier(watchManager, handler)
	watchManager.add_watch(watchingDir, watchingMask)
	notifier.loop()
