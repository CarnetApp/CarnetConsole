import os
import sys
import signal
import gettext

VERSION = '0.1.0'
pkgdatadir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
localedir = '/usr/local/share/locale'

sys.path.insert(1, pkgdatadir)
signal.signal(signal.SIGINT, signal.SIG_DFL)
gettext.install('carnettty', localedir)

if __name__ == '__main__':
    print(pkgdatadir)
    from carnettty import main
    sys.exit(main.main(VERSION))