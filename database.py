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

import sqlite3
import os.path
import time

import pprint

DATABASEFILE = '~/.autoconvert.db'
DATABASEFILE = os.path.expanduser(DATABASEFILE)

class Database:
	def __init__(self):
		self.db = sqlite3.connect(DATABASEFILE)	
		sql = """
		CREATE TABLE IF NOT EXISTS files (
			date INTEGER,
			file TEXT,
			size INTEGER,
			encodefile TEXT
		)"""
		cursor = self.db.cursor()
		cursor.execute(sql)
		cursor.close()
		self.db.commit()
	
	def insert(self, fileName, fileSize):
		sql = 'INSERT INTO files VALUES (?, ?, ?, ".")'
		cursor = self.db.cursor()
		cursor.execute(sql, [int(time.time()), fileName, fileSize])
		cursor.close()
		self.db.commit()
	
	def update(self, fileName, fileSize):
		if not self.exists(fileName):
			self.insert(fileName, fileSize)
		else:		
			sql = 'SELECT size FROM files WHERE file = ?'
			cursor = self.db.cursor()
			a = cursor.execute(sql, [fileName])
			for i in a:
				if i[0] == fileSize :
					return
			sql = 'UPDATE files SET date = ?, size = ? WHERE file = ?'
			cursor.close()
			cursor = self.db.cursor()
			cursor.execute(sql, [int(time.time()), fileSize, fileName])
			cursor.close()
			self.db.commit()
	
	def delete(self, fileName):
		sql = 'DELETE FROM files WHERE file = ?'
		cursor = self.db.cursor()
		cursor.execute(sql, [fileName, ])
		cursor.close()
		self.db.commit()
	
	def exists(self, fileName):
		sql = 'SELECT * FROM files WHERE file = ?'
		cursor = self.db.cursor()		
		cursor.close()
		for a in cursor.execute(sql, [fileName, ]):
			return True
		return False
		
	def get(self):
		sql = 'SELECT ALL * FROM files'
		cursor = self.db.cursor()
		result = list()
		for a in cursor.execute(sql):
			result.append(a)
		cursor.close()
		return result
	
	def encode(self, fileName, fileNameEncode):
		if self.exists(fileName):
			sql = 'UPDATE files SET encodefile = ? WHERE file = ?'
			cursor = self.db.cursor()
			cursor.execute(sql, [fileNameEncode, fileName ])
			cursor.close()
			self.db.commit()
		
	def __del__(self):
		self.db.close()
		
if __name__ == '__main__':
	d = Database()
	d.insert('asd', 123)
	pprint.pprint( d.get())
		
