
import os, subprocess
from collections import deque
import base_classes
from typing import Deque



class Stream(object):

	""" Data Stream class with text file argument
		text file is input is 'file_name.csv' and lives in ./input
		"""
	def __init__(self, filename, inactivity_file, out_file,
					offset, length=None):
		
		base_dir = '/'.join(os.getcwd().split('/'))

		if len(filename.split('/')) > 1:
			self.filename =  filename
			self.inactivity_file =  inactivity_file
			self.out_file =  out_file
			print('Data file path is given as:' + filename )
			print('Inactivity file path is given as:' + inactivity_file )
		else:
			self.filename = base_dir + '/input/' + filename
			self.inactivity_file =  base_dir + '/input/' + inactivity_file
		
		ia = open(self.inactivity_file)
		self.Inactivity_Period = float(ia.readline())    ## delta TIME intervals \
														   ## are INCLUSIVE!!!
		ia.close()
		self.data = open(self.filename)
		self.offset = offset
		
		## Try to get wc -l output from OS
		if (0 == subprocess.check_call(["wc","-l","./input/log.csv"])):
			wc = subprocess.check_output(["wc","-l","./input/log.csv"])
			numlines = int(wc.decode().split('.')[0]) - 1
			self.File_LineCount = numlines 
		else:   ### slow for big files
			with open(self.filename) as f:
				self.File_LineCount = len(f.readlines()) - 1
			f.close()

		if (length == None) | (length + offset) > self.File_LineCount:
			self.length = self.File_LineCount
		else:
			self.length = length
	
	
	def __str__(self):
		s1 = 'EDGAR data pulled from: ' + self.filename 
		s2 = " at line number {0:2d}".format(self.offset)
		return s1 + s2 

class an_outputDQ(deque):
	def __init__(self, out_file, a_DQ):
		super().__init__(a_DQ)
		self.out = out_file


	def output(self):
		"""Writes only Sessions_out which is a deque([dict()]) that 
			   contains the lightly post-processed _Sessions_inactive_
		"""
	
		with open(self.out, 'w') as out:
			if len(self) > 0:
				print('printing output..')
				column_len = len(self[0])
				for k in self:

					idx = 0
					for key, val in k.items():
						idx += 1
						if idx < column_len:
							out.write('{0},'.format(val))
						elif idx == column_len:
							out.write('{0}\n'.format(val))

		out.close()			
		return self

	def tally(self):
		"""in-situ and post processing of input stream. Handles Accessions
			and detwermines where Accessions go and manages when they expire
			as closed sessions.
			"""
		prettySESSIONS = deque()	
		for i in self:
			session_time = int(i['posixTime'][-1] - i['posixTime'][0] + 1)  # CHECK! min time resolution? 
			numfiles = len(i.a_FILE[i.a_FILE.file_keystr])
			start_date = i['date'][0]
			end_date = i['date'][-1]
			start_time = i['time'][0]
			end_time = i['time'][-1]
			start = start_date + ' ' + start_time
			end = end_date + ' ' + end_time
			SO_dict = {'userIP': i['userIP'], 'start': start, 'end': end, \
								'SESSION_time': session_time,'numfiles': numfiles}
			prettySESSIONS.append(SO_dict)
	
		return prettySESSIONS 





class EDGAR_Raw(object):
	
	"""EDGAR CC: collects unfiltered subsets of Raw /n delimited EDGAR 
	   records (blocks of size _length_). Data subsets are prepared for 
	   further alternative processing"""

	def __init__(self, Stream):
		# Stream information 
		self.Stream = Stream
		self.Stream.data.seek(0)
		self.Stream_iter = enumerate(self.Stream.data, 0)
		self.length = Stream.length 
		self.offset = Stream.offset
		self.File_LineCount = Stream.File_LineCount
		self.Inactivity_Period = Stream.Inactivity_Period
		
		# Defines a basic "Line of data" comprised in a data Block
		self.Accessions = [dict() for i in range(Stream.length) ]
	



		# Builds the Raw data for a block defined by length L of records
	def BUILD(self, Stream):
		""" Builds the raw data in the form of _Accessions_ of type
			deque([dict()]). Keys are summarized: 
				an_Accession  = {'userIP': <str>,'access_TIME': <float>,
									'file_ID': <str>,'date_time_str': <str>}
			"""
		for i, line in self.Stream_iter:
			start = self.offset + 1
			finish = start + self.length - 1
			if (i >= start):
				if (i <= finish):
					line_List = line.split(',')
					userIP = line_List[0]
					date = line_List[1]
					time = line_List[2]
					CIK = ':' + line_List[4]
					file = line_List[5]
					ext = line_List[6]
					an_Accession  = {'userIP': userIP,
								  'date': date,
								  'time': time,
								  'order': i,
								  'CIK': CIK,
								  'file': file,
								  'ext': ext}
					self.Accessions[i-(self.offset + 1)] = an_Accession 
				else:
					print('\n{0} lines read from input file\n'.format(i-1))
					break
		return self

		
