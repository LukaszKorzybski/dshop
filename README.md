# DShop

DShop is a Django based e-commerce platform

## Development environment setup

Download and install VirtualBox and Vagrant

Clone Dshop Git repository

In the repository root directory create `dshop-data.url` file. Put into this
file an URL to the DShop database dump file.

Run:

    vagrant up

When that finishes without errors start the application:

    ./run

You can now access the application at `http://localhost:8000`

Admin panel is located at `http://localhost:8000/new-admin/` username/password is 
*dshop/dshop*

PostgreSQL database is *dshop_devel* username/password: *dshop/dshop*

Have fun.