#!/bin/bash
PKGS="python2.7-dev python-pillow libxml2-dev libxslt-dev python-lxml"

for pkg in $PKGS ; do
    if [ "dpkg-query -W $pkg | awk {'print $1'} = """ ]; then
        echo -e "$pkg is already installed"
    else
        apt-get -qq install $pkg
        echo "Successfully installed $pkg"
    fi
done