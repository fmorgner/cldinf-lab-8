#!/bin/bash

if [ "$1" == "3" ] ; then
  sudo mn --custom clos3.py --topo clos3,leaf=3,spine=3
else
  sudo mn --custom clos.py --topo clos,leaf=3,spine=3 --switch ovs-stp
fi
