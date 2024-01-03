# volleyball_project

This project is designed to use deep learning methods in Volleyball
Sports Data Analytics.

# tasks done:

1. volleyball actions/objects detection :
- sets
- spikes
- blocks
- receives
- ball

2. volleyball game-state detection:
- in-play scenes
- no-play scenes
- service scenes

3. Integrated the project with DB.


# Todo:

## Video Analysis
- [ ] Setter sets distribution.
- [ ] Ball trajectories for:
- - [ ] sets
- - [ ] receives
- - [ ] serves
- [ ] receives distribution for setters.
- [ ] spike zones and distributions.
- [ ] blocks and sets and how they are related with successful spikes.
- [ ] umpire/referee gesture recognition for score detection.
- [ ] Objects Visualizations
- [ ] Find bounce points.


## ML:
- [ ] Try Intel OpenVino...
- [ ] Add object detection results to the DB.
- [ ] Use batch prediction for 30 frames.
- [ ] Add ball detection and its results to DB.
## BackEnd:

- Integrate video clipping:
- - [x] Add AI-based video-clipper.
- - [ ] add DB integration for video storage.
- - [ ] Add RabbitMQ for job scheduling.
- - [ ] Integrate it with flask for backend processes.
- - [ ] Integrate FastAPI for API calls.

## Issues
- - [ ] Fix the issue with clipping the videos where 'service' comes after a `play`.


