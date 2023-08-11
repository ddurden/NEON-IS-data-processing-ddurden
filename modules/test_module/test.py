#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import inspect
import structlog
from common.err_datum import err_datum_path

log = structlog.get_logger()


def test_err_datum_path () -> None:
    try:
        x = 4/0
    except:
        err_datum_path(err = 'error testing bad input path',DirDatm = 'qfs/proc_group/prt/2019/01/01/27134',
                                                     DirErrBase = 'pfs/proc_group_out/errored_datums',
                                                    RmvDatmOut = True, DirOutBase = 'pfs/proc_group_out')
        err_datum_path(err='error testing correct input path',DirDatm='pfs/proc_group/prt/2019/01/01/27134',
                       DirErrBase='pfs/out/errored_datums',
                       RmvDatmOut=True)

if __name__ == '__main__':
    test_err_datum_path()
