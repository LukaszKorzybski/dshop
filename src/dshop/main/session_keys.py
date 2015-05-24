# -*- coding: utf-8 -*-

''' List of all session keys that are in use in application.

    This module mainly serves as documentation to developers, so we know what
    sits in session objects, what keys are already reserved for what.
'''

# Client login timestamp
login_time = 'login_time'

# Id of currently logged in client
client_id = 'client_id'

# Authorization level of currently logged in client, see dshop.settings module for more details.
# 0 - not logged in (no access to restricted areas) , 1 - partial access , 2 - full access
auth_level = 'auth_level'

# Shopping cart id, always available (added by middleware)
cart = 'cart_id'

# Return url from shopping cart
cart_return_url = 'cart_return_url'