"""
   Transmission2Folder.py
   aimed to move episodes files of some series to the right folder
   @author Sylvain Desbureaux
   @copyright Copyright (c) 2008, Sylvain Desbureaux
   @license http://www.opensource.org/licenses/gpl-3.0.html
   @version 0.2
"""

import os.path
import re
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
  logging.debug('Entering get_finished_torrents')
  torrents = transmission_server.list()
  logging.debug('torrents running: ' + repr(torrents))
  finished_torrents = []
  if torrents != {}:
    for key in torrents.keys():
      torrent = tc.info(key)[key]
      if torrent.percentDone >= 1.0:
        logging.debug('Download of torrent ' + repr(torrent.name) + ' is finished')
        finished_torrents.append(torrent)
      
  return finished_torrents

def get_torrents_with_ratio_sup(transmission_server, ratio):
  """ Return the torrents of the ``transmission_server`` which are completely 
  downloaded  and which have a ratio superior or equal of ``ratio``"""
  logging.debug('Entering get_torrents_with_ratio_sup')
  torrents = transmission_server.list() 
  logging.debug('torrents running: ' + repr(torrents))
  ratio_torrents = []
  if torrents != {}:
    for key in torrents.keys():
      torrent = tc.info(key)[key]
      if ((torrent.percentDone >= 1.0) and (torrent.uploadRatio >= ratio)):
        ratio_torrents.append(torrent)
      
  return ratio_torrents

def is_included_series(name, series):
  """ Return True if the ``name`` of the torrent is included in 
  the array ``series``, with space can be [ ._-] """
  logging.debug('is_included_series')
  name = name.lower()
  for serie in series:
    regex = re.sub(r" ",'[ ._-]',serie.lower())
    logging.debug('regex to apply: ' + repr(regex) )
    if re.search(regex,name): 
      logging.debug('torrent with name ' + repr(name) + 'match the serie name ' + repr(serie))
      return True
  logging.debug('torrent with name ' + repr(name) + ' doesn\'t match with any of the serie name')
  return False
    

def link_files(files, serie_path):
  """ Hard Link the relevant ``files`` to the ``serie_path`` """
  logging.debug('Entering link_files')
  pass

def files_to_move(files, extensions):
  """ Return the file to move, i.e. the files with extension included in 
  ``extensions`` array"""
  logging.debug('Entering files_to_move')
  logging.debug('Files to check: ' + repr(files))
  files_to_move = [] 
  for filee in files.itervalues():
    filee = filee["name"]
    file_extension = filee.split('.')[-1]
    for extension in extensions:
      if extension == file_extension: 
        logging.debug('file ' + repr(filee) + ' has an extension(' +  
        repr('file_extension') + ') matching one of the extension allowed: ' + repr(extension))
        files_to_move.append(filee) 

  logging.debug('files to move: ' + repr(files_to_move))
  return files_to_move

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

  if 'transmission_rpc_level' not in config:
    logging.info('level of logging for the transmission rpc client not set, putting "info"')
    config['transmission_rpc_level'] = 'info'
  rpclevel=LEVELS.get(config['transmission_rpc_level'], logging.NOTSET)
  logging.getLogger('transmissionrpc').setLevel(rpclevel)
  logging.debug('configuration: \n' + repr(config))
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
    exit() -1

  return config
  
path = os.path.dirname(os.path.abspath( __file__ ))
print 'trying to find the configuration file (Transmission2Folder.yaml) in the folder ' + repr(path)

if os.path.exists(path + '/Transmission2Folder.yaml'):
  conf_file = open(path + '/Transmission2Folder.yaml', 'r')
  config = yaml.load(conf_file)
  config = verify_config(config)
  logging.debug('configuration after verification: \n' + repr(config))
  if 'user' in config and 'password' in config:
    tc = transmissionrpc.Client(address=config['host'], port=config['port'], user=config['user'], password=config['password'])
  else:
    tc = transmissionrpc.Client(config['host'], port=config['port'])
  finished_torrents = get_finished_torrents(tc)
  for torrent in finished_torrents:
    if is_included_series(torrent.name, config['series']):
      files = files_to_move(torrent.files(), config['extensions'])
      link_files(files)
  torrents_to_stop = get_torrents_with_ratio_sup(tc, config['ratio'])
  for torrent in torrents_to_stop:
    logging.info('Stopping torrent ' + repr(torrent.name))
    tc.stop(torrent.id)
    if is_included_series(torrent.name, config['series']): tc.remove(torrent.id) 
else:
  print "configuration file (Transmission2Folder.yaml) doesn't exist, aborting..."
    
