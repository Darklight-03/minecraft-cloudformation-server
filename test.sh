#!/bin/bash
for D in tst/lambda/*; do
    if [ -d "${D}" ]; then
        function_name=$(basename "${D}")

        # copy the tests into build
        echo "copying ${function_name} tests" 
        cp -r "${D}"/* "build/${function_name}"
    fi
done
echo "executing tests"
cd build || exit
pytest || { echo "tests failed, exiting" ; exit 1; }
cd .. || exit