from tensorflow.keras.callbacks import Callback
from tensorflow.keras import backend as K
import threading, sys
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets

from .JukeBox_UI import App

class JukeBoxCallback(Callback):

  def __init__(self, verbose=0):
    super(JukeBoxCallback, self).__init__()
    self.verbose = verbose

    self.backend_learning_rate = 0
    self.frontend_learning_rate = 0

  def startUI(self):
    self.app = QtWidgets.QApplication(sys.argv)
    self.ex = App()
    self.app.exec_()
    #sys.exit(self.app.exec_())

  def on_train_begin(self, logs):
    if not hasattr(self.model.optimizer, 'lr'):
      raise ValueError('Optimizer must have a "lr" attribute.')


    self.UIthr = threading.Thread(target=self.startUI)
    self.UIthr.daemon = True
    self.UIthr.start()
    #self.startUI()

    self.backend_learning_rate = float(K.get_value(self.model.optimizer.lr))
    #initialize this in GUI
    self.ex.window.learning_rate = self.backend_learning_rate


  def on_batch_begin(self, epoch, logs=None):

    # if play has not been initiated, go into an infinite loop
    #run_status_displayed=False
    #if self.ex.window.run_status == 'pause':
    #    print('Paused from Frontend')
    #    while self.ex.window.run_status == 'pause':
    #        pass
    #    print('Resuming ..')


    if not hasattr(self.model.optimizer, 'lr'):
      raise ValueError('Optimizer must have a "lr" attribute.')

    self.backend_learning_rate = float(K.get_value(self.model.optimizer.lr))

    #lr = float(K.get_value(self.model.optimizer.lr))
    self.frontend_learning_rate = self.ex.window.learning_rate # get this from UI

    if not isinstance(self.frontend_learning_rate, (float, np.float32, np.float64)):
      raise ValueError('The output of the "schedule" function '
                       'should be float.')
    if self.backend_learning_rate != self.frontend_learning_rate:
        K.set_value(self.model.optimizer.lr, self.frontend_learning_rate)

    # recapture this learning rate to send to FrontEnd
    self.backend_learning_rate = float(K.get_value(self.model.optimizer.lr))
    # send learning rate to frontend
    self.ex.window.learning_rate = self.backend_learning_rate

    if self.verbose > 0:
      print('\nEpoch %05d: JukeBox reducing learning '
            'rate to %s.' % (epoch + 1, lr))

  def on_epoch_end(self, epoch, logs=None):
    logs = logs or {}
    logs['lr'] = K.get_value(self.model.optimizer.lr)