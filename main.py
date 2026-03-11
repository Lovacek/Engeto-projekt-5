"""projekt_5.py: Pátý projekt do Engeto Online Tester s Pythonem

author: Vítězslav Dlábek
email: vitezslavdlabek@gmail.com
"""


import mysql.connector


def pripojeni_db():
    try:
        global conn
        conn = mysql.connector.connect(
            host="localhost",       
            user="root",            
            password="12.Kveten97",       
            database="sys", 
            )   
        global cursor
        cursor = conn.cursor(buffered=True)
        print("\nPřipojení k databázi bylo úspěšné.")
    except mysql.connector.Error as error:
        print(f'\nPři připojení nastala chyba: {error}')

def vytvoreni_tabulky():
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



def hlavni_menu():
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
            pridat_ukol()
        elif vyber == "2":
            zobrazit_ukoly()
        elif vyber == "3":
            aktualizovat_ukol()
        elif vyber == "4":
            odstranit_ukol()
        elif vyber == "5":
            cursor.close()
            conn.close()
            print("\nKonec programu...")
            break
        else:
            print("\nNeplatný vstup")

def pridat_ukol():
    while True:
        nazev = input("\nZadejte název úkolu nebo zadejte 'zpět' pro návrat: ")
        if nazev == "zpět":
            break
        while len(nazev) == 0:
            print("\nNezadali jste název úkolu.")
            nazev = input("\nZadejte název úkolu nebo zadejte 'zpět' pro návrat: ") 
        while len(nazev) > 50:
            print("\nMaximalní délka názvu je 50 znaků")
            nazev = input("\nZadejte název úkolu nebo zadejte 'zpět' pro návrat: ")      
        popis = input("\nZadejte popis úkolu nebo zadejte 'zpět' pro návrat: ")
        if popis == "zpět":
            break
        while len(popis) == 0:
            print("\nNezadali jste popis úkolu.")
            popis = input("\nZadejte popis úkolu nebo zadejte 'zpět' pro návrat: ")
        while len(popis) > 100:
            print("\nMaximalní délka popisu je 100 znaků")
            popis = input("\nZadejte popis úkolu nebo zadejte 'zpět' pro návrat: ")
        else:
            try:
                cursor.execute(f'''INSERT INTO ukoly (nazev, popis, datum_vytvoreni)
                                VALUES ('{nazev}', '{popis}', CURDATE());''')
                conn.commit()
            except mysql.connector.Error as error:
                print(f"\nChyba při vkládání dat:{error}")
                break
            print(f"\nÚkol '{nazev}' byl přidán.")
            break

def zobrazit_ukoly():
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

def odstranit_ukol():
        while True:
            try:
                seznam_ukolu_del = []
                seznam_ID_del = []

                cursor.execute('''SELECT * FROM ukoly;''')
                for row in cursor.fetchall():
                    seznam_ukolu_del.append(row)
                if len(seznam_ukolu_del) == 0:
                    print("\nSeznam úkolů je prázdný")
                    break
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
                        if int(odstraneni) not in seznam_ID_del:
                            print(f"\nÚkol číslo '{odstraneni}' není v seznamu úkolů")
                        else:
                            cursor.execute(f'''DELETE FROM ukoly WHERE ID = "{odstraneni}"''' )
                            conn.commit()
                            print(f"\nÚkol '{odstraneni}' byl odstraněn")
                            break
            except mysql.connector.Error as err:
                print(f"\nPři odstranění došlo k chybě!: {err}")

def aktualizovat_ukol():
    while True:
        try:
            seznam_ukolu_act = []
            seznam_ID_act = []

            cursor.execute('''SELECT ID, nazev, stav FROM ukoly''')
            for row in cursor.fetchall():
                seznam_ukolu_act.append(row)
            if len(seznam_ukolu_act) == 0:
                    print("\nSeznam úkolů je prázdný")
                    break
            else:
                print("\nSeznam úkolů:")
                for row in seznam_ukolu_act:
                    seznam_ID_act.append(row[0])
                    print(f"ID: {row[0]} | Název: {row[1]} | Stav: {row[2]}")
                vyber_ID = input("\nVyberte ID úkolu nebo zadejte 'zpět' pro návrat: ")
                if vyber_ID == "zpět":
                    break
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
                            break
                        elif zmena_stavu not in ['1','2']:
                            print("\nZadali jste nesprávnou hodnotu")
                            zmena_stavu = input("\nZadejte 1 pro nový stav 'Probíhá', 2 pro nový stav 'Hotovo' nebo zadejte 'zpět' pro návrat: ")
                        elif zmena_stavu == "1":
                            cursor.execute(f'''UPDATE ukoly SET stav = 'Probíhá' where  ID ={vyber_ID} ''')
                            conn.commit()
                            print(f"\nstav úkolu číslo {vyber_ID} byl změněn.")
                            break
                        else:
                            cursor.execute(f'''UPDATE ukoly SET stav = 'Hotovo' where  ID ={vyber_ID} ''')
                            conn.commit()
                            print(f"\nstav úkolu číslo {vyber_ID} byl změněn.")
                            break
            break           
        except mysql.connector.Error as err:
                print(f"\nChyba při aktualizaci dat: {err}")
                break

pripojeni_db()
vytvoreni_tabulky()   
hlavni_menu()