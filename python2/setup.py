import sys
from setuptools import setup, find_packages 

__version__ = open("VERSION").read().strip()

requires = []
if sys.version_info[1] < 6:
    requires.append("simplejson")
if sys.version_info[1] < 5:
    requires.append("uuid")

setup(name = 'berrymq',
      version = __version__,
      author = 'SHIBUKAWA Yoshiki',
      author_email = 'yoshiki at shibu.jp',
      url = 'http://berrymq.org',
      description = 'Small message queue system for building applications',
      long_description = ('Programmer friendly message queue module. '
                        'It supports push/pull API, thread pool'),
      keywords = "python ruby message queue mq",
      classifiers = [
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python"
      ],
      license = "MIT License",
      packages = find_packages(),
      install_requires = requires)
