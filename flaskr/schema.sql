DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS answers;

CREATE TABLE user (
    username TEXT PRIMARY KEY UNIQUE NOT NULL,
    emailid TEXT NOT NULL,
    password TEXT NOT NULL,
    img TEXT
);

CREATE TABLE problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT,
    FOREIGN KEY (author_id) REFERENCES user (username)
);


CREATE TABLE solution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    body TEXT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES problems (id)
);

CREATE TABLE user_sol (
     userid TEXT NOT NULL,
     problemid INTEGER NOT NULL,
     answerid INTEGER PRIMARY KEY AUTOINCREMENT,
     FOREIGN KEY (answerid) REFERENCES solution (id)
);

CREATE TABLE contests (
     site TEXT,
     schedule TEXT,
     contestlink TEXT,
     other_det TEXT
);
