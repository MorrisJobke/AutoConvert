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

import pyinotify
import time
import os

import pprint

import sys
import logging
import logging.handlers

WATCHINGDIR = '~/tmp'
WATCHINGDIR = os.path.expanduser(WATCHINGDIR)

LOGFILE = './log-watch'
LOGFORMAT = '%(levelname)s\t%(name)s\t%(relativeCreated)d\t%(message)s'
LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

class EventHandler(pyinotify.ProcessEvent):
	def __init__(self):
		''' initializes EventHandler '''
		log.debug('init EventHandler')
		pyinotify.ProcessEvent.__init__(self)
		self.db = Database()
		self.check()
		
	def check(self):
		files = os.listdir(WATCHINGDIR)
		for f in files:
			f = os.path.join(WATCHINGDIR, f)
			if os.path.isfile(f):
				self.db.update(f, os.path.getsize(f))

	def process_IN_CLOSE_WRITE(self, event):
		''' event handler for close file after writing event - insert path '''
		path = unicode(event.pathname, 'utf-8')
		log.info('close:\t' + path)
		try:
			size = os.path.getsize(path)
		except Exception, e:
			pass
		else:
			self.db.update(path, size)

	def process_IN_MOVED_TO(self, event):
		''' event handler for move file event - insert path '''
		path = unicode(event.pathname, 'utf-8')
		log.info('moved:\t' + path)
		try:
			size = os.path.getsize(path)
		except Exception, e:
			pass
		else:
			self.db.update(path, size)
		
	def process_IN_DELETE(self, event):
		''' event handler for delete event - removes path'''
		path = unicode(event.pathname, 'utf-8')
		log.info('delete:\t' + path)
		self.db.delete(path)

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
	# TMP vvvvvvvvvvvvvv
	level = logging.INFO
	# TMP ^^^^^^^^^^^^^^
	log.setLevel(level)
    
    ##############
    # initialize #
	##############
	watchManager = pyinotify.WatchManager()
	notifier = pyinotify.Notifier(watchManager, EventHandler())
	watchManager.add_watch(
		WATCHINGDIR, 
		pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_TO
	)
	notifier.loop()
