#!/bin/bash

function die() {
    echo "DSHOP_ENV_SET not set. Please set enviroment first!"
    exit 1
}

[[ $DSHOP_ENV_SET != "" ]] || die

ipython $DSHOP_SRC_DIR/dshop/shell_init.py