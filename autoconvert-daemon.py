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

import subprocess
import string

import gtk

import pprint

import gobject

import sys
import logging
import logging.handlers

LOGFILE = './log-daemon'
LOGFORMAT = '%(levelname)s\t%(name)s\t%(relativeCreated)d\t%(message)s'
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


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
		log.info('check for new files ...')
		cursor = self.db.cursor()
		sql = """SELECT * FROM incoming ORDER BY date ASC"""
		cursor.execute(sql);
		for row in cursor:
			if ( time.time() - row[0] ) <= self.settings['minimalUntouchedTime']:
				continue
			fromPath = row[1].encode('utf-8')
			log.info('found...\t%s'%fromPath)
			if os.path.exists(fromPath):
				self.move(fromPath)
		cursor.close()

		gobject.timeout_add_seconds(5, self.check)
		
	def move(self, fromPath):
		filename = os.path.basename(fromPath)
		print 'from:\t\t', string.rsplit(fromPath,'/',1)[0]
		print 'to:\t\t', os.path.realpath(self.tmpDir)
		filename = string.rsplit(filename,'.',1)
		if len(filename) == 2:
			extension = '.' + filename[1]
		else:
			extension = ''
		encodeFilename = filename[0] + '_encode'
		filename = filename[0] + '_original'
		
		print 'filename:\t', filename
		print 'extension:\t',  extension
		toPath = os.path.realpath(os.path.join(self.tmpDir,filename + extension))
		encodePath = os.path.realpath(os.path.join(self.tmpDir,encodeFilename + '.mp4'))		
		if os.path.exists(toPath):
			filename += '_new'
			print 'new filename:\t', filename
			
		if os.path.exists(encodePath):
			encodeFilename += '_new'
			print 'new eFilename:\t', encodeFilename
		
		encodeFilename += '.mp4'
		filename += extension		
		toPath = os.path.realpath(os.path.join(self.tmpDir,filename))
		print 'move from:\t', fromPath
		print 'move to:\t', toPath
		print 'encode to:\t', encodePath
		if not os.path.exists(os.path.dirname(toPath)):
			os.mkdir(os.path.dirname)
		shutil.move(fromPath, toPath)
		self.delete('incoming', fromPath)
		self.insert(toPath)
		self.encode(toPath, encodePath)
	
		
	def encode(self,iF, oF):
		times = {}
		presets = ['slow', 'medium', 'normal', 'fast', 'faster', 'default', 'veryfast', 'ultrafast', 'veryslow', 'hq', 'max']
		for preset in presets:
			print preset
			f = string.rsplit(oF,'.',1)
			if len(f) == 2:
				outF = f[0] + '_' + preset + '.' + f[1]
			else:
				outF = f[0] + '_' + preset
			print outF
			t1 = time.time()
			log.info('in:\t%s'%iF)
			log.info('out:\t%s'%outF)
			log.info('start:\t%s'%time.strftime('%H:%M:%S',time.localtime(t1)))
			print subprocess.Popen(
				'ffmpeg -y -i "%s" -deinterlace -vcodec libx264 -vpre %s -f mp4 -acodec libfaac -threads 0 -crf 22 "%s"'%(iF, preset, outF),
				'''[	'ffmpeg',
					'-y', 
					'-i', 
					iF, 
					'-deinterlace', 
					'-vcodec',
					'libx264',
					'-vpre',
					preset,
					'-f',
					'mp4',
					'-acodec',
					'libfaac',
					'-threads',
					'0',
					'-crf',
					'22',
					outF
				], '''
				shell=True
				#stdout=subprocess.PIPE,
				#stderr=subprocess.STDOUT
				).communicate()[0]
			t2 = time.time()
			log.info('end:\t%s'%time.strftime('%H:%M:%S',time.localtime(t2)))
			t = t2 - t1
			h = int(t / 3600)
			t -= h * 3600
			m = int(t / 60)
			t -= m * 60
			s = '%s - %i h %i m %i s'%(preset,h,m,t)
			log.info(s)
			times[preset] = {
				'start': time.strftime('%H:%M:%S',time.localtime(t1)),
				'end':  time.strftime('%H:%M:%S',time.localtime(t2)),
				'time': s
			}
		pprint.pprint(times)
	
if __name__ == '__main__':
	######################
	# initialize logfile #
	######################
	logging.basicConfig(filename=LOGFILE, filemode='w', format=LOGFORMAT)
	log = logging.getLogger('Log')
	level = logging.NOTSET
	if len(sys.argv) > 1:
		level_name = sys.argv[1]
		level = LEVELS.get(level_name, logging.NOTSET)
	level = logging.DEBUG
	log.setLevel(level)
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
	
	gtk.main()
	
