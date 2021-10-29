CREATE TABLE parties (
  id uuid NOT NULL PRIMARY KEY,
  name text NOT NULL,
  url text NOT NULL,
  email text,
  password text
);

CREATE TABLE items (
  id uuid NOT NULL PRIMARY KEY,
  party_id uuid NOT NULL,
  name text NOT NULL,
  info text,
  container_id uuid,
  CONSTRAINT fk_party_id
    FOREIGN KEY(container_id)
      REFERENCES items(id)
      ON DELETE CASCADE
);

INSERT INTO parties VALUES 
( gen_random_uuid(), 'Held land', 'www.helo.com', null, null ),
( gen_random_uuid(), 'AD Party', 'www.asdo.com', null, null ),
( gen_random_uuid(), 'sadf', 'www.123.com', null, null )

insert into items VALUES
( gen_random_uuid(), '3bf7ef85-46fb-4e86-b323-06520e12713d', 'cloak', null, null ),
( gen_random_uuid(), '3bf7ef85-46fb-4e86-b323-06520e12713d', 'staff', null, null ),
( gen_random_uuid(), '428b13dd-7631-47ba-9bd9-1a0bb78a701d', 'axe', null, null ),
( gen_random_uuid(), '428b13dd-7631-47ba-9bd9-1a0bb78a701d', 'bag', 'food', null ),
( gen_random_uuid(), 'f564a79e-0e4f-4a3d-afc0-f4b000861b8f', 'chest', 'gold', null ),
( gen_random_uuid(), 'f564a79e-0e4f-4a3d-afc0-f4b000861b8f', 'plate', null, null ),
( gen_random_uuid(), 'f564a79e-0e4f-4a3d-afc0-f4b000861b8f', 'jacket', 'knifes', null )
