#! /bin/sh

cd ../../python2

echo "Python 2.4"
python2.4 run_tests.py --all
python2.4 tests/test_interprocess_low.py -primary -growl &
python2.4 tests/test_interprocess_low.py -secondary -growl
python2.4 tests/test_interprocess.py -primary -growl &
python2.4 tests/test_interprocess.py -secondary -growl

echo "Python 2.5"
python2.5 run_tests.py --all
python2.5 tests/test_interprocess_low.py -primary -growl &
python2.5 tests/test_interprocess_low.py -secondary -growl
python2.5 tests/test_interprocess.py -primary -growl &
python2.5 tests/test_interprocess.py -secondary -growl

echo "Python 2.6"
python2.6 run_tests.py --all
python2.6 tests/test_interprocess_low.py -primary -growl &
python2.6 tests/test_interprocess_low.py -secondary -growl
python2.6 tests/test_interprocess.py -primary -growl &
python2.6 tests/test_interprocess.py -secondary -growl

cd ..
cd python3

echo "Python 3.0"
python3.0 run_tests.py --all

echo "Python 3.1"
python3.1 run_tests.py --all

echo "Python 3.1 & single thread version"
python3.1 run_tests.py --single-thread --basic

cd ..
cd ruby

echo "Ruby 1.8"
ruby setup.rb test

echo "Ruby 1.9"
ruby1.9 setup.rb test

cd ../contrib/devtool
