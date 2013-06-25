#!/usr/bin/env python
#coding:utf-8
# Author:   
# Purpose: 
# Created: 2013/6/25

import sys
import unittest

########################################################################
class System(object):
    def __init__(self):
        """Constructor"""
        
        
    ########################################################################
    class Windows(System):
        """"""
    
        #----------------------------------------------------------------------
        def __init__(self):
            """Constructor"""
            
        def set_swap(self):
            print '''cscript c:\WINDOWS\system32\pagefileconfig.vbs /Change /m 10240 /i 10240 /vo c:'''
        
        
    

if __name__=='__main__':
    unittest.main()