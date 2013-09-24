'''
Created on 05.09.2013

@author: marschalek.m
'''

from optparse import OptionParser
import Parsing.Library
import Database.MSSqlDB
import os.path
import sys
import logging.config

def main():
    
    try:
        logging.config.fileConfig(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'conf', 'logger.conf'))
        log = logging.getLogger('Main')
    except:
        # here could go some configuration of a default logger -- me too lazy
        # additionally one could add a cmdline option for loggint to a file instead of stdout -- me too lazy
        print "Error, logger.conf not found or broken. Check on http://docs.python.org/2/howto/logging.html what to do."
        exit(1)
    
    parser = OptionParser()
       
    ### Parsing
    parser.add_option("-p", "--parse", dest="filename", help="The file to parse, needs the OS option and the type option too")
    parser.add_option("-o", "--os", dest="os", help="OS the Library belongs to, Win7 or Win8")
    #TODO parse lst
    parser.add_option("-t", "--type", dest="type", help="Type of file to parse - .c or .lst")
    
    ### Maintenance
    parser.add_option("-f", "--flushall", action="store_true", dest="flush", help="Flush the Database Scheme")
    parser.add_option("-c", "--create-scheme", action="store_true", dest="createall", help="(Re)Create Database Scheme (same as flushall option)")
    parser.add_option("-u", "--update-sigs", action="store_true", dest="updatesigs", help="Flushes the signature table and re-reads the signatures.conf for update")
        
    
    # TODO add MORE
    # DB Backend?
    # C or LST?
    
    (options, args) = parser.parse_args()
    
    ### OPTION parse ###
 
    if options.filename is not None and options.os is not None:
        
        try:
            
            lib = Parsing.Library.Library(options.filename, options.os)
            
            # if lib exists - flush functions
            lib.flush_me()
            lib.parse_cfile()
            log.info("Finished Parsing")

        except:
            print sys.exc_info()[1]
            #log.error("An Error occurred: ", sys.exc_info()[1])
        
        
    ### OPTION parse incomplete ###
    
    elif (options.flush == True or options.createall == True) and options.updatesigs is None:
        log.error("Options flushall and create-scheme need option --update-sigs or -u !!")
        
        
    ### OPTION recreate, flush or updatesigs ### 
        
    elif options.updatesigs == True:
        
        try:
        
            db = Database.MSSqlDB.MSSqlDB()
            
            if options.flush == True or options.createall == True:
                db.flush_all()
                db.create_scheme()
                
            signatures = []
            
            try:
                sigfile = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'conf', 'signatures.conf'))
            except IOError:
                log.error("Signatures.conf can't be read, check conf directory")
            except:
                log.error("An error occurred: ", sys.exc_info[1])
            else:  
                for line in sigfile:
                    
                    # TODO sanitize line
                    signatures.append(line.rstrip())
                db.insert_signatures(signatures)
                sigfile.close()
        
        except:
            log.error("An Error occurred: ", sys.exc_info()[1])
        

    else:
        log.error("Wrong Arguments - type -h or --help for Info")
        
if __name__ == '__main__':
    main()
    