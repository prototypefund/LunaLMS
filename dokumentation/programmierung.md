Die Programmierung von Luna LMS
===============================

## Ausführbare Dokumentation

Diese Dokumentation enthält Programm-Beispiele in der Sprache Python.

Diese Beispiele lassen sich direkt testen.

Dazu muss auf einer Kommando-Zeile dieser Befehl ausgeführt werden:

	python -m doctest programmierung.md


## Leitgedanken zur Programmierung von Luna

Luna verwaltet strukturierte Kurse und Lern-Inhalte.

Die Struktur ist so gewählt, dass die Daten möglichst leicht verständlich
gespeichert werden.

Kurse und Lern-Inhalte sollen über ein Browser-Programm in HTML
zugänglich sein.

Luna erzeugt dazu aus den Daten Ansichten in HTML.

Diese Ansichten erzeugt Luna vor der Betrachtung und nach jeder Änderung an den
Daten.


## Sprache

Wir dokumentieren Luna LMS in deutscher Sprache.

Ausnahme: Kommentare im Programm-Code schreiben wir auf Englisch.


## Versions-Nummern

Für Luna nehmem wir [semantische Versionierung](https://semver.org/lang/de/).

Das Schema sind drei mit Punkten getrennte Zahlen:

MAJOR.MINOR.PATCH

Vor-Versionen von Luna haben die MAJOR-Nummer 0.

Die erste Vor-Version von Luna ist Version 0.1.0 .

Ab der ersten Vor-Version müssen bereits in der Versionskontrolle Versionen mit
unterschiedlicher Funktion auch unterschiedliche Versionsnummern haben.

Nur so können Fehlerberichte der richtigen Version zugeordnet werden.

In der Versionskontrolle muss die Versionsnummer in Branches zum Ausprobieren
nicht bei jeder Funktionsänderung hochgezählt werden.

Im Test-Branch "development" und im stabilen Branch "trunk" jedoch muss die
Versionsnummer mit jeder Funktionsänderung hochgezählt werden.


## Programmier-Stil

In Python verwenden wir Tabulatoren zum Einrücken.


## Programmier-Schnittstelle (API)

### Regeln

Luna ist eine Web-Anwendung über das Hypertext Transfer Protocol (HTTP).

Adressen (URIs) spielen dabei eine wichtige Rolle.

Wir wollen uns wo immer möglich an die Regeln von Representational
State Transfer (REST) halten.

Eine wichtige Regel ist:

HTTP `GET` ändert niemals Daten.

Nur HTTP `POST`, `PUT` und `DELETE` ändern Daten.


### Methoden für Web-Zugriff

Luna soll wesentlich über eine HTML-HTTP-Schnittstelle ohne Scripting bedient
werden.

Aus HTML können aber nur die HTTP-Methoden `GET` und `POST` ausgelöst werden.

Die für REST elementaren Methoden `PUT` oder `DELETE` gehen aus HTML heraus nicht.

Eine übliche Umgehung dafür ist, den Parameter `_method` mit den Werten `PUT`
oder `DELETE` per `POST` mitzugeben und das Programm reagieren zu lassen, als
wäre tatsächlich die übergebene Methode aufgerufen worden. Siehe die
[Antwort auf "Why don't browsers support PUT and DELETE requests and when will
they?"](https://stackoverflow.com/a/16812862), die verlinkt auf [die
Symfony-Dokumentation](https://symfony.com/doc/current/routing.html#matching-http-methods)
und [die Dokumentation von node expressjs](https://github.com/expressjs/method-override#override-using-a-query-value).


### Endpunkte und Methoden

#### Kurse

#### `POST /redaktion`

Legt einen neuen Kurs im Redaktionssystem an.

Parameter: `title`

#### `PUT /redaktion/ID/Lern-Inhalte`

Aktualisiert die Liste der Lern-Inhalte für den Kurs
mit identifier `ID`.

Parameter: `lerninhalte`

#### Lern-Inhalte

#### `POST /redaktion/ID`

Legt einen neuen Lern-Inhalt für den Kurs mit identifier `ID` im
Redaktionssystem an.

Parameter: `title`

#### Varianten

#### `POST /redaktion/K_ID/L_ID`

Legt eine neue Variante für den Lern-Inhalt mit identifier `L_ID`
in dem Kurs mit dem identifier `K_ID` im Redaktionssystem an.

Parameter: `filename`, `content`


## Übersetzung

Wir bereiten Luna so vor, dass es leicht in andere Sprachen zu
übersetzen ist.

Dafür verwenden wir bei der Programmierung das Modul `gettext` .

Zeichenketten, die übersetzt werden sollen, klammern wir ein in `_(...)` .

Zum Beispiel:

	_("Willkommen bei Luna LMS!")


## Logs

Für eine fehlerarme Programmierung ist es wichtig,

jederzeit sehen zu können,

was das Programm zu tun versucht.

Dafür verwenden wir Logging.

Das Programm sollte alles,

was es zu tun versucht,

in das Log schreiben.

Danach sollte es den Erfolg oder Misserfolg vom Versuch loggen.

Dafür verwenden wir bei der Programmierung das Modul `logging` .

Im Programm sind 5 Log-Funktionen eingebaut:

- `LOGGER.debug(msg)` , für kleinste Schritte, die nur bei
  der Fehlersuche interessant sind
- `LOGGER.info(msg)` , für Schritte, die aus mehreren kleinsten
  Schritten bestehen
- `LOGGER.warning(msg)` , für Warnungen, die den normalen Ablauf
  nicht behindern
- `LOGGER.error(msg)` , für Fehler, die den normalen Ablauf behindern
- `LOGGER.critical(msg)` , für Fehler, bei denen das Programm
  abbrechen muss.


## Daten-Speicherung

### Leitgedanken zur Daten-Speicherung

Luna speichert alle Daten von einem Kurs in einer relationalen Datenbank.

Dazu gehören auch binäre Daten.

Alle binären Daten kommen in eine eigene Tabelle.

FÜr jeden Kurs gibt es eine eigene Datenbank.

Das Datenbank-Format muss rückwärtskompatibel sein:

Auch ältere Versionen von Luna

sollen die Datenbank einer neueren Version von Luna benutzen können.


### Datenbank-Format.

Aktuell verwendet Luna die Datenbank-Software [SQLite](https://www.sqlite.org/index.html).

SQLite speichert Datenbanken in einzelnen Dateien.

	>>> import sqlite3

Sicherstellen, dass keine alte Beispiel-Datei existiert:

	>>> import os
	>>> import os.path
	>>> if os.path.exists("luna-beispiel.sqlite"):
	...     os.remove("luna-beispiel.sqlite")

Mit der Beispiel-Datenbank verbinden:

	>>> connection = sqlite3.connect("luna-beispiel.sqlite")
	>>> cursor = connection.cursor()

Luna verwendet das SQLite-PRAGMA `foreign_keys`.

	 >>> result = cursor.execute("PRAGMA foreign_keys = ON")
	 >>> result = cursor.execute("PRAGMA foreign_keys")
	 >>> result.fetchone()
	 (1,)


### Datenbank-Tabellen

Das sind die Tabellen in der Datenbank:


#### cache

Die Tabelle *cache* speichert statische Dateien sowie generierte Ansichten für
eine effizientere Anzeige.

	>>> result = cursor.execute('''
	... CREATE TABLE "cache" (
	... 	"key"	INTEGER,
	... 	"path"	TEXT NOT NULL UNIQUE,
	... 	"data"	BLOB,
	... 	"format"	TEXT NOT NULL,
	... 	"description"	TEXT,
	... 	PRIMARY KEY("key")
	... );
	... ''')
	>>> result.fetchone()

`path` ist die Pfad-Komponente der URL.

`format` ist der MIME-Type der Ressource.

`description` ist eine optionale Beschreibung. Bei visuellen Daten wird sie als
Alternativtext genutzt.

	>>> result = cursor.execute('''
	... INSERT INTO "cache" ("key","path","data","format", "description") VALUES (
	... 	'1',
	... 	'square.svg',
	... 	'<?xml version="1.0" encoding="UTF-8" standalone="no"?><svg width="512" height="512" viewBox="0 0 135.46666 135.46667" version="1.1" id="svg5" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"><defs id="defs2" /><g id="layer1"><rect style="fill:#ba2bcd;fill-opacity:1;stroke:none;stroke-width:0.187088;stroke-linecap:square;stroke-linejoin:round" id="rect286" width="95.789398" height="95.789398" x="-47.894699" y="47.894699" transform="rotate(-45)" /></g></svg>',
	... 	'image/svg+xml',
	... 	'Ein lila Quadrat, das auf der Spitze steht.'
	... );
	... ''')
	>>> result.fetchone()
	>>> connection.commit()


#### course

Ein Kurs erfasst alle Lern-Pfade, Lern-Inhalte und Varianten,
die eine abgeschlossene Lern-Erfahrung ergeben.

Die Tabelle *course* speichert Daten über den Kurs.
Sie beschreibt den Kurs mit allen notwendigen Meta-Daten.
Die Tabelle hat nur einen einzigen Eintrag.

	>>> result = cursor.execute('''
	... CREATE TABLE "course" (
	... 	"identifier"	TEXT NOT NULL,
	... 	"title"	TEXT NOT NULL,
	... 	"description"	TEXT NOT NULL,
	... 	"relation"	TEXT,
	... 	"created"	TEXT NOT NULL,
	... 	"modified"	TEXT NOT NULL,
	... 	"dateAccepted"	TEXT,
	... 	"issued"	TEXT,
	... 	"contributor"	TEXT NOT NULL,
	... 	"requires"	TEXT NOT NULL,
	... 	FOREIGN KEY("relation") REFERENCES "cache"("path") ON UPDATE CASCADE ON DELETE RESTRICT
	... );
	... ''')
	>>> result.fetchone()

`identifier` ist eine UUID.

`relation` bezieht sich auf einen Eintrag in der Tabelle `cache`, der ein
Vorschau-Bild des Kurses enthält.

`issued`, `dateAccepted`, `created`, `modified` sind Datums-Angaben im Format
ISO 8601.

`contributor` ist eine durch Kommas getrennte Liste von Beitragenden.

`requires` gibt die mindestens benötigte Version von Luna LMS als Zeichenkette
"Luna LMS ", gefolgt von einer Versions-Nummer an (siehe dort).

	>>> result = cursor.execute('''
	... INSERT INTO "course" (
	... 	"identifier",
	... 	"title",
	... 	"description",
	... 	"relation",
	... 	"created",
	... 	"modified",
	... 	"dateAccepted",
	... 	"issued",
	... 	"contributor",
	... 	"requires"
	... ) VALUES (
	... 	'021741e6-692d-4d09-b3b7-ab5716a1afe7',
	... 	'Verschachtelungs-Test',
	... 	'Ein Kurs zum Test von verschachtelten Lern-Schritten',
	... 	'square.svg',
	... 	'2023-08-23',
	... 	'2023-08-23',
	... 	NULL,
	... 	NULL,
	... 	'Martina',
	... 	'Luna LMS 0.2.0');
	... ''')
	>>> result.fetchone()
	>>> connection.commit()


#### variants

Die Tabelle *variants* speichert die Varianten.

Eine Variante ist das kleinstes Element in Luna.

	>>> result = cursor.execute('''
	... CREATE TABLE "variants" (
	... 	"key"	INTEGER,
	... 	"identifier"	TEXT NOT NULL UNIQUE,
	... 	"filename"	TEXT NOT NULL,
	... 	"isPartOf"	TEXT,
	... 	"data"	BLOB,
	... 	"format"	TEXT NOT NULL,
	... 	PRIMARY KEY("key")
	... );
	... ''')
	>>> result.fetchone()

- Jede Variante ist entweder eine Datei oder ein Ordner.
    - Diese Dateien und Ordner sind **nicht** die Mediathek.
    - Dateien enthalten die zulässigen Datentypen
        - insbesondere: `.html` (für HTML-Schnipsel, keine kompletten
          Dateien), `.png`, `.jpg`, `.opus` etc.
        - Dateien dürfen beliebige, im Betriebssystem zulässige Namen haben
            - Das ist ein Zugeständnis an Nicht-Programmierer*innen,
              die verwirrt wären, wenn ihre "Lufballon.JPEG" plötzlich
              "2022-04-02-img445-67.jpg" heißt.
    - Ordner entstehen, wenn eine Variante zwingend aus mehreren Dateien besteht
        - Zum Beispiel: HTML mit extra JavaScript
        - Zum Beispiel: HTML mit Bildern an ganz bestimmter Position
        - Ordner sollen die Ausnahme sein
        - Die Datenbank bildet Ordner durch die Spalte `isPartOf` ab. Alle
          Einträge mit dem gleichen Spalteneintrag in `isPartOf` liegen im
          gleichen Ordner.
    - Beispiel: _Einleitung.opus_, _Begrueßung.JPG_, _Einleitung_
      (Ordner mit _Einleitung/Inhalt.html_, _Einleitung/Hintergrund.png_)
- Zu jeder Datei mit Bezug zu Varianten werden Meta-Informationen erfasst
    - Die Meta-Daten werde nach dem
      [Dublin Core-Standard](https://en.wikipedia.org/wiki/Dublin_Core)
      notiert.
        - Offizielle aktuelle Spezifikation:
          https://www.dublincore.org/specifications/dublin-core/dcmi-terms/
    - Die Metadaten müssen mindestens die Werte `identifier` und `format`
      beschreiben.
        - Der `identifier` ist eine Abfolge aus 6 alphanumerischen Zeichen:
		  `[a-z0-9][a-z0-9][0-9][0-9][a-z0-9][a-z0-9]`
		- Der `identifier` ist identisch für alle Dateien im gleichen
		  `isPartOf`-Ordner.
        - Das `format` ist der MIME-Type der Datei
        - Beispiel: `INSERT INTO "variants" ("identifier", "filename",
          "format") VALUES ('fb48ea', 'Luftballon.JPEG', 'image/jpeg');`
    - Später können wir dort sehr leicht z. B. Copyright oder Lizenz
      pro Variante erfassen
        - Auch Ersteller, Bearbeiterin, ...
    - Probleme ergeben sich aus der Konsistenz der Meta-Daten

<!-- language: python -->
	>>> result = cursor.execute('''
	... INSERT INTO "variants" (
	... 	"key",
	... 	"identifier",
	... 	"filename",
	... 	"isPartOf",
	... 	"data",
	... 	"format"
	... ) VALUES (
	... 	1,
	... 	'fb48ea',
	... 	'Luftballon.JPEG',
	... 	NULL,
	... 	NULL,
	... 	'image/jpeg'
	... );
	... ''')
	>>> result.fetchone()
	>>> connection.commit()


#### contents

Die Tabelle *contents* speichert die Lern-Inhalte.

Ein Lern-Inhalt besteht aus einer oder mehreren Varianten. Sie geben den
Lern-Inhalt in verschiedenen Modalitäten oder Formaten wieder.

	>>> result = cursor.execute('''
	... CREATE TABLE "contents" (
	... 	"key"	INTEGER,
	... 	"identifier"	TEXT UNIQUE,
	... 	"title"	TEXT NOT NULL,
	... 	PRIMARY KEY("key")
	... );
	... ''')
	>>> result.fetchone()

- Die Meta-Daten eines Lern-Inhalts müssen mindestens den `identifier`, den `type`
  und einen `title` enthalten
    - Der `identifier ist eine Abfolge aus 6 alphanumerischen Zeichen:
      `[a-z0-9][a-z0-9][0-9][0-9][a-z0-9][a-z0-9]`
- Beispiel: `INSERT INTO contents ("identifier", "title") VALUES ('ca3276',
  'Einleitung zum Kurs');`

<!-- language: python -->
	>>> result = cursor.execute('''
	... INSERT INTO "contents" ("key","identifier","title") VALUES
	...  (1,'0a32m2','Lern-Inhalt 1'),
	...  (2,'n367f1','Lern-Inhalt 2'),
	...  (3,'zv9085','Lern-Inhalt 3'),
	...  (4,'6i86c8','Lern-Inhalt 1.1'),
	...  (5,'no93v8','Lern-Inhalt 1.2'),
	...  (6,'dp0344','Lern-Inhalt 1.1.1'),
	...  (7,'mo252y','Lern-Inhalt 1.1.2'),
	...  (8,'9017x8','Lern-Inhalt 2.1'),
	...  (9,'ze16r1','Lern-Inhalt 2.2'),
	...  (10,'g970zo','Lern-Inhalt 2.1.1.1'),
	...  (11,'oz0969','Lern-Inhalt 2.1.1.2'),
	...  (12,'0x518z','Lern-Inhalt 2.1.2.1'),
	...  (13,'es819b','Lern-Inhalt 2.1.2.2');
	... ''')
	>>> result.fetchone()
	>>> connection.commit()


#### steps

Die Tabelle *steps* speichert die Abfolge und die verschachtelte
Gruppierung der Lern-Inhalte in dem Kurs.

	>>> result = cursor.execute('''
	... CREATE TABLE "steps" (
	... 	"key"	INTEGER,
	... 	"title"	TEXT NOT NULL,
	... 	"identifier"	TEXT UNIQUE,
	... 	"content_id"	TEXT,
	... 	"successor"	TEXT,
	... 	"parent"	TEXT,
	... 	PRIMARY KEY("key"),
	... 	FOREIGN KEY("content_id") REFERENCES "contents"("identifier") ON UPDATE CASCADE ON DELETE RESTRICT,
	... 	FOREIGN KEY("parent") REFERENCES "steps"("identifier") ON UPDATE CASCADE ON DELETE RESTRICT,
	... 	FOREIGN KEY("successor") REFERENCES "steps"("identifier") ON UPDATE CASCADE ON DELETE SET NULL
	... );
	... ''')
	>>> result.fetchone()

Der `identifier` ist eine Abfolge aus 6 alphanumerischen Zeichen:
`[a-z0-9][a-z0-9][0-9][0-9][a-z0-9][a-z0-9]`

	>>> result = cursor.execute('''
	... INSERT INTO "steps" ("key","title","identifier","content_id","successor","parent") VALUES
	...  (9,'Lern-Inhalt 3','tj769r','zv9085',NULL,NULL),
	...  (3,'Gruppe 2','8h60e2',NULL,'tj769r',NULL),
	...  (8,'Lern-Inhalt 2','7w13pw','n367f1','8h60e2',NULL),
	...  (1,'Gruppe 1','dv927u',NULL,'7w13pw',NULL),
	...  (7,'Lern-Inhalt 1','4b47ek','0a32m2','dv927u',NULL),
	...  (11,'Lern-Inhalt 1.2','cz42fz','no93v8',NULL,'dv927u'),
	...  (15,'Lern-Inhalt 2.2','r728ue','ze16r1',NULL,'8h60e2'),
	...  (2,'Gruppe 1.1','lh39qn',NULL,'cz42fz','dv927u'),
	...  (13,'Lern-Inhalt 1.1.2','1336lp','mo252y',NULL,'lh39qn'),
	...  (10,'Lern-Inhalt 1.1','au11su','6i86c8','lh39qn','dv927u'),
	...  (12,'Lern-Inhalt 1.1.1','wa99kr','dp0344','1336lp','lh39qn'),
	...  (14,'Lern-Inhalt 2.1','9a16kj','9017x8','r728ue','8h60e2'),
	...  (4,'Gruppe 2.1','8m4465',NULL,'9a16kj','8h60e2'),
	...  (6,'Gruppe 2.1.2','db07kt',NULL,NULL,'8m4465'),
	...  (19,'Lern-Inhalt 2.1.2.2','8r37bi','es819b',NULL,'db07kt'),
	...  (5,'Gruppe 2.1.1','3957og',NULL,'db07kt','8m4465'),
	...  (17,'Lern-Inhalt 2.1.1.2','be5775','oz0969',NULL,'3957og'),
	...  (16,'Lern-Inhalt 2.1.1.1','dn39tw','g970zo','be5775','3957og'),
	...  (18,'Lern-Inhalt 2.1.2.1','4519l3','0x518z','8r37bi','db07kt');
	... ''')
 	>>> result.fetchone()
	>>> connection.commit()


#### mapping

Ein Lern-Inhalt besteht aus einer oder mehreren Varianten. Umgekehrt
kann es aber sein, dass eine Variante in mehreren Lern-Inhalten
auftaucht. Daher speichert die Tabelle *mapping* beiderseitige Zuordnungen.

	>>> result = cursor.execute('''
	... CREATE TABLE "mapping" (
	... 	"content_id"	TEXT,
	... 	"variant_id"	TEXT,
	... 	FOREIGN KEY("variant_id") REFERENCES "variants"("identifier") ON UPDATE CASCADE ON DELETE CASCADE,
	... 	FOREIGN KEY("content_id") REFERENCES "contents"("identifier") ON UPDATE CASCADE ON DELETE CASCADE
	... );
	... ''')
	>>> result.fetchone()


Damit endet die Datenbank-Dokumentation.

	>>> connection.close()


### Lern-Pfad

Eine gerichtete Abfolge aus Varianten in Lern-Inhalten; die
angesteuerten Varianten kann die Lernerin selbst live bestimmen.

- Lern-Pfade ergeben sich insbesondere zur Laufzeit
- Lern-Pfade können vorgeneriert werden, z. B. "Pfad aus allen
  Audio-Varianten"
- später legen wir die im Ordner "Lern-Pfade" ab
- werden vorerst nicht implementiert
