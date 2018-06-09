import datetime
# import os, subprocess
import copy
from typing import List, Deque, Dict
from collections import deque

def join(self, DQ2):
		
	DQ2_Li = list(DQ2)
	for i in DQ2_Li:
		self.append(i)
	return self

def posixTime(self, date, time):
		date_li = date.split('-')
		time_li = time.split(':')
		DT_args = [ int(i) for i in (date_li+time_li) ]

		return datetime.datetime(*DT_args).timestamp()


class a_USER(dict):
	""" Consumeable class to be used to build a_SESSION instance.
		In this case, a {key: <str>} with fixed keystr and append()"""
	def __init__(self, **kwds):
		self.keystr = tuple(kwds)[0]
		if len(kwds) == 1 & isinstance(kwds.get(tuple(kwds)[0],False), str):
			super().__init__(kwds)
		else:
			print('a_USER requires a single key-val')
			print('pair with <str> value type\n')
			# throw error HERE
			pass

class a_DATE_TIME(dict):
	""" Consumeable class to be used to build a_SESSION instance.
		In this case, a {key: List(<str>)]} with fixed keystr and append()
		that only grows the list until two elements of [date_time] exist.
		If two elements exist already, the last element is always replaced.
		This way date_time only contains the first and date_time strings
		for the session; intermediate date_time strings are of no interest.

		Usage:
			DT_instance = a_DATE_TIME(a_date_key = 'YYYY-MM-DD', 
									  a_time_key = 'hh:mm:ss' )
			
			another_DT_instance = 
					D_instance.append( a_date_key = 'YYYY-MM-DD', 
									  a_time_key = 'hh:mm:ss' )
			another_DT_instance = 
					D_instance.append( DT_instance )
			"""
	def __init__(self, **kwds):

		if (len(kwds) >= 2):
			self.posix_keystr = 'posixTime'
			self.datekeystr = tuple(kwds)[0]
			self.timekeystr = tuple(kwds)[1]
			date_is_str = isinstance(kwds.get(self.datekeystr,False), str)
			time_is_str = isinstance(kwds.get(self.timekeystr,False), str)
			posix_is_List = isinstance(kwds.get(self.posix_keystr,False), List)

		if (len(kwds) == 2):
			
			if ( date_is_str & time_is_str ):
				# sets up the builtin type
				super().__init__(**kwds)
				for key, val in self.items():
					self[key] = [val]
				posix_t = posixTime(self, kwds.get(self.datekeystr,False),
									kwds.get(self.timekeystr,False))
				self.update(posixTime = [posix_t])
			else:
				print('a_date_time requires two key-val')
				print('pairs with <str> value types.\n')

		elif (len(kwds) == 3)  & posix_is_List:
		# sets up the builtin type
			super().__init__(**kwds)
		else:
			print('a_date_time requires two key-val')
			print('pairs with <str> value types.\n')
			pass
				# throw ERROR here

	def check_keystrings(self,kwds):
		""" keystrings between self and argument being appended
			must agree
			"""
		checkdatekey = (self.datekeystr == kwds.datekeystr)
		checktimekey = (self.timekeystr == kwds.timekeystr)
		if checkdatekey & checktimekey:
			return	True

	def sub_append(self, datekeystr, timekeystr, date, time):
		if len(self[datekeystr]) <= 1:
			self[datekeystr].append(date)
		else:
			self[datekeystr][-1] = date
		if len(self[timekeystr]) <= 1:
			self[timekeystr].append(time)
		else:
			self[timekeystr][-1] = time
		posix_t = posixTime(self, date, time)		
		self[self.posix_keystr].append(posix_t)	

	def append(self, *nargs, **kwds):

		datekeystr = self.datekeystr
		timekeystr = self.timekeystr	
		if len(nargs) == 1:
			if isinstance(nargs[0], type(self)):
				kwds = nargs[0]
						
				if self.check_keystrings(kwds):
					len_time = len(kwds[timekeystr])
					for i in range(len_time):
						date = kwds[datekeystr][i]
						time = kwds[timekeystr][i]
						self.sub_append( datekeystr, timekeystr, date, time)
				else:
					## throw key ERROR HERE
					pass
			elif isinstance(nargs[0], Dict):
					#	handles direct Dict() argument 
				kwds = nargs[0]
				self.append(a_DATE_TIME(**kwds))
			else:
				## throw invalid arg input HERE
				pass

		else:
				# handles direct keyword args
			self.append(a_DATE_TIME(**kwds))

		

