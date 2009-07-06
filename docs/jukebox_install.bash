#!/bin/bash
if [ -z $1 ]; then
   ENVDIR=jukebox_env
else
   ENVDIR=$1
fi

MYSQL_CONFIG=`which mysql_config`
if [ $? -ne 0 ]; then
   echo "ERROR: mysql_config not found on your system! Maybe it's in package 'libmysqlclient-dev'?"
   exit 1
fi

virtualenv --no-site-packages ${ENVDIR}
cd ${ENVDIR}
source bin/activate
easy_install "SQLAlchemy<0.6"
easy_install ply==2.3
easy_install shoutpy==1.0.0
easy_install scrobbler
easy_install simplejson==1.3
easy_install mutagen==1.15

wget http://downloads.us.xiph.org/releases/libshout/shout-python-0.2.1.tar.gz
tar xzf shout-python-0.2.1.tar.gz
cd shout-python-0.2.1
python setup.py install
cd ..
rm -rf shout-python-0.2.1
rm shout-python-0.2.1.tar.gz

wget http://garr.dl.sourceforge.net/sourceforge/mysql-python/MySQL-python-1.2.2.tar.gz
tar xzf MySQL-python-1.2.2.tar.gz
cd MySQL-python-1.2.2
python setup.py install
cd ..
rm -rf MySQL-python-1.2.2
rm MySQL-python-1.2.2.tar.gz

svn co http://svn.foobar.lu/wickedjukebox/trunk jukebox

echo "=============================================================================="
echo "   Jukebox core system installed.                                             "
echo "       Please see jukebox/INSTALL for further instructions!                   "
echo "=============================================================================="
