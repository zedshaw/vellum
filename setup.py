## this file is generated from settings in build.vel

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# from options["setup"] in build.vel
config = {'description': 'A flexible small make alternative for Python programmers.', 'author': 'Zed A. Shaw', 'author_email': 'zedshaw@zedshaw.com', 'url': 'http://www.zedshaw.com/projects/vellum', 'version': '0.17', 'scripts': ['bin/vellum'], 'packages': ['vellum'], 'name': 'vellum'}
setup(**config)

