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
import os
import time
import shutil

import gtk

class AutoEncode():
	def __init__(self, fooFile, tmpDir):
		print 'starting AutoEncode ...'
		self.file = fooFile
		self.tmpDir = tmpDir
		if not os.path.exists(self.tmpDir):
			os.mkdir(self.tmpDir)
		elif not os.path.isdir(self.tmpDir):
			raise Exception()
		self.settings = {}
		self.settings['minimalUntouchedTime'] = 300
		self.check()
		
	def check(self):
		while True:
			print 'check for new files ...'
			toRemove = []
			fileHandler = open(self.file, 'r')
			while True:
				line = fileHandler.readline()
				if line == '':
					break
				tmp = line.split('\t')
				if ( float(tmp[0]) - time.time() ) <= self.settings['minimalUntouchedTime']:
					tmpPath = tmp[1][:-1]
					print 'moving file - ' + tmpPath
					toRemove.append(tmpPath)
					shutil.move(tmpPath,self.tmpDir)
				
				
			fileHandler.close()
			
			time.sleep(30)
		

if __name__ == '__main__':
	# parse config file
	config = ConfigParser.ConfigParser()
	if os.path.exists('settings.conf'):
		config.read('settings.conf')
		# settings
		fooFile = config.get('Main', 'fooFile')
		tmpDir = config.get('Main', 'tmpDirectory')
	else:
		fooFile = '/tmp/fooFile'
		tmpDir = '/tmp/tmp'
	#myAE = AutoEncode(fooFile, tmpDir)
	
	fh = open(fooFile, 'w+')
	gtk.main()