class a_FILE(dict):
	""" Consumeable class to be used to build a_SESSION instance.
		In this case, a {key: List(<str>)]} with fixed keystr and append()
		that only grows the list until two elements of [date_time] exist.
		If two elements exist already, the last element is always replaced.
		This way date_time only contains the first and date_time strings
		for the session; intermediate date_time strings are of no interest."""
	def __init__(self, **kwds):

		

		self.file_keystr = tuple(kwds)[0]
		self.Inactivity_Period = None
		file_ID_is_List = isinstance(kwds.get(self.file_keystr,
												False), List)

		if len(tuple(kwds)) == 3:
			ext_keystr = tuple(kwds)[1]
			CID_keystr = tuple(kwds)[2]
			file_is_str = isinstance(kwds.get(self.file_keystr,False), str)
			ext_is_str = isinstance(kwds.get(ext_keystr,False), str)
			CID_is_str = isinstance(kwds.get(CID_keystr,False), str)
			if  ( file_is_str & ext_is_str & CID_is_str ):
				# sets up the builtin type
				file_ID = ''
				for key, val in kwds.items():
					file_ID = file_ID + val
				file = {self.file_keystr: [file_ID]}
				super().__init__(**file)
		elif (len(kwds) == 1)  & file_ID_is_List:
			# sets up the builtin type
			super().__init__(**kwds)
		
		else:
			print('a_File requires three key-val')
			print('pairs (file, ext, and CID) with')
			print('<str> value type.\n')
			# throw ERROR here
			pass

	def check_keystrings(self,kwds):
		""" keystrings between self and argument being appended
			must agree
			"""
		checkfilekey = (self.file_keystr == kwds.file_keystr)
		if checkfilekey:
			return	True

	def append(self, *nargs, **kwds):
		file_keystr = self.file_keystr
		if len(nargs) == 1:
			kwds = nargs[0]
			if isinstance(nargs[0], type(self)):
				if self.check_keystrings(kwds):
					len_files = len(kwds[file_keystr]) 
					for i in range(len_files):
						file = kwds[file_keystr][i]
						self[file_keystr].append( file)
				else:
					## throw key ERROR HERE
					pass
			elif isinstance(nargs[0], Dict):
						#	handles direct Dict() argument
				self.append(a_FILE(**kwds))
			else:
				## throw invalid arg input HERE
				pass
		else:
				# handles direct keyword args
			self.append(a_FILE(**kwds))








class a_userSESSION(dict):
	""" a_userSESSION - <Dict>. builds the record from consumeable classes
		a_USER, a_DATE_TIME, a_FILE, and possible others. a_userSESSION
		instance initializes an indivual session and determines the behavior 
		of append. Behavior of a_userSESSION is influenced by its superclasses
		in an independent manner (default). Interaction between superclass
		objects like a_USER, a_DATE_TIME, and a_FILE can be coded within
		a_userSESSION."""


	def __init__(self, user, datetime, file, **kwds):
		
		

		# if isUSER & isDATETIME & isFILE:
		# datetime_copy = copy.deepcopy(datetime)
		# file_copy = copy.deepcopy(file)
		super().__init__()
		self.a_USER = user
		self.a_FILE = file
		self.a_DATE_TIME = datetime
		self.update(user)
		self.update(file)
		self.update(datetime)

		self.case = ''
		for key, val in kwds.items():
		 	self[key] = [val]

	
	def append(self, user, datetime, file, **kwds):
		# datetime_copy = copy.deepcopy(datetime)
		# file_copy = copy.deepcopy(file)

		if self.a_USER[self.a_USER.keystr] == user[self.a_USER.keystr]:
			
			self.a_DATE_TIME.append(datetime)
			self.a_FILE.append(file)
			self.update(user)
			self.update(file)
			self.update(datetime)
			for key, val in kwds.items():
			 	self[key].append(val)
		else:
			print('\n userID mismatch...')
			



