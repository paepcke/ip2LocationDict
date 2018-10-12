# Copyright (c) 2014, Stanford University
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
Created on Oct 11, 2018, based on ipCountryState.py

Implements an in-memory lookup table that maps IP addresses
to the countries, region (in US that's a.k.a. State), city,
lat/long, and zip code that they are assigned to. 

For any IP the two and three letter codes, and the full country 
name can be obtained, in addition to the other info.

Instance creation builds the table from information on disk.
It is therefore recommended that only one instance is made,
and then used for many lookups. But creating multiple instances
does no harm.

The out-facing method is lookupIP(ipString)

The underlying IP->FullLOcation information comes from http://software77.net/geo-ip/,
and is expected to be in data/IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-AREACODE.CSV

@author: paepcke
'''

import argparse
import csv
import os
import sys
import unittest


class IpFullLocation(unittest.TestCase):
    '''
    Implements lookup mapping IP to country.
    '''
    START_IP_POS = 0
    END_IP_POS   = 1
    TWO_LETTER_POS = 2
    COUNTRY_POS = 3
    STATE_POS = 4
    CITY_POS = 5
    LAT_POS = 6
    LONG_POS = 7
    ZIP_POS = 8
    TIMEZONE_POS = 9
    COUNTRY_PHONE_POS = 10
    AREA_PHONE_POS = 11
    
    XLATION_CSV = 'IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-AREACODE.CSV'


    #--------------------------
    # Constructor 
    #----------------

    def __init__(self, ipTablePath=None):
        '''
        Create an in-memory dict for quickly looking up IP addresses.
        The underlying IP->Country information comes from http://software77.net/geo-ip/
        If an unzipped table from their Web site is not passed in, then 
        the table is expected to reside in subdirectory 'data' of this script's directory
        under the name IpFullLocation.XLATION_CSV. Their table contains
        columns for (decimal)startRange, endRange, and the other values.
        
        The lookup table we construct uses the first four digits of the 
        starting ranges as key. Values are an array of tuples:
            (startIpRange,endIPRange,2-letterCode,3-letterCode,Country)
        All IPs in one key's values thus start with the key's digits.
        The arrays are just a few tuples long, so the scan through them
        is fast. The arrays are ordered by rising start and (therefore)
        end IP.
        
        We also construct a simpler dict that maps a country's three-letter
        code to a tuple: (two-letter code, three-letter code, full country name).
        '''
        currKey = 0
        self.ipDict = {currKey : []}
        self.twoLetterKeyedDict = {}
        if ipTablePath is None:
            tableSubPath = os.path.join('data/', IpFullLocation.XLATION_CSV)
            ipTablePath = os.path.join(os.path.dirname(__file__), tableSubPath)
        with open(ipTablePath, 'r') as fd:
            for line in csv.reader(fd):
                if len(line) == 0 or line[0] == '#' or line == '\n' or line[0] == '0':
                    continue
                try: 
                    (startIPStr,endIPStr,twoLetterCountry,country, state, city,
                     latitude, longitude, zipcode, timezone, country_phone_code, area_code) = line
                except ValueError as e:
                    print("Irregularity in IP db line '%s': %s" % (line, `e`))
                    continue
                # Use first four digits of start ip as hash key:
                hashKey = startIPStr.strip('"').zfill(10)[0:4]
                if hashKey != currKey:
                    self.ipDict[hashKey] = []
                    currKey = hashKey
                self.ipDict[hashKey].append((int(startIPStr.strip('"')), 
                                                       int(endIPStr.strip('"')), 
                                                       twoLetterCountry.strip('"'), 
                                                       country.strip('"'), 
                                                       state.strip('"'),
                                                       city.strip('"'),
                                                       float(latitude),
                                                       float(longitude),
                                                       zipcode.strip('"'),
                                                       timezone.strip('"'),
                                                       country_phone_code.strip('"'),
                                                       area_code.strip('"')
                                                       )
                                                    )
                self.twoLetterKeyedDict[twoLetterCountry.strip('"')] = (twoLetterCountry.strip('"'), 
                                                                        country.strip('"'),
                                                                        state.strip('"'),
                                                                        city.strip('"')
                                                                        )

    #--------------------------
    #  get
    #----------------

    def get(self, ipStr, default=None):
        '''
        Same as lookupIP, but returns default if
        IP not found, rather than throwing a KeyError.
        This method is analogous to the get() method
        on dictionaries.
        :param ipStr: string of an IP address 
        :type ipStr: String
        :param default: return value in case IP address country is not found.
        :type default: <any>
        :return: 2-letter country code, country, region, city, 
            lat, long, zipcode, timezone, country_phone_code, area_phone_code 
        :rtype: {any | (str,str,str,str,float,float,int,str,int,int)}
        '''
        try:
            return self.lookupIP(ipStr)
        except KeyError:
            return default

    #--------------------------
    # getBy3LetterCode 
    #----------------

    def getBy3LetterCode(self, threeLetterCode):
        return self.twoLetterKeyedDict[threeLetterCode]
    
    #--------------------------
    # lookupIP 
    #----------------
    
    def lookupIP(self,ipStr):
        '''
        Top level lookup: pass an IP string, get a
        four-tuple: two-letter country code, full country name, region, and city:
        :param ipStr: string of an IP address
        :type ipStr: string
        :return: 2-letter country code, country, region, city, 
            lat, long, zipcode, timezone, country_phone_code, area_phone_code 
        :rtype: (str,str,str,str,float,float,int,str,int,int)
        :raise ValueError: when given IP address is None
        :raise KeyError: when the country for the given IP is not found. 
        '''
        (ipNum, lookupKey) = self.ipStrToIntAndKey(ipStr)
        if ipNum is None or lookupKey is None:
            raise ValueError("IP string is not a valid IP address: '%s'" % str(ipStr))
        while lookupKey > 0:
            try:
                ipRangeChain = self.ipDict[lookupKey]
                if ipRangeChain is None:
                    raise ValueError("IP string is not a valid IP address: '%s'" % str(ipStr))
                # Sometimes the correct entry is *lower* than
                # where the initial lookup key points:
                if ipRangeChain[0][0] > ipNum:
                    # Backtrack to an earlier key:
                    raise KeyError()
                break
            except KeyError:
                lookupKey = str(int(lookupKey) - 1).zfill(4)[0:4]
                continue
        for ipInfo in ipRangeChain:
            # Have (rangeStart,rangeEnd,country2Let,country3Let,county)
            # Sorted by rangeStart:
            if ipNum > ipInfo[IpFullLocation.END_IP_POS]:
                continue
            return(ipInfo[IpFullLocation.TWO_LETTER_POS], 
                   ipInfo[IpFullLocation.COUNTRY_POS],
                   ipInfo[IpFullLocation.STATE_POS],
                   ipInfo[IpFullLocation.CITY_POS],
                   ipInfo[IpFullLocation.LAT_POS],
                   ipInfo[IpFullLocation.LONG_POS],
                   ipInfo[IpFullLocation.ZIP_POS],
                   ipInfo[IpFullLocation.TIMEZONE_POS],
                   ipInfo[IpFullLocation.COUNTRY_PHONE_POS],
                   ipInfo[IpFullLocation.AREA_PHONE_POS]
                   )
        # If we get here, the IP is in a range in which
        # the IP-->Country table has a hole:
        raise KeyError("Ip %s not found in location translator." % ipStr)
        
    # ------------------------------------- Utility Methods ---------------
        
    #--------------------------
    # ipStrToIntAndKey
    #----------------
        
            
    def ipStrToIntAndKey(self, ipStr):
        '''
        Given an IP string, return two-tuple: the numeric
        int, and a lookup key into self.ipDict.
         
        :param ipStr: ip string like '171.64.65.66'
        :type ipStr: string
        :return: two-tuple of ip int and the first four digits, i.e. a lookup key. Like (16793600, 1679). Returns (None,None) if IP was not a four-octed str.
        :rtype: (int,int)
        '''
        try:
            (oct0,oct1,oct2,oct3) = ipStr.split('.')
        except ValueError:
            # Given ip str does not contain four octets:
            return (None,None)
        ipNum = int(oct3) + (int(oct2) * 256) + (int(oct1) * 256 * 256) + (int(oct0) * 256 * 256 * 256)
        return (ipNum, str(ipNum).zfill(10)[0:4])

    #---------------------------- Self Test ---------------------------

    #--------------------------
    # testAll 
    #----------------
    
    def testAll(self):
        #(ip,lookupKey) = lookup.ipStrToIntAndKey('171.64.64.64')
        res = self.lookupIP('171.64.75.96')
        self.assertEqual(res, ('US', 'United States', 'California', 
                               'Stanford', 37.421262, -122.163949, 
                               '94305', '-07:00', 1, 650)
                         )
        
        
    #---------------------------- Main ---------------------------

if __name__ == '__main__':
    
    DEFAULT_DB_FILE = os.path.join(os.path.dirname(__file__), 'data/%s' % IpFullLocation.XLATION_CSV),
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-d', '--dbfile',
                        help='fully qualified name of IP decoding CSV file. Default: %s' % DEFAULT_DB_FILE,
                        default=DEFAULT_DB_FILE);
    parser.add_argument('-t', '--test',
                        help='run a self test',
                        action='store_true');
    parser.add_argument('ipaddr',
                        help='IP address to look up.'
                        )

    args = parser.parse_args();

    if args.test:
        IpFullLocation().testAll()
        sys.exit()
            
    lookup_dict = IpFullLocation()
    (twoLetter,country,region,city,latitude,longitude,zipcode,timezone,phone_country_code,phone_area_code) = lookup_dict.get(args.ipaddr)
    print('%s; %s; %s; %s; %s; %s; %s; %s; %s; %s' %\
          (twoLetter,country,region,city,latitude,longitude,zipcode,timezone,phone_country_code,phone_area_code)
          )
    
    
    