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

def verify_config(config):
  """ Verify the config and return it\n
  Verification of the log level, log file, transmission host, transmission port,
  ratio, source folder and destination folder"""
  if 'log_level' not in config: 
    print 'log_level not set in the config file, putting level "info"'
    config['log_level'] = 'info'
    
  if 'log_file' not in config: 
    print 'log_file not set in the config file, putting "Transmission2Folder.log"'
    config['log_file'] = 'Transmission2Folder.log'
  
  level = LEVELS.get(config['log_level'], logging.NOTSET)
  logging.basicConfig(filename=config['log_file'], level=level)
  logging.getLogger('transmissionrpc').setLevel(level)
  logging.debug('configuration: ' + repr(config))
  if 'host' not in config:
    logging.info('host not set in the config, putting "localhost"')
    config['host'] = 'localhost'
    
  if 'port' not in config:
    logging.info('port not set in the config, putting 9091')
    config['port'] = 9091
    
  if 'ratio' not in config:
    logging.info('ratio not set in the config, putting 1.50')
    config['ratio'] = 1.50
  
  if 'destination_folder' not in config:
    logging.error('destination folder not set, exiting')
    print 'destination folder not set, exiting'
    exit -1
  
  
  config
  

print 'trying to find the configuration file (Transmission2Folder.yaml)'
if os.path.exists('./Transmission2Folder.yaml'):
  conf_file = open('./Transmission2Folder.yaml', 'r')
  config = yaml.load(conf_file)
  config = verify_config(config)
  #TODO we should give default value if the config is not complete 
  tc = transmissionrpc.Client('10.193.35.152', port=9091)
  finished_torrents = get_finished_torrents(tc)
  for torrent in finished_torrents:
    if is_included_series(torrent.name, config.series):
      files = files_to_move(torrent.files, config['extensions'])
      #TODO Serie Path is inexistant, should derive it from the config
      link_files(files, serie_path)
  torrents_to_stop = get_torrents_with_ratio_sup(tc, config['ratio'])
  for torrent in torrents_to_stop:
    logging.info('Stopping torrent ' + repr(torrent.name))
    tc.stop(torrent.id)
    if is_included_series(torrent.name, config['series']): tc.remove(torrent.id) 
else:
  print "configuration file (Transmission2Folder.yaml) doesn't exist, aborting..."
    
