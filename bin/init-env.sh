# Setup dshop shell environment, it is necessery if you want to use shell scripts
# bundled with dshop (for eg. dshop-shell.sh which runs dshop interactive console)
#
#export WEBAPP_ROOT_DIR='Your installation root dir'

function die() {
    echo "WEBAPP_ROOT_DIR not set. Please set WEBAPP_ROOT_DIR first!"
    exit 1
}
[[ $WEBAPP_ROOT_DIR != "" ]] || die

export PATH=$WEBAPP_ROOT_DIR/bin:$PATH
export PYTHONPATH=$WAPP_SD:$WAPP_RD/lib
export JYTHONPATH=$WAPP_SD:$WAPP_RD/lib

export CLASSPATH="$WAPP_SD/lib/*"