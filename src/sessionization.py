# ~/edgar-analytics-SANGREY/src/sessionization.py

import sys
import EDGAR

name = sys.argv[0]
logfile = sys.argv[1]
inact_file = sys.argv[2]
out_file = sys.argv[3]

##  Offset "knows" about 1 line of header content  ##
		        # offset from 1st data line  offset 
offset = 0 		# of 0 is 1st line of data
length = 100     # Number of lines to read


a_Stream = EDGAR.Stream(logfile,inact_file, out_file, offset,length)



ED = EDGAR.block_PROCESS(a_Stream).sessionize_block()

###  Some testing
UT = False
if(UT):
	BP = EDGAR.block_PROCESS(a_Stream).UT_ini(3)
	BP = EDGAR.block_PROCESS(a_Stream).UT_check_status(3)
	BP = EDGAR.block_PROCESS(a_Stream).UT_process_Accession(3)
	BP = EDGAR.block_PROCESS(a_Stream).UT_check_Update(9)
	BP = EDGAR.block_PROCESS(a_Stream).UT_sessionize_block(9)

a_Stream.data.close()

numTasks = 10   # splits load into numTasks for streaming, processing
taskLoad = 10 # number of records to stream and preprocess


print('\n...goodbye...')

