#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
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

from database import Database

import time
import os
import gobject
import gtk
import string
import shutil
import subprocess

import pprint

import sys
import logging
import logging.handlers

TMPDIR = './in-arbeit'
WAITTIME = 60
PRESET = 'faster'

LOGFILE = './log-daemon'
LOGFORMAT = '%(levelname)s\t%(name)s\t%(relativeCreated)d\t%(message)s'
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
          
class AutoEncode():
	def __init__(self):
		''' initializes AutoEncode '''
		self.db = Database()
		self.check()
	
	def check(self):
		print 'check for new files ...'
		files = self.db.get()
		for f in files:
			if not os.path.exists(f[1]):
				self.db.delete(f[1].encode('utf-8'))
				continue
			
			if os.path.getsize(f[1]) != f[2]:
				self.db.update(f[1], os.path.getsize(f[1]))
				continue
				
			if time.time() - f[0] <= WAITTIME:
				continue
				
			if f[3] == '.':
				log.info('found...\t%s'%f[1])
				self.process(f[1])
			else:
				pass
				#TODO
		
		#gobject.timeout_add_seconds(30, self.check)
			
	def process(self, fromPath):
		path = {
			'ext': '',
			'encodeext': '.mp4',
			'from':	{
				'root': '',
				'name': '',
			},
			'to': {
				'root': '',
				'original': '',
				'encode': ''
			}
		}
		
		path['from']['root'] = os.path.dirname(fromPath)
		f = os.path.basename(fromPath)
		fs = string.rsplit(f, '.', 1)
		if len(fs) == 2:
			path['ext'] = '.' + fs[1]
			path['from']['name'] = fs[0]
		else:
			path['from']['name'] = f
		
		path['to']['root'] = tmpDir = os.path.realpath(os.path.join(
			path['from']['root'], 
			TMPDIR
		))
		
		path['to']['original'] = path['from']['name'] + '_original'
		path['to']['encode'] = path['from']['name'] + '_encode'
		
		if not os.path.exists(path['to']['root']):
			os.mkdir(path['to']['root'])
		if not os.path.isdir(path['to']['root']):
			log.info('tmp-dir is a file')
			raise Exception('tmp-dir is a file')
		
		while True:
			p1 = os.path.join(
				path['to']['root'], 
				path['to']['original'] + path['ext']
			)
			p2 = os.path.join(
				path['to']['root'], 
				path['to']['encode'] + path['encodeext']
			)
			if not( os.path.exists(p1) or os.path.exists(p2) ):
				break
			path['to']['original'] += '#'
			path['to']['encode'] += '#'
		
		self.db.encode(fromPath, p1)
		shutil.move(fromPath, p1)
		self.encode(p1, p2)
		self.db.delete(fromPath)				
				
	def encode(self,iF, oF):
		times = {}
		t1 = time.time()
		log.info('in:\t%s'%iF)
		log.info('out:\t%s'%oF)
		log.info('start:\t%s'%time.strftime('%H:%M:%S',time.localtime(t1)))
		cmd = 'ffmpeg -y -i "%s" -deinterlace -vcodec libx264 -vpre %s -f mp4 -acodec copy -threads 0 -crf 22 "%s"'%(iF, PRESET, oF)
		log.info(cmd)
		print subprocess.Popen(
			cmd,
			shell=True
			).communicate()[0]
		t2 = time.time()
		log.info('end:\t%s'%time.strftime('%H:%M:%S',time.localtime(t2)))
		t = t2 - t1
		h = int(t / 3600)
		t -= h * 3600
		m = int(t / 60)
		t -= m * 60
		s = '%s - %i h %i m %i s'%(PRESET,h,m,t)
		log.info(s)
		subprocess.Popen('touch "%s.finished"'%oF, shell=True)

if __name__ == '__main__':
	######################
	# initialize logfile #
	######################
	logFile = os.path.join(
                sys.path[0],
                LOGFILE
        )	
	logging.basicConfig(filename=logFile, filemode='a', format=LOGFORMAT)
	log = logging.getLogger('Log')
	level = logging.NOTSET
	if len(sys.argv) > 1:
		level_name = sys.argv[1]
		level = LEVELS.get(level_name, logging.NOTSET)
	level = logging.DEBUG
	log.setLevel(level)
    
    ##############
    # initialize #
	##############
	
	myAE = AutoEncode()
	
	#gtk.main()
