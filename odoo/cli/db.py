import optparse
import os
import sys

import odoo
from . import Command
from odoo.service import db
from odoo.http import dispatch_rpc


class Db(Command):

    def run(self, cmdargs):
        parser = optparse.OptionParser(
            prog="%s start" % sys.argv[0].split(os.path.sep)[-1],
            description=self.__doc__
        )
        parser.add_option("-d", "--database", dest="db_name", default=None,
                          help="Specify the database name (default to project's directory name")
        parser.add_option('--restore_db_file',
                          help="Directory where your project's modules are stored (will autodetect from current dir)")
        parser.add_option('--master_password',
                          help="Specify the master password if need it.")

        # group = optparse.OptionGroup(parser, "Command")
        parser.add_option("--drop", action="store_true", help="Command drop database.")
        parser.add_option("--restore", action="store_true", help="Command restore database.")
        parser.add_option("--list", action="store_true", help="Command list database.")
        parser.add_option("--list_incompatible_db", action="store_true", help="Command list database incompatible.")
        parser.add_option("--version", action="store_true", help="Command show odoo version.")

        opt, args = parser.parse_args(cmdargs)

        die(bool(opt.drop) and bool(opt.restore) and bool(opt.list) and bool(opt.version) and bool(
            opt.list_incompatible_db),
            "Can only run one command, --drop, --list, --version, --list_incompatible_db or --restore.")

        die(bool(opt.restore) and not bool(opt.restore_db_file),
            "Missing argument --restore_db_file of option --restore.")

        die(bool(opt.restore) and not bool(opt.db_name),
            "Missing argument --database of option --restore.")

        die(bool(opt.drop) and not bool(opt.db_name),
            "Missing argument --database of option --drop.")

        with odoo.api.Environment.manage():
            if opt.list:
                lst_db = db.list_dbs()
                for db_obj in lst_db:
                    print(db_obj)
            elif opt.list_incompatible_db:
                lst_db = db.list_db_incompatible(db.list_dbs())
                for db_obj in lst_db:
                    print(db_obj)
            elif opt.drop:
                master_password = opt.master_password if opt.master_password else 'admin'
                dispatch_rpc('db', 'drop', [master_password, opt.db_name])
            elif opt.restore:
                db.restore_db(opt.db_name, opt.restore_db_file, False)
            elif opt.version:
                print(db.exp_server_version())
            else:
                parser.print_help(sys.stderr)
                die(True, "ERROR, missing command")


def die(cond, message, code=1):
    if cond:
        print(message, file=sys.stderr)
        sys.exit(code)
