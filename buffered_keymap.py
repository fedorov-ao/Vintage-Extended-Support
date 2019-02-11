import logging
from logging import debug

def lower_bound(seq, val, cmp=lambda a, b : a < b, l=None, h=None):
	if l is None: l = 0
	if h is None: h = len(seq)

	count = h - l
	step = 0

	while (count > 0):
		step = int(count / 2)
		i = l + step
		if cmp(seq[i], val):
			l = i + 1
			count -= step + 1
		else:
			count = step

	return l

def upper_bound(seq, val, cmp=lambda a, b : a < b, l=None, h=None):
	if l is None: l = 0
	if h is None: h = len(seq)

	count = h - l
	step = 0

	while (count > 0):
		step = int(count / 2)
		i = l + step
		if not cmp(val, seq[i]):
			l = i + 1
			count -= step + 1
		else:
			count = step

	return l

def equal_range(seq, val, cmp=lambda a, b : a < b, l=None, h=None):
	if l is None: l = 0
	if h is None: h = len(seq)
	return (lower_bound(seq, val, cmp, l, h), upper_bound(seq, val, cmp, l, h))

# a   : б
# aa  : в
# aaa : г
# a -> б
# ab -> бb
# aab -> вb
# prefixes of values in [l; h) are equal to each other
# can find 0, 1 or several possible matches

def find_best_mapping(map, s, cmp=lambda a,b : a[0] < b[0], l=None, h=None):
	'''Finds best mapping for s.
		Longest match wins
		map should be presorted
	'''
	if l is None: l = 0
	if h is None: h = len(map)

	result = ""
	b, e = 0, len(s)

	while b != len(s):
		# candidate is a part of input we are trying to find a match for
		candidate = s[b:e]
		r = equal_range(map, (candidate, 0), cmp, l, h)
		debug(candidate, ':', r)
		# if there is one or several prefixes and the first one matches the candidate:
		#	map candidate, append to result, and advance past it
		if r[1] > r[0] and map[r[0]][0] == candidate:
			result += map[r[0]][1]
			b = e
			e = len(s)
		# else none of the prefixes match the candidate exactly
		else:
			# if our candidate is down to one character which was impossible to match:
			#	append it to result and advance past it
			if e == b+1:
				result += candidate
				b = e
				e = len(s)
			# else decrement candidate by one character from the back
			else:
				e -= 1

	return result	

class BufferedKeymap:
	def __init__(self, map):
		self.buffer = ""
		self.map = map
		map.sort(key=lambda x : x[0])

	def get(self, c, repl=None):
		assert(len(c) == 1)
		l = len(self.buffer)
		temp_buffer = self.buffer + c
		lt = len(temp_buffer)
		cmp=lambda a,b : a[0][:lt] < b[0][:lt] # prefix comparison
		r = equal_range(self.map, (temp_buffer, 0), cmp)
		# new character has produced an exact match:
		#	map this exact match, clear the buffer
		b, e = r[0], r[1]
		if e == b+1 and self.map[b][0] == temp_buffer:
			debug("Match found")
			self.buffer = ""
			return (self.map[b][1], l)
		# new character has broken the sequence:
		#	find best mapping for previous sequence, set buffer to char
		elif b == e:
			debug("Sequence interrupted")
			if len(self.buffer) > 0:
				mapped_buffer = find_best_mapping(self.map, self.buffer, cmp)
				debug(mapped_buffer)
				self.buffer = "" # clear buffer to avoid infinite recursion
				cr = self.get(c)
				return (mapped_buffer+cr[0], l+cr[1])
			# we end up here if trying to map a single character and it does not have a mapping
			else:
				assert(temp_buffer == c)
				return (c if repl is None else repl, 0)
		# add new char to buffer
		else:
			debug("Append to buffer")
			self.buffer = self.buffer + c
			return (c if repl is None else repl, 0)

	def pop(self):
		self.buffer = self.buffer[:-1]

	def clear(self):
		self.buffer = ""