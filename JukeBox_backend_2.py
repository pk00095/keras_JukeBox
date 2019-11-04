from tensorflow.keras.callbacks import Callback
from tensorflow.keras import backend as K
import threading, sys, json
import numpy as np

import paho.mqtt.client as mqtt

from PyQt5 import QtCore, QtGui, QtWidgets

def red_print(text):
    print('\033[31m{}\033[0m'.format(text))

class JukeBoxCallback(Callback):

  def __init__(self, verbose=0, host='localhost', port=1883):
    super(JukeBoxCallback, self).__init__()
    self.verbose = verbose

    self.PID = 199 #np.random.randint(0,100)

    self.backend_learning_rate = 0
    self.frontend_learning_rate = 0
    self.frontend_learning_rate_prev = 0

    self.host = host
    self.port = port
    self.client = mqtt.Client()
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.subscribe_topic = 'keras_JukeBox/backend/{}'.format(self.PID)
    self.publish_topic = 'keras_JukeBox/frontend/{}'.format(self.PID)
    self.msg = None
    self.client.connect(host=self.host, port=self.port, keepalive=60, bind_address="")
    self.start = False

    #TODO make a PID checker

    self.client.subscribe(self.subscribe_topic)

    self.play_status = 'pause'

    self.current_epoch = 0
    self.current_batch = 0

    self.update_learning_rate = False

    payload = {'PID':self.PID, 'status': 'not_started'}
    self.publish_data(payload)

    self.running = False
    red_print('called init function')

  def start_listening(self):
      self.running = True
      while self.running:
          self.client.loop(timeout=1.0, max_packets=1)

  def on_connect(self, client, userdata, flags, rc):
      red_print("Connected to {} with result code {}".format(self.host,rc))

      #send a connection request
      #payload = {'PID':self.PID, 'status': 'not_started'}
      #self.publish_data(payload)

  def publish_data(self, payload, qos=0, retain=True):
    if isinstance(payload, dict):
      payload = json.dumps(payload, indent=2)
      self.client.publish(self.publish_topic, payload=payload, qos=qos, retain=retain)
    else:
      red_print("payload was not dictionary, did not send")

  def on_message(self,client, userdata, msg):

    message = json.loads(msg.payload.decode('utf-8'))
    print(message)

    if self.start ==False:
      #connection has not been acknowledged
      #message = json.loads(msg.payload.decode('utf-8'))
      if message['status'] == 'acknowledged':
        self.start = True
      else:
        red_print('did not understand msg::{}'.format(message))

    else:
      #self.subscribe_topic = msg.topic
      self.msg = message
      #red_print("got a message")
      if self.verbose > 0:
        red_print(self.subscribe_topic+" "+str(self.msg))

      self.update_variables()

  def update_variables(self):
    tab_1_cmd = self.msg['tab1']
    tab_2_cmd = self.msg['tab2']

    self.play_status = tab_1_cmd['play_status']
    self.frontend_learning_rate = tab_2_cmd['learning_rate']

    if self.frontend_learning_rate != self.frontend_learning_rate_prev:
    	self.update_learning_rate = True
    	self.frontend_learning_rate_prev = self.frontend_learning_rate
    #self.update_learning_rate = tab_2_cmd['update_learning_rate']


  def on_train_begin(self, logs):

    thr = threading.Thread(target=self.start_listening)
    thr.daemon = True
    thr.start()

    if not hasattr(self.model.optimizer, 'lr'):
      raise ValueError('Optimizer must have a "lr" attribute.')

    red_print('waiting for a JukeBox')
    while not self.start:
      pass
    red_print('connected to JukeBox')

    self.backend_learning_rate = float(K.get_value(self.model.optimizer.lr))
    # After connection is ack initialize this lr in GUI


  def on_batch_begin(self, batch, logs=None):

    self.current_batch = batch

    # if play has not been initiated, go into an infinite loop
    #run_status_displayed=False
    if self.play_status in ['pause']:
      red_print('paused from frontend')
      while self.play_status in ['pause','not_started']:
        pass
      red_print('Resuming ..')


    if not hasattr(self.model.optimizer, 'lr'):
      raise ValueError('Optimizer must have a "lr" attribute.')

    self.backend_learning_rate = float(K.get_value(self.model.optimizer.lr))

    #lr = float(K.get_value(self.model.optimizer.lr))
    #self.frontend_learning_rate is updated by on_message function

    if not isinstance(self.frontend_learning_rate, (float, np.float32, np.float64)):
      raise ValueError('The output of the "schedule" function '
                       'should be float.')
    #if self.backend_learning_rate != self.frontend_learning_rate:
    if self.update_learning_rate:
      if self.verbose > 0:
        red_print('updated learning rate from {} to {}'.format(self.backend_learning_rate, self.frontend_learning_rate))
      K.set_value(self.model.optimizer.lr, self.frontend_learning_rate)

      self.update_learning_rate = False

    # recapture this learning rate to send to FrontEnd
    self.backend_learning_rate = float(K.get_value(self.model.optimizer.lr))
    # send learning rate to frontend

    #if self.verbose > 0:
    #  red_print('\nEpoch %05d: JukeBox reducing learning '
    #        'rate to %s.' % (epoch + 1, lr))

  def on_batch_end(self, batch, logs=None):
    payload = {'learning_rate':self.backend_learning_rate,
    'epoch':self.current_epoch,
    'batch':self.current_batch}

    self.publish_data(payload)

  def on_epoch_end(self, epoch, logs=None):
    logs = logs or {}
    logs['lr'] = K.get_value(self.model.optimizer.lr)
    self.current_epoch = epoch+1