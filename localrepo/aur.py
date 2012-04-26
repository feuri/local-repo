# aur.py
# vim:ts=4:sw=4:noexpandtab

from urllib.request import urlopen
from json import loads as parse

from localrepo.utils import LocalRepoError

class AurError(LocalRepoError):
	''' Handles Aur errors '''
	pass

class Aur:
	''' A class that manages request to the AUR '''

	#: Uri of the AUR
	HOST = 'https://aur.archlinux.org'

	#: Uri of the AUR API
	API = '/rpc.php'

	#: Max number of packages per request
	MAX = 50

	#: Translations from AUR to localrepo
	TRANS = {'Name': 'name',
	         'Version': 'version',
	         'URLPath': lambda p: ('uri', Aur.HOST + p)}

	@staticmethod
	def decode_info(info):
		''' Turns an AUR info dict into a localrepo style package info  dict '''
		return dict(t(info[k]) if callable(t) else (t, info[k]) for k, t in Aur.TRANS.items())

	@staticmethod
	def request(request, data):
		''' Performs the AUR API request '''
		uri = '{0}{1}?type={2}'.format(Aur.HOST, Aur.API, request)

		if type(data) is str:
			uri += '&arg={0}'.format(data)
		else:
			uri += ''.join(['&arg[]={0}'.format(d) for d in data])

		try:
			res = urlopen(uri)
		except:
			raise AurError(_('Could not reach the AUR'))

		if res.status is not 200:
			raise AurError(_('AUR responded with error: {0}').format(res.reason))

		try:
			info = parse(res.read().decode('utf8'))
			error = info['type'] == 'error'
			results = info['results']
		except:
			raise AurError(_('AUR responded with invalid data'))

		if error:
			raise AurError(_('AUR responded with error: {0}').format(results))

		try:
			if type(results) is dict:
				return Aur.decode_info(results)

			return dict((i['Name'], Aur.decode_info(i)) for i in results)
		except:
			raise AurError(_('AUR responded with invalid data'))

	@staticmethod
	def package(name):
		''' Asks the AUR for informations about a single package '''
		return Aur.request('info', name)

	@staticmethod
	def packages(names):
		''' Asks the AUR for informations about multiple packages '''
		result = {}

		for i in range(0, len(names), Aur.MAX):
			result.update(Aur.request('multiinfo', names[i:i + Aur.MAX]))

		return result

	@staticmethod
	def search(q):
		''' Searches the AUR for packages '''
		return Aur.request('search', q)
