#!/bin/bash

if [ "${@}" ]; then
  pip3 install ${@}
  python3 -m pip freeze >requirements.txt
else
  python3 -m pip freeze >requirements.txt
  pip3 install -r requirements.txt
fi
