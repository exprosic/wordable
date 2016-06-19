# vim: set noet ts=4 sw=4 fileencoding=utf-8:

import os
import sys
import termios

# [\t]zerstoren: destroy[\n](echo back id)
# [\t]wers[esc]
# :del [id]
# [\t][\t](dictation...)yyynynynnnyn[esc]

class TcAttr:
	def __init__(self, fd):
		self.fd = fd
		self.origin_attr = termios.tcgetattr(fd)

	def restore(self):
		termios.tcsetattr(self.fd, termios.TCSADRAIN, self.origin_attr)

	def _set(self, attrname, **kwargs):
		idx = 'iflag oflag cflag lflag ispeed ospeed cc'.split().index(attrname)
		attr = termios.tcgetattr(self.fd)
		for k,v in kwargs.items():
			k = termios.__dict__[k]
			if idx<4:
				attr[idx] |= k
				if not v: attr[idx] ^= k
			elif idx==6:
				attr[idx][k] = v
			else:
				raise NotImplementedError
		termios.tcsetattr(self.fd, termios.TCSADRAIN, attr)

	def setLFlag(self, **kwargs):
		self._set('lflag', **kwargs)

	def setCC(self, **kwargs):
		self._set('cc', **kwargs)

	def setNoEcho(self):
		self.setLFlag(ECHO=False)

	def setOneChar(self):
		# as specified by bash source
		self.setLFlag(ICANON=False, ISIG=True, ICRNL=True, INLCR=False)
		self.setCC(VMIN=1, VTIME=0)


def main():
	x = os.read(sys.stdin.fileno(), 1)
	print(ord(x))


tc = TcAttr(sys.stdin.fileno())
try:
	tc.setNoEcho()
	tc.setOneChar()
	main()
finally:
	tc.restore()
