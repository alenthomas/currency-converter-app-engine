#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib
import logging
import json#, simplejson
import datetime

from google.appengine.api import urlfetch

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# [START currency]
class Currency(webapp2.RequestHandler):

    def get(self):

        url = 'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.xchange%20where%20pair%20in%20(%22USDSGD%22)&env=store://datatables.org/alltableswithkeys'
        try:
            result = urlfetch.fetch(url)
            if result.status_code == 200:
                print(str(result.content)[222:228])
                #self.response.write(result.content)
            else:
                self.response.status_code = result.status_code
        except urlfetch.Error:
            logging.exception('Caught exception fetching url')
        
        template_values = {
            'rate': str(result.content)[222:228],
            'current_date': datetime.datetime.today().strftime('%Y-%m-%d'),
        }


        template = JINJA_ENVIRONMENT.get_template('currency.html')
        self.response.write(template.render(template_values))

# [END currency]

# [START Data]

class Data(webapp2.RequestHandler):

    def get(self, date=None):

        url = "http://finance.yahoo.com/connection/currency-converter-cache?bypass=true&date="
        if date:
            url = url + str(date)
            
        data = None
        try:
            result = urlfetch.fetch(url)
            if result.status_code == 200:
                #self.response.write(str(result.content)[55:-3])
                #data = str(result.content)[55:-3]
                #print(str(result.content))
                data = None
            else:
                self.response.status_code = result.status_code
        except urlfetch.Error:
            logging.exception('Caught exception fetching url')

        data = json.loads(result.content[55:-3])
        #print(data)

        current_rate = None
        for i in data['list']['resources']:
            if i['resource']['fields']['symbol'] == "SGD=X":
                current_rate = i['resource']['fields']['price']
                print(current_rate)

        if current_rate:
            error = None
        else:
            error = "Please enter a valid date in the url. Format as YYYYMMDD"
        template_values = {
            'rate': current_rate,
            'date': date,
            'current_date': datetime.datetime.today().strftime('%Y-%m-%d'),
            'error':error,
        }
        

        
        template = JINJA_ENVIRONMENT.get_template('currency.html')
        self.response.write(template.render(template_values))


# [END DATA]

# [START app]

app = webapp2.WSGIApplication(routes=[
    ('/', Currency),
    (r'/(?P<date>\w+)', Data),
], debug=True)
# [END app]
