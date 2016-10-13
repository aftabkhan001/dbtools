#!/usr/bin/python
import sys, os, commands, time, re, ConfigParser, datetime, argparse,getpass
from ConfigParser import SafeConfigParser
import mysql.connector

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

database=[]
ignore_columns=[]
ignore_tables=[]
server="localhost"
admin_user=""
admin_pass=""
output_path="/tmp"

try:

    def log_status(msg):
       print(str(time.ctime()),str(msg))
       return

    def end_sub(msg):
       print(color.RED + str(msg) + color.END)
       sys.exit()

    def db_connect(db_user, passcode,server, server_port=3306):
      try:
           cnx=mysql.connector.connect(user=db_user,password=passcode, host=server, port=server_port,connect_timeout=5,buffered=True)
           cnx.raise_on_warnings=True
           return cnx
      except (KeyboardInterrupt, SystemExit):
           raise
      except Exception, err:
           end_sub(str(err))

    def export_data():
       try:
           for db in database:
               sql="SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA='" + str(db) + "' AND TABLE_NAME NOT IN (" + "'%s'" %"','".join(ignore_tables) + ")"
               cnx=db_connect(admin_user,admin_pass,server)
               cnx.raise_on_warnings=True
               cursor = cnx.cursor()
               cursor.execute(sql)
               if cursor.rowcount <=0:
                  raise ValueError("No tables found in database:" + db)
               else:
                  tables_to_export=cursor.fetchall()
               # Dump data excluding data using --ignore_columns list
               for tbl in tables_to_export:
                   sql="select t1.table_name, GROUP_CONCAT(t1.column_name) cols FROM (select table_name, column_name from information_schema.columns where TABLE_SCHEMA='"+str(db) +"' AND column_name NOT IN ("+"'%s'" %"','".join(ignore_columns) +")) t1 WHERE  t1.table_name ='"+str(tbl[0])+"'"
                   #print sql
                   cursor.execute(sql)
                   # Start dumping
                   resultset=cursor.fetchall()
                   for rs in resultset:
                       sql="SELECT SQL_NO_CACHE " + str(rs[1]) + " INTO OUTFILE '"+ output_path + "/"+str(tbl[0]) +".txt' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\\\"'  FROM "+ str(tbl[0])
                       cmd='mysql -h'+server + ' -u'+admin_user+' -p'+admin_pass + ' '+ db +' --execute=\"'+ sql +'\"'
                       #print cmd
                       status,out=commands.getstatusoutput(cmd)
                       if status !=0:
                          raise ValueError(str(out.replace(admin_pass,'*******')) )
                       cmd="mysqldump -h"+server + " -u"+admin_user+" -p"+admin_pass + " --no-data "+ db +" " + str(tbl[0]) + " | egrep -v " + "'%s'" %"|".join(ignore_columns) + " > "+ output_path + "/"+str(tbl[0]) + ".sql"
                       #end_sub(str(cmd))
                       status,out=commands.getstatusoutput(cmd)
                       if status !=0:
                          raise ValueError(str(out.replace(admin_pass,'*******')) )
           cursor.close()
           cnx.close()
       except (KeyboardInterrupt, SystemExit):
           raise
           end_sub(str(err))

# Read command line args
#myopts, args = getopt.getopt(sys.argv[1:],"",['host=','user=','password=','database=','where=','limit='])

    parser = argparse.ArgumentParser(description="")

    parser.add_argument('--databases', dest='database', type=str, required=True,
                   help='This option is similar to mysqldump "--databases" options. Specify list of databases to dump')

    parser.add_argument('--path', dest='output_dir', type=str, required=True,
                   help='Produce tab(comma)-separated text-format data files. The option value is the directory in which to write the files, (default: %(default)s)', default="/tmp")

    parser.add_argument('--ignore-columns', dest='ignore_columns', default=None,
                   help='Do not dump the specified column. To specify more than one  columns to ignore, use Comma \',\' as separator   ')

    parser.add_argument('--ignore-tables', dest='ignore_tables', default=None,
                   help='Do not dump the specified table. To specify more than one  table to ignore, use Comma \',\' as delimiter')

    parser.add_argument('--host', dest='hostname',
                   help='Connect to host (default: %(default)s)', default="localhost")

    parser.add_argument('--user', dest='db_user',
                   help='User for login, (default: %(default)s)', default='root')

    parser.add_argument('--password', dest='db_pass', default=None,
                   help='Password to use when connecting to server')

    parser.add_argument('--log-error', dest='log_error', type=str,
                   help='Append warnings and errors to given file (default: %(default)s) ', default=None)

    parser.add_argument('--flush-logs', dest='flush_logs', action='store_true',
                   help='Flush logs file in server before starting dump. ')

    args = parser.parse_args()
# processing command-line parameters
    admin_user=args.db_user
    server=args.hostname
    if args.db_pass:
       admin_pass=args.db_pass
    else:
       admin_pass = getpass.getpass("Enter password (" +admin_user +"):")

    if args.database:
       database=args.database.split(',')

    if args.ignore_columns:
       ignore_columns=args.ignore_columns.split(',')

    if args.ignore_tables:
       ignore_tables=args.ignore_tables.split(',')
    if args.output_dir:
       output_path=args.output_dir
   # Start data export
    export_data()
except Exception, err:
       end_sub(color.RED +  str(err) + color.END)
