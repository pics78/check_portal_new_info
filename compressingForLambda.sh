#!/bin/bash

cd $(dirname $0)

mkdir temp
cp -r $(ls -I README.md -I compressingForLambda.sh -I local -I modules -I temp) modules/*  temp/

cd temp
echo PRD > env/environment
zip -r ../packaging.zip *

cd ..; rm -r temp/