## Making MySQL backups (sensitive or private information removed)

The sql_dump client utility performs logical backups, producing CSV text-format data files. It supports `--ignore-columns` option, that can be used to ignore specific column(s) e.g. sensitive information such as user name, address, bank account number etc 

## Requirements
Install following tools/packages
* `Python 2.7.x`
* `mysql connector/python` - e.g. mysql-connector-python-2.0.4.zip

## Limitations
it can be run only on the same machine where the database server is running.

## Usage
```
 python sql_dump.py   -h
usage: sql_dump.py    [-h] --databases DATABASE --path OUTPUT_DIR
                      [--ignore-columns IGNORE_COLUMNS]
                      [--ignore-tables IGNORE_TABLES] [--host HOSTNAME]
                      [--user DB_USER] [--password DB_PASS]
                      [--log-error LOG_ERROR] [--flush-logs]

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
  --log-error LOG_ERROR
                        Append warnings and errors to given file (default:
                        None)
  --flush-logs          Flush logs file in server before starting dump.
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
*Backup files:
```
$ ls -lh /data/backup/sql_dump/
total 208K
-rw-r--r-- 1 root  root  2.0K Oct 13 11:14 customers.sql
-rw-rw-rw- 1 mysql mysql 3.9K Oct 13 11:14 customers.txt
-rw-r--r-- 1 root  root  2.2K Oct 13 11:14 employees.sql
-rw-rw-rw- 1 mysql mysql 1.9K Oct 13 11:14 employees.txt
-rw-r--r-- 1 root  root  1.8K Oct 13 11:14 offices.sql
-rw-rw-rw- 1 mysql mysql  174 Oct 13 11:14 offices.txt
-rw-r--r-- 1 root  root  2.1K Oct 13 11:14 orderdetails.sql
-rw-rw-rw- 1 mysql mysql  85K Oct 13 11:14 orderdetails.txt
-rw-r--r-- 1 root  root  2.0K Oct 13 11:14 orders.sql
-rw-rw-rw- 1 mysql mysql  27K Oct 13 11:14 orders.txt
-rw-r--r-- 1 root  root  1.9K Oct 13 11:14 payments.sql
-rw-rw-rw- 1 mysql mysql 9.9K Oct 13 11:14 payments.txt
-rw-r--r-- 1 root  root  1.8K Oct 13 11:14 productlines.sql
-rw-rw-rw- 1 mysql mysql 3.4K Oct 13 11:14 productlines.txt
-rw-r--r-- 1 root  root  2.1K Oct 13 11:14 products.sql
-rw-rw-rw- 1 mysql mysql  30K Oct 13 11:14 products.txt
```

***Restore***

When restoring backup, perform following steps:
* Create database on destination server and disable `foreign key` checks
```
mysql> CREATE DATABASE IF NOT EXISTS classicmodels_REDACTED;
mysql> SET GLOBAL FOREIGN_KEY_CHECKS=0;
```
* Create tables 
```
cat /data/backup/sql_dump/*.sql | mysql -udba -p classicmodels_REDACTED
```
* Load data files
```
$ mysqlimport -udba -p --local classicmodels_REDACTED /data/backup/sql_dump/*.txt --fields-optionally-enclosed-by='"' --fields-terminated-by=',' --replace --use-threads=5
Enter password:
classicmodels_REDACTED.employees: Records: 23  Deleted: 0  Skipped: 0  Warnings: 0
classicmodels_REDACTED.offices: Records: 7  Deleted: 0  Skipped: 0  Warnings: 0
classicmodels_REDACTED.productlines: Records: 7  Deleted: 0  Skipped: 0  Warnings: 0
classicmodels_REDACTED.customers: Records: 122  Deleted: 0  Skipped: 0  Warnings: 0
classicmodels_REDACTED.payments: Records: 273  Deleted: 0  Skipped: 0  Warnings: 0
classicmodels_REDACTED.products: Records: 110  Deleted: 0  Skipped: 0  Warnings: 0
classicmodels_REDACTED.orders: Records: 326  Deleted: 0  Skipped: 0  Warnings: 0
classicmodels_REDACTED.orderdetails: Records: 2996  Deleted: 0  Skipped: 0  Warnings: 0
```
* Enable `foreign key` checks
```
mysql> SET GLOBAL FOREIGN_KEY_CHECKS=0;
```

***Verify***

Examine contents of `customers` table:
```
mysql [classicmodels_REDACTED]> select * from customers;
+----------------+-------------------+---------------+------------------------+-------------+
| customerNumber | city              | state         | salesRepEmployeeNumber | creditLimit |
+----------------+-------------------+---------------+------------------------+-------------+
|            103 | Nantes            | NULL          |                   1370 |    21000.00 |
|            112 | Las Vegas         | NV            |                   1166 |    71800.00 |
|            114 | Melbourne         | Victoria      |                   1611 |   117300.00 |
|            119 | Nantes            | NULL          |                   1370 |   118200.00 |
|            121 | Stavern           | NULL          |                   1504 |    81700.00 |
|            124 | San Rafael        | CA            |                   1165 |   210500.00 |
|            125 | Warszawa          | NULL          |                   NULL |        0.00 |
```

## Known issues:
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
