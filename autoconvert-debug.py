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

if __name__ == '__main__':
	db = Database()
	r = db.get()
	for i in r:
		d = int(time.time()) - i[0]
		s = d%60
		d /= 60
		m = d%60
		d /= 60
		diff = '%2ih %2im %2is'%(d, m, s)
		t = time.strftime( '%d.%m.%Y %H:%M:%S' ,time.localtime(i[0]))
		print '%-20s %-70s %-70s %11i %s'%(t, i[1], i[3], i[2], diff)
	
