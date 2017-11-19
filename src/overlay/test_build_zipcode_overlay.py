'''
Created on Nov 18, 2017

@author: paepcke
'''
import csv
import os
import unittest

from wheel.signatures import assertTrue

from overlay.build_zipcode_overlay import ZipOverlayer


TEST_ALL = True
#TEST_ALL = False

class TestZipOverlayer(unittest.TestCase):

    TEST_FILE_ONE_COL  = os.path.join(os.path.dirname(__file__), 'test_one_col.csv')
    TEST_FILE_TWO_COLS = os.path.join(os.path.dirname(__file__), 'test_two_cols.csv')
    TEST_FILE_TWO_COLS_EXTRA_COLS = os.path.join(os.path.dirname(__file__), 'test_two_cols_extras.csv')
    
    @classmethod
    def setUpClass(cls):
        super(TestZipOverlayer, cls).setUpClass()
        cls.build_test_files()
        outfile = os.path.join(os.path.dirname(__file__), 'output_test.csv')
        # Ensure test outfile doesn't exist
        try:
            os.remove(outfile)
        except OSError:
            pass
        
        
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.outfile = os.path.join(os.path.dirname(__file__), 'output_test.csv')
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        # Ensure test outfile doesn't exist
        try:
            os.remove(self.outfile)
        except OSError:
            pass

    #-----------------------------
    # test_one_col 
    #-----------------------    

    @unittest.skipIf(not TEST_ALL, "Temporarily disabled")
    def test_one_col(self):
        overlayer = ZipOverlayer(TestZipOverlayer.TEST_FILE_ONE_COL)
        node1_zip = overlayer['node1']
        self.assertTrue(self.is_zip(node1_zip))
        
        # Make sure the next row was computed too:
        node2_zip = overlayer['node2']
        self.assertTrue(self.is_zip(node2_zip))        

    #-----------------------------
    # test_inversion
    #-----------------------    

    @unittest.skipIf(not TEST_ALL, "Temporarily disabled")
    def test_inversion(self):
        overlayer = ZipOverlayer(TestZipOverlayer.TEST_FILE_ONE_COL)
        node1_zip = overlayer['node1']
        
        # Get a reverser, and ensure that
        # node(zip) == origin-node: 
        reverse_overlayer = overlayer.get_overlay_reverser()
        self.assertEqual(reverse_overlayer[node1_zip],'node1')
        
    #-----------------------------
    # test_multi_cols
    #-----------------------    

    @unittest.skipIf(not TEST_ALL, "Temporarily disabled")
    def test_multi_cols(self):
        overlayer = ZipOverlayer(TestZipOverlayer.TEST_FILE_TWO_COLS, columns=[0,1])
        node1_zip = overlayer['node1']
        assertTrue(self.is_zip(node1_zip))
        
        node2_zip = overlayer['node2']
        assertTrue(self.is_zip(node2_zip))
        
        node3_zip = overlayer['node3']
        assertTrue(self.is_zip(node3_zip))
        
        node4_zip = overlayer['node4']
        assertTrue(self.is_zip(node4_zip))

    #-----------------------------
    # test_multi_cols_extra_info 
    #-----------------------    

    @unittest.skipIf(not TEST_ALL, "Temporarily disabled")
    def test_multi_cols_extra_info(self):
        overlayer = ZipOverlayer(TestZipOverlayer.TEST_FILE_TWO_COLS_EXTRA_COLS, columns=[0,2])
        node1_zip = overlayer['node1']
        assertTrue(self.is_zip(node1_zip))
        
        node2_zip = overlayer['node2']
        assertTrue(self.is_zip(node2_zip))
        
        node3_zip = overlayer['node3']
        assertTrue(self.is_zip(node3_zip))
        
        node4_zip = overlayer['node4']
        assertTrue(self.is_zip(node4_zip))
        
        # There should be no others:
        self.assertEqual(len(overlayer), 4)
    
    #-----------------------------
    # test_export_extra_info
    #-----------------------    

    @unittest.skipIf(not TEST_ALL, "Temporarily disabled")
    def test_export_extra_info(self):
        '''
        Input will be:
        
        'node1,Extra,node2'
        'node3,Extra,node4'
        'node1,Extra,node4'
        
        So output must be:
        'zip1,Extra,zip2'
        'zip3,Extra,zip4'
        'zip1,Extra,zip4'
        
        '''
        
        
        overlayer = ZipOverlayer(TestZipOverlayer.TEST_FILE_TWO_COLS_EXTRA_COLS, columns=[0,2])
        overlayer.export_converted_input(self.outfile)
        
        with open(self.outfile, 'r') as source_fd:
            nodes_file_reader = csv.reader(source_fd,
                                           delimiter=',',
                                           quotechar='"')
            exported_line = nodes_file_reader.next()
            self.assertEqual(exported_line[1], 'Extra')
            self.assertTrue(self.is_zip(exported_line[0]))
            self.assertTrue(self.is_zip(exported_line[2]))
            zip1 = exported_line[0]
            
            exported_line = nodes_file_reader.next()
            self.assertEqual(exported_line[1], 'Extra')
            self.assertTrue(self.is_zip(exported_line[0]))
            self.assertTrue(self.is_zip(exported_line[2]))
            zip4 = exported_line[2]
            
            exported_line = nodes_file_reader.next()
            self.assertEqual(exported_line[1], 'Extra')
            self.assertEqual(exported_line[0], zip1)
            self.assertEqual(exported_line[2], zip4)
    
    #-----------------------------
    # test_export_two_cols 
    #-----------------------    
    
    @unittest.skipIf(not TEST_ALL, "Temporarily disabled")
    def test_export_two_cols(self):
        '''
        Input will be:
        
        'node1,node2'
        'node3,node4'
        'node1,node4'
        
        So output must be:
        'zip1,zip2'
        'zip3,zip4'
        'zip1,zip4'
        
        '''
        
        overlayer = ZipOverlayer(TestZipOverlayer.TEST_FILE_TWO_COLS, columns=[0,1])
        overlayer.export_converted_input(self.outfile)
        
        with open(self.outfile, 'r') as source_fd:
            nodes_file_reader = csv.reader(source_fd,
                                           delimiter=',',
                                           quotechar='"')
            exported_line = nodes_file_reader.next()
            self.assertTrue(self.is_zip(exported_line[0]))
            self.assertTrue(self.is_zip(exported_line[1]))
            zip1 = exported_line[0]
            
            exported_line = nodes_file_reader.next()
            self.assertTrue(self.is_zip(exported_line[0]))
            self.assertTrue(self.is_zip(exported_line[1]))
            zip4 = exported_line[1]
            
            exported_line = nodes_file_reader.next()
            self.assertEqual(exported_line[0], zip1)
            self.assertEqual(exported_line[1], zip4)

    #-----------------------------
    # test_export_one_col 
    #-----------------------    
    
    @unittest.skipIf(not TEST_ALL, "Temporarily disabled")
    def test_export_one_col(self):
        '''
        Input will be:
        
        'node1'
        'node2'
        'node3'
        
        So output must be:
        'zip1'
        'zip2'
        'zip3'
        
        '''
        
        overlayer = ZipOverlayer(TestZipOverlayer.TEST_FILE_TWO_COLS)
        overlayer.export_converted_input(self.outfile)
        
        with open(self.outfile, 'r') as source_fd:
            nodes_file_reader = csv.reader(source_fd,
                                           delimiter=',',
                                           quotechar='"')
            exported_line = nodes_file_reader.next()
            self.assertTrue(self.is_zip(exported_line[0]))

            exported_line = nodes_file_reader.next()
            self.assertTrue(self.is_zip(exported_line[0]))
            
            exported_line = nodes_file_reader.next()
            self.assertTrue(self.is_zip(exported_line[0]))

    #-----------------------------
    # test_bad_cols_spec 
    #-----------------------    

    @unittest.skipIf(not TEST_ALL, "Temporarily disabled")
    def test_bad_cols_spec(self):
        try:
            ZipOverlayer(TestZipOverlayer.TEST_FILE_TWO_COLS, columns=[0,5])
            self.fail("Should have ValueError for bad columns")
        except ValueError:
            pass
        
    
    # ------------------ Utilities --------------------

    #-----------------------------
    # build_test_files 
    #-----------------------    

    @classmethod
    def build_test_files(cls):
        with open(cls.TEST_FILE_ONE_COL, 'w') as fd:
            fd.write('node1\n')
            fd.write('node2\n')
            fd.write('node3\n')
            
        with open(cls.TEST_FILE_TWO_COLS, 'w') as fd:
            fd.write('node1,node2\n')
            fd.write('node3,node4\n')
            fd.write('node1,node4\n')

        with open(cls.TEST_FILE_TWO_COLS_EXTRA_COLS, 'w') as fd:
            fd.write('node1,Extra,node2\n')
            fd.write('node3,Extra,node4\n')
            fd.write('node1,Extra,node4\n')
            
    #-----------------------------
    # is_zip 
    #-----------------------    
            
    def is_zip(self, maybe_zip):
        try:
            int(maybe_zip)
        except ValueError:
            self.fail('Zip code %s is not an integer string.' % str(maybe_zip))
        self.assertTrue(len(maybe_zip) == 5)
        return True

        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()