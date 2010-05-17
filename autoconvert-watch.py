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
import sqlite3

class EventHandler(pyinotify.ProcessEvent):
	def __init__(self, databaseFile):
		''' initializes EventHandler '''
		pyinotify.ProcessEvent.__init__(self)
		self.db = sqlite3.connect(databaseFile)
	
		cursor = self.db.cursor()
		sql = """
		CREATE TABLE IF NOT EXISTS incoming (
			date INTEGER,
			file TEXT
		)"""
		cursor.execute(sql);
		cursor.close()
		
		self.db.commit()
		
	def __del__(self):
		''' destructor '''
		self.db.close()

	def process_IN_CLOSE_WRITE(self, event):
		''' event handler for close file after writing event - insert path '''
		print 'close:\t', event.pathname
		self.delete(event.pathname) # TODO use UPDATE
		self.insert(event.pathname)
	
	def process_IN_DELETE(self, event):
		''' event handler for delete event - removes path'''
		print 'delete:\t', event.pathname
		self.delete(event.pathname)
		
	def insert(self, path):
		''' insert path and timestamp '''
		cursor = self.db.cursor()
		sql = 'INSERT INTO incoming VALUES (?, ?)'
		cursor.execute(sql, [int(time.time()), path])
		cursor.close()
		self.db.commit()
		
	def delete(self, path):
		''' delete path from db '''
		cursor = self.db.cursor()
		sql = 'DELETE FROM incoming WHERE file=?'
		cursor.execute(sql, (path,))
		cursor.close()
		self.db.commit()

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
		watchingDir = config.get('Main', 'watchingDirectory')
		databaseFile = config.get('Main', 'database')
	else:
		###############
		# set default #
		###############
		watchingDir = '/home'
		databaseFile = '/tmp/files.db'
	watchingMask = pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE
    
    ##############
    # initialize #
	##############
	watchManager = pyinotify.WatchManager()
	handler = EventHandler(databaseFile)
	notifier = pyinotify.Notifier(watchManager, handler)
	watchManager.add_watch(watchingDir, watchingMask)
	notifier.loop()