class block_PROCESS(base_classes.SESSIONS):
	"""Subclasses EDGAR_Raw. Sessionizes a restricted segment
	   of the input log. Identifies and Populates information lists
	   with details about both active and inactive Sessions using 
	   only disconnected subsets of the data. Data subsets are contiguous 
	   in time. Prepares 'Sessions_inactive' data for subsequent 
	   processing and write to output.
	   """

	def __init__(self, Stream, BLOCK_params):
		
		raw_BLOCK = EDGAR_Raw(Stream)
		raw_BLOCK.length = BLOCK_params['length']
		raw_BLOCK.offset = BLOCK_params['offset']
		
		super().__init__('userIP',raw_BLOCK.Inactivity_Period)
		
		self.BLOCK_length = raw_BLOCK.length
		self.BLOCK_start = raw_BLOCK.offset
		self.raw_BLOCK = raw_BLOCK.BUILD(Stream)
		self.IA_SESSIONS = base_classes.SESSIONS('userIP', \
									raw_BLOCK.Inactivity_Period)
		self.out_file = Stream.out_file

		return None




	def update(self, IA_SESSIONS, an_Accession):
		""" Tests to see if oldest Session is still active. If so, pops() it
			and moves it to the attribut 'Sessions_inactive'
			"""
		def is_elapsed(self,  an_Accession):
			if len(self) > 0:
				oldest = self[-1].a_DATE_TIME['posixTime'][-1]  # CHECK!!
				current_time = base_classes.posixTime(self,an_Accession['date'], \
									an_Accession['time'])
				
				return ((current_time  - oldest) > self.Inactivity_Period)
			else:
				return False	
		
		def flag_IA_SESSION(self, Inactive_SESSION):
			SESSION_start_time = Inactive_SESSION['posixTime'][-1] 
			BLOCK_start = self.BLOCK_start
			if SESSION_start_time  - BLOCK_start < self.Inactivity_Period:
				return 'SAI'
			else:
				return 'SII'
		
		SESSION_len = len(self)
		print(len(self))
		IA_SESSIONS = deque()
		while ( SESSION_len > 0):
			if is_elapsed(self, an_Accession):
				IA_SESSION = self.pop()
				IA_SESSION.case = flag_IA_SESSION(self, IA_SESSION)
				IA_SESSIONS.append(IA_SESSION)
			else:
				self.rotate(1)
			SESSION_len -= 1


		return IA_SESSIONS

	def sessionize_block(self):
		""" Sessionizes the block (subset) of input data using all Accessions
			obtained from the block of input. If EOF (or similar), then
			inactivity_period is set hard to -1, forcing the rest of the 
			program elements to convert all Sessions to Sessions_inactive,
			and subsequently to Sessions_out for output.
			"""
		
		idx = 0
		for an_Accession in self.raw_BLOCK.Accessions:
			
			idx += 1
			
			user = base_classes.a_USER(userIP = an_Accession['userIP'])
			date_time = base_classes.a_DATE_TIME(date = an_Accession['date'], 
												 time = an_Accession['time'])
			file = base_classes.a_FILE(file = an_Accession['file'], 
									    ext = an_Accession['ext'], 
									    CIK = an_Accession['CIK'])
			userSESSION = base_classes.a_userSESSION(user, date_time, file, order = an_Accession['order'])

			self.append(userSESSION)
			

		return self
	

		

	#######################
	# UNIT TESTS    BEGIN #
	#######################
	def UT_ini(self,L=1):
		"""Checks out Accessions derived from EDGAR_Raw.Build()
			"""
		print('hello from UT_ini...')
		print('Number of Accessions is {0}'.format(len(self.Accessions)))
		L_Accessions = self.Accessions[0:L]
		for i in L_Accessions:
			print(i.items())
		return self

	
		
	def UT_process_Accession(self,L=1):
		"""Checks 'is_NewSession(an_Accession)' whether an Accession 
		fits into an existing Session or should open a new Session. 
		Tests repeated applications of 2 'Accessions[0]' and sequential
		application of Accessions[0:L] on fresh instantiations of
		'EDGAR_Raw.Build()'.
		"""
		print('hello from UT_process_Accession...')
		print('Number of Accessions is {0}'.format(len(self.Accessions)))

		L_Accessions = self.Accessions[0:L]
		print('1st Acession presented to is_NewSession\n')
		print(self.is_NewSession(L_Accessions[0]))
		print('1st Acession presented again to is_NewSession\n')
		print(self.is_NewSession(L_Accessions[0]))
		print('\n Rebuilding block_PROCESS(EDGAR_Raw)...\n ')
		self.__init__(self.Stream)
		L_Accessions = self.Accessions[0:L]
		idx = 0
		for i in L_Accessions:
			idx += 1
			print('\nAccession #{0}\n'.format(idx))
			print(i.items())
			is_NS = self.is_NewSession(i)
			print('\nPrinting the Sessions at current Accession # {0}\n'.format(idx))
			self.process_Accession(i, is_NS)
			idx2 = 0
			for j in self.Sessions:
				idx2 += 1
				print('Session #{0}\n'.format(idx2))
				print(j.items())
				print('\n')
		return self

	def UT_sessionize_block(self,L=1):
		""" Suppressing most output now. Checking whether current time at an 
			Accession instance triggers a session close. Test whether it does so
			correctly and whether it correctly appends to the 'Session_inactive'
			attribute
			"""
		print('hello from UT_sessionize_block...')
		print('Number of Accessions is {0}'.format(len(self.Accessions)))
		print('Start of Accessions in {0} is {1}'.format(self.Stream.filename,
															self.Stream.offset))
		self.sessionize_block()
		print('\nPrinting the Inactive Sessions at End.\n')
		idx1 = 0
		for k in self.Sessions_inactive:
			idx1 += 1
			print('Inactive Session #{0}\n'.format(idx1))
			print(k.items())
			print('\n')
		
		print('\nPrinting the Active Sessions at END\n')
		idx2 = 0
		for k in self.Sessions:
			idx2 += 1
			print('Active Session #{0}\n'.format(idx2))
			print(k.items())
			print('\n')
		print('\nPrinting the Sessions_out at END\n')
		idx3 = 0
		for k in self.Sessions_out:
			idx3 += 1
			print('Session_out #{0}\n'.format(idx3))
			print(k.items())
			print('\n')
		return self

	def UT_check_Update(self,L=1):
		""" Suppressing most output now. Checking whether current time at an 
			Accession instance triggers a session close. Test whether it does so
			correctly and whether it correctly appends to the 'Session_inactive'
			attribute
			"""
		print('hello from UT_process_Accession...')
		print('Number of Accessions is {0}'.format(len(self.Accessions)))
		print('Start of Accessions in {0} is {1}'.format(self.Stream.filename,
															self.Stream.offset))
		L_Accessions = self.Accessions[0:L]
		idx = 0
		for i in L_Accessions:
			idx += 1
			print('\nAccession #{0}\n'.format(idx))
			print(i.items())
			is_NS = self.is_NewSession(i)
			print('\nPrinting the Sessions at current Accession # {0}\n'.format(idx))
			self.process_Accession(i, is_NS)
			idx2 = 0
			for j in self.Sessions:
				idx2 += 1
				print('Session #{0}\n'.format(idx2))
				print(j.items())
				print('\n')	
			
			self.Update(i)
			print('\nPrinting the Inactive Sessions at current Accession # {0}\n'.format(idx))
			idx3 = 0
			for k in self.Sessions_inactive:
				idx3 += 1
				print('Inactive Session #{0}\n'.format(idx3))
				print(k.items())
				print('\n')
		return self

	#######################
	# UNIT TESTS    END   #
	#######################






