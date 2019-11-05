# keras JukeBox

This is a UI based hyper-parameter controller, which let's you control the following.

* start, pause and stop a live training.
* reset the learning rate on dynamically while training is in progress.

more functionalities are to be added

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

then in a separate terminal, type:

```

start_JukeBox

```

and you should see the UI pop up, note the algorithm is in **pause** mode by default. Hit the play button to start the training.