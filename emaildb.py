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
    persons = cursor.fetchall()
    if not persons:
        bprint("No Data Stored")
    for p in persons:
        print(p)
    close_db()

def add_email():
    run_db()
    bprint("Adding Email...")
    add_query = "INSERT INTO Person (Name, Email) VALUES (?, ?)"

    bprint("Name of person:")
    name = input()
    update_query = None
    lookup_query = "SELECT * FROM Person WHERE Name=?"
    cursor.execute(lookup_query, (name,))
    lookup_person = cursor.fetchall()
    if lookup_person:
        bprint("Person already exists! Would you like to update?")
        update = input()
        if (update[0] == 'y'):
            update_query = "UPDATE Person SET Email=? WHERE Name=?"
        if (update[0] == 'n'):
            return
    email_prompt = "Email Address of " + name + ":"
    bprint(email_prompt)
    email = input()
    if update_query:
        cursor.execute(update_query, (email, name))
        db.commit()
    elif not update_query: #then just add
        cursor.execute(add_query, (name, email))
        db.commit()
        bprint("Succesfully added!")
    close_db()

def delete_email():
    run_db()
    bprint("Deleting email...")
    bprint("Name of person:")
    name = input()
    lookup_query = "SELECT * FROM Person WHERE Name=?"
    cursor.execute(lookup_query, (name,))
    dropped_person = cursor.fetchall()
    if not dropped_person:
        bprint("Oops! No entry exists in the database!")
        return
    bprint("Drop this person?")
    for p in dropped_person:
        print (p)
    drop = input()
    if (drop[0] == 'y'):
        delete_query = "DELETE FROM Person WHERE Name=?"
        cursor.execute(delete_query, (name,))
        db.commit()
        bprint("Succesfully dropped!")
    close_db()

#Returns list of persons
def loadDB():
    run_db()
    bprint("Sending emails to those in database...")
    list = []
    cursor.execute("SELECT Person.Name, Person.Email FROM Person;")
    results = cursor.fetchall()
    for r in results:
        # print(r)
        list.append(r)
    return list
    close_db()

def restartDB():
    run_db()
    db.execute('DROP TABLE IF EXISTS Person')
    db.execute('CREATE TABLE Person (Name text, Email text)')
    bprint("Database Restarted")
    close_db()

def bprint(obj):
    bolded = BOLD + obj + unBOLD
    print (bolded)
    return bolded
