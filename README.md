# volleyball_project

This project is designed to use deep learning methods in Volleyball
Sports Data Analytics.

Helpful links:

- https://github.com/dmlc/decord
- https://dev.to/mfts/how-to-write-a-perfect-readme-for-your-github-project-59f2
- https://dev.to/mfts/how-to-write-a-perfect-readme-for-your-github-project-59f2
- https://www.freecodecamp.org/news/how-to-write-a-good-readme-file/

# tasks:

1. volleyball actions/objects detection :

- [x] sets
- [x] spikes
- [x] blocks
- [x] receives
- [x] ball

2. volleyball game-state detection:

- [x] in-play scenes
- [x] no-play scenes
- [x] service scenes

3. Integrated the project with DB.

## Video Analysis

- [ ] Setter sets distribution.
- Ball trajectories for:
    - [ ] sets
    - [ ] receives
    - [ ] serves
- [ ] receives distribution for setters.
- [ ] spike zones and distributions.
- [ ] blocks and sets and how they are related with successful spikes.
- [ ] umpire/referee gesture recognition for score detection.
- [ ] Objects Visualizations
- [ ] Find bounce points.

## ML:

- [x] Try Intel OpenVino...
- [x] Add object detection results to the DB.
- [x] Use batch prediction for 30 frames.
- [x] Add ball detection and its results to DB.

## BackEnd:

- Integrate video clipping:
    - [x] Add AI-based video-clipper.
    - [x] add DB integration for video storage.
    - [x] Integrate FastAPI for API calls.
    - [ ] Add RabbitMQ for job scheduling.
    - [ ] Work with decord for faster video reading/writing.

# Readme file:

- [ ] Publish datasets ...
- [ ] Publish model weights ...
- [ ] Add notes about how to generate videos.(description about notebooks)
- [ ] Add gif from game-state detection model.
- [ ] Add gif from volleyball objects detection model.
- [ ] Add gif from volleyball ball segmentation model.
- [ ] Add descriptions about accuracy/recall/ ...
- [ ] Add description about how to run each model and get a demo.
- [ ] Add notes about how to improve.
- [ ] Add notes about how to set up the postgres/mysql.