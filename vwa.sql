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
    FOREIGN KEY(vozidlo) REFERENCES vozidla(id)
);

CREATE TABLE IF NOT EXISTS operace(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    cena INTEGER NOT NULL,
    soucastky TEXT NOT NULL,
    typ TEXT NOT NULL,
    provadi INTEGER NOT NULL,
    soucast_servisu INTEGER NOT NULL,
    FOREIGN KEY(soucast_servisu) REFERENCES servis(id),
    FOREIGN KEY(provadi) REFERENCES uzivately(id),
    FOREIGN KEY(typ) REFERENCES typ_operace(nazev)
);

CREATE TABLE IF NOT EXISTS stav_servisu(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    id_servisu INTEGER NOT NULL,
    stav TEXT NOT NULL,
    dokonceni DATETIME,
    FOREIGN KEY(id_servisu) REFERENCES servis(id)
);

CREATE TABLE IF NOT EXISTS notifikace(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    id_stav INTEGER NOT NULL,
    datum DATETIME NOT NULL,
    zprava TEXT NOT NULL,
    FOREIGN KEY(id_stav) REFERENCES stav_servisu(id)
);

INSERT OR IGNORE INTO role (nazev, popis) VALUES ('client', 'Obycejny user');
INSERT OR IGNORE INTO role (nazev, popis) VALUES ('mechanic', 'Obycejny mechanic');
INSERT OR IGNORE INTO role (nazev, popis) VALUES ('manager', 'Manager');
INSERT OR IGNORE INTO role (nazev, popis) VALUES ('admin', 'Super mega amin');
INSERT OR IGNORE INTO typ_operace (nazev, popis) VALUES('Technicka kontrola', 'Technicka kontrola vozidla za ucelem najit problem');
INSERT OR IGNORE INTO typ_operace (nazev, popis) VALUES('Oprava', 'Prodelani kroku s cilem likvidace problemu');
INSERT OR IGNORE INTO typ_operace (nazev, popis) VALUES('Likvidace', 'Likvidace vraku');