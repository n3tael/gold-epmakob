BEGIN TRANSACTION;
DROP TABLE IF EXISTS "authors";
CREATE TABLE IF NOT EXISTS "authors" (
	"id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"url"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "images";
CREATE TABLE IF NOT EXISTS "images" (
	"id"	INTEGER NOT NULL,
	"post_id"	INTEGER NOT NULL,
	"image"	BLOB NOT NULL,
	FOREIGN KEY("post_id") REFERENCES "posts"("id") ON DELETE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "posts";
CREATE TABLE IF NOT EXISTS "posts" (
	"id"	INTEGER NOT NULL,
	"chat"	TEXT NOT NULL,
	"message_id"	INTEGER NOT NULL UNIQUE,
	"author_id"	INTEGER NOT NULL,
	"caption"	TEXT,
	"total_votes"	INTEGER NOT NULL DEFAULT 0,
	"created_at"	TEXT NOT NULL,
	"uploaded_at"	INTEGER NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S+00:00', 'now')),
	FOREIGN KEY("author_id") REFERENCES "authors"("id") ON DELETE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "votes";
CREATE TABLE IF NOT EXISTS "votes" (
	"token"	TEXT NOT NULL,
	"post_id"	INTEGER NOT NULL,
	FOREIGN KEY("post_id") REFERENCES "posts"("id") ON DELETE CASCADE,
	FOREIGN KEY("token") REFERENCES "tokens"("token") ON DELETE CASCADE ON UPDATE CASCADE
);
DROP TABLE IF EXISTS "tokens";
CREATE TABLE IF NOT EXISTS "tokens" (
	"token"	TEXT NOT NULL CHECK(length("token") = 32) UNIQUE,
	"valid_before"	TEXT NOT NULL DEFAULT (datetime('now', '+1 month')),
	"created_at"	TEXT NOT NULL DEFAULT (datetime('now'))
);
DROP TRIGGER IF EXISTS "update_total_votes_delete";
CREATE TRIGGER update_total_votes_delete
AFTER DELETE ON votes
BEGIN
    UPDATE posts
    SET total_votes = total_votes - 1
    WHERE id = OLD.post_id;
END;
DROP TRIGGER IF EXISTS "update_total_votes_insert";
CREATE TRIGGER update_total_votes_insert
AFTER INSERT ON votes
BEGIN
    UPDATE posts
    SET total_votes = total_votes + 1
    WHERE id = NEW.post_id;
END;
DROP VIEW IF EXISTS "all_posts";
CREATE VIEW all_posts AS
SELECT posts.id,
    posts.author_id,
	posts.message_id,
	posts.chat,
    authors.name AS author_name,
	authors.url AS author_url,
    images.id AS image_id,
	total_votes,
    caption,
    strftime('%Y-%m-%d %H:%M:%S', created_at) AS created_at,
	strftime('%Y-%m-%d %H:%M:%S', uploaded_at) AS uploaded_at
FROM posts
INNER JOIN authors ON authors.id = posts.author_id
INNER JOIN images ON images.post_id = posts.id
WHERE images.id IN (SELECT MIN(id) FROM images GROUP BY post_id);
DROP VIEW IF EXISTS "all_authors";
CREATE VIEW all_authors AS
SELECT authors.id,
	name,
	replace(url, 'https://t.me/', '') AS username,
	url,
	strftime('%d.%m.%Y', MIN(posts.uploaded_at)) AS joined_at,
	COUNT(posts.author_id) AS total_posts,
	COUNT(votes.post_id) AS total_votes
FROM authors
LEFT JOIN posts ON posts.author_id = authors.id
LEFT JOIN votes ON votes.post_id = posts.id
GROUP BY author_id;
COMMIT;
