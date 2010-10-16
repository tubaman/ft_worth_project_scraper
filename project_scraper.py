#!/usr/bin/env python
import csv
import sys
from urllib2 import urlopen, Request
from BeautifulSoup import BeautifulSoup

projects = []

url = 'http://projects.fortworthgov.org/FindByList.aspx'
req = Request(url)
response = urlopen(req)
html = response.read()
#print html

soup = BeautifulSoup(html)
table = soup.find(name='table', attrs={'id': 'ctl00_PageContent_grid_DXMainTable'})
#print table
rows = table.findAll('tr', attrs={'class': 'dxgvDataRow'})
#print rows
for row in rows:
	#print "row: %s" % row
	cols = row.findAll('td')
	#print "col num: %s" % len(cols)
	project = {
		'district': cols[0].contents[0], 
		'name': cols[1].contents[0],
		'category': cols[2].contents[0],
		'status': cols[3].contents[0],
		'details_url': cols[4].find('a').attrs[0][1],
	}
	#print "project: %s" % project
	projects.append(project)	

csv_writer = csv.writer(sys.stdout)
csv_writer.writerow(['district', 'name', 'category', 'status', 'details_url'])
for p in projects:
	csv_writer.writerow([p['district'], p['name'], p['category'], p['status'], p['details_url']])
