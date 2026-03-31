"""projekt_5.py: Pátý projekt do Engeto Online Tester s Pythonem

author: Vítězslav Dlábek
email: vitezslavdlabek@gmail.com
"""
import os
from dotenv import load_dotenv
import mysql.connector
import pytest
import main

@pytest.fixture(scope="function")

def priprava_db(): #Funkce připojí program k testovací databázi, vytvoří tabulku stejné struktury jako tabulka hlavní databáze a následně po testu vše smaže.
        
    conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")       
        )   
    cursor = conn.cursor(buffered=True)

    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db")
    cursor.execute("USE test_db")
    
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS ukoly (
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
    
    main.pridat_ukol_db(conn,cursor, nazev='Úkol 1', popis='Umýt nádobí')

    cursor.execute('''SELECT * FROM ukoly WHERE nazev = "Úkol 1"''')

    vysledek = cursor.fetchone()

    assert vysledek is not None, "Záznam nebyl vložen do tabulky."
    assert vysledek[1] == 'Úkol 1', "Jméno úkolu se nepřidalo správně."
    assert vysledek[2] == 'Umýt nádobí', "Popis úkolu se nepřidal správně."

def test_pridani_ukolu_negativni(priprava_db): #Test reakce programu na zadání názvu delšího než je povolená délka. 
    conn, cursor = priprava_db
    prilis_dlouhy_nazev = "a"*300
    prilis_dlouhy_popis = "b"*300

    with pytest.raises(mysql.connector.Error, match="Data too long for column"):
    
        main.pridat_ukol_db(conn,cursor, nazev=prilis_dlouhy_nazev, popis=prilis_dlouhy_popis)
        

def test_aktualizace_ukolu_pozitivni(priprava_db): #Pozitivní test změný stavu úkolu na validní hodnotu 'Hotovo'
    conn, cursor = priprava_db

    main.pridat_ukol_db(conn,cursor, nazev='Úkol 1', popis='Umýt nádobí')

    main.aktualizovat_ukol_db(conn, cursor, vyber_ID="1", zmena_stavu= "2")

    cursor.execute('''SELECT * FROM ukoly WHERE nazev = "Úkol 1"''')

    vysledek = cursor.fetchone()

    assert vysledek[3] == 'Hotovo', "Aktualizace úkolu neproběhla správně."

def test_aktualizace_ukolu_negativni(priprava_db, capsys): #Test reakce programu na pokus změnit stav úkolu na hodnotu nedefinovanou v možnostech kolonky "stav". 
    conn, cursor = priprava_db

    main.pridat_ukol_db(conn,cursor, nazev='Úkol 1', popis='Umýt nádobí')

    main.aktualizovat_ukol_db(conn, cursor, vyber_ID="1", zmena_stavu= "5")

    captured = capsys.readouterr()

    assert "Zadali jste nesprávnou hodnotu" in captured.out

def test_odstraneni_ukolu_pozitivni(priprava_db): #Odstranění existujícího úkolu, funkce nejdříve vytvoří předem nadefinovaný úkol a následně se jej pokusí odstranit. 
    conn, cursor = priprava_db

    main.pridat_ukol_db(conn,cursor, nazev='Úkol 1', popis='Umýt nádobí')

    main.odstranit_ukol_db(conn, cursor, odstraneni= 1 ,seznam_ID_del=[1])

    cursor.execute('''SELECT * FROM ukoly WHERE nazev = "Úkol 1"''')

    vysledek = cursor.fetchone()

    assert vysledek is None, "Odstranění úkolu se nepodařilo."

def test_odstraneni_ukolu_negativni(priprava_db): #Odstranění neexistujícího úkolu, funkce vytvoří do prázdné tabulky úkolu s ID "1" a poté se pokusí odstranit neexistující úkol s ID "2", následně zkotroluje jestli obsah tabulky zůstal zachován.
    conn, cursor = priprava_db

    main.pridat_ukol_db(conn,cursor, nazev='Úkol 1', popis='Umýt nádobí')

    cursor.execute('''SELECT COUNT(*) FROM ukoly''')

    pocatecni_pocet_ukolu = cursor.fetchall()

    main.odstranit_ukol_db(conn, cursor, odstraneni= 2 ,seznam_ID_del=[1])

    cursor.execute('''SELECT COUNT(*) FROM ukoly''')

    konecny_pocet_ukolu = cursor.fetchall()

    assert konecny_pocet_ukolu == pocatecni_pocet_ukolu, "Část obsahu databáze byla odebrána"


    

