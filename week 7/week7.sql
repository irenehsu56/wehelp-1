create database if not exists website;
use website;
create table if not exists member(
	id int unsigned primary key auto_increment,
    name varchar(255) not null,
    email varchar(255) not null,
    password varchar(255) not null,
    follower_count int unsigned not null default 0,
    time datetime not null default current_timestamp
);
alter table member add constraint unique_member_email unique(email);
alter table member add column token varchar(64);
select * from member;

use website;
create table if not exists message(
	id int unsigned primary key auto_increment,
    member_id int unsigned not null,
    content text not null,
    like_count int unsigned not null default 0,
    time datetime not null default current_timestamp,
    foreign key(member_id) references member(id)
);
select * from message;
select id, token from member;
