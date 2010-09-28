"""
   Transmission2Folder.py
   aimed to move episodes files of some series to the right folder
   @author Sylvain Desbureaux
   @copyright Copyright (c) 2008, Sylvain Desbureaux
   @license http://www.opensource.org/licenses/gpl-3.0.html
   @version 0.2
"""

import os.path

import logging
import transmissionrpc
import yaml

LEVELS = {'debug': logging.DEBUG,
  'info': logging.INFO,
  'warning': logging.WARNING,
  'error': logging.ERROR,
  'critical': logging.CRITICAL}

def get_finished_torrents(transmission_server):
  """ Return the torrents of the ``transmission_server`` which are completely 
  downloaded """
  torrents = transmission_server.list()
  finished_torrents = []
  for key in torrents.keys:
    torrent = tc.info(key)[key]
    if torrent.percentDone >= 1.0:
      finished_torrents.append(torrent)
      
  finished_torrents

def get_torrents_with_ratio_sup(transmission_server, ratio):
  """ Return the torrents of the ``transmission_server`` which are completely 
  downloaded  and which have a ratio superior or equal of ``ratio``"""
  torrents = transmission_server.list()
  ratio_torrents = []
  for key in torrents.keys:
    torrent = tc.info(key)[key]
    if ((torrent.percentDone >= 1.0) and (torrent.uploadRatio >= ratio)):
      ratio_torrents.append(torrent)
      
  ratio_torrents

def is_included_series(name, series):
  """ Return True if the ``name`` of the torrent is included in 
  the array ``series``, with space can be [ ._-] """
  pass
    

def link_files(files, serie_path):
  """ Hard Link the relevant ``files`` to the ``serie_path`` """
  pass

def files_to_move(files, extensions):
  """ Return the file to move, i.e. the files with extension included in 
  ``extensions`` array"""
  pass

print 'trying to find the configuration file (Transmission2Folder.yaml)'
if os.path.exists('./Transmission2Folder.yaml'):
  conf_file = open('./Transmission2Folder.yaml', 'r')
  config = yaml.load(conf_file)
  level = LEVELS.get(config['log_level'], logging.NOTSET)
  logging.basicConfig(config['Transmission2Folder.log'], level=level)    
  tc = transmissionrpc.Client(config['address'], config['port'])
  finished_torrents = get_finished_torrents(tc)
  for torrent in finished_torrents:
    if is_included_series(torrent['name'], config['series']):
      files = files_to_move(torrent['files'], config['extensions'])
      link_files(files, serie_path)
  torrents_to_stop = get_torrents_with_ratio_sup(tc, config['ratio'])
  for torrent in torrents_to_stop:
    logging.info('Stopping torrent ' + repr(torrent['name']))
    tc.stop(torrent['id'])
    if is_included_series(torrent['name'], config['series']): tc.remove(torrent['id']) 
else:
  print "configuration file (Transmission2Folder.yaml) doesn't exist, aborting..."
    
