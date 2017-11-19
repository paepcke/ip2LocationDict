#!/usr/bin/env python
'''
Created on Nov 18, 2017

@author: paepcke
'''
import argparse
import collections
import csv
import os
import random
import sys

class ZipOverlayer(collections.MutableMapping):
    '''
    classdocs
    '''
    ZIPCODE_SOURCE = os.path.join('%s' % os.path.dirname(__file__), 
                                  'Data/zip_code_database.csv')
            
    ZIP_INDEX = 0
    ZIP_TYPE = 1       # 'STANDARD', 'PO BOX', 'UNIQUE', 'MILITARY'
    STATE_INDEX = 5
    COUNTY_INDEX = 6
    LAT_INDEX = 9
    LONG_INDEX = 10
    
    def __init__(self, node_file, 
                       columns=[0], 
                       delimiter=',',
                       firstLineIsColHeader=False):
        '''
        Constructor
        
        @param node_file:
        @type node_file:
        @param columns:
        @type columns:
        @param delimiter:
        @type delimiter:
        @param firstLineIsColHeader:
        @type firstLineIsColHeader:
        '''
        
        super(ZipOverlayer, self).__init__()
        
        # Ensure input file is there and
        # readable right away:
        with open(node_file, 'r') as fd:  #@UnusedVariable
            pass
    
        self.node_file = node_file
        self.columns = columns
        self.delimiter = delimiter
        self.first_line_is_col_header = firstLineIsColHeader
        
        self.zipcode_to_node = {}
        self.node_to_zipcode = {}
        
        self.zipcodes        = {}
        self.county_zips     = {}
        self.state_zips      = {}
        
        self.used_zipcodes   = []
        
        self.internalize_zipcodes()
        
        self.assign_codes()
        
    # ------------------------- Output in Various Forms --------------
            
    #-----------------------------
    # export_converted_input 
    #-----------------------    
            
    def export_converted_input(self, outfile):
        '''
        Output a copy of the input file, with all
        nodes replaced by their zip codes. Example:
        Each line of the form:
        
          node1,father_of,node2
        
        is turned into:
        
          zipcode1,father_of,zipcode2
        
        @param outfile: full path to output file
        @type outfile: str
        '''

        coded_source = []
        with open(self.node_file) as source_fd:
            nodes_file_reader = csv.reader(source_fd,
                                           delimiter=self.delimiter,
                                           quotechar='"')
            # Copy header unchanged, if present:
            if self.first_line_is_col_header:
                coded_source.append(nodes_file_reader.next())
                
            for source_line in nodes_file_reader: 
                for col in self.columns:
                    source_line[col] = self.node_to_zipcode[source_line[col]]
                coded_source.append(source_line)
                
        with open(outfile, 'w') as out_fd:
            nodes_file_writer = csv.writer(out_fd,
                                           delimiter=self.delimiter,
                                           quotechar='"')
            nodes_file_writer.writerows(coded_source)

    #-----------------------------
    # get_overlay_reverser
    #-----------------------    
    
    def get_overlay_reverser(self):
        return ZipOverlayer.OverlayReverser(self.zipcode_to_node)

