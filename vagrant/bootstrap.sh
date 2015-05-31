#!/usr/bin/env bash

function die() {
    printf "${1}.\n"
    printf "Provisioning aborted due to errors. Check console output for details.\n"
    exit 1
}

cd /vagrant/vagrant

# Locale
locale-gen en_GB.UTF-8
locale-gen pl_PL.UTF-8
update-locale

# Base software
apt-get update
apt-get install -y vim
apt-get install -y unzip
apt-get install -y curl
apt-get install -y expect
apt-get install -y python-pip

# Download database data dump
if [ ! -f ../dshop-data.url ]
then
    die "dshop-data.url file is missing. Please read README.md file and try again"    
fi

DB_DUMP_URL=$(cat ../dshop-data.url | head -n 1)
curl -L -o dshop-data.sql "$DB_DUMP_URL" || die "Downloading DB dump file failed"

# DShop software dependencies
apt-get install -y libxml2-dev 
apt-get install -y libxslt-dev
apt-get install -y python-dev
apt-get install -y postgresql
apt-get install -y libpq-dev
apt-get install -y sphinxsearch
apt-get install -y apache2

# Python modules
pip install -r requirements.txt || die "Installing Python modules failed"

# Apache
rm -rf /var/www
ln -s /vagrant/src /var/www
#cp dshop.vhost /etc/apache2/sites-available/dshop
#a2ensite dshop
#/etc/init.d/apache2 restart

# PostgreSQL
export PGPASSFILE=pgpass
chmod 600 pgpass

PG_CLUSTER=$(pg_lsclusters | cut -d ' ' -f 1 | tail -n 1)
pg_dropcluster --stop $PG_CLUSTER main
pg_createcluster --locale pl_PL.UTF8 --start $PG_CLUSTER main

sudo -u postgres psql -c "create user dshop with superuser createdb password 'dshop';"
sudo -u postgres psql -c "create database dshop_devel with encoding 'utf8' lc_ctype 'pl_PL.UTF8' owner dshop;"

psql -h localhost -U dshop -f dshop-schema.sql dshop_devel 1>/dev/null
psql -h localhost -U dshop -f dshop-data.sql dshop_devel 1>/dev/null

# Sphinx search
cp sphinx.conf /etc/sphinxsearch

curl -L -O https://github.com/szoper/sphinxsearch-wordforms-pl/raw/master/pl_PL.UTF-8.txt.zip || die "Downloading polish word forms for Sphinx Search failed"
unzip pl_PL.UTF-8.txt.zip
rm pl_PL.UTF-8.txt.zip
mv pl_PL.UTF-8.txt /var/lib/sphinxsearch
chown sphinxsearch /var/lib/sphinxsearch/pl_PL.UTF-8.txt

/usr/bin/indexer --quiet --rotate --all

echo 'START=yes' > /etc/default/sphinxsearch
/etc/init.d/sphinxsearch start

# Dshop 
cp settings_local.py /vagrant/src/dshop

chmod +x create-superuser.ex
cd ../src/dshop
../../vagrant/create-superuser.ex
cd ../../vagrant

cp run.template /home/vagrant/run
chmod +x /home/vagrant/run
chown vagrant:vagrant /home/vagrant/run