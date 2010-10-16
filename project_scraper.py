#!/usr/bin/env python
import csv
import sys
from urllib2 import urlopen, Request
from BeautifulSoup import BeautifulSoup

def output_csv(projects):
    csv_writer = csv.writer(sys.stdout)
    csv_writer.writerow(['district', 'name', 'category', 'status', 'details_url'])
    for p in projects:
        csv_writer.writerow([p['district'], p['name'], p['category'], p['status'], p['details_url']])

def get_projects_html():
    url = 'http://projects.fortworthgov.org/FindByList.aspx'
    req = Request(url)
    response = urlopen(req)
    html = response.read()
    return html

def get_project_html(id):
    url = 'http://projects.fortworthgov.org/FindByListProjectDetail.aspx?PID=%05d' % id
    print url
    req = Request(url)
    response = urlopen(req)
    html = response.read()
    return html

def find_projects(projects, html):
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
    return projects


def get_project(html):
    soup = BeautifulSoup(html)
    p = {}
    p['name'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblProjName'}).contents[0]
    p['description'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblNotes'}).contents[0]
    p['number'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblProj_id'}).contents[0]
    p['district'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblDISTRICT'}).contents[0]
    p['manager'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lbProjectManager'}).contents[0]
    p['manager_company'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblProjectManagerCompany'}).contents[0]
    p['manager_email'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblProjectManagerEmail'}).contents[0]
    p['manager_phone'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblProjectManagerPhone'}).contents[0]
    p['consultant'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblCONSULTANT'}).contents[0]
    p['contractor'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblCONTRACTOR'}).contents[0]
    p['status'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblStatus'}).contents[0]
    p['status'] = soup.find(name='span', attrs={'id': 'ctl00_PageContent_lblStatus'}).contents[0]

    phases = []
    phase_table = soup.find(name='table', attrs={'id': 'ctl00_PageContent_grid_DXMainTable'})
    for row in phase_table.findAll('tr'):
        try:
            if 'dxgvDataRow' in row.attrs[1][1]:
                cols = row.findAll('td')
                phase = {'name': cols[0].contents[0], 'date': cols[1].contents[0]}
                phases.append(phase)
        except IndexError:
            pass

    p['phases'] = phases
    print p
    return p

projects = []

# Here's the main code
#html = get_projects_html()
#projects = find_projects(projects, html)
#output_csv(projects)

html = get_project_html(628)
print html
project = get_project(html)
