#!/usr/bin/env python
import sys, logging, csv, re, time
from urllib2 import urlopen, Request
from BeautifulSoup import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SITE_URL = 'http://projects.fortworthgov.org'
MAX_PIDS = 2000
INTER_PROJECT_POLL_DELAY = 1 # secs
MAX_NUM_PHASES = 10
MAX_NUM_POINTS = 15

def get_project_html(id):
    """Get the HTML from a particular project's details page"""
    url = SITE_URL + '/FindByListProjectDetail.aspx?PID=%05d' % id
    logger.debug("getting %s" % url)
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

class ProjectParseError(Exception): pass

def parse_project(html):
    soup = BeautifulSoup(html)
   
    p = {}
    for key, label in PROJECT_DATA.items():
        p[key] = soup.find(name='span', attrs={
            'id': 'ctl00_PageContent_%s' % label
        }).contents[0]

    if p['name'] == 'Label':
        raise ProjectParseError("HTML page appears to have default values('Label'")

    p['phases'] = parse_phases(soup)
    p['geo'] = parse_geo(soup)
    logger.debug("project: %s" % p)
    return p

def parse_phases(soup):
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
    return phases

def parse_geo(soup):
    script = find_script_containing_geodata(soup)
    geo = find_geodata_in_script(script)
    return geo

def find_script_containing_geodata(soup):
    for s in soup.findAll('script'):
        if s.contents and 'showPolygons' in s.contents[0]: 
            #logger.debug("geo script: %s" % s.contents[0])
            return s.contents[0]

def find_geodata_in_script(script):
    geo_re = "tmp_String = '(.*)';"
    matches = re.findall(geo_re, script)[2:]
    #logger.debug("matches: %s" % matches)
    lats = matches[0].split('|')
    logger.debug("lats: %s" % lats)
    longs = matches[1].split('|')
    logger.debug("longs: %s" % longs)
    geo = zip(lats, longs)
    return geo

def output_csv(projects):
    csv_writer = csv.writer(sys.stdout)
    project_headers = PROJECT_DATA.keys()
    phase_headers = []
    for n in range(MAX_NUM_PHASES):
        phase_headers.append('phase%d_name' % (n+1))
        phase_headers.append('phase%d_date' % (n+1))
    geo_headers = []
    for n in range(MAX_NUM_POINTS):
        geo_headers.append('lat%d' % (n+1))
        geo_headers.append('long%d' % (n+1))
    headers = project_headers + phase_headers + geo_headers
    csv_writer.writerow(headers)
    for p in projects:
        project_data = [p[k] for k in project_headers]
        phase_data = []
        for n in range(MAX_NUM_PHASES):
            try:
                phase = p['phases'][n]
                phase_data.append(phase['name'])
                phase_data.append(phase['date'])
            except IndexError:
                phase_data.append('')
                phase_data.append('')
        geo_data = []
        for n in range(MAX_NUM_POINTS):
            try:
                point = p['geo'][n]
                geo_data.append(point[0]) 
                geo_data.append(point[1]) 
            except IndexError:
                geo_data.append('') 
                geo_data.append('') 
        data = project_data + phase_data + geo_data
        csv_writer.writerow(data)

def main():
    projects = []

    for pid in range(MAX_PIDS):
        try:
            html = get_project_html(pid)
            project = parse_project(html)
            projects.append(project)
        except:
            pass
        time.sleep(INTER_PROJECT_POLL_DELAY)

    #html = get_project_html(414)
    #project = parse_project(html)
    #projects.append(project)

    output_csv(projects)

if __name__ == '__main__':
    logging.basicConfig()
    main()
