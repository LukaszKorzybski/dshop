export WAPP_DIR=/data/www/dshop_optionall
export PYTHONPATH=$WAPP_DIR/src
export DJANGO_SETTINGS_MODULE=dshop.settings

python $WAPP_DIR/src/dshop/wfmag.py sync
