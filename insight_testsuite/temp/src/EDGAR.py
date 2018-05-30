import datetime
import os, subprocess
from collections import deque




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
		self.inactivity_period = Stream.inactivity_period
		
		# Defines a basic "Line of data" comprised in a data Block
		self.Accessions = [dict() for i in range(Stream.length) ]
		
		return None

		# Thinking of the whole logfile DB, which goes back to 2003
	def posixTime(self, date, time):
		date_li = date.split('-')
		time_li = time.split(':')
		DT_args = [ int(i) for i in (date_li+time_li) ]

		return datetime.datetime(*DT_args).timestamp()

		# Builds the Raw data for a block defined by length L of records
	def BUILD(self):
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
					Accession_time = self.posixTime(line_List[1],line_List[2])
					an_Accession  = {'userIP': line_List[0],
								  'access_TIME': Accession_time,
								  'file_ID': line_List[5] + line_List[6],
								  'date_time_str': line_List[1]+ ' ' + line_List[2]}
					self.Accessions[i-(self.offset + 1)] = an_Accession 
				else:
					print('\n{0} lines read from input file\n'.format(i-1))
					break
		return self

		
class block_PROCESS(EDGAR_Raw):
	"""Subclasses EDGAR_Raw. Sessionizes a restricted segment
	   of the input log. Identifies and Populates information lists
	   with details about both active and inactive Sessions using 
	   only disconnected subsets of the data. Data subsets are contiguous 
	   in time. Prepares 'Sessions_inactive' data for subsequent 
	   processing and write to output.
	   """

	def __init__(self, Stream):
		super().__init__(Stream)
		self.BUILD()
		self.Sessions = deque()
		self.Sessions_inactive = deque()
		self.Sessions_out = deque()
		self.out_file = Stream.out_file
		return None

	def is_NewSession(self, an_Accession):
		
		"""Identifies if an Accession opens a new Session or belongs 
		   and existing Session. Returns deque location. 
		   session_status =  {'exists': <bool>, 'Sessions Index': <int>}
		   """
		
		session_status =  {'exists': False, 'Sessions Index': -1}
		for i in range(len(self.Sessions)):
			if self.Sessions[i]['userIP'] == an_Accession['userIP']:
				session_status =  {'exists': True, 'Sessions Index': i}
				break
		return session_status
		

	def process_Accession(self, an_Accession, session_status):
		""" Processes the Accession according to 'session_status'. If 
			'session_status' is FALSE, then it creates and appends a new Session. 
			If 'session_status' is TRUE Accession is processed and incorporated
			into an existing Session element.
			"""
		if session_status['exists']:
			idx = session_status['Sessions Index']
			self.Sessions[idx]['access_TIMES'].append(an_Accession['access_TIME'])
			self.Sessions[idx]['file_IDs'].append(an_Accession['file_ID'])
			self.Sessions[idx]['DT_STRs'].append(an_Accession['date_time_str'])
			self.Sessions.rotate(-idx)
			S = self.Sessions.popleft()
			self.Sessions.rotate(idx)
			self.Sessions.append(S)
		else:
			Session_dict = {'userIP': an_Accession['userIP'], 
							'access_TIMES': [an_Accession['access_TIME']], 
							'file_IDs': [an_Accession['file_ID']], 
							'DT_STRs':[an_Accession['date_time_str']]}
			self.Sessions.append(Session_dict)
		return self

	def Update(self, an_Accession):
		""" Tests to see if oldest Session is still active. If so, pops() it
			and moves it to the attribut 'Sessions_inactive'
			"""
		def is_elapsed(self, an_Accession):
			if self.inactivity_period < 0:
				return True
			else: 
				most_recent_time = self.Sessions[0]['access_TIMES'][-1]  # CHECK!!
				current_time = an_Accession['access_TIME']
				return ((current_time - most_recent_time) > self.inactivity_period)
		
		SL_len = len(self.Sessions)
		while (is_elapsed(self, an_Accession) & (SL_len > 0)):
			IA_Sess = self.Sessions.popleft()
			SL_len += -1
			self.Sessions_inactive.append(IA_Sess)
		return self

	def tally(self):
		"""in-situ and post processing of input stream. Handles Accessions
			and detwermines where Accessions go and manages when they expire
			as closed sessions.
			"""
		for i in self.Sessions_inactive:
			session_time = i['access_TIMES'][-1] - i['access_TIMES'][0] + 1  # CHECK! min time resolution? 
			numfiles = len(i['file_IDs'])
			start_DT = i['DT_STRs'][0]
			end_DT = i['DT_STRs'][-1]
			SO_dict = {'userIP': i['userIP'], 'start_DT': start_DT,
						'end_DT': end_DT, 'SESSION_time': session_time,
						'Number_Accessed': numfiles}
			self.Sessions_out.append(SO_dict)

		return self

	def output(self):
		"""Writes only Sessions_out which is a deque([dict()]) that 
			contains the lightly post-processed _Sessions_inactive_
			"""
		if len(self.Sessions_out) > 0:
			with open(self.out_file, 'w') as out:
				column_len = len(self.Sessions_out[0])
				for k in self.Sessions_out:

					idx = 0
					for key, val in k.items():
						idx += 1
						if idx < column_len:
							out.write('{0},'.format(val))
						elif idx == column_len:
							out.write('{0}\n'.format(val))
			out.close()			
		return self

	def sessionize_block(self):
		""" Sessionizes the block (subset) of input data using all Accessions
			obtained from the block of input. If EOF (or similar), then
			inactivity_period is set hard to -1, forcing the rest of the 
			program elements to convert all Sessions to Sessions_inactive,
			and subsequently to Sessions_out for output.
			"""
		idx = 0
		for i in range(len(self.Accessions)):
			idx += 1
			an_Accession = self.Accessions[i]
			session_status = self.is_NewSession(an_Accession)
			self.process_Accession(an_Accession, session_status)
			if idx == self.File_LineCount :
				self.inactivity_period = -1   # all sessions time out at EOS
			self.Update(an_Accession)
		self.tally()
		self.output()
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

	def UT_check_status(self,L=1):
		"""Checks 'is_NewSession(an_Accession)' whether an Accession 
		fits into an existing Session or should open a new Session. 
		Tests repeated applications of 2 'Accessions[0]' and sequential
		application of Accessions[0:L] on fresh instantiations of
		'EDGAR_Raw.Build()'.
		"""
		print('hello from UT_check_status...')
		print('Number of Accessions is {0}'.format(len(self.Accessions)))

		L_Accessions = self.Accessions[0:L]
		print('1st Acession presented to is_NewSession\n')
		print(self.is_NewSession(L_Accessions[0]))
		print('1st Acession presented again to is_NewSession\n')
		print(self.is_NewSession(L_Accessions[0]))
		print('\n Rebuilding block_PROCESS(EDGAR_Raw)...\n ')
		self.__init__(self.Stream)
		L_Accessions = self.Accessions[0:L]
		for i in L_Accessions:
			print(i.items())
			print(self.is_NewSession(i))
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
		self.inactivity_period = int(ia.readline())
		ia.close()
		self.data = open(self.filename)
		self.offset = offset
		
		## Try to get wc -l output from OS
		if (0 == subprocess.check_call(["wc","-l","./input/log.csv"])):
			wc=subprocess.check_output(["wc","-l","./input/log.csv"])
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



