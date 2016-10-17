## Making MySQL backups (Masking sensitive or private information )

The sql_dump client utility performs logical backups, producing CSV text-format data files. It supports `--ignore-columns` option,  to  replace sensitive column values with data mask.

## Requirements
Install following tools/packages
* `Python 2.7.x`
* `mysql connector/python` - e.g. mysql-connector-python-2.0.4.zip

## Usage
```
$ python sql_dump.py   -h
usage: sql_dump.py [-h] --databases DATABASE --path OUTPUT_DIR
                   [--ignore-columns IGNORE_COLUMNS]
                   [--ignore-tables IGNORE_TABLES] [--host HOSTNAME]
                   [--user DB_USER] [--password DB_PASS] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  --databases DATABASE  This option is similar to mysqldump "--databases"
                        options. Specify list of databases to dump
  --path OUTPUT_DIR     Produce tab(comma)-separated text-format data files.
                        The option value is the directory in which to write
                        the files, (default: /tmp)
  --ignore-columns IGNORE_COLUMNS
                        Do not dump the specified column. To specify more than
                        one columns to ignore, use Comma ',' as separator
  --ignore-tables IGNORE_TABLES
                        Do not dump the specified table. To specify more than
                        one table to ignore, use Comma ',' as delimiter
  --host HOSTNAME       Connect to host (default: localhost)
  --user DB_USER        User for login, (default: root)
  --password DB_PASS    Password to use when connecting to server
  --verbose             Print info about the various stages.

```

**Examples**

Below examples use sample database: http://www.mysqltutorial.org/mysql-sample-database.aspx

***Backup***

* Using `--ignore-columns` option

Ignore following columns from all tables ( in this case we have these columns in `customers` table)
customerName, contactLastName, contactFirstName, phone, postalCode, country, addressLine1, addressLine2 

```
$ sudo python sql_dump.py \
> --user dba \
> --ignore-columns customerName,contactLastName,contactFirstName,phone,postalCode,country,addressLine1,addressLine2 \
> --databases classicmodels \
> --path /data/backup/sql_dump/
Enter password (dba):

```
**Output files:**
```
$ ls -lh /data/backup/sql_dump/
total 208K
-rw-r--r-- 1 root  root  2.0K Oct 13 11:14 customers.sql
-rw-rw-rw- 1 mysql mysql 3.9K Oct 13 11:14 customers.txt
-rw-r--r-- 1 root  root  2.2K Oct 13 11:14 employees.sql
-rw-rw-rw- 1 mysql mysql 1.9K Oct 13 11:14 employees.txt
-rw-r--r-- 1 root  root  1.8K Oct 13 11:14 offices.sql
-rw-rw-rw- 1 mysql mysql  174 Oct 13 11:14 offices.txt
...
```
***Restore***

When restoring backup, perform following steps:
* Create database on destination server and disable `foreign key` checks
```
mysql> CREATE DATABASE IF NOT EXISTS classicmodels_REDACTED;
```
* Create tables 
```
cat /data/backup/sql_dump/*.sql | mysql -udba -p classicmodels_REDACTED
```
* Load data files
```
$ cd /data/backup/sql_dump

$ echo 'SET FOREIGN_KEY_CHECKS=0;' > /tmp/load_data.sql

$ for file in $(ls *.txt) ; \
> do table=$(echo $file|sed 's/.txt//g') ; \
> echo "LOAD DATA INFILE '$(pwd)/${file}' REPLACE INTO TABLE $table FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"';" >> /tmp/load_data.sql ; \
> done

$ cat /tmp/load_data.sql | mysql -udba -p classicmodels_REDACTED
Enter password:
```

***Verify***

Examine contents of `customers` table:
```
mysql [classicmodels_REDACTED]> select * from customers limit 10;
+----------------+------------------------------+-----------------+------------------+-------------------+------------------------------+--------------+---------------+----------+------------+-----------+------------------------+-------------+
| customerNumber | customerName                 | contactLastName | contactFirstName | phone             | addressLine1                 | addressLine2 | city          | state    | postalCode | country   | salesRepEmployeeNumber | creditLimit |
+----------------+------------------------------+-----------------+------------------+-------------------+------------------------------+--------------+---------------+----------+------------+-----------+------------------------+-------------+
|            103 | *****************            | *******         | Carine           | **********        | **************               | NULL         | Nantes        | NULL     | 44000      | France    |                   1370 |    21000.00 |
|            112 | ******************           | ****            | Jean             | **********        | ***************              | NULL         | Las Vegas     | NV       | 83030      | USA       |                   1166 |    71800.00 |
|            114 | **************************   | ********        | Peter            | ************      | *****************            | *******      | Melbourne     | Victoria | 3004       | Australia |                   1611 |   117300.00 |
|            119 | *****************            | *******         | Janine           | **********        | **************************** | NULL         | Nantes        | NULL     | 44000      | France    |                   1370 |   118200.00 |
|            121 | ******************           | **********      | Jonas            | **********        | **********************       | NULL         | Stavern       | NULL     | 4110       | Norway    |                   1504 |    81700.00 |
|            124 | **************************** | ******          | Susan            | **********        | ***************              | NULL         | San Rafael    | CA       | 97562      | USA       |                   1165 |   210500.00 |
|            125 | ******************           | *************** | Zbyszek          | *************     | ***************              | NULL         | Warszawa      | NULL     | 01-012     | Poland    |                   NULL |        0.00 |
|            128 | ********************         | ******          | Roland           | ***************** | *************                | NULL         | Frankfurt     | NULL     | 60528      | Germany   |                   1504 |    59700.00 |
|            129 | ***************              | ******          | Julie            | **********        | *************************    | NULL         | San Francisco | CA       | 94217      | USA       |                   1165 |    64600.00 |
|            131 | *****************            | ***             | Kwai             | **********        | ***********************      | NULL         | NYC           | NY       | 10022      | USA       |                   1323 |   114900.00 |
+----------------+------------------------------+-----------------+------------------+-------------------+------------------------------+--------------+---------------+----------+------------+-----------+------------------------+-------------+
10 rows in set (0.00 sec)
```

## Known issues & limitations:
* Error: File already exists
```
ERROR 1086 (HY000) at line 1: File '/data/backup/sql_dump//customers.txt' already exists
```
This happpens when output directory is not empty.
* Error Permission denied
```
ERROR 1 (HY000) at line 1: Can't create/write to file '/data/backup/sql_dump/customers.txt' (Errcode: 13 "Permission denied"
```
When the output directory not owned by user `mysql`
* Output files (*.sql and *.txt) are created on the server host running MySQL instance, so it is not possible to create resulting files on a host other than the server host.
