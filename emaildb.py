import sqlite3

BOLD = '\033[1m'
unBOLD = '\033[0m'
db = None
cursor = None

# db.execute('INSERT INTO Person (Name text, Email text) VALUES (Anderson, anderswang924@gmail.com)')
def run_db():
    global db
    db = sqlite3.connect('Emails.db')
    global cursor
    cursor = db.cursor()

def close_db():
    cursor.close()
    db.close()

def email_list():
    run_db()
    bprint("Printing Email List...")
    cursor.execute("SELECT Person.Name, Person.Email FROM Person;")
    results = cursor.fetchall()
    if not results:
        bprint("No Data Stored")
    for r in results:
        print(r)
    close_db()

def add_email():
    run_db()
    bprint("Adding Email...")
    name = input("Name of person:\n")
    email = input("Email Address of " + name + ":\n")
    new_person = (name, email)
    query = "INSERT INTO Person (Name, Email) VALUES (?, ?)"
    cursor = db.cursor()
    cursor.execute(query, list(new_person))
    db.commit()
    print (new_person)
    bprint("Succesfully added!")
    close_db()

def loadDB():
    run_db()
    bprint("Sending emails to those in database...")
    list = []
    cursor.execute("SELECT Person.Name, Person.Email FROM Person;")
    results = cursor.fetchall()
    for r in results:
        bprint ("Sending to ")
        print(r)
        list.append(r[1])
    return list
    close_db()

def restartDB():
    run_db()
    bprint("Database Restarted")
    db.execute('DROP TABLE IF EXISTS Person')
    db.execute('CREATE TABLE Person (Name text, Email text)')
    close_db()

def bprint(obj):
    print (BOLD + obj + unBOLD)
