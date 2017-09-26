#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2017 bily     Huazhong University of Science and Technology
#
# Distributed under terms of the MIT license.

import itchat
from subprocess import Popen, check_output

# commands that you'd like to immediately get log message.
SIMPLE_OUTPUT_CMD = ['ls', 'pwd', 'whoami', 'users', 'git', 'cat', 'nvidia-smi', 'df']
FORBIDDEN_CMD = ['vim', 'top', 'htop', 'ipython']
FREQUENT_CMD = ['nvidia-smi']

def send_file(filepath):
  """send file to your wechat filehelper

  :param filepath: path of the file to be sent, can be relative/absolute path
  :return: None
  """
  status = itchat.send('@fil@{}'.format(filepath), toUserName='filehelper')
  return status

def send_msg(msg):
  """send message to your wechat filehelper

  :param msg: message of string type
  :return: None
  """
  itchat.send(msg, toUserName='filehelper')

def get_log_file_path(ind=None, create_new=True, log_prefix='/tmp/welog', maximum_log_file=100):
  """get log file path

  :param ind: log file index
  :param create_new: if create new log file
  :param log_prefix: prefix of log file
  :param maximum_log_file: maximum number of log files
  :return: log file index, log file path
  """
  cur_ind = get_log_file_path.cur_ind
  if create_new:
    ind = (cur_ind + 1) % maximum_log_file
    get_log_file_path.cur_ind = ind
  else:
    if ind is None:
      ind = cur_ind
    ind = ind % maximum_log_file
  return ind, '{}.{}.txt'.format(log_prefix, ind)
get_log_file_path.cur_ind = 0

@itchat.msg_register([itchat.content.TEXT])
def chat_trigger(msg):
  if msg['ToUserName'] != 'filehelper': return
  try:
    msg_text = msg['Text'].strip()
    cmd = msg_text.split(' ')

    if cmd[0] == 'help':
      send_msg('Send command just like in ssh.\n'
               'additional useful commands:\n'
               'log [index]: download the log file of the index-th command\n'
               'dl filepath: download file\n'
               'list: list frequently used commands\n')
    elif cmd[0] == 'list':
      for c in FREQUENT_CMD:
        send_msg(c)
    elif cmd[0] == 'dl':
      if len(cmd) == 2:
        send_file(cmd[1])
      else:
        send_msg('usage: dl filepath')
    elif cmd[0] == 'log':
      if len(cmd) == 2:
        ind = int(cmd[1])
      else:
        ind = None
      ind, log_file = get_log_file_path(ind=ind, create_new=False)
      send_file(log_file)
    elif cmd[0] in SIMPLE_OUTPUT_CMD:
      out = check_output(cmd)
      send_msg(out)
    elif cmd[0] in FORBIDDEN_CMD:
      send_msg('{} are not supported...'.format(','.join(FORBIDDEN_CMD)))
    else:
      ind, log_file = get_log_file_path()
      with open(log_file, 'w') as f:
        Popen(cmd, stdout=f, stderr=f)
      send_msg('log index: {}'.format(ind))

  except Exception as e:
    send_msg(e.__str__())

if __name__ == '__main__':
  itchat.auto_login(hotReload=True, enableCmdQR=2)
  itchat.run()