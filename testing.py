"""projekt_5.py: Pátý projekt do Engeto Online Tester s Pythonem

author: Vítězslav Dlábek
email: vitezslavdlabek@gmail.com
"""

import mysql.connector
import pytest

@pytest.fixture(scope="function")

def priprava_db(): #Funkce připojí program k testovací databázi, vytvoří tabulku stejné struktury jako tabulka hlavní databáze a následně po testu vše smaže.
        
    conn = mysql.connector.connect(
        host="localhost",       
        user="root",            
        password="12345",       
        )   
    cursor = conn.cursor(buffered=True)

    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
    cursor.execute("USE test_db")
    
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_tabulka (
			id INT AUTO_INCREMENT PRIMARY KEY,
			nazev VARCHAR(50),
			popis VARCHAR(100),
			stav ENUM('Nezahájeno', 'Hotovo', 'Probíhá') DEFAULT 'Nezahájeno',
			datum_vytvoreni DATE);  
                ''')
    conn.commit()

    yield conn, cursor
    cursor.execute("DROP DATABASE test_db")
    conn.commit()

    cursor.close()
    conn.close()

def test_pridani_ukolu_pozitivni(priprava_db): #Test přidání úkolu do tabulky při použití validních hodnot.
    conn, cursor = priprava_db
    cursor.execute('''INSERT INTO test_tabulka (nazev, popis, datum_vytvoreni) VALUES ('Úkol 1', 'Umýt nádobí', CURDATE());''')
    conn.commit()

    cursor.execute('''SELECT * FROM test_tabulka WHERE nazev = "Úkol 1"''')

    vysledek = cursor.fetchone()

    assert vysledek is not None, "Záznam nebyl vložen do tabulky."
    assert vysledek[1] == 'Úkol 1', "Jméno úkolu se nepřidalo správně."
    assert vysledek[2] == 'Umýt nádobí', "Popis úkolu se nepřidal správně."

def test_pridani_ukolu_negativni(priprava_db): #Test reakce programu na zadání názvu delšího než je povolená délka. 
    conn, cursor = priprava_db

    with pytest.raises(mysql.connector.Error, match="Data too long for column"):
        cursor.execute('''INSERT INTO test_tabulka (nazev, popis) VALUES (REPEAT('a', 100), REPEAT('b', 100));''')
        conn.commit()

def test_aktualizace_ukolu_pozitivni(priprava_db): #Pozitivní test změný stavu úkolu na validní hodnotu 'Hotovo'
    conn, cursor = priprava_db

    cursor.execute('''INSERT INTO test_tabulka (nazev, popis, datum_vytvoreni) VALUES ('Úkol 1', 'Umýt nádobí', CURDATE());''')
    conn.commit()

    cursor.execute('''UPDATE test_tabulka SET stav = "Hotovo" WHERE nazev = "Úkol 1"''')
    conn.commit()

    cursor.execute('''SELECT * FROM test_tabulka WHERE nazev = "Úkol 1"''')

    vysledek = cursor.fetchone()

    assert vysledek[3] == 'Hotovo', "Aktualizace úkolu neproběhla správně."

def test_aktualizace_ukolu_negativni(priprava_db): #Test reakce programu na pokus změnit stav úkolu na hodnotu nedefinovanou v možnostech kolonky "stav". 
    conn, cursor = priprava_db

    cursor.execute('''INSERT INTO test_tabulka (nazev, popis, datum_vytvoreni) VALUES ('Úkol 1', 'Umýt nádobí', CURDATE());''')
    conn.commit()

    with pytest.raises(mysql.connector.Error, match="Data truncated for column"):
        cursor.execute('''UPDATE test_tabulka SET stav = "Rozděláno" WHERE nazev = "Úkol 1"''')
        conn.commit()

def test_odstraneni_ukolu_pozitivni(priprava_db): #Odstranění existujícího úkolu, funkce nejdříve vytvoří předem nadefinovaný úkol a následně se jej pokusí odstranit. 
    conn, cursor = priprava_db

    cursor.execute('''INSERT INTO test_tabulka (nazev, popis, datum_vytvoreni) VALUES ('Úkol 1', 'Umýt nádobí', CURDATE());''')
    conn.commit()

    cursor.execute('''DELETE from test_tabulka WHERE nazev = "Úkol 1"''')
    conn.commit()

    cursor.execute('''SELECT * FROM test_tabulka WHERE nazev = "Úkol 1"''')

    vysledek = cursor.fetchone()

    assert vysledek is None, "Odstranění úkolu se nepodařilo."

def test_odstraneni_ukolu_negativni(priprava_db): #Odstranění neexistujícího úkolu, funkce vytvoří do prázdné tabulky úkolu s názvem "úkol 1" a poté se pokusí odstranit neexistující úkol s názvem "úkol 2", následě zkotroluje jestli obsah tabulky zůstal zachován.
    conn, cursor = priprava_db

    cursor.execute('''INSERT INTO test_tabulka (nazev, popis, datum_vytvoreni) VALUES ('Úkol 1', 'Umýt nádobí', CURDATE());''')
    conn.commit()

    cursor.execute('''SELECT COUNT(*) FROM test_tabulka''')

    pocatecni_pocet_ukolu = cursor.fetchall()

    cursor.execute('''DELETE from test_tabulka WHERE nazev = "Úkol 2"''')
    conn.commit()

    cursor.execute('''SELECT COUNT(*) FROM test_tabulka''')

    konecny_pocet_ukolu = cursor.fetchall()

    assert konecny_pocet_ukolu == pocatecni_pocet_ukolu, "Část obsahu databáze byla odebrána"


    