class SESSIONS(deque):
	"""subclasses deque and has the following syntax expectations:
		1)	a_SESSIONS = SESSIONS()
			>>> deque([{}])
			Constructs a deque of dict objects where the lefmost iterates SESSIONS[0] are 
			he oldest sessions, and the rightmost iterates, SESSIONS[-1]] are the newest
			sessions.
		2)	Implementation first checks if val1 already exists in any SESSIONS iterate. If 
			iterate position P already contains 'key1': val1, SESSIONS[P] is updated in the 
			following manner:
				key1, val1 pair is preserved and all others are appended as below:
				
				SESSIONS[P] = {'key1': val1, 'key2': list2.append(val2), 
							   'key3': list3.append(val3),'key_N':,listN.append(val_N) }
				SESSIONS[P] is then popped and right appended as SESSIONS[-1]

		4)	If val1 does not exist in any iterate of SESSIONS, a new iterate is created as:

				SESSIONS[0] = {'key1': val1, 'key2': [].append(val2), 
							   'key3': []].append(val3),'key_N':,[].append(val_N) }
		5)	[optional] provide a suitable way to flag any key for appending only unique 
			values to its corresponding val list.
		6)	Add an additional key: val pair called Accession index. It refers to the global
			value of the accession number of the session's 1st web accession. Loosely speaking,
			it is the line number of the file wherein the session's 1st accession record was
			pulled. If the file or stream is chopped into blocks for scalable processing, this
			line number must be preserved for later SESSIONS merging tasks.
		7)	A SESSIONS object can be be merged with another SESSIONS object. Rules for merging
			SESSIONS1 and SESSIONS2 first require that each cover non-overlapping time ranges.
			These are referred to as BLOCKS of the input stream. The rules for merging SESSIONS
			are:
				
				1)	Assume SESSIONS1 is older than SESSIONS2. SESSIONS iterates SESSIONS1[P] 
					and SESSIONS2[Q] may be merged if their key1 values (userIP) agree.
				
				2)	if key4 represents accession time, then:
					SESSIONS2[P]['key4'][0] - SESSIONS2[Q]['key4'][-1] > inactivity_period
				
				3) 	Merging looks like:
							SESSIONS1[P]['keyN'].append(SESSIONS2[Q]['keyN'])
					Further clarification of SESSIONS is required to properly organize each
					merged pair in the proper deque order and for determining whethe a merged 
					section is established as inactive.
				
				4)	Some SESSIONS are begun within at least one inactivity period of the time 
					boundary of each BLOCK. This means that a SESSION could be carried over to 
					or from a neighboring BLOCK. After processing a block of accessions, and 
					prior to each stage of a merge operation, SESSIONS must be identified 
					according time from a BLOCKS beginning or end as measured from the 
					left and right SESSION iterate's boundary. The SESSION iterates can be 
					classified as: 
							1) left inactive, right active (SIA)
							2) left inactive, right inactive (process and save to file) (SII)
							3) left active, right inactive (SAI)
							4) left active, right active (SAA)
				
				5)	Finally, merging is always done upon pairs of SESSIONS, from contiguous
					BLOCKS. After merging, each pair {S_left, S_right} must have activity classification as 
					either {S_left, S_right} -> {{1, 3} or {1, 4}}. That is:
							{S_left, S_right} -> {{SIA, SAI} or {SIA, SAA}}
				
				6)	During SESSIONS creation on a BLOCK by BLOCK basis, all SESSIONS[P] that
					satisfy condition 4) are set aside in a special SESSIONS called SAA. 
					During subsequent pairwise merging, all merged SESSIONS that contain at 
					least one candidate merge dyad {S_left, S_right} -> {{SIA, SAA}} 

		"""

