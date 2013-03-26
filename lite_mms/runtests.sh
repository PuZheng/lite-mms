#! /bin/bash

find . -name "test_*.py" -exec py.test {} \;
