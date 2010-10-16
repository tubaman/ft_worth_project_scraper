#!/usr/bin/env python
import sys
import logging
import csv
from urllib2 import urlopen, Request
from BeautifulSoup import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SITE_URL = 'http://projects.fortworthgov.org'
MAX_NUM_PHASES = 10

def get_project_html(id):
    """Get the HTML from a particular project's details page"""
    url = SITE_URL + '/FindByListProjectDetail.aspx?PID=%05d' % id
    logger.info("getting %s" % url)
    req = Request(url)
    response = urlopen(req)
    html = response.read()
    return html

PROJECT_DATA = {
    'name': 'lblProjName',
    'description': 'lblNotes',
    'number': 'lblProj_id',
    'district': 'lblDISTRICT',
    'manager': 'lbProjectManager',
    'manager_company': 'lblProjectManagerCompany',
    'manager_email': 'lblProjectManagerEmail',
    'manager_phone': 'lblProjectManagerPhone',
    'consultant': 'lblCONSULTANT',
    'contractor': 'lblCONTRACTOR',
    'status': 'lblStatus',
}

def parse_project(html):
    soup = BeautifulSoup(html)
   
    p = {}
    for key, label in PROJECT_DATA.items():
        p[key] = soup.find(name='span', attrs={
            'id': 'ctl00_PageContent_%s' % label
        }).contents[0]

    phases = []
    phase_table = soup.find(name='table', attrs={
        'id': 'ctl00_PageContent_grid_DXMainTable'})
    for row in phase_table.findAll('tr'):
        try:
            if 'dxgvDataRow' in row.attrs[1][1]:
                cols = row.findAll('td')
                phase = {'name': cols[0].contents[0],
                         'date': cols[1].contents[0]}
                phases.append(phase)
        except IndexError:
            pass

    # TODO: raise exception if project name is 'Label' (ex: pid 00000)
    p['phases'] = phases
    logger.debug("project: %s" % p)
    return p

def output_csv(projects):
    csv_writer = csv.writer(sys.stdout)
    project_headers = PROJECT_DATA.keys()
    phase_headers = []
    for n in range(MAX_NUM_PHASES):
        phase_headers.append('phase%d_name' % (n+1))
        phase_headers.append('phase%d_date' % (n+1))
    headers = project_headers + phase_headers
    csv_writer.writerow(headers)
    for p in projects:
        project_data = [p[k] for k in project_headers]
        phase_data = []
        for phase in p['phases'][:MAX_NUM_PHASES]:
            phase_data.append(phase['name'])
            phase_data.append(phase['date'])
        data = project_data + phase_data
        csv_writer.writerow(data)

def main():
    projects = []

    for pid in range(100):
        try:
            html = get_project_html(pid)
            project = parse_project(html)
            projects.append(project)
        except:
            pass

    #html = get_project_html(84)
    #project = parse_project(html)
    #projects.append(project)

    output_csv(projects)

if __name__ == '__main__':
    logging.basicConfig()
    main()
