# log.py
# vim:ts=4:sw=4:noexpandtab

from os import makedirs
from os.path import basename, dirname, isabs, isdir, join
from shutil import move
from time import strftime

from localrepo.utils import LocalRepoError
from localrepo.config import Config

class LogError(LocalRepoError):
	''' Handles log errors '''
	pass


class BuildLogError(LogError):
	''' Handles buildlog errors '''
	pass


class Log:
	''' Handles Logging '''

	#: Default log filename
	FILENAME = '.log'

	#: Path to the log file
	_path = None

	#: Log file object
	_file = None

	@staticmethod
	def init(repo_path):
		''' Sets the path and opens the log file '''
		Log._path = Config.get('log', Log.FILENAME)

		if not isabs(Log._path):
			Log._path = join(repo_path, Log._path)

		try:
			if not isdir(dirname(Log._path)):
				makedirs(dirname(Log._path), mode=0o755, exist_ok=True)
			Log._file = open(Log._path, 'a')
		except:
			raise LogError(_('Could not open log file: {0}').format(Log._path))

	@staticmethod
	def log(msg):
		''' Logs a message '''
		try:
			Log._file.write('[{0}] {1}\n'.format(strftime('%Y-%m-%d %H:%M'), msg))
		except:
			pass

	@staticmethod
	def error(message):
		''' Logs an error '''
		Log.log(_('[Error] {0}').format(message))

	@staticmethod
	def close():
		''' Closes the log file '''
		try:
			Log._file.close()
		except:
			pass


class BuildLog:
	''' Stores build logs '''

	#: Default buildlog dirname
	DIRNAME = '.buildlog'

	#: Path to the buildlogs
	_path = None

	@staticmethod
	def init(repo_path):
		''' Sets the path '''
		BuildLog._path = Config.get('buildlog', BuildLog.DIRNAME)

		if not isabs(BuildLog._path):
			BuildLog._path = join(repo_path, BuildLog._path)

	@staticmethod
	def store(pkg_name, buildlog):
		''' Stores a buildlog '''
		path = join(BuildLog._path, pkg_name)

		try:
			if not isdir(path):
				makedirs(path, mode=0o755, exist_ok=True)

			move(buildlog, join(path, basename(buildlog)))
		except Exception as e:
			pass
