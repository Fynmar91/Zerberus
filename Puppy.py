#!/usr/bin/env python

#	Projekt: Zerberus FS2V Zugangskontrolle
#	Puppy v1.0
#	Yannik Seitz 30.04.19
#	Dieses Programm startet eine zweite Instanz von Zerberus welche die SQL-Datenbank auf Oeffnunganfragen ueberwacht
#	Sollte es zu einem Fehler kommen wird eine eMail mit einer Fehlermeldung verschickt und ein Neustart durchgefuehrt

import Zerberus

Zerberus.manual()