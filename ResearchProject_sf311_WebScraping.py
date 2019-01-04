# author: Vlad Sliusar

"""
    This program parses through 20 pages on 311SF.org and collects all links to the pages of individual street cleaning requests.
    It then parses the pages of the individual requests, collects the data and saves it in a .csv file.
"""

from bs4 import BeautifulSoup
import urllib.request
import csv

# Creating the csv file to write it
# encoding="utf-8" prevents the program from crashing due to unknown elemnts (emoji)
# Change 'a' - append to 'w' write for initial run.
csv_file = open('sf311_requests_v3.csv','a',encoding="utf-8")
csv_writer = csv.writer(csv_file,lineterminator='\n') # lineterminator='\n' prevents blank rows when writing to csv
csv_writer.writerow(['id','status', 'case_notes','date','time','title','description','address','latitude','longitude',\
                     'submitted_via','image_link'])

# list of pages to loop though using for loop; having checked https for pages
pageNumbers = ['','page=2','page=3','page=4','page=5','page=6','page=7','page=8','page=9','page=10',\
               'page=11','page=12','page=13','page=14','page=15','page=16','page=17','page=18','page=19','page=20']

# for loop creates https for each page using .format
for pageNo in pageNumbers:
    url = "https://mobile311.sfgov.org/?external=false&{}&service_id=518d5892601827e3880000c5&status=open".format(pageNo)
    #print (url)
    # link for CLOSED requests: https://mobile311.sfgov.org/?external=false&{}&service_id=518d5892601827e3880000c5&status=closed
    # link for OPEN requests: https://mobile311.sfgov.org/?external=false&{}&service_id=518d5892601827e3880000c5&status=open

    # opens each https with beatiful soup package and parses data using lxml package
    soup = BeautifulSoup(urllib.request.urlopen(url).read(),'lxml')
    #print (soup)

#request = soup.find('tr') # this was used to test one request first prior to implementing for loop to search all requests
#print (request.prettify())

        # for loop allows to search all requests and parse the necessary info from them
        # in this instance each web page (https) is searched for links to individual request pages
    for request in soup.find_all('tr'):
            link_src = request['onclick']
            link_id = link_src.split('=')[1] # split src into a list of itmes by = sign. Select element by using its index location.
            link_id = link_id.split(";")[0] # split on ;
            link_id = link_id.strip('\'"') # remove '' by escaping the '' caracter using .strip method
            #print (link_id)

            # created an array (list) of links, so for loop below can be implimented
            #individual link; using format method to insert link_id.
            ind_links = ['https://mobile311.sfgov.org{}'.format(link_id)]

            # this for loop goes through each of the individual links, opens and parses them
            for ind_link in ind_links:
                url = ind_link
                soup1 = BeautifulSoup(urllib.request.urlopen(url).read(), 'lxml')
                ind_request = soup1.find('div',class_='span8')
                #print (url)

                ### this finds the data of interest from each individual page (request):

                # id of each request, utilized replace method to remove # in from of the id
                id = ind_request.find('div',class_='blue-bar').strong.text
                id = id.replace('#','')

                status = ind_request.find('div',class_='blue-bar').span.text
                case_notes = ind_request.find('div',class_='blue-bar').text

                # finding date and time for each of the requests and seperating them into two columns
                dateTime_submitted = ind_request.td.text
                date = dateTime_submitted[:16] # this only prints first 15 characters of a string
                date = date.replace(',','') # replaces comma Tue Apr 24, 2018 with empty space Tue Apr 24 2018

                time = dateTime_submitted[17:]

                header = ind_request.h2.text
                description = ind_request.blockquote.p.text

                # address is split at : into ['address','1230 Howard st.']
                address = ind_request.find('div',class_='tab-content').p.text
                address = address.split(':')[1]

                # coordinates are split at comma into lat and lon
                coordinates = ind_request.find('div',class_='tab-content').a.text
                lat = coordinates.split(',')[0]
                lon = coordinates.split(',')[1]

                # finidng method used to submit a request (e.g. iPhone, Web, Android)
                submitted_via = ind_request.find('img',class_='channel-icon')['alt']

                # finidng images associated with requests. Using try/except as not all requests have images.
                try:
                    image_src = ind_request.find('div','boxInner').a['href']
                    image_link = 'https://mobile311.sfgov.org{}'.format(image_src)
                except Exception as e:
                    image_link = None
                #print(case_notes)

                # writing data to csv going through each iteration
                csv_writer.writerow([id,status,case_notes,date,time,header,description,address,lat,lon,submitted_via,image_link])

csv_file.close()
