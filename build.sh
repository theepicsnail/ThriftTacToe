#!/bin/bash
echo "Generating thrift libraries"
thrift --gen py -o python ttt.thrift
