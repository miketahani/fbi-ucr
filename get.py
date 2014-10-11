# scrape Uniform Crime Report data from the FBI
import os
from time import sleep
from random import randrange
from optparse import OptionParser 

import mechanize

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'

parser = OptionParser()
parser.add_option('-w','--wait', default='10,27', help='range of times to sleep bt requests (sec); eg "10,27"')
parser.add_option('-u','--ua', default=DEFAULT_USER_AGENT, help='user agent string')
(options, args) = parser.parse_args()

sleep_range = map(lambda t: int(t), options.wait.split(','))


def select_all_control_options(control_name):
    """ select all options in a <select> tag """
    control = br.form.find_control(control_name)
    control_items = [item.name for item in control.items]
    control.value = control_items

def select_writeable_form(form_name):
    """ select a form and set readonly to false """
    br.select_form(form_name)
    br.set_all_readonly(False)

br = mechanize.Browser()

br.set_handle_robots(False)   # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
br.addheaders = [('User-agent', options.ua)]


url = 'http://www.ucrdatatool.gov/Search/Crime/Local/OneYearofData.cfm'
base_output_dir = 'downloaded'


def stateid_control_data():
    response = br.open(url)
    select_writeable_form('CFForm_1')
    control = br.form.find_control('StateId')
    control.value = ['1']
    # print control.items[]
    for item in control.items:
        if item.name == control.value[0]:
            # print " name=%s values=%s" % (item.name, [label.text for label in item.get_labels()][0])
            # print [label.text for label in item.get_labels()][0]
            print item.get_labels()[0].text
            break

# stateid_control_data()

def get_all():

    start_state, end_state = 1, 51+1
    for state_id in xrange(start_state, end_state):

        response = br.open(url)
        #print response.read()      # the text of the page

        select_writeable_form('CFForm_1')

        state_id_control = br.form.find_control('StateId')
        state_id_control.value = [str(state_id)]
        for item in state_id_control.items:
            if item.name == state_id_control.value[0]:
                state_name = item.get_labels()[0].text
                break

        # have to get the state name before we do all this, forcing us to request a page for each id
        # regardless of completion status
        state_output_dir = '%s/%s' % (base_output_dir, state_name)
        if not os.path.exists(state_output_dir):
            os.makedirs(state_output_dir)
            print 'made a new output directory: %s' % state_output_dir

        start_year, end_year = 1985, 2012+1
        already_done = [int(yr.replace('.html','')) for yr in os.listdir(state_output_dir) if yr.endswith('.html')]
        years_to_do = list(set(range(start_year, end_year)) - set(already_done))

        if not years_to_do:
            print 'already got all years for %s' % state_name
            # i dunno..
            sleep(1)
            continue

        response = br.submit()
        # print response.read()

        print 'submitted form for state %s (id=%d)' % (state_name, state_id)


        for year in years_to_do:

            filename = '%s/%d.html' % (state_output_dir, year)
            if os.path.exists(filename):
                print 'already exists, skipping %s' % filename
                continue

            print 'selecting form for year %d' % year

            select_writeable_form('CFForm_1')
            select_all_control_options('CrimeCrossId')
            select_all_control_options('DataType')

            # print br.form

            response = br.submit()

            print 'submitted form for state %s (id=%d) year %d' % (state_name, state_id, year)

            with open(filename, 'w') as outfile:
                outfile.write(response.read())
                print 'wrote file %s' % filename

            sleep_time = randrange(sleep_range[0], sleep_range[1])
            print 'sleeping for %d seconds' % sleep_time
            sleep(sleep_time)

            br.back()



get_all()
print 'done. have a nice day!'
