# Acknowledgement
  
This project is supported by [Segmind](https://segmind.com)

# keras JukeBox

This is a UI based hyper-parameter controller, which let's you control the following.

* start, pause and stop a live training.
* reset the learning rate on dynamically while training is in progress.

more functionalities are to be added

# Dependencies

This package depends on **MQTT** protocol for communication. So, it is expected that an MQTT broker is up and running in 'localhost' at port 1883(default port).

Install it by :

```

sudo apt-get update
sudo apt-get install mosquitto
sudo apt-get install mosquitto-clients

```

Python dependencies:

* python >= 3.6.8
* paho-mqtt
* PyQt5
* tensorflow >= 1.14

**Note: This package is intended and tested for tensorflow-keras api and NOT keras with tensorflow 'backend'**

# Usage

import as 

```

from keras_JukeBox import JukeBoxCallback

```

and pass it to the fit method of `keras.model`

as follows :

```

model.fit(train_images, train_labels, epochs=20, callbacks=[JukeBoxCallback(verbose=True)])

```

and run your training script. You will note that the script gets blocked, this is because it is waiting for a JukeBox UI to capture it's session. 
Now, in a separate terminal, type:

```

start_JukeBox

```

and you should see the UI pop up, note the algorithm is in **pause** mode by default. Hit the play button to start the training.