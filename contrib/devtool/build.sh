#! /bin/sh

cd ../../docs
echo "Building Documents"
make html

cd ..

cd python2

echo "Python 2.4"
python2.4 setup.py sdist bdist_egg upload

echo "Python 2.5"
python2.5 setup.py bdist_egg upload

echo "Python 2.6"
python2.6 setup.py bdist_egg upload

cd ..
cd python3

echo "Python 3.0"
python3.0 setup.py bdist_egg upload

echo "Python 3.1"
python3.1 setup.py bdist_egg upload
python3.1 setup.py sdist

cd contrib/devtool