#class SESSIONS(deque):		
	def __init__(self, *nargs ):
		
		def error_msg():
			s1 = 'Sessions must be initialized with a string argument representing'
			s2 = 'the key field for unique users. A good example is "userIP"'
			s3 = 'SESSIONS also requires <float> Inactivity_Period.'
			s4 = 'SESSIONS may be initialized with a SESSIONS object of a deque() object '
			s5 = 'containing, at least, elements of a_userSESSION()'
			
			print('\n{0}\n{1}\n{2}\n{3}\n{4}'.format(s1, s2, s3, s4, s5))

		if (len(nargs) == 2):
			is_ID_keystr = isinstance(nargs[0], str)
			is_Inactivity_Period = isinstance(nargs[1], float)
			if is_ID_keystr & is_Inactivity_Period:
				super().__init__()
				self.ID_keystr = nargs[0]
				self.Inactivity_Period = nargs[1]
			else:
				error_msg()
		elif (len(nargs) == 1) & isinstance(nargs[0],Deque):
			super().__init__(nargs[0])
			self.ID_keystr =  tuple(nargs[0][0])[0]
			self.Inactivity_Period = nargs[0][0].a_FILE.Inactivity_Period
		else:
			error_msg()



	def Inactivity_Test(self,S, user_session):
		elapsed =  user_session.a_DATE_TIME[user_session.a_DATE_TIME.posix_keystr][-1] - \
					S.a_DATE_TIME[S.a_DATE_TIME.posix_keystr][-1]
				
		if elapsed > self.Inactivity_Period:
			return True
		else:
			return False

	def append(self,user_session):
		# user_session = copy.deepcopy(user_sess)
		ID_key = self.ID_keystr
		the_user = user_session.a_USER.get(ID_key,False)
		if(the_user):
			if len(self):
				found_key = False
				idx = -1
				for S in self:
					
					idx += 1
					user_test = S.get(ID_key, False) == the_user
					expired = self.Inactivity_Test(S, user_session)
					# print('\nexpired = {0}'.format(expired))
					if  user_test  & (not expired) & (not found_key):
						found_key = True
						S.a_DATE_TIME.append(user_session.a_DATE_TIME)
						S.a_FILE.append(user_session.a_FILE)
						S.a_FILE.Inactivity_Period = self.Inactivity_Period
						S['order'].append(user_session['order'][0])
						# user_session = copy.deepcopy(user_sess)
						if idx > 0:
							super().rotate(-idx)
							super().popleft()	
							super().rotate(idx)
							super().appendleft(S)
						break
				if not(found_key):
					super().appendleft(user_session)
			else:
				super().appendleft(user_session)
		else:
			print('\n{0}\n{1}{2}. \n{3}'.\
				format('Sessions is previously initialized with ',
						'the key field for unique users called:  ',
						'self.ID_keystr, But no such key was found \
						in last key-val assignment.'))
			pass


	def EOSdump(self):
		idx = 0
		for i in range(len(self)):
			idx +=1
			jdx = 0
			for j in range(len(self)):
				jdx +=1
				if self[i]['order'][0] < \
					self[j]['order'][0]:
				# if self[i].a_DATE_TIME['posixTime'][0] < \
				# 	self[j].a_DATE_TIME['posixTime'][0]:
						self.rotate(-i)
						i_temp = self.popleft()
						self.rotate(i-j)
						j_temp = self.popleft()
						self.appendleft(i_temp)
						self.rotate(j-i)
						self.appendleft(j_temp)
						self.rotate(i)
				print(self[j]['order'][0])		
						
		return self











# class a_SESSION(dict):
# 	"""ACCESSION - Needs the record ID keyname. i.e. "userID"
# 		"""
# 	def __init__(self,  ID_keystr, **kwds):
		
# 		super().__init__(**kwds)
# 		self.ID_keystr=ID_keystr
# 		self.case = None
# 		if len(kwds) > 0:
# 			val = kwds.get(ID_keystr, False)
# 			if val == False:
# 				s0 = 'key-word argument to a_SESSION does not include\n'
# 				s1 = 'a valid key representing a unique userID'
# 				print('\n{0} {1}\n'.format(s0,s1))
# 			else:
# 				self[ID_keystr] = val
# 				print('\na_SESSION: last else: self[ID_keystr] = {0}\n'.format(self[ID_keystr]))
# 				kwds.pop(ID_keystr)
# 				for key, val in kwds.items():
# 			 		self[key] = [val]
# 			 		print('aSESSION: key,val: self[key] = [val] is: {0}\n'.format(self[key]))
					

