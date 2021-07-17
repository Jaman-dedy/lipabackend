#!/bin/bash

git push heroku-staging ${1:-"HEAD:main"}
