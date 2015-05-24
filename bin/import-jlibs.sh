#!/bin/bash
#
# Build and import complete PerfektShop java libraries into the project.
# Requires PSHOP_ROOT_DIR shell variable to be set. Uses ant to rebuild pshop.

function die() {
    echo "DSHOP_ENV_SET not set. Please set enviroment first!"
    exit 1
}

function rebuild_perfektshop() {
    if ant -version 2>/dev/null 1>&2
    then
        cd $PSHOP_ROOT_DIR
        ant dist-jython
    else
        echo "ant executable not found, skipping perfektshop build step."
    fi
}

function import-jlibs() {
    [[ -d $DSHOP_JLIB_DIR/pshop ]] || mkdir -p $DSHOP_JLIB_DIR/pshop

    rm -f $DSHOP_JLIB_DIR/pshop/*.jar
    cp $PSHOP_ROOT_DIR/dist/jython-build/*.jar $DSHOP_JLIB_DIR/pshop
    echo ""
    echo "Imported $(ls $PSHOP_ROOT_DIR/dist/jython-build/*.jar | wc -l) PerfektShop jar files to $DSHOP_JLIB_DIR directory"
    echo ""
}

function main() {
    [[ $DSHOP_ENV_SET != "" ]] || die
    rebuild_perfektshop
    import-jlibs
}

main