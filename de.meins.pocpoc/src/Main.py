'''
Created on 05.09.2013

@author: pinkflawd
'''

from optparse import OptionParser
import Parsing.Library
#import Database.MSSqlDB
import Database.SQLiteDB
import sys
import logging.config
import re
import os

def main():
    
    '''
    MAIN CLASS
    command line option parsing
    exception catching
    '''
    
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
    parser.add_option("-d", "--dirparse", dest="directory", help="The directory which contains EITHER c or lst files for ONE os! Needs OS and type option.")
    parser.add_option("-p", "--parse", dest="filename", help="The file to parse, needs the OS option and the type option too")
    parser.add_option("-o", "--os", dest="os", help="OS the Library belongs to, Win7 or Win8")
    parser.add_option("-t", "--type", dest="ftype", help="Type of file to parse - .c or .lst")
    
    ### Maintenance
    parser.add_option("-f", "--flushall", action="store_true", dest="flush", help="Flush the Database Scheme")
    parser.add_option("-c", "--create-scheme", action="store_true", dest="createall", help="(Re)Create Database Scheme (same as flushall option)")
    parser.add_option("-u", "--update-sigs", action="store_true", dest="updatesigs", help="Flushes the signature table and re-reads the signatures.conf for update")
        
    
    # TODO add MORE
    # DB Backend?
    
    (options, args) = parser.parse_args()
    
    ### OPTION parse ###
 
    if (options.filename is not None or options.directory is not None) and options.os is not None and options.ftype is not None:
        
        try:
            
            lib_files = []
            
            if options.directory is not None:
                lib_files = [os.path.join(options.directory, f) for f in os.listdir(options.directory) if os.path.isfile(os.path.join(options.directory,f))]
            else:
                lib_files.append(options.filename)
                
            for lib_file in lib_files:        
                lib = Parsing.Library.Library(lib_file, options.os, options.ftype)
                
                # if lib exists - flush functions
                lib.flush_me()
                
                if options.ftype == "c" or options.ftype == "C":
                    lib.parse_cfile()
                elif options.ftype == "lst" or options.ftype == "LST":
                    lib.parse_lstfile()
                else:
                    log.error("Wrong file type! Either c or C or lst or LST, pleeease dont mix caps with small letters, dont have all day for op parsing ;)")
                
                log.info("Finished Parsing")

        except:
            log.error("Something went wrong when parsing a library: %s" % (sys.exc_info()[1]))
        
        
    ### OPTION recreate or flush incomplete ###
    
    elif (options.flush == True or options.createall == True) and options.updatesigs is None:
        log.error("Options flushall and create-scheme need option --update-sigs or -u !!")
        
        
    ### OPTION recreate, flush or updatesigs ### 
        
    elif options.updatesigs == True:
        
        try:
            # !!! TEST !!!
            # db = Database.MSSqlDB.MSSqlDB()
            
            db = Database.SQLiteDB.SQLiteDB()
             
            if options.flush == True or options.createall == True:
                db.flush_all()
                db.create_scheme()
                
            signatures = []
            
            try:
                sigfile = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'conf', 'signatures.conf'))
                
            except:
                log.error("Something went wrong when reading signature file.")
            else:  
                for line in sigfile:
                    #sanitizing the signatures
                    sig = re.sub('\'','', line.rstrip(),0)
                    signatures.append(sig)
                db.insert_signatures(signatures)
                sigfile.close()
        
        except:
            log.error("Something went wrong when updating the signatures in DB.")
        
    else:
        log.error("Wrong Arguments - type -h or --help for Info")
        
if __name__ == '__main__':
    main()
    