# class SESSIONS(deque):
# 	"""subclasses deque and has the following syntax expectations:
# 		1)	a_SESSIONS = SESSIONS()
# 			>>> deque([{}])
# 			Constructs a deque of dict objects where the lefmost iterates SESSIONS[0] are 
# 			he oldest sessions, and the rightmost iterates, SESSIONS[-1]] are the newest
# 			sessions.
# 		2)	Implementation first checks if val1 already exists in any SESSIONS iterate. If 
# 			iterate position P already contains 'key1': val1, SESSIONS[P] is updated in the 
# 			following manner:
# 				key1, val1 pair is preserved and all others are appended as below:
				
# 				SESSIONS[P] = {'key1': val1, 'key2': list2.append(val2), 
# 							   'key3': list3.append(val3),'key_N':,listN.append(val_N) }
# 				SESSIONS[P] is then popped and right appended as SESSIONS[-1]

# 		4)	If val1 does not exist in any iterate of SESSIONS, a new iterate is created as:

# 				SESSIONS[0] = {'key1': val1, 'key2': [].append(val2), 
# 							   'key3': []].append(val3),'key_N':,[].append(val_N) }
# 		5)	[optional] provide a suitable way to flag any key for appending only unique 
# 			values to its corresponding val list.
# 		6)	Add an additional key: val pair called Accession index. It refers to the global
# 			value of the accession number of the session's 1st web accession. Loosely speaking,
# 			it is the line number of the file wherein the session's 1st accession record was
# 			pulled. If the file or stream is chopped into blocks for scalable processing, this
# 			line number must be preserved for later SESSIONS merging tasks.
# 		7)	A SESSIONS object can be be merged with another SESSIONS object. Rules for merging
# 			SESSIONS1 and SESSIONS2 first require that each cover non-overlapping time ranges.
# 			These are referred to as BLOCKS of the input stream. The rules for merging SESSIONS
# 			are:
				
# 				1)	Assume SESSIONS1 is older than SESSIONS2. SESSIONS iterates SESSIONS1[P] 
# 					and SESSIONS2[Q] may be merged if their key1 values (userIP) agree.
				
# 				2)	if key4 represents accession time, then:
# 					SESSIONS2[P]['key4'][0] - SESSIONS2[Q]['key4'][-1] > inactivity_period
				
# 				3) 	Merging looks like:
# 							SESSIONS1[P]['keyN'].append(SESSIONS2[Q]['keyN'])
# 					Further clarification of SESSIONS is required to properly organize each
# 					merged pair in the proper deque order and for determining whethe a merged 
# 					section is established as inactive.
				
# 				4)	Some SESSIONS are begun within at least one inactivity period of the time 
# 					boundary of each BLOCK. This means that a SESSION could be carried over to 
# 					or from a neighboring BLOCK. After processing a block of accessions, and 
# 					prior to each stage of a merge operation, SESSIONS must be identified 
# 					according time from a BLOCKS beginning or end as measured from the 
# 					left and right SESSION iterate's boundary. The SESSION iterates can be 
# 					classified as: 
# 							1) left inactive, right active (SIA)
# 							2) left inactive, right inactive (process and save to file) (SII)
# 							3) left active, right inactive (SAI)
# 							4) left active, right active (SAA)
				
# 				5)	Finally, merging is always done upon pairs of SESSIONS, from contiguous
# 					BLOCKS. After merging, each pair {S_left, S_right} must have activity classification as 
# 					either {S_left, S_right} -> {{1, 3} or {1, 4}}. That is:
# 							{S_left, S_right} -> {{SIA, SAI} or {SIA, SAA}}
				
