#!/bin/bash

# install global requirements and create build folder
echo "Installing requirements"
pip install -r requirements.txt > /dev/null 2>&1
mkdir build > /dev/null 2>&1

# install requirements for each function
for D in src/lambda/*; do
    if [ -d "${D}" ]; then
        function_name=$(basename "${D}")
        echo "Installing ${function_name} requirements" 
        pip install -r "${D}/requirements.txt" > /dev/null 2>&1
    fi
done