# #!/bin/bash
# cd matrix
# echo "Running rgbmatrix installation..."
# sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y
# make build-python
# sudo make install-python
# cd bindings
# sudo pip install -e python/
# cd ../../
# echo "Installing required dependencies. This may take some time (10-20 minutes-ish)..."
# git reset --hard
# git checkout master
# git fetch origin --prune
# git pull
# sudo apt-get install libxml2-dev libxslt-dev python-lxml
# sudo pip install requests datetime pytz tzlocal
# mkdir -m 777 logos
# echo "If you didn't see any errors above, everything should be installed!"
# echo "Installation complete! Play around with the examples in matrix/bindings/python/samples to make sure your matrix is working."

#!/bin/bash
echo "Installing required dependencies. This may take some time (10-20 minutes-ish)..."
sudo apt-get update && sudo apt-get install python3-dev python3-pip python3-pillow libxml2-dev libxslt-dev -y
sudo pip3 install pytz tzlocal requests
echo "Running rgbmatrix installation..."
mkdir submodules
cd submodules
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git matrix
cd matrix
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
echo "If you didn't see any errors above, everything should be installed!"
echo "Installation complete! Play around with the examples in matrix/bindings/python/samples to make sure your matrix is working."