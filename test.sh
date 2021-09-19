#!/bin/bash

# clean build folder
./clean.sh

# copy files into build folder
for D in src/lambda/*; do
    if [ -d "${D}" ]; then
        function_name=$(basename "${D}")
        echo "Copying ${function_name} to build/" 
        cp -r "${D}/" "build/${function_name}"
    fi
done
for D in tst/lambda/*; do
    if [ -d "${D}" ]; then
        function_name=$(basename "${D}")
        echo "copying ${function_name} tests" 
        cp -r "${D}"/* "build/${function_name}"
    fi
done

### Test ###

echo "executing tests"
cd build || exit
pytest || { echo "tests failed, exiting" ; exit 1; }
cd .. || exit