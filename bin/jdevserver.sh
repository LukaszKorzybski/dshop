DD=""
if [[ $1 == 'jdebug' ]]
then
    DD='-J-Xdebug -J-Xrunjdwp:transport=dt_socket,server=y,address=8888,suspend=n'
fi

jython $DD $DSHOP_SRC_DIR/dshop/manage.py runserver 0.0.0.0:8000