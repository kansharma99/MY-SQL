create database bank;
use bank;
-- create account table
create table accounts (
account_number int primary key auto_increment,
customer_name varchar(50) not null ,
account_type varchar(50) check( account_type in ('Savings','Current')) not null,
balance float8 default 0.0 check(balance >=0),
pin_hash varchar(50) not null);

-- create transaction table 
create table transactions(
transaction_id int primary key auto_increment,
account_number int not null,
transaction_type varchar(50) check( transaction_type in ('Deposit','Withdrawal')) not null,
amount float8 not null check(amount >0),
timestamp datetime default current_timestamp,
foreign key (account_number) references accounts(account_number) on delete cascade);

show tables;
select * from transactions;
select * from accounts;



