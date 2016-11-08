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
verbose=0

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

    def data_anonymized(column,data_type):
        string_types="varchar,char,binary,varbinary,text,mediumtext,longtext,blob,mediumblob,longblob"
        if re.search(r''+ data_type +'', string_types, re.M|re.I):
           #return " REPEAT(\'*\', LENGTH(\`"+column+"\`))"
           return " right(md5("+ column+ "), length(" + column +")) "
        else:
           return 0

    def export_data():
       try:
           for db in database:
               sql="SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA='" + str(db) + "' AND TABLE_TYPE <> 'VIEW' AND TABLE_NAME NOT IN (" + "'%s'" %"','".join(ignore_tables) + ")"
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
                   sql="SELECT table_name, column_name cols, data_type FROM information_schema.columns where TABLE_SCHEMA='"+str(db) +"' and  table_name ='"+str(tbl[0])+"'"
                   #print sql
                   cursor.execute(sql)
                   # Start dumping
                   resultset=cursor.fetchall()
                   columns=[]
                   for rs in resultset:
                       phrase="%s" %",".join(ignore_columns)
                       word="\\b" + rs[1] + "\\b"
                       if re.search(r''+word, phrase,flags=re.IGNORECASE):
                          columns.append(str(data_anonymized(rs[1],rs[2])))
                          #print "Table:"+ str(tbl[0])+ " " + str(word) + ""
                       else:
                          columns.append("\`"+str(rs[1]+"\`"))
                       #print rs[0] +"---"+rs[1] + "---" + str(data_anonymized(rs[2])) + "-" + rs[2]
                   sql="SELECT SQL_NO_CACHE " + str(','.join(columns)) + " INTO OUTFILE '"+ output_path + "/"+str(tbl[0]) +".txt' FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\\\"'  FROM "+ str(tbl[0])
                   cmd='mysql -h'+server + ' -u'+admin_user+' -p'+admin_pass + ' '+ db +' --execute=\"'+ sql +'\"'
                   if verbose:
                       print sql.replace('\\','') + "\n"
                   status,out=commands.getstatusoutput(cmd)
                   if status !=0:
                      raise ValueError(str(out.replace(admin_pass,'*******')) )
                   cmd="mysqldump -h"+server + " -u"+admin_user+" -p"+admin_pass + " --no-data "+ db +" " + str(tbl[0])  + " > "+ output_path + "/"+str(tbl[0]) + ".sql"
                   #if verbose:
                   #     print (color.CYAN+str(cmd.replace(admin_pass,'*******'))+color.END+ "\n")
                   status,out=commands.getstatusoutput(cmd)
                   if status !=0:
                      raise ValueError(str(out.replace(admin_pass,'*******')) )
           cursor.close()
           cnx.close()
       except (KeyboardInterrupt, SystemExit):
           raise

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

    parser.add_argument('--verbose', dest='verbose', action='store_true',
                   help='Print info about the various stages. ')

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
    if args.verbose:
       verbose=args.verbose
    # Start data export
    export_data()
except Exception, err:
       end_sub(color.RED +  str(err) + color.END)
