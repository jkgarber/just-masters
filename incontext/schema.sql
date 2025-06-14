DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS specs;
DROP TABLE IF EXISTS spec_items;
DROP TABLE IF EXISTS spec_details;
DROP TABLE IF EXISTS spec_item_detail_relations;
DROP TABLE IF EXISTS spec_item_relations;
DROP TABLE IF EXISTS spec_detail_relations;
DROP TABLE IF EXISTS spec_agents;
DROP TABLE IF EXISTS spec_agent_relations;

CREATE TABLE users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL
);

CREATE TABLE specs (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	creator_id INTEGER NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name TEXT NOT NULL,
	spec_type INTEGER NOT NULL,
	description TEXT,
	FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE spec_items (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	creator_id INTEGER NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name TEXT NOT NULL,
	FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE spec_details (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	creator_id INTEGER NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	name TEXT NOT NULL,
	description TEXT,
	FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE spec_item_detail_relations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	spec_item_id INTEGER NOT NULL,
	spec_detail_id INTEGER NOT NULL,
	content TEXT,
	FOREIGN KEY (spec_item_id) REFERENCES spec_items (id)
	FOREIGN KEY (spec_detail_id) REFERENCES spec_details (id)
);

CREATE TABLE spec_item_relations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	spec_id INTEGER NOT NULL,
	item_id INTEGER NOT NULL,
	FOREIGN KEY (spec_id) REFERENCES specs (id),
	FOREIGN KEY (item_id) REFERENCES spec_items (id)
);

CREATE TABLE spec_detail_relations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	spec_id INTEGER NOT NULL,
	detail_id INTEGER NOT NULL,
	FOREIGN KEY (spec_id) REFERENCES specs (id),
	FOREIGN KEY (detail_id) REFERENCES spec_details (id)
);

CREATE TABLE spec_agents (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	creator_id INTEGER NOT NULL,
	created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	model TEXT NOT NULL,
	name TEXT NOT NULL,
	role TEXT NOT NULL,
	instructions TEXT NOT NULL,
	vendor TEXT NOT NULL,
	FOREIGN KEY (creator_id) REFERENCES users (id)
);

CREATE TABLE spec_agent_relations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	spec_id INTEGER NOT NULL,
	agent_id INTEGER NOT NULL,
	FOREIGN KEY (spec_id) REFERENCES specs (id),
	FOREIGN KEY (agent_id) REFERENCES agents (id)
);
