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

import ConfigParser
import time
import sqlite3
import os
import shutil

import gtk


class AutoEncode():
	def __init__(self, databaseFile, tmpDir):
		''' initializes AutoEncode '''
		self.tmpDir = tmpDir
		self.settings = {}
		self.settings['minimalUntouchedTime'] = 3
	
		self.db = sqlite3.connect(databaseFile)
	
		cursor = self.db.cursor()
		sql = """
		CREATE TABLE IF NOT EXISTS incoming (
			date INTEGER,
			file TEXT
		)"""
		cursor.execute(sql);
		
		sql = """
		CREATE TABLE IF NOT EXISTS encode (
			date INTEGER,
			file TEXT
		)"""
		cursor.execute(sql);
		cursor.close()
		
		self.db.commit()
		
		self.check()
		
	def __del__(self):
		''' destructor '''
		self.db.close()
		
	def insert(self, path):
		''' insert path and timestamp '''
		cursor = self.db.cursor()
		sql = 'INSERT INTO encode VALUES (?, ?)'
		cursor.execute(sql, [int(time.time()), path])
		cursor.close()
		self.db.commit()
		
	def delete(self, table, path):
		''' delete path from db '''
		cursor = self.db.cursor()
		if table == 'incoming':
			sql = 'DELETE FROM incoming WHERE file=?'
		elif table == 'encode':
			sql = 'DELETE FROM encode WHERE file=?'		
		cursor.execute(sql, (path, ))
		cursor.close()
		self.db.commit()
	
	def check(self):
		print 'check for new files ...'
		cursor = self.db.cursor()
		sql = """SELECT * FROM incoming ORDER BY date ASC"""
		cursor.execute(sql);
		for row in cursor:
			if ( time.time() - row[0] ) <= self.settings['minimalUntouchedTime']:
				continue
			fromPath = row[1].encode('utf-8')
			toPath = os.path.realpath(os.path.join(self.tmpDir,os.path.basename(fromPath)))
			if os.path.exists(toPath):
				toPath += '2'
			print 'moving ...', fromPath, ' => ', toPath
			shutil.move(fromPath, toPath)
			self.delete('incoming', fromPath)
			self.insert(toPath)
		cursor.close()
		
#				print 'moving file - ' + tmpPath
#				toRemove.append(tmpPath)
#				shutil.move(tmpPath,self.tmpDir)
			
		time.sleep(30)
		self.check()	
	
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
		tmpDir = config.get('Main', 'tmpDirectory')
		databaseFile = config.get('Main', 'database')
	else:
		###############
		# set default #
		###############
		tmpDir = '/tmp'
		databaseFile = '/tmp/files.db'
    
    ##############
    # initialize #
	##############
	
	myAE = AutoEncode(databaseFile, tmpDir)
	
	
	
