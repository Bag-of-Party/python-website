CREATE TABLE parties (
  id uuid NOT NULL PRIMARY KEY,
  name text NOT NULL,
  url text NOT NULL,
  email text,
  password text
)

CREATE TABLE items (
  id uuid NOT NULL PRIMARY KEY,
  party_id uuid NOT NULL,
  name text NOT NULL,
  info text,
  container_id uuid,
  CONSTRAINT fk_party_id
    FOREIGN KEY(party_id)
      REFERENCES parties(id)
)

INSERT INTO parties VALUES 
( uuid(), 'Held land', 'www.helo.com', null, null, ),
( uuid(), 'AD Party', 'www.asdo.com', null, null, ),
( uuid(), 'sadf', 'www.123.com', null, null, ),