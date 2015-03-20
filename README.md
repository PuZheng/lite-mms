lite-mms
========

## packages required

* libmysqlclient-dev
* libxml2-dev 
* libxslt1-dev


## use mysql as database

```sql
mysql> create user 'foo-user' identified by 'foo-password'
mysql> create database foo_db character set 'utf8';
mysql> grant all on foo_db.* to 'foo-user';
mysql> flush privileges;
```
and set DBSTR to "mysql://foo-user:foo-password@"
