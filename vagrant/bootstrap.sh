#!/usr/bin/env bash

# Locale
locale-gen pl_PL.UTF-8
update-locale

# Base software
apt-get update
apt-get install -y vim
apt-get install -y unzip
apt-get install -y python-pip

# DShop software dependencies
apt-get install -y libxml2-dev 
apt-get install -y libxslt-dev
apt-get install -y python-dev
apt-get install -y postgresql
apt-get install -y libpq-dev
apt-get install -y sphinxsearch
apt-get install -y apache2

# Python modules
pip install -r /vagrant/vagrant/requirements.txt

# Apache
rm -rf /var/www
ln -s /vagrant/src /var/www
#cp /vagrant/dshop.vhost /etc/apache2/sites-available/dshop
#a2ensite dshop
#/etc/init.d/apache2 restart

# PostgreSQL
export PGPASSFILE=/vagrant/vagrant/pgpass

PG_CLUSTER=$(pg_lsclusters | cut -d ' ' -f 1 | tail -n 1)
pg_dropcluster --stop $PG_CLUSTER main
pg_createcluster --locale pl_PL.UTF8 --start $PG_CLUSTER main

sudo -u postgres psql -c "create user dshop with superuser createdb password 'dshop';"
sudo -u postgres psql -c "create database dshop_devel with encoding 'utf8' lc_ctype 'pl_PL.UTF8' owner dshop;"
sudo -u postgres psql -f


tar -xzf /vagrant/vagrant/dshop_optionall.sql.tgz
chmod +x /vagrant/vagrant/load_database.ex
/vagrant/load_database.ex

# Sphinx search
cp /vagrant/vagrant/sphinx.conf /etc/sphinxsearch

wget https://github.com/szoper/sphinxsearch-wordforms-pl/raw/master/pl_PL.UTF-8.txt.zip
unzip pl_PL.UTF-8.txt.zip
rm pl_PL.UTF-8.txt.zip
mv pl_PL.UTF-8.txt /var/lib/sphinxsearch
chown sphinxsearch /var/lib/sphinxsearch/pl_PL.UTF-8.txt

/usr/bin/indexer --quiet --rotate --all

echo 'START=yes' > /etc/default/sphinxsearch
/etc/init.d/sphinxsearch start

# Source files

