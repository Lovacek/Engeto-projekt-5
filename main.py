"""projekt_5.py: Pátý projekt do Engeto Online Tester s Pythonem

author: Vítězslav Dlábek
email: vitezslavdlabek@gmail.com
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def pripojeni_db(): #Funkce zajišťující připojení python souboru k dané databázi. 
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME") 
            )   
        cursor = conn.cursor(buffered=True)
        print("\nPřipojení k databázi bylo úspěšné.")
        return conn, cursor
    except mysql.connector.Error as error:
        print(f'\nPři připojení nastala chyba: {error}')
        return None, None
   

def vytvoreni_tabulky(conn, cursor): # Funkce pro vytvoření zakladní tabulky (pokud již neexistuje), se kterou bude program dále pracovat. 
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ukoly (
			id INT AUTO_INCREMENT PRIMARY KEY,
			nazev VARCHAR(50),
			popis VARCHAR(100),
			stav ENUM('Nezahájeno', 'Hotovo', 'Probíhá') DEFAULT 'Nezahájeno',
			datum_vytvoreni DATE);  
                ''')
        conn.commit() 
        
    except mysql.connector.Error as error:
        print(f'\nNastala chyba při tvoření tabulky: {error}')



def hlavni_menu(conn,cursor): #vizualizace základního rozhraní pro další využití programu.

    while True:
        print("""\n
