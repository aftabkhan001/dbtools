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
## Supported Data Types
The list of supported data types

**String Types**
* CHAR
* VARCHAR
* BINARY
* VARBINARY
* TEXT
* BLOB
* MEDIUMBLOB
* MEDIUMTEXT
* LONGTEXT
* LONGBLOB

**Date Types**
* DATETIME
* TIMESTAMP

**Numeric Types**
* INT
* DECIMAL 
* FLOAT

## Masking Rules
All string values are replaced with MD5 checksum of a random value e.g. 'secret' would be masked as followed:
```
SELECT SUBSTRING(MD5(RAND()) FROM 1 FOR LENGTH('secret'));
+----------------------------------------------------+
| SUBSTRING(MD5(RAND()) FROM 1 FOR LENGTH('secret')) |
+----------------------------------------------------+
| a386cb                                             |
+----------------------------------------------------+
1 row in set (0.00 sec)

```
Datetime and timestamp are replaced with `0000-00-00 00:00:00`, and numeric data is replaced with value 0

**Examples**

Below examples use sample database: http://www.mysqltutorial.org/mysql-sample-database.aspx

***Backup***

* Using `--ignore-columns` option

Ignore following columns from all tables ( in this case we have these columns in `customers` table)
customerName,contactLastName,contactFirstName,phone,addressLine1,addressLine2

```
$ sudo python sql_dump.py \
> --user dba \
> --ignore-columns customerName,contactLastName,contactFirstName,phone,addressLine1,addressLine2 \
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
* Create database on destination server
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
mysql [classicmodels_REDACTED]>  select * from customers limit 1\G
*************************** 1. row ***************************
        customerNumber: 103
          customerName: 0dfa59bc08f6eaeb4
       contactLastName: 6099549
      contactFirstName: b35b943
                 phone: 37bdfb7215
          addressLine1: 226d8ef722d36c
          addressLine2: NULL
                  city: Nantes
                 state: NULL
            postalCode: 44000
               country: France
salesRepEmployeeNumber: 1370
           creditLimit: 21000.00
1 row in set (0.00 sec)
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
