"""
   Transmission2Folder.py
   aimed to move episodes files of some series to the right folder
   @author Sylvain Desbureaux
   @copyright Copyright (c) 2008, Sylvain Desbureaux
   @license http://www.opensource.org/licenses/gpl-3.0.html
   @version 0.2
"""

import os
import re
import string
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
      if torrent.progress == 100:
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
      if ((torrent.progress == 100) and (torrent.ratio >= ratio)):
        ratio_torrents.append(torrent)
      
  return ratio_torrents

def is_included_series(name, series):
  """ Return the name of the serie if the ``name`` of the torrent is included in 
  the array ``series``, with space can be [ ._-] """
  logging.debug('is_included_series')
  name = name.lower()
  for serie in series:
    regex = re.sub(r" ",'[ ._-]',serie.lower())
    logging.debug('regex to apply: ' + repr(regex) )
    if re.search(regex,name): 
      logging.debug('torrent with name ' + repr(name) + 'match the serie name ' + repr(serie))
      return serie
  logging.debug('torrent with name ' + repr(name) + ' doesn\'t match with any of the serie name')
  return False
    
def search_season_and_episode(name, serie):
  """ Return the season and the episode number of the serie found in the 
  ``name`` of the torrent, just after the name of the ``serie`` """
  regex_serie = re.sub(r" ",'[ ._-]',serie.lower())
  regex_start = '[a-zA-Z/0-9.]*' + regex_serie + '[ ._-]*[Ss]*'
  regex_end = '[0-9]+[eExX]+[0-9]+'
  logging.debug('Regex to search name: ' + regex_start)
  sub_name = re.sub(regex_start,'',name.lower())
  logging.debug('  Result: ' + sub_name)
  logging.debug('Regex to search season and episode: ' + regex_end)
  season_and_episode = re.findall(regex_end,sub_name)[0]
  logging.debug('Season and Episode found: ' + repr(season_and_episode))
  result={}
  result['season'] = re.split(r"[eExX]+",season_and_episode)[0]
  logging.debug('Season Found: ' + repr(result['season']))
  result['episode'] = re.split(r"[eExX]+",season_and_episode)[1]
  logging.debug('Episode Found: ' + repr(result['episode']))
  return result

def link_files(files, folder, serie, episode, season):
  """ Hard Link the relevant ``files`` to the ``destination_folder`` with the 
  relevant name (composed with ``serie``, ``season`` and ``episode``)"""
  logging.debug('Entering link_files')
  for filee in files:
    ext = '.' + filee.split('.')[-1]
    destination = folder + serie.title() + ' - S' + season + 'E' + episode + ext
    logging.debug('Linking file ' + repr(filee) + ' to ' + destination)
#    os.link(filee, destination)

def files_to_move(files, extensions,src_folder):
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
        repr('file_extension') + ') matching one of the extension allowed: ' +
        repr(extension))
        files_to_move.append(src_folder + filee) 

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
  
  if config['destination_folder'][-1] != '/': config['destination_folder'] += '/'

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
    serie = is_included_series(torrent.name, config['series'])
    if serie:
      src_folder = torrent.fields['downloadDir']
      files = files_to_move(torrent.files(), config['extensions'],src_folder)
      result = search_season_and_episode(torrent.name, serie)
      episode = string.zfill(int(result['episode']),2)
      season = string.zfill(int(result['season']),2)
      folder_destination = config['destination_folder'] + serie.title() + '/Season ' + season +'/'
      logging.debug('Making the directory(ies): ' + folder_destination)
#      os.makedirs(folder_destination)
      link_files(files,folder_destination, serie, episode, season)
  torrents_to_stop = get_torrents_with_ratio_sup(tc, config['ratio'])
  for torrent in torrents_to_stop:
    logging.info('Stopping torrent ' + repr(torrent.name))
#    tc.stop(torrent.id)
#    if is_included_series(torrent.name, config['series']): tc.remove(torrent.id)
else:
  print "configuration file (Transmission2Folder.yaml) doesn't exist, aborting..."
