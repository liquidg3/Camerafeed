from distutils.core import setup

files = ["camerafeed/*"]

setup(name="Camerafeed",
      version="0.0.1",
      author="Taylor Romero",
      author_email="me@taylorrome.ro",
      packages=['camerafeed'],
      install_requires=[
          'imutils',
          'shapely',
          'grequests',
          'imutils',
          'configparser',
          'picamera[array]'
      ],
      scripts=['bin/camerafeed'])