#     #-----------------------------
#     # get_zipode_to_nodes 
#     #-----------------------
#     
#     def get_zipcode_to_nodes(self, asMultilineString=False):
#         arr_of_2tuple_strings = ['%s,%s' % (zipcode, node) for 
#                                  zipcode,node in self.zipcode_to_node.values()]
#         if asMultilineString:
#             return '\n'.join(arr_of_2tuple_strings)
#         else:
#             return arr_of_2tuple_strings
#         
#     #-----------------------------
#     # get_nodes_to_zipcodes
#     #-----------------------
#     
#     def get_nodes_to_zipcodes(self, asMultilineString=False):
#         arr_of_2tuple_strings = ['%s,%s' % (node, zipcode) for 
#                                  node,zipcode in self.node_to_zipcode.values()]
#         if asMultilineString:
#             return '\n'.join(arr_of_2tuple_strings)
#         else:
#             return arr_of_2tuple_strings
#         
#     #-----------------------------
#     # export_zipcodes_to_nodes 
#     #-----------------------    
# 
#     def export_zipcodes_to_nodes(self, outfile):
#         writer = csv.writer(outfile)
#         for line in self.get_zipcode_to_nodes():
#             writer.writerow(line) 
# 
#     #-----------------------------
#     # export_nodes_to_zipcodes 
#     #-----------------------    
# 
#     def export_nodes_to_zipcodes(self, outfile):
#         writer = csv.writer(outfile)
#         for line in self.get_nodes_to_zipcodes():
#             writer.writerow(line) 

    # ------------------------- Computations --------------
    
    #-----------------------------
    # assign_codes 
    #-----------------------    
        
    def assign_codes(self):
        with open(self.node_file, 'r') as node_fd:
            nodes_file_reader = csv.reader(node_fd, delimiter=self.delimiter)
            # Pull in all node input lines:
            # Every line in the input may have 
            # multiple node columns; but get_next_node()
            # takes care of that:
            for node in self.get_next_node(nodes_file_reader):
                try:
                    self.node_to_zipcode[node]
                    # This node already has an 
                    # associated zipcode:
                    continue
                except KeyError:
                    # The node still needs an assignment:
                    zipcode = self.get_next_zipcode()
                    self.node_to_zipcode[node]    = zipcode
                    self.zipcode_to_node[zipcode] = node
        
    #-----------------------------
    # get_next_nodes
    #-----------------------    
        
    def get_next_node(self, nodes_file_reader):
        if self.first_line_is_col_header:
            # Nodes file's first line are the column
            # headers. Discard them:
            nodes_file_reader.next()
        for source_line in nodes_file_reader: 
            for col in self.columns:
                try:
                    yield source_line[col]
                except IndexError:
                    raise ValueError("At least one column number in %s is beyond width of source file %s" %\
                                      (self.columns, self.node_file))
    
    #-----------------------------
    # get_next_zipcode 
    #-----------------------    
        
    def get_next_zipcode(self):
        '''
        Return a random zip code from
        a randomly chosen US state. Ensure
        that successive calls never return
        the same zip code.
        '''
        # Pick a random US state:
        rand_us_state       = random.choice(self.state_zips.keys())
        # Pick a random zip code within that state:
        rand_zip_from_state = random.choice(self.state_zips[rand_us_state])
        # Ensure that each zip code is only used once:
        self.state_zips[rand_us_state].remove(rand_zip_from_state)
        # If we used all of this state's zipcodes, remove
        # the state from consideration:
        if len(self.state_zips[rand_us_state]) == 0:
            del self.state_zips[rand_us_state]
            # If this was the last state at our disposal,
            # complain:
            if len(self.state_zips.keys()) == 0:
                raise ValueError("Not enough zipcodes in the US to cover this dataset.")
        return rand_zip_from_state

    #-----------------------------
    # internalize_zipcodes
    #-----------------------    

    def internalize_zipcodes(self):
        '''
        Read all zip codes from file into memory.
        Build three dicts: 
            self.zipcodes: {'state'  : ...,
                            'county' : ...,
                            'lat'    : ...,
                            'long'   : ...
                            }
            self.county_zips: {county : [zip1,zip2,...]}
            self.state_zips:  {state  : [zip1,zip2,...]}
        '''
        with open(ZipOverlayer.ZIPCODE_SOURCE) as source_fd:
            reader = csv.reader(source_fd,
                                delimiter=self.delimiter,
                                quotechar='"')
            # Discard header of zip codes dataset:
            reader.next()
            for line in reader:
                the_zip   = line[ZipOverlayer.ZIP_INDEX]
                zip_type  = line[ZipOverlayer.ZIP_TYPE]
                if zip_type == 'MILITARY':
                    # No lat/long for military zip codes:
                    continue
                state     = line[ZipOverlayer.STATE_INDEX]
                county    = line[ZipOverlayer.COUNTY_INDEX]
                lat       = line[ZipOverlayer.LAT_INDEX]
                longitute = line[ZipOverlayer.LONG_INDEX]
                
                self.zipcodes[the_zip] = {'state' : state,
                                          'county' : county,
                                          'lat' : lat,
                                          'long' : longitute
                                          }  
                try:
                    self.county_zips[county].append(the_zip)
                except KeyError:
                    self.county_zips[county] = [the_zip]
                    
                try:
                    self.state_zips[state].append(the_zip)
                except KeyError:
                    self.state_zips[state] = [the_zip]
                
        self.all_zipcodes = self.zipcodes.keys()

    # --------- Dict Capabilities -----------
        
    def __getitem__(self, key):
        return self.node_to_zipcode[key]

    def __setitem__(self, key, value):
        raise NotImplemented("Zip overlays are read-only")

    def __delitem__(self, key):
        raise NotImplemented("Zip overlays are read-only")            

    def __iter__(self, zipOrNode='node'):
        return iter(self.node_to_zipcode)

    def __len__(self, zipOrNode='node'):
        return len(self.node_to_zipcode)

    def __keytransform__(self, key):
        return key
    
# ---------------------------- OverlayReverse -----------    

    class OverlayReverser(collections.MutableMapping):
        '''
        Dictionary to complement an instance of 
        ZipOverlayer. Provides zipcode-to-node
        conversion.
        
        Not intended for direct instantiation.
        Instantiated via ZipOverlayer.get_reverse_dict()
        '''
        
        def __init__(self, zipToNodeDict):
    
            super(ZipOverlayer.OverlayReverser, self).__init__()
            self.zip_to_node = zipToNodeDict
                
        def __getitem__(self, key):
            return self.zip_to_node[key]
    
        def __setitem__(self, key, value):
            raise NotImplemented("Zip overlays are read-only")
    
        def __delitem__(self, key):
            raise NotImplemented("Zip overlays are read-only")            
    
        def __iter__(self):
            return iter(self.zip_to_node)
    
        def __len__(self):
            return len(self.zip_to_node)            
    
        def __keytransform__(self, key):
            return key



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-c', '--columns',
                        nargs='*',
                        help='''Column numbers of input file where nodes are to be found (zero-based).
                        Default is column 0.''',
                        default=[])
    parser.add_argument('-d', '--delimiter',
                        help='Column delimiter; default: ","',
                        default=',')
    parser.add_argument('-f', '--firstLine',
                        help='If this option is present, the first line of node_file must have column names.',
                        action='store_true')
    parser.add_argument('-o', '--outfile',
                        help='Full output CSV file name if result output desired.',
                        default=None)
    parser.add_argument('node_file',
                        help='Fully qualified name of file with nodes to overlay onto zip codes',
                        default=None)
    args = parser.parse_args();
    args.columns = [int(col_num) for col_num in args.columns] 
    zipOverlayer = ZipOverlayer(args.node_file,
                                columns=args.columns,
                                delimiter=args.delimiter,
                                firstLineIsColHeader=args.firstLine)
    if args.outfile is not None:
        zipOverlayer.export_converted_input(args.outfile)