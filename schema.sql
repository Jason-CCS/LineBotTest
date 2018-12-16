CREATE TABLE users (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    username TEXT NOT NULL,
    balance INTEGER
);

INSERT INTO users (username, balance) Values('Joe', 100);
INSERT INTO users (username, balance) Values('Jane', 200);
INSERT INTO users (username, balance) Values('Jay', 300);
INSERT INTO users (username, balance) Values('Jim', 1000000)