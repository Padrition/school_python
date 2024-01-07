SAVEPOINT start_transaction;

PRAGMA foreign_keys=off;

CREATE TABLE IF NOT EXISTS backup_uzivately AS SELECT * FROM uzivately;
CREATE TABLE IF NOT EXISTS backup_vozidla AS SELECT * FROM vozidla;
CREATE TABLE IF NOT EXISTS backup_role AS SELECT * FROM role;
CREATE TABLE IF NOT EXISTS backup_role_uzivately AS SELECT * FROM role_uzivately;
CREATE TABLE IF NOT EXISTS backup_typ_operace AS SELECT * FROM typ_operace;
CREATE TABLE IF NOT EXISTS backup_servis AS SELECT * FROM servis;
CREATE TABLE IF NOT EXISTS backup_operace AS SELECT * FROM operace;
CREATE TABLE IF NOT EXISTS backup_stav_servisu AS SELECT * FROM stav_servisu;
CREATE TABLE IF NOT EXISTS backup_notifikace AS SELECT * FROM notifikace;

DROP TABLE IF EXISTS uzivately;
DROP TABLE IF EXISTS vozidla;
DROP TABLE IF EXISTS role;
DROP TABLE IF EXISTS role_uzivately;
DROP TABLE IF EXISTS typ_operace;
DROP TABLE IF EXISTS servis;
DROP TABLE IF EXISTS operace;
DROP TABLE IF EXISTS stav_servisu;
DROP TABLE IF EXISTS notifikace;

CREATE TABLE IF NOT EXISTS uzivately(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    jmeno TEXT NOT NULL,
    primeni TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    heslo TEXT NOT NULL,
    vkladan INTEGER,
    FOREIGN KEY(vkladan) REFERENCES uzivately(id)
);

CREATE TABLE IF NOT EXISTS vozidla(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    spz TEXT NOT NULL,
    model TEXT NOT NULL, 
    rok_vyroby INTEGER NOT NULL,
    vlastnik INTEGER NOT NULL,
    FOREIGN KEY(vlastnik) REFERENCES uzivately(id)
);

CREATE TABLE IF NOT EXISTS role(
    nazev TEXT NOT NULL PRIMARY KEY,
    popis TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS role_uzivately(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    vlozeno DATETIME DEFAULT CURRENT_TIMESTAMP,
    platnost INTEGER NOT NULL, -- 0 - false; 1 - true
    nazev TEXT NOT NULL,
    id_uzivatele INTEGER NOT NULL,
    pridelil INTEGER,
    FOREIGN KEY(id_uzivatele) REFERENCES uzivately(id),
    FOREIGN KEY(nazev) REFERENCES role(nazev),
    FOREIGN KEY(pridelil) REFERENCES uzivately(id)
);

CREATE TABLE IF NOT EXISTS typ_operace(
    nazev TEXT NOT NULL PRIMARY KEY,
    popis TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS servis(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    datum DATETIME DEFAULT CURRENT_TIMESTAMP,
    vozidlo INTEGER NOT NULL,
    problem TEXT,
    FOREIGN KEY(vozidlo) REFERENCES vozidla(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS operace(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    cena INTEGER NOT NULL,
    soucastky TEXT NOT NULL,
    typ TEXT NOT NULL,
    provadi INTEGER NOT NULL,
    soucast_servisu INTEGER NOT NULL,
    FOREIGN KEY(soucast_servisu) REFERENCES servis(id) ON DELETE CASCADE,
    FOREIGN KEY(provadi) REFERENCES uzivately(id) ON DELETE CASCADE,
    FOREIGN KEY(typ) REFERENCES typ_operace(nazev)
);

CREATE TABLE IF NOT EXISTS stav_servisu(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    id_servisu INTEGER NOT NULL,
    stav TEXT NOT NULL,
    dokonceni DATETIME,
    FOREIGN KEY(id_servisu) REFERENCES servis(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifikace(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    id_stav INTEGER NOT NULL,
    datum DATETIME NOT NULL,
    zprava TEXT NOT NULL,
    FOREIGN KEY(id_stav) REFERENCES stav_servisu(id) ON DELETE CASCADE
);

INSERT INTO uzivately SELECT * FROM backup_uzivately;
INSERT INTO vozidla SELECT * FROM backup_vozidla;
INSERT INTO role SELECT * FROM backup_role;
INSERT INTO role_uzivately SELECT * FROM backup_role_uzivately;
INSERT INTO typ_operace SELECT * FROM backup_typ_operace;
INSERT INTO servis SELECT * FROM backup_servis;
INSERT INTO operace SELECT * FROM backup_operace;
INSERT INTO stav_servisu SELECT * FROM backup_stav_servisu;
INSERT INTO notifikace SELECT * FROM backup_notifikace;

DROP TABLE IF EXISTS backup_uzivately;
DROP TABLE IF EXISTS backup_vozidla;
DROP TABLE IF EXISTS backup_role;
DROP TABLE IF EXISTS backup_role_uzivately;
DROP TABLE IF EXISTS backup_typ_operace;
DROP TABLE IF EXISTS backup_servis;
DROP TABLE IF EXISTS backup_operace;
DROP TABLE IF EXISTS backup_stav_servisu;
DROP TABLE IF EXISTS backup_notifikace;

PRAGMA foreign_keys=on;

RELEASE start_transaction;

INSERT OR IGNORE INTO role (nazev, popis) VALUES ('client', 'Obycejny user');
INSERT OR IGNORE INTO role (nazev, popis) VALUES ('mechanic', 'Obycejny mechanic');
INSERT OR IGNORE INTO role (nazev, popis) VALUES ('manager', 'Manager');
INSERT OR IGNORE INTO role (nazev, popis) VALUES ('admin', 'Super mega amin');
INSERT OR IGNORE INTO typ_operace (nazev, popis) VALUES('Technicka kontrola', 'Technicka kontrola vozidla za ucelem najit problem');
INSERT OR IGNORE INTO typ_operace (nazev, popis) VALUES('Oprava', 'Prodelani kroku s cilem likvidace problemu');
INSERT OR IGNORE INTO typ_operace (nazev, popis) VALUES('Likvidace', 'Likvidace vraku');