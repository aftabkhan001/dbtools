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
All string values are replaced with MD5 checksum of the values stored in the column e.g. 'abc' would be masked as followed:
```
 SELECT RIGHT(MD5('abc'),LENGTH('abc'));
+---------------------------------+
| RIGHT(MD5('abc'),LENGTH('abc')) |
+---------------------------------+
| f72                             |
+---------------------------------+
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
|            103 | 85178a8ddbb210f23            | dc6896b         | 7b4418b          | e7d37a4017        | 5cd671b78a43ce               | NULL         | Nantes        | NULL     | 44000      | France    |                   1370 |    21000.00 |
|            112 | 12113da072c8cb38f6           | d885            | b9ab             | 833223700a        | 74fb0ca79714b8e              | NULL         | Las Vegas     | NV       | 83030      | USA       |                   1166 |    71800.00 |
|            114 | 6bb38c814b819680199a62a78f   | 0199057b        | 3382f            | e54b35a3a4ed      | af957d29aaa43cb75            | 64ceae8      | Melbourne     | Victoria | 3004       | Australia |                   1611 |   117300.00 |
|            119 | 81a61c05c4bfc222e            | 39753ae         | 9528dcd          | ee919d1a54        | 671756bd38b98bef230db5809cb0 | NULL         | Nantes        | NULL     | 44000      | France    |                   1370 |   118200.00 |
|            121 | 6555d696cc4cad0ae9           | fe43d6ab0e      | 0438fb           | d1b1b15f93        | 56b73c7bf30bfa5b51de54       | NULL         | Stavern       | NULL     | 4110       | Norway    |                   1504 |    81700.00 |
|            124 | 3da54937c9d16ef976f3aa7983b9 | 4af893          | cc76e            | f94c406820        | a1fa24c9f6e4412              | NULL         | San Rafael    | CA       | 97562      | USA       |                   1165 |   210500.00 |
|            125 | 828adf12f6595eaa0b           | 2965853768ec984 | 9688a595         | 46ab548acf119     | 023fff8172325d2              | NULL         | Warszawa      | NULL     | 01-012     | Poland    |                   NULL |        0.00 |
|            128 | 47aec0e3203f15dadf74         | 9a3baa          | d3a0fa           | 8993ede8b50c72ff2 | 6a6a340dc2a94                | NULL         | Frankfurt     | NULL     | 60528      | Germany   |                   1504 |    59700.00 |
|            129 | 9dcb1729beae2bd              | 62c86c          | 647dd            | 60dd2b5a91        | 21bce2015c12b67f50d217a0e    | NULL         | San Francisco | CA       | 94217      | USA       |                   1165 |    64600.00 |
|            131 | c95bc140aeb2e41b7            | a0f             | 6dc5             | 1154c3decb        | 6268a2776cfaaf843de0549      | NULL         | NYC           | NY       | 10022      | USA       |                   1323 |   114900.00 |
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
