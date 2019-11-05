import sys, json, threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                             QHBoxLayout, QGroupBox, QVBoxLayout, QLineEdit,
                             QLabel, QFormLayout)

import paho.mqtt.client as mqtt

from PyQt5.QtCore import pyqtSlot

from keras_jukebox.utils import calculate_efffective_lr, FloatNotEmptyValidator, red_print


class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Window Settings
        self.x, self.y, self.w, self.h = 0, 0, 300, 200
        self.setGeometry(self.x, self.y, self.w, self.h)

        self.window = MainWindow(self)
        self.setCentralWidget(self.window)
        self.setWindowTitle("Keras-JukeBox(Powered by Segmind Solutions Pvt Ltd)") # Window Title
        self.show()

class MainWindow(QtWidgets.QWidget):        
    def __init__(self, parent, host='localhost', port=1883):   
        super(MainWindow, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)  

        self.run_status = 'pause'      
        self.supported_run_statuses = ['play','pause','stop']
        self.initial_operand_value = 1e-5


        self.current_epoch = 0
        self.current_batch = 0

        self.current_epoch_label_tab2 = QLabel("Current Epoch : {}".format(self.current_epoch))
        self.current_batch_label_tab2 = QLabel("Current Batch : {}".format(self.current_batch))

        self.current_epoch_label_tab1 = QLabel("Current Epoch : {}".format(self.current_epoch))
        self.current_batch_label_tab1 = QLabel("Current Batch : {}".format(self.current_batch))


        # Run this after settings
        # Initialize tabs
        tab_holder = QtWidgets.QTabWidget()   # Create tab holder
        self.setup_tab_1() 
        self.setup_tab_2()          # Tab one
        # Add tabs
        tab_holder.addTab(self.tab1,"Tab 1") #self.lang["tab_1_title"]) # Add "tab1" to the tabs holder "tabs"
        tab_holder.addTab(self.tab2,"Tab 2") #self.lang["tab_2_title"]) # Add "tab2" to the tabs holder "tabs" 

        layout.addWidget(tab_holder)


        self.host = host
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.subscribe_topic =  'keras_JukeBox/frontend/#'
        #self.publish_topic = 'keras_JukeBox/backend/99' #.format(self.PID)
        self.msg = None
        self.client.connect(host=self.host, port=self.port, keepalive=60, bind_address="")
        self.start = False

        self.PID = None
        self.client.subscribe(self.subscribe_topic)
        print("INit done")

        self.running = False

        thr = threading.Thread(target=self.start_listening)
        thr.daemon = True
        thr.start()



    def start_listening(self):

        print('started listening')
        self.running = True
        while self.running:
            self.client.loop(timeout=1.0, max_packets=1)


    def publish_data(self, payload=None, qos=0, retain=True):
        if isinstance(payload, dict):
          payload = json.dumps(payload, indent=2)
          self.client.publish(self.publish_topic, payload=payload, qos=qos, retain=retain)
        elif payload==None:
            self.client.publish(self.publish_topic, payload=payload, qos=1, retain=True)
            red_print("cleared all meassages under topic name {}".format(self.publish_topic))
        else:
          red_print("payload was not dictionary, did not send")

    def send_payload(self):
        payload = {
        'tab1':self.tab1_payload,
        'tab2':self.tab2_payload
        }
        self.publish_data(payload)


    def on_connect(self, client, userdata, flags, rc):
        print("Connected to {} with result code {}".format(self.host,rc))

        #send a connection request
        #payload = {'PID':self.PID}

    def on_message(self,client, userdata, msg):

        message = json.loads(msg.payload.decode('utf-8'))
        #print(message)

        if self.PID == None: #not yet got any backend
            #assign itself a PID
            if message['status'] == 'not_started':
                self.PID = message['PID']

                # clear messages under the topic name 'keras_JukeBox/frontend/'
                self.publish_topic = 'keras_JukeBox/frontend/{}'.format(self.PID)
                payload = None
                self.publish_data(payload)

                self.publish_topic = 'keras_JukeBox/backend/{}'.format(self.PID)
                payload = {'status':'acknowledged'}
                self.publish_data(payload)
                print('subscribed to PID :: {}'.format(self.PID))



                # TO DO unsubscribe from previous topic
                self.client.unsubscribe(self.subscribe_topic)
                self.subscribe_topic = 'keras_JukeBox/frontend/{}'.format(self.PID)
                self.client.subscribe(self.subscribe_topic)

        else:
            self.learning_rate = message['learning_rate']
            self.lr_label.setText(str(self.learning_rate))
            #self.lr_label = QLabel("Current lr : {}".format(self.learning_rate))

            self.current_epoch = message['epoch']
            self.current_batch = message['batch']

            self.current_epoch_label_tab2.setText("Current Epoch : {}".format(self.current_epoch))
            self.current_batch_label_tab2.setText("Current Batch : {}".format(self.current_batch))

            self.current_epoch_label_tab1.setText("Current Epoch : {}".format(self.current_epoch))
            self.current_batch_label_tab1.setText("Current Batch : {}".format(self.current_batch))


    def setup_tab_2_variables(self, learning_rate=0.99, selected_operand='f(x)=x'):
        self.learning_rate = learning_rate
        self.selected_operandQLabel = QLabel('\t{}'.format(selected_operand))

        # initial value of payload['tab1'] to be sent on connect
        self.tab2_payload = {'learning_rate':0.001}

        print("tab2 variables set up")

    def setup_tab_1(self):
        self.tab1 = QWidget()
        self.horizontalLayout_tab1 = QHBoxLayout(self.tab1)

        self.button_start = QtWidgets.QPushButton('play') #self.lang["btn_start"])
        self.button_start.setIcon(QtGui.QIcon('keras_jukebox/images/play.png'))
        #self.button_start.setIconSize(QtCore.QSize(self.w/10,self.h/10))
        self.button_start.setToolTip("Start Training")    # Message to show when mouse hover
        self.button_start.clicked.connect(lambda : self.tab1_response(action='play'))


        self.button_stop = QtWidgets.QPushButton('stop') #self.lang["btn_stop"])
        self.button_stop.setIcon(QtGui.QIcon('keras_jukebox/images/stop.png'))
        #self.button_stop.setIconSize(QtCore.QSize(self.w/10,self.h/10))
        self.button_stop.setToolTip("Stop Training")    # Message to show when mouse hover
        self.button_stop.clicked.connect(lambda : self.tab1_response(action='stop'))



        self.button_pause = QtWidgets.QPushButton('pause')
        self.button_pause.setIcon(QtGui.QIcon('keras_jukebox/images/pause.png'))
        #self.button_pause.setIconSize(QtCore.QSize(self.w/10,self.h/10))
        self.button_pause.setToolTip("Pause Training")    # Message to show when mouse hover
        self.button_pause.clicked.connect(lambda : self.tab1_response(action='pause'))


        self.horizontalLayout_tab1.addWidget(self.current_epoch_label_tab1)
        self.horizontalLayout_tab1.addWidget(self.current_batch_label_tab1)

        self.horizontalLayout_tab1.addWidget(self.button_start)
        self.horizontalLayout_tab1.addWidget(self.button_pause)
        self.horizontalLayout_tab1.addWidget(self.button_stop)

        # initial value of payload['tab1'] to be sent on connect
        self.tab1_payload = {'play_status':self.run_status}

        print("tab1 set up")

    @pyqtSlot()
    def tab1_response(self, action):
        assert action in self.supported_run_statuses
        self.run_status = action
        print(self.run_status)
        self.tab1_payload = {'play_status':self.run_status}
        #publish to frontend

        self.send_payload()

        # if command is stop clear all reatined messages under 'keras_JukeBox/backend/PID'
        if self.run_status == 'stop':
            self.publish_data(payload=None)



    def setup_tab_2(self):
        self.setup_tab_2_variables()
        self.tab2 = QWidget()
        self.horizontalLayout_tab2 = QHBoxLayout(self.tab2)

        self.OperandsGroupBox = QGroupBox( "Operands" )
        self.horizontalLayout_tab2.addWidget(self.OperandsGroupBox)
        self.left_vertical_layout = QVBoxLayout()
        self.OperandsGroupBox.setLayout(self.left_vertical_layout)

        self.lr_label = QLabel("Current lr : {}".format(self.learning_rate))
        factor_label  = QLabel("Factor : ")

        self.operand_textbox = QLineEdit()
        self.operand_textbox.setText(str(self.initial_operand_value))
        self.onlyFloatValidator = QtGui.QDoubleValidator()
        #self.onlyFloatValidator = FloatNotEmptyValidator()
        self.operand_textbox.setValidator(self.onlyFloatValidator)

        self.left_vertical_layout.addWidget(self.current_epoch_label_tab2)
        self.left_vertical_layout.addWidget(self.current_batch_label_tab2)

        self.left_vertical_layout.addStretch(1)
        self.left_vertical_layout.addWidget(self.lr_label)

        self.left_vertical_layout.addWidget(self.selected_operandQLabel)
        self.left_vertical_layout.addWidget(factor_label)
        self.left_vertical_layout.addWidget(self.operand_textbox)

        self.OperatorsGroupBox = QGroupBox( "Operators" )
        self.horizontalLayout_tab2.addWidget( self.OperatorsGroupBox )

        self.right_vertical_layout = QVBoxLayout()
        self.OperatorsGroupBox.setLayout( self.right_vertical_layout )
        button1 = QPushButton( '+' )
        button1.clicked.connect(lambda: self.on_click('+'))

        button2 = QPushButton( '-' )
        button2.clicked.connect(lambda: self.on_click('-'))

        button3 = QPushButton( '*' )
        button3.clicked.connect(lambda: self.on_click('*'))

        button4 = QPushButton( '/' )
        button4.clicked.connect(lambda: self.on_click('/'))

        button5 = QPushButton( 'f(x)=x' )
        button5.clicked.connect(lambda: self.on_click('f(x)=x'))

        self.right_vertical_layout.addStretch(1)
        self.right_vertical_layout.addWidget( button1 )
        self.right_vertical_layout.addWidget( button2 )
        self.right_vertical_layout.addWidget( button3 )
        self.right_vertical_layout.addWidget( button4 )
        self.right_vertical_layout.addWidget( button5 )


        print("tab2 set up")

    @pyqtSlot()
    def on_click(self, selected_operator='f(x)=x'):
        assert selected_operator in('+','-','/','*','f(x)=x')
        self.selected_operandQLabel.setText('\t{}'.format(selected_operator))
        print(self.selected_operandQLabel.text().strip())

        operand = self.operand_textbox.text()

        if operand == '':
            print('no command send since operand field was empty')

        else:

            eff_lr =calculate_efffective_lr(
                initial_lr=self.learning_rate, 
                operator=self.selected_operandQLabel.text().strip(), 
                operand=float(operand))

            self.tab2_payload = {'learning_rate':eff_lr}
            # calculate effective learning rate and publish to backend
            print(self.tab2_payload)
            self.send_payload()

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    print('App Init Done.')
    sys.exit(app.exec_())
    print('Done')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    print('App Init Done.')
    sys.exit(app.exec_())
    print('Done')