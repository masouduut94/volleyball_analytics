
<h1 align="center">
    Volleyball Analytics
</h1>
<h1 align="center">
    <img src="data/wiki/images/coach2.jpg">
</h1>
    


# What is Volleyball Analytics?

Volleyball analytics involves the use of statistical data and 
advanced metrics to analyze and evaluate various aspects of 
volleyball performance. The goal is to gain insights into player 
and team performance, identify strengths and weaknesses, 
and make informed decisions to improve overall efficiency and effectiveness 
on the court.

Volleyball analytics leverages technology, such as sensors and video
analysis, to collect and process data, offering valuable insights 
for coaches, players, and teams to enhance their training, 
strategy, and overall performance.

# Introduction
This machine learning project consists of a 3-step process which is able to get live broadcast feed as input, 
and outputs statistical data.

These are the ML components that made this MLOps possible:

- VideoMAE model: This is a module that can classify videos in real-time. This model is trained on a 
    custom dataset and it gets 30 frames as input, and outputs `service`, `play`, `no-play` as output.
  - service indicates the start of the play when a player tosses the ball to serve it.
  - play indicates the periods of game where the players are playing and the game is on.
  - no-play indicates the periods of the game where the players are not playing.
- Yolov8 model: This state-of-the-art model for object detection is trained on a dataset which includes 
   several objects along with several volleyball actions.

Let's see some demos to get some idea:

### Demo 1: FRANCE - POLAND

![demo1](data/wiki/gifs/11_f1.gif)

### Demo 2: USA - CANADA

![demo2](data/wiki/gifs/20_2_demo.gif)

### Demo 3: USA - POLAND

![demo3](data/wiki/gifs/22_2_DEMO.gif)

There is a text on the left top corner of video that indicates the output of 
video classification output.

The annotated objects in these videos are:

- Red box: volleyball ball
- Brown box: volleyball service action
- Green box: volleyball reception action.
- Blue box: volleyball setting action.
- Purple box: volleyball blocking action.
- Orange box: volleyball spike action.

the third step is to use the generated data to find insights about the game. 
for example, in the below gif, one of the ace points is fetched 

### Demo 4: FRANCE - POLAND

![demo2](data/wiki/gifs/ace.gif)

Development
---------

The whole project is developed with python 3.11. 

The running scripts to make demos are listed here:

- `src/demo.py`: It uses both video classification + yolo in the inference code and 
    outputs the demos just like the ones shared here.
- `src/VideoMAE_inference.py`: Only runs inference with video classification.
- `src/yolo_inferece.py`: Runs inference with yolo v8 object detection.

To run models along with data storage, you must install some dependencies:

- install Postgres sql.
- create a yaml file on `conf` directory named `db_conf.yaml`, and put these values on it.
  - development:
  - - user: "user"
  - - password: "something"
  - - db: "volleyball_development"
  - - host: "some_ip"
  - - port: 5432
  - - dialect: 'postgresql'
  - - driver: 'psycopg2'
  - test:
  - - user: "user2"
  - - password: "something"
  - - db: "volleyball_test"
  - - host: "some_ip"
  - - port: 5432
  - - dialect: 'postgresql'
  - - driver: 'psycopg2'

- After that run `make install`, `make test` to install dependencies 
   and run the backend tests.
- Then run this on root directory: `uvicorn src.backend.app.app:app`
- Now you can run the `src/main.py`
