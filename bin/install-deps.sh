#!/bin/bash
#
# Install development and runtime python dependencies for djangoshop project

# TODO: install django patch for jython (thix fix in core/management/__init__.py)
# TODO: get jython executable from command line param
# TODO: provide full sphinx config

PYTHON_BIN="jython"
LOG_FILE="dshop-ideps.log"
PREFIX="/usr/local"

JYTHON_HOME=`which jython`
JYTHON_HOME=${JYTHON_HOME%/jython}

function die() {
    echo $1
    exit 1
}

function check_deps() {
    which $PYTHON_BIN 2>/dev/null || die "$PYTHON_BIN command missing! Please install Jython 2.5.x"
    which wget 2>/dev/null || die "wget command missing!"
    which svn 2>/dev/null || die "svn command missing!"
    which gcc 2>/dev/null || die "gcc compiler missing!"
    which make 2>/dev/null || die "make command missing!"
}

function pymod_tarball() {
    echo "" && echo "Installing $1" && echo ""
    url=$2
    fname="pymod.tgz"
    tmpdir="ideps-$1"

    mkdir $tmpdir && cd $tmpdir 
    wget -O $fname $url 
    tar -xzf $fname && rm $fname
    cd *
    $PYTHON_BIN setup.py install || die "Installation of $1 python module failed."
    cd ../..
}

function pymod_svn() {
    echo "" && echo "Installing $1" && echo ""
    url=$2
    dname="pymod"
    tmpdir="ideps-$1"

    mkdir $tmpdir && cd $tmpdir 
    svn co $url $dname
    cd $dname 
    $PYTHON_BIN setup.py install || die "Installation of $1 python module failed."
    cd ../..
}

function install_sphinx() {
    curr=`pwd`
    prefix=$1
    tmpdir="ideps-sphinx"

    echo "" && echo "Installing Sphinx 0.9.9rc2" && echo ""
    mkdir $tmpdir && cd $tmpdir
    wget -O sphinx.tgz "http://www.sphinxsearch.com/downloads/sphinx-0.9.9-rc2.tar.gz"
    tar -xzf sphinx.tgz && rm sphinx.tgz
    cd *
    ./configure --with-pgsql --without-mysql --prefix=$prefix  || die "Configure for Sphinx failed."
    make install || die "Installation of Sphinx failed."

    cp api/sphinxapi.py $JYTHON_HOME/Lib/site-packages

    mkdir $prefix/share/sphinx
    cd $prefix/share/sphinx
    wget --http-user gosc --http-password '$!optioGosc!' http://fileshare.optionall.pl/pl-utf8.txt || die "Download of Polish wordforms failed."
    cd $curr
}

function main() {
    check_deps

    # install setuptools python utility
    pymod_tarball "setuptools" "http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c9.tar.gz#md5=3864c01d9c719c8924c455714492295e"

    # install Django
    pymod_tarball "django" "http://www.djangoproject.com/download/1.0.3/tarball/"

    # install django-jython extension (JDBC-based DB driver and WAR deployment utility)
    pymod_svn "django-jython" "http://django-jython.googlecode.com/svn/trunk/"

    # install django-compress extension
    pymod_svn "django-compress" "http://django-compress.googlecode.com/svn/trunk/"

    # install django-mptt
    pymod_svn "django-mptt" "http://django-mptt.googlecode.com/svn/trunk/"

    # install sphinx
    install_sphinx $PREFIX

    # install premailer
    easy_install premailer

    echo ""
    echo "Please manually configure Sphinx, use config sections from DSHOP_ROOT_DIR/fts/sphinx.conf"
    echo "If you are creating database from scratch don't forget to run DSHOP_ROOT_DIR/fts/install-fts.sql on the DB."
    echo ""
}

main
