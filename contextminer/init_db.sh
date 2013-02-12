#!/bin/bash
echo Killing all mongod and mongos
killall mongod
killall mongos

echo Erasing data folder
rm -rf ./data

mkdir ./data
touch ./data/log
echo $(pwd)

mongod --rest --dbpath data --logpath data/log --fork

sleep 10
mongo contextminer db.js
