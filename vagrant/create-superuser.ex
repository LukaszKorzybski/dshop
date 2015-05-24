#!/usr/bin/expect -f
spawn python ./manage.py createsuperuser
expect "Username"
send "dshop\r"
expect "E-mail address:"
send "dshop@example.com\r"
expect "Password:"
send "dshop\r"
expect "Password (again):"
send "dshop\r"
interact