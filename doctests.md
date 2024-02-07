# doctests für Luna LMS

## Doctests ausführen

Die Tests in dieser Datei können auf einer Kommandozeile ausgeführt werden mit:

	python -m doctest doctests.md


## Module

	>>> import luna_lms
	>>> import luna_lms.storage
	>>> import luna_lms.webapp


## storage-Klassen

	>>> fs = luna_lms.storage.FileStorage()
	>>> sq = luna_lms.storage.SQLiteStorage()