# 				6)	During SESSIONS creation on a BLOCK by BLOCK basis, all SESSIONS[P] that
# 					satisfy condition 4) are set aside in a special SESSIONS called SAA. 
# 					During subsequent pairwise merging, all merged SESSIONS that contain at 
# 					least one candidate merge dyad {S_left, S_right} -> {{SIA, SAA}} 

# 		"""

# #class SESSIONS(deque):		
# 	def __init__(self, *nargs ):
# 		super().__init__()
# 		if len(nargs) == 1 & isinstance(nargs[0], str):
# 			super().__init__()
# 			self.ID_keystr = nargs[0]
# 		else:
# 			print('\n{0}\n{1}\n{2}\n{3}\n'.format('Sessions must be initialized with a',
# 												'single string arguement representing',
# 												'the key field for unique users.',
# 												'A good example is "userIP"'))
# 			pass

# 	def append(self,**kwargs):		
# 		ID_key = self.ID_keystr
# 		the_user = kwargs.get(ID_key,False)
# 		print('\nSESSIONS:append():ID_keystr\n')
# 		print(the_user)
# 		if(the_user):
# 			print('\nSESSIONS:append():kwds\n')
# 			print(kwargs.items())
# 			print('\nSESSIONS:append():ID_keystr\n')
# 			print(self.ID_keystr)
# 			if len(self):
# 				found_key = False
# 				idx = -1
# 				for S in self:
# 					idx += 1
# 					print('\nSESSIONS:append(): S.get(ID_key, False) is: {0}\n'.format(S.get(ID_key, False)))
# 					if S.get(ID_key, False) == the_user:
# 						found_key = True
# 						kwargs.pop(ID_key)
# 						for key, val in kwargs.items():
# 							if(S.get(key,False)):
# 								S.get(key).append(val)
# 							else:
# 								S.update({key:[val]})
# 						if idx > 0:
# 							super().rotate(-idx)
# 							super().popleft()	
# 							super().rotate(idx)
# 							super().appendleft(S)
# 						break
# 				if not(found_key):
# 					print('NOT: found key is still false')
# 					S = a_SESSION(ID_key, **kwargs)
# 					super().append(S)
# 			else:
# 				print('inside last else\n')
# 				S = a_SESSION(ID_key, **kwargs)
# 				super().append(S)
# 		else:
# 			print('\n{0}\n{1}{2}. \n{3}\n'.format('Sessions is previously initialized with ',
# 												'the key field for unique users called:  ',
# 												self.ID_keystr, 'But no such key was found in last key-val assignment.'))
# 			pass
	




class parent(deque):
	"""docstring for parent"""
	def __init__(self): 
		super().__init__()
		
	def parent_funct1(self):
		print('\nhello from parent class and parent_funct1 ...\n')
		return self
	
	def parent_funct2(self):
		print('\nhello from parent class and parent_funct2 ...\n')
		return self

class child(parent):
	"""docstring for child"""
	def __init__(self):
		super(parent).__init__()
		return None
		
	def child_funct1(self):
		print('\nhello from child class and child_funct1 ...\n')
		return self
	def parent_funct2(self):
		print('\nhello from child class and parent_func2 ...\n')
		return self


a_dict0 = {'a1':[],'a2':[],'a3':[]}
a_dict1 = {'a1':[1,2],'b1':['b11', 'b12']}
a_dict2 = {'a2':[3,4],'c1':['c11', 'c12']}




# Session_dict = {'userIP': an_Accession['userIP'], 
# 							'access_TIMES': [an_Accession['access_TIME']], 
# 							'file_IDs': [an_Accession['file_ID']], 
# 							'DT_STRs':[an_Accession['date_time_str']]}

# SO_dict = {'userIP': i['userIP'], 'start_DT': start_DT,
# 						'end_DT': end_DT, 'SESSION_time': session_time,
# 						'Number_Accessed': numfiles}

# an_Accession  = {'userIP': line_List[0],
# 								  'access_TIME': Accession_time,
# 								  'file_ID': line_List[5] + line_List[6],
# 								  'date_time_str': line_List[1]+ ' ' + line_List[2]}

