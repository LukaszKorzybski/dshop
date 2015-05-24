#!/usr/bin/expect -f
spawn psql -h localhost -U dshop_optionall -d dshop_optionall -f /vagrant/dshop_optionall.sql
expect "assword:"
send "dshop_optionall\r"
interact