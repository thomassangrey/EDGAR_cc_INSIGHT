This was part of a data challenge for the INSIGHT data engineering internship found here: https://github.com/InsightDataScience/edgar-analytics

This code processes EDGAR log files retrieved from the SEC: https://www.sec.gov/edgar/searchedgar/webusers.htm

From the home directory, exectute ./run.sh

To test the code execute ./insight_testsuite/run_tests.sh 
Some parameters described in USAGE can be modified in the main source file: ./src/sessionization.py

USAGE:
1) Set _length_ of file to read
2) Set _offset_ of 0 means a 1-line header is skipped
3) if _length_ is greater than file than $wc -l ./input/an_input_file.txt
   then _length_ is set to the file length
4) Input files: Can take relative or full path designation of files in the run.sh 
	script
5) Or, just the file name can be given as long as it lives in ./input of top-level

CURRENT STATE of EDGAR project and Scalability:
	1)	The output almost matches the correct output as given in the helper file for
		the small example input. One line is swapped when sessions are rendered inactive by the EOF condition. This is because at the EOF, I pop() active sessions in the order of least recently active. That is, after inactive sessions have timed out during active streaming they are written to the output in the order they time out. When dumping all active sessions at an EOF, oldest active sessions are popped() to the output first, then more recent are popped(), and finally the last, most recent sessions are popped() to the output. 
	
	2)	Two main classes are used: _EDGAR_Raw()_ which is sub-classed by
		_block_PROCESS()_ . _block_PROCESS()_ can be sub-classed by a Bi_UNION class
		which operates on basic deque([dict()]) objects of _block_PROCESS()_ . 
		THe tentative Bi_UNION, will excersise, essentially, the recursive method 
		on BP = Bi_UNION.block_PROCESS(EDGAR):

			merge(merge(BP1, BP2),merge(BP3), merge(BP4)) 

		which conjoins active sessions and whittles them down as the union operation is compounded. 

	3)	The steps in 2) need to be complemented by an efficient socket between nodes, where presumably each BP object is created and merged with a nearby BP.


 I'd like to finish those steps today, but time is running past... fun project!
