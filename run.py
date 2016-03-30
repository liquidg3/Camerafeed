#!/usr/bin/env python
from camerafeed import CameraFeed
from argparse import ArgumentParser

# make dict from args
parser = ArgumentParser(description="Camerafeed")
parser.add_argument('--config_path', dest='config_path', default="settings.ini", help='path to settinsg.ini')
args = parser.parse_args()

# start app
camerafeed = CameraFeed()
camerafeed.go_config(config_path=args.config_path)
