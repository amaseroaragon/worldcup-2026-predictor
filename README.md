# World Cup 2026 Predictor

Dynamic FIFA World Cup 2026 prediction system based on Elo ratings, momentum tracking and Monte Carlo tournament simulations.

## Overview

This project aims to build a continuously updating prediction engine for the 2026 FIFA World Cup.

Unlike static predictors, team ratings evolve after every match depending not only on the final result, but also on performance quality, upset factor and recent form ("momentum").

The system predicts:

* Match outcomes
* Score probabilities
* Group stage standings
* Knockout brackets
* Tournament winner probabilities
* Dynamic team rankings

The project will also include full tournament simulations using Monte Carlo methods in order to estimate how likely each team is to reach every stage of the competition.

## Core Features

Each national team will have a dynamic strength value composed of multiple components:

* Base Elo rating
* Offensive strength
* Defensive performance
* Recent form
* Tournament momentum
* Opponent-adjusted performance
* Contextual adjustments such as host advantage

After every match, ratings will be updated depending not only on the result itself, but also on how expected or unexpected the performance was.

## Tech Stack

The backend will be developed in Python using pandas, numpy and scikit-learn, while the frontend and visualizations will initially be built with Streamlit in order to iterate quickly during the tournament.

Data will be will be dynamically ingested from automated football data APIs, ensuring the predictor updates in near real-time as the tournament progresses.