Správce úkolů - Hlavni menu
1. Přidat nový úkol
2. Zobrazit všechny úkoly 
3. Aktualizovat úkol
4. Odstranit úkol
5. Ukončit program""")
        
        vyber = input("\nVyberte možnosti (1-5): ")
        if vyber == "1":
            pridat_ukol(conn,cursor)
        elif vyber == "2":
            zobrazit_ukoly(cursor)
        elif vyber == "3":
            aktualizovat_ukol(conn,cursor)
        elif vyber == "4":
            odstranit_ukol(conn,cursor)
        elif vyber == "5":
            cursor.close()
            conn.close()
            print("\nKonec programu...")
            return
        else:
            print("\nNeplatný vstup")

def pridat_ukol(conn,cursor): #Funkce sbírající data pro přidání nového úkolu do databázové tabulky. Uživatel zadává nazev a popis úkolu, který chce přidat. V případě chybného zadání je funkcí upozorněn.
    while True:
        nazev = input("\nZadejte název úkolu nebo zadejte 'zpět' pro návrat: ")
        if nazev == "zpět":
            break
        if not nazev:
            print("\nNezadali jste název úkolu.")
            continue
        if len(nazev) > 50:
            print("\nMaximalní délka názvu je 50 znaků")
            continue    
        popis = input("\nZadejte popis úkolu nebo zadejte 'zpět' pro návrat: ")
        if popis == "zpět":
            break
        if not popis:
            print("\nNezadali jste popis úkolu.")
            continue
        if len(popis) > 100:
            print("\nMaximalní délka popisu je 100 znaků")
            continue

        pridat_ukol_db(conn, cursor, nazev, popis)
        return

def pridat_ukol_db(conn, cursor,nazev, popis): # Funkce přidávající sesbíraná data do databázové tabulky
    try:
        hodnoty = (nazev, popis)
        sql_prikaz = '''INSERT INTO ukoly (nazev, popis, datum_vytvoreni)
                        VALUES (%s, %s, CURDATE());'''
        cursor.execute(sql_prikaz, hodnoty)
        conn.commit()
    except mysql.connector.Error as error:
        print(f"\nChyba při vkládání dat:{error}")
        raise
    print(f"\nÚkol '{nazev}' byl přidán.")


def zobrazit_ukoly(cursor): #Funkce pro vyobrazení aktuálního seznamu úkolů
            try:
                seznam_ukolu_zob = []
                cursor.execute('''SELECT * FROM ukoly WHERE stav != "Hotovo";''')
                ukoly = cursor.fetchall()
                if len(ukoly) == 0:
                        print("\nSeznam úkolů je prázdný")
                else:
                    print("\nSeznam úkolů:\n")
                    for row in ukoly:
                        seznam_ukolu_zob.append(row)
                    for radek in seznam_ukolu_zob:
                        print(f"ID: {radek[0]} | Název: {radek[1]} | Popis: {radek[2]} | Stav: {radek[3]} | Datum vytvoření: {radek[4]}")
            except mysql.connector.Error as err:
                print(f"\nChyba při načítání dat: {err}")

def odstranit_ukol(conn,cursor): #Funkce pro sběr dat k odstranění úkolu ze seznamu. Funkce vzobrazí seznam úkolu, kde uživatel zadá ID úkolu, který chce odstranit. 
        while True:
            seznam_ukolu_del = []
            seznam_ID_del = []

            cursor.execute('''SELECT * FROM ukoly;''')
            for row in cursor.fetchall():
                seznam_ukolu_del.append(row)
            if len(seznam_ukolu_del) == 0:
                print("\nSeznam úkolů je prázdný")
                return
            else:
                print("\nSeznam úkolů:\n")
                for row in seznam_ukolu_del:
                    seznam_ID_del.append(row[0])
                    print(f"ID: {row[0]} | Název: {row[1]} | Popis: {row[2]} | Stav: {row[3]} | Datum vytvoření: {row[4]}")
                odstraneni = input("\nZadejte číslo úkolu, který chcete odstranit nebo zadejte 'zpět' pro návrat: ")
                if odstraneni == "zpět":
                    break
                elif len(odstraneni) == 0:
                        print("\nNebylo zadáno žádné číslo úkolu.")
                elif not odstraneni.isnumeric():
                    print("\nZadaná hodnota není číslo.")
                else:
                    odstranit_ukol_db(conn, cursor,odstraneni, seznam_ID_del)
                    return

def odstranit_ukol_db(conn, cursor,odstraneni, seznam_ID_del): # Funkce pro odstranění dat z databázové tabulky
    try:
        if int(odstraneni) not in seznam_ID_del:
            print(f"\nÚkol číslo '{odstraneni}' není v seznamu úkolů")
        else:
            cursor.execute('''DELETE FROM ukoly WHERE ID = %s''', (odstraneni,))
            conn.commit()
            print(f"\nÚkol '{odstraneni}' byl odstraněn")
    except mysql.connector.Error as err:
                print(f"\nPři odstranění došlo k chybě!: {err}")

def aktualizovat_ukol(conn,cursor): #Funkce umožňuje uživateli vybrat na jaký stav chce změnit vybraný úkol, a to na "Hotovo" nebo "Probíhající"
    while True:
            seznam_ukolu_act = []
            seznam_ID_act = []

            cursor.execute('''SELECT ID, nazev, stav FROM ukoly''')
            for row in cursor.fetchall():
                seznam_ukolu_act.append(row)
            if len(seznam_ukolu_act) == 0:
                    print("\nSeznam úkolů je prázdný")
                    return
            else:
                print("\nSeznam úkolů:")
                for row in seznam_ukolu_act:
                    seznam_ID_act.append(row[0])
                    print(f"ID: {row[0]} | Název: {row[1]} | Stav: {row[2]}")
                vyber_ID = input("\nVyberte ID úkolu nebo zadejte 'zpět' pro návrat: ")
                if vyber_ID == "zpět":
                    return
                elif len(vyber_ID) == 0:
                    print("\nNebyla vybrána žádná možnost.")
                    vyber_ID = input("\nVyberte ID úkolu nebo zadejte 'zpět' pro návrat: ")
                elif  not vyber_ID.isnumeric():
                    print("\nZadaná hodnota musí být číslo.")
                    vyber_ID = input("\nVyberte ID úkolu nebo zadejte 'zpět' pro návrat: ")
                elif int(vyber_ID) not in seznam_ID_act:
                    print(f"\nÚkol číslo '{vyber_ID}' není v seznamu úkolů")
                    vyber_ID = input("\nVyberte ID úkolu nebo zadejte 'zpět' pro návrat: ")
                else:
                    while True:
                        zmena_stavu = input("\nZadejte 1 pro nový stav 'Probíhá', 2 pro nový stav 'Hotovo' nebo zadejte 'zpět' pro návrat: ")
                        if zmena_stavu == "zpět":
                            return
                        elif zmena_stavu in ['1','2']:
                            aktualizovat_ukol_db(conn,cursor,vyber_ID,zmena_stavu)
                            return 
                        else:
                            print("\nZadali jste nesprávnou hodnotu")          
        
def aktualizovat_ukol_db(conn,cursor,vyber_ID,zmena_stavu): # Funkce aktualizuje stav uzivatelem vybraného úkolu v databázové tabulce
    while True:
        try:
            if zmena_stavu == "1":
                cursor.execute('''UPDATE ukoly SET stav = 'Probíhá' where  ID = %s''', (vyber_ID,))
                conn.commit()
                print(f"\nstav úkolu číslo {vyber_ID} byl změněn.")
                return
            elif zmena_stavu == "2":
                cursor.execute('''UPDATE ukoly SET stav = 'Hotovo' where  ID = %s''', (vyber_ID,))
                conn.commit()
                print(f"\nstav úkolu číslo {vyber_ID} byl změněn.")
                return
            else:
                 print("\nZadali jste nesprávnou hodnotu")
                 break
                 
        except mysql.connector.Error as err:
                print(f"\nChyba při aktualizaci dat: {err}")
                return
        
        

if __name__ == "__main__":

    db_conn, db_cursor = pripojeni_db()

    if db_conn and db_cursor:
        vytvoreni_tabulky(db_conn, db_cursor)   
        hlavni_menu(db_conn, db_cursor)
