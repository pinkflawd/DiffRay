'''
Created on 05.09.2013

@author: marschalek.m
'''

from optparse import OptionParser
import Parsing.Library
import Database.MSSqlDB
import os.path

def main():
    parser = OptionParser()
    
    ### Parsing
    parser.add_option("-p", "--parse", dest="filename", help="The file to parse, needs the OS option too")
    parser.add_option("-o", "--os", dest="os", help="OS the Library belongs to, Win7 or Win8")
    
    ### Maintenance
    parser.add_option("-f", "--flushall", action="store_true", dest="flush", help="Flush the Database Scheme")
    parser.add_option("-c", "--create-scheme", action="store_true", dest="createall", help="(Re)Create Database Scheme (same as flushall option)")
    parser.add_option("-u", "--update-sigs", action="store_true", dest="updatesigs", help="Flushes the signature table and re-reads the signatures.conf for update")
        
    
    # TODO add MORE
    # Logging?
    # DB Backend?
    # C or LST?
    
    (options, args) = parser.parse_args()
    
    ### OPTION parse ###
 
    if options.filename is not None and options.os is not None:
        
        lib = Parsing.Library.Library(options.filename, options.os)
        
        if lib is not None:
            # if lib exists - flush functions
            lib.flush_me()
            lib.parse_cfile()
            print "LOG Main - library parsed to DB"
        
        
    ### OPTION parse incomplete ###
    
    elif (options.flush == True or options.createall == True) and options.updatesigs is None:
        print "LOG Main - Options flushall and create-scheme need option --update-sigs or -u !!"
        
        
    ### OPTION recreate, flush or updatesigs ### 
        
    elif options.updatesigs == True:
        
        db = Database.MSSqlDB.MSSqlDB()
        
        if options.flush == True or options.createall == True:
            db.flush_all()
            db.create_scheme()
            
        signatures = []
        
        try:
            sigfile = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'conf', 'signatures.conf'))
        except IOError:
            print "LOG Main - signatures.conf can't be read, check conf directory"
        except:
            print "LOG Main - An error occurred."
        else:  
            for line in sigfile:
                
                # TODO sanitize line
                signatures.append(line.rstrip())
            db.insert_signatures(signatures)
            sigfile.close()
        
        

    else:
        print "LOG Main - Wrong Arguments"
        
if __name__ == '__main__':
    main()
    