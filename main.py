from flask import *
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.secret_key = "123"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'bayat'
app.config['MYSQL_PASSWORD'] = '111'
app.config['MYSQL_DB'] = 'dbfinal'

mysql = MySQL(app)


@app.route("/")
@app.route("/Home")
def index():
    if "email" in session:
        email = session["email"]
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (email,))
        userID = c.fetchone()
        c.execute("SELECT title, creationDate, reminderDate, description, ID FROM reminder WHERE creatorID = %s", (userID,))
        userReminders = c.fetchall()
        c.execute("SELECT title, creationDate, deadline, description, status, ID FROM task WHERE creatorID = %s", (userID,))
        userTasks = c.fetchall()
        c.execute("SELECT title, creationDate, body, ID FROM note WHERE creatorID = %s", (userID,))
        userNotes = c.fetchall()
        
        c.close()
        
        allItems = []
        
        for reminder in userReminders:
            allItems.append({'type': 'reminder', 'title': reminder[0], 'creationDate': reminder[1], 'reminderDate': reminder[2], 'description': reminder[3], 'ID': reminder[4]})
        
        for task in userTasks:
            allItems.append({'type': 'task', 'title': task[0], 'creationDate': task[1], 'deadline': task[2], 'description': task[3], 'status': task[4], 'ID': task[5]})
        
        for note in userNotes:
            allItems.append({'type': 'note', 'title': note[0], 'creationDate': note[1], 'body': note[2], 'ID': note[3]})
        
        allItems.sort(key=lambda x: x['title'])
        print(allItems)
        
        return render_template("Home.html", username=session["email"], allItems=allItems)
    else:
        return render_template("Home.html")

@app.route("/add/<string:type>", methods=['GET', 'POST'])
def add_item(type):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        creation_date = datetime.now().strftime("%Y-%m-%d")
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (session["email"],))
        userID = c.fetchone()
        if type == 'reminder':
            reminder_date = request.form['reminder_date']
            c.execute("INSERT INTO reminder (title, description, creationDate, reminderDate, creatorID) VALUES (%s, %s, %s, %s, %s)",
                      (title, description, creation_date, reminder_date, userID))
        elif type == 'task':
            default = "0"
            deadline = request.form['deadline']
            c.execute("INSERT INTO task (title, description, creationDate, deadline, creatorID, type, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                      (title, description, creation_date, deadline, userID, default, default))
        elif type == 'note':
            body = request.form['body']
            c.execute("INSERT INTO note (title, body, creationDate, creatorID) VALUES (%s, %s, %s, %s)",
                      (title, body, creation_date, userID))
        mysql.connection.commit()
        c.close()
        return redirect(url_for('index'))
    return render_template('additem.html', type = type)
    
@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        c = mysql.connection.cursor()
        c.execute("SELECT * FROM registereduser WHERE email = %s AND password = %s", (email, password))
        row = c.fetchone()
        c.close()
        if row != None:
            session["email"] = email
            return render_template("Home.html", message = "Successfully logged in!")
        else:
            return render_template("login.html", message="User not found!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for('index'))

@app.route("/register", methods = ["GET", "POST"])
def Register():
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]
        password = request.form["password"]
        email = request.form["email"]
        bdate = request.form["bdate"]
        c = mysql.connection.cursor()
        c.execute("SELECT * FROM registereduser WHERE email = %s", (email,))
        row = c.fetchone()
        if row != None:
            return render_template("register.html", message = "The email is already in use. Please select a different email.")
        typeDefault = 0
        typeNull = 'NULL'
        c.execute("INSERT INTO user (type) VALUE (%s)", (typeDefault,))

        c.execute("SELECT LAST_INSERT_ID();")
        row = c.fetchone()
        c.execute("INSERT INTO registereduser (userID, email, name, surname, password, birthDate, ) VALUES (%s, %s, %s, %s, %s, %s)", (row[0], email, name, surname, password, bdate))

        c.close()
        return render_template("login.html", message = "Successfully registered!")
    return render_template("register.html", message="Error registering")

@app.route('/seemore/<string:type>/<int:itemID>', methods=['GET', 'POST'])
def seemore(type, itemID):
    temp = []
    c = mysql.connection.cursor()
    if type == 'reminder':
        c.execute("SELECT title, creationDate, reminderDate, description FROM reminder WHERE ID = %s", (itemID,))
        row = c.fetchone()
        temp.append(itemID)
        temp.append(row[0])
        temp.append(row[1])
        temp.append(row[2])
        temp.append(row[3])
        return render_template("seemore.html", type = type, temp = temp)
    elif type == 'task':
        c.execute("SELECT title, creationDate, deadline, description, status FROM task WHERE ID = %s", (itemID,))
        row = c.fetchone()
        temp.append(itemID)
        temp.append(row[0])
        temp.append(row[1])
        temp.append(row[2])
        temp.append(row[3])
        temp.append(row[4])
        return render_template("seemore.html", type = type, temp = temp)
    elif type == 'note':
        c.execute("SELECT title, creationDate, body FROM note WHERE ID = %s", (itemID,))
        row = c.fetchone()
        temp.append(itemID)
        temp.append(row[0])
        temp.append(row[1])
        temp.append(row[2])
        return render_template("seemore.html", type = type, temp = temp)
    else:
        return render_template("Home.html")
    
@app.route('/edit/<string:type>/<int:itemID>', methods=['GET', 'POST'])
def edit_item(type, itemID):
    if request.method == 'POST':
        # Update the item in the database
        title = request.form['title']
        description = request.form['description']
        c = mysql.connection.cursor()
        if type == 'reminder':
            c.execute("UPDATE reminder SET title=%s, description=%s WHERE ID=%s", (title, description, itemID))
        elif type == 'task':
            c.execute("UPDATE task SET title=%s, description=%s WHERE ID=%s", (title, description, itemID))
        elif type == 'note':
            c.execute("UPDATE note SET title=%s, body=%s WHERE ID=%s", (title, description, itemID))
        mysql.connection.commit()
        return redirect(url_for('seeadvertisements', type=type, itemID=itemID))
    else:
        c = mysql.connection.cursor()
        temp = []
        if type == 'reminder':
            c.execute("SELECT title, description FROM reminder WHERE ID = %s", (itemID,))
        elif type == 'task':
            c.execute("SELECT title, description FROM task WHERE ID = %s", (itemID,))
        elif type == 'note':
            c.execute("SELECT title, body FROM note WHERE ID = %s", (itemID,))
        row = c.fetchone()
        temp.append(itemID)
        temp.append(row[0])
        temp.append(row[1])
        return render_template("edit.html", type=type, temp=temp)

@app.route('/delete/<string:type>/<int:itemID>', methods=['GET', 'POST'])
def delete_item(type, itemID):
    c = mysql.connection.cursor()
    if type == 'reminder':
        c.execute("DELETE FROM reminder WHERE ID = %s", (itemID,))
    elif type == 'task':
        c.execute("DELETE FROM task WHERE ID = %s", (itemID,))
    elif type == 'note':
        c.execute("DELETE FROM note WHERE ID = %s", (itemID,))
    mysql.connection.commit()
    return redirect(url_for('index'))

@app.route("/reminders")
def reminders():
    if "email" in session:
        email = session["email"]
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (email, ))
        userID = c.fetchone()
        c.execute("SELECT title, creationDate, reminderDate, description, ID FROM reminder WHERE creatorID = %s", (userID,))
        userReminders = c.fetchall()
        c.close()
        
        allItems = []
        
        for reminder in userReminders:
            allItems.append({'type': 'reminder', 'title': reminder[0], 'creationDate': reminder[1], 'reminderDate': reminder[2], 'description': reminder[3], 'ID': reminder[4]})
        
        
        allItems.sort(key=lambda x: x['title'])
        print(allItems)
        
        return render_template("reminders.html", username = session["email"], allItems=allItems)
    else:
        return render_template("reminders.html")

@app.route("/tasks")
def tasks():
    if "email" in session:
        email = session["email"]
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (email, ))
        userID = c.fetchone()
        c.execute("SELECT title, creationDate, deadline, description, status, ID FROM task WHERE creatorID = %s", (userID,))
        userTasks = c.fetchall()
    
        c.close()
        
        allItems = []
        
      
        for task in userTasks:
            allItems.append({'type': 'task', 'title': task[0], 'creationDate': task[1], 'deadline': task[2], 'description': task[3], 'status': task[4], 'ID': task[5]})
       
        allItems.sort(key=lambda x: x['title'])
        print(allItems)
        
        return render_template("tasks.html", username = session["email"], allItems=allItems)
    else:
        return render_template("tasks.html")
    
@app.route("/togglestatus/<int:task_id>/<int:camefrom>")
def toggle_status(task_id, camefrom):
    c = mysql.connection.cursor()
    c.execute("SELECT status FROM task WHERE ID = %s", (task_id,))
    current_status = c.fetchone()[0]
    new_status = 1 if current_status == 0 else 0
    c.execute("UPDATE task SET status = %s WHERE ID = %s", (new_status, task_id))
    mysql.connection.commit()
    c.close()
    if camefrom == 1:
        return redirect(url_for('boards'))
    else:
        return redirect(url_for('index'))

@app.route("/notes")
def notes():
    if "email" in session:
        email = session["email"]
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (email, ))
        userID = c.fetchone()
        c.execute("SELECT title, creationDate, body, ID FROM note WHERE creatorID = %s", (userID,))
        userNotes = c.fetchall()
        
        c.close()
        
        
        allItems = []
        
        
        for note in userNotes:
            allItems.append({'type': 'note', 'title': note[0], 'creationDate': note[1], 'body': note[2], 'ID': note[3]})
        
        allItems.sort(key=lambda x: x['title'])
        print(allItems)
        
        return render_template("notes.html", username = session["email"], allItems=allItems)
    else:
        return render_template("notes.html")

@app.route("/friendslist")
def friendslist():
    if "email" in session:
        email = session["email"]
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (email, ))
        userID = c.fetchone()[0]
        c.execute("SELECT user2ID FROM friends WHERE user1ID = %s", (userID,))
        userFriends = c.fetchall()
        
        allItems = []
        
        for item in userFriends:
            c.execute("SELECT userID, email, name, surname FROM registereduser WHERE userID = %s", (item,))
            userFriendsList = c.fetchone()
            allItems.append({'userID': userFriendsList[0], 'email': userFriendsList[1], 'name': userFriendsList[2], 'surname': userFriendsList[3]})
        
        c.close()
        
        allItems.sort(key=lambda x: x['name'])
        
        return render_template("friendslist.html", username=session["email"], allItems=allItems)
    else:
        return render_template("friendslist.html")
    
@app.route("/addfriend", methods=["GET", "POST"])
def addfriend():
    if "email" in session:
        if request.method == "POST":
            friend_email = request.form["email"]
            c = mysql.connection.cursor()
            c.execute("SELECT userID FROM registereduser WHERE email = %s", (session["email"], ))
            userID = c.fetchone()[0]
            c.execute("SELECT userID FROM registereduser WHERE email = %s", (friend_email, ))
            friendID = c.fetchone()
            
            if friendID:
                friendID = friendID[0]
                c.execute("INSERT INTO friends (user1ID, user2ID) VALUES (%s, %s)", (userID, friendID))
                mysql.connection.commit()
            c.close()
            return redirect(url_for("friendslist"))
        
        return '''
            <form method="POST">
                Friend Email: <input type="text" name="email">
                <input type="submit" value="Add Friend">
            </form>
        '''
    else:
        return redirect(url_for("login"))

@app.route("/deletefriend/<int:friend_id>")
def deletefriend(friend_id):
    if "email" in session:
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (session["email"], ))
        userID = c.fetchone()[0]
        c.execute("DELETE FROM friends WHERE user1ID = %s AND user2ID = %s", (userID, friend_id))
        mysql.connection.commit()
        c.close()
        return redirect(url_for("friendslist"))
    else:
        return redirect(url_for("login"))


@app.route("/sharedwithme")
def sharedwithme():
    if "email" in session:
        email = session["email"]
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (email,))
        userID = c.fetchone()[0]
        
        # Fetch shared notes
        c.execute("""
            SELECT note.ID, note.title, note.body, registereduser.name, registereduser.surname, registereduser.email, noteaccess.accessType
            FROM note
            JOIN noteaccess ON note.ID = noteaccess.noteID
            JOIN registereduser ON note.creatorID = registereduser.userID
            WHERE noteaccess.userID = %s
        """, (userID,))
        shared_notes = c.fetchall()
        
        # Fetch shared reminders
        c.execute("""
            SELECT reminder.ID, reminder.title, reminder.description, registereduser.name, registereduser.surname, registereduser.email, reminderaccess.accessType
            FROM reminder
            JOIN reminderaccess ON reminder.ID = reminderaccess.reminderID
            JOIN registereduser ON reminder.creatorID = registereduser.userID
            WHERE reminderaccess.userID = %s
        """, (userID,))
        shared_reminders = c.fetchall()
        
        # Fetch shared tasks
        c.execute("""
            SELECT task.ID, task.title, task.description, registereduser.name, registereduser.surname, registereduser.email, taskaccess.accessType
            FROM task
            JOIN taskaccess ON task.ID = taskaccess.taskID
            JOIN registereduser ON task.creatorID = registereduser.userID
            WHERE taskaccess.userID = %s
        """, (userID,))
        shared_tasks = c.fetchall()
        
        c.close()
        
        shared_items = {
            'notes': shared_notes,
            'reminders': shared_reminders,
            'tasks': shared_tasks
        }
        
        return render_template("sharedwithme.html", shared_items=shared_items)
    else:
        return render_template("sharedwithme.html")
    
    
@app.route("/boards")
def boards():
    if "email" in session:
        email = session["email"]
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (email,))
        userID = c.fetchone()

        c.execute("SELECT ID, title FROM board WHERE creatorID = %s", (userID,))
        userBoards = c.fetchall()

        boards_data = []
        for board in userBoards:
            boardID = board[0]
            board_name = board[1]

            c.execute("SELECT title, creationDate, reminderDate, description, ID FROM reminder WHERE ID = %s", (boardID,))
            boardReminders = c.fetchall()

            c.execute("SELECT title, creationDate, deadline, description, status, ID FROM task WHERE ID = %s", (boardID,))
            boardTasks = c.fetchall()

            c.execute("SELECT title, creationDate, body, ID FROM note WHERE ID = %s", (boardID,))
            boardNotes = c.fetchall()

            boardItems = []
            for reminder in boardReminders:
                boardItems.append({'type': 'reminder', 'title': reminder[0], 'creationDate': reminder[1], 'reminderDate': reminder[2], 'description': reminder[3], 'ID': reminder[4]})

            for task in boardTasks:
                boardItems.append({'type': 'task', 'title': task[0], 'creationDate': task[1], 'deadline': task[2], 'description': task[3], 'status': task[4], 'ID': task[5]})

            for note in boardNotes:
                boardItems.append({'type': 'note', 'title': note[0], 'creationDate': note[1], 'body': note[2], 'ID': note[3]})

            boards_data.append({'id': boardID, 'name': board_name, 'items': boardItems})

        c.close()

        return render_template("boards.html", username=session["email"], boards=boards_data)
    else:
        return redirect(url_for('login'))

@app.route("/add/<string:type>/<int:board_id>", methods=['GET', 'POST'])
def additemtoboard(type, board_id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        creation_date = datetime.now().strftime("%Y-%m-%d")
        c = mysql.connection.cursor()
        c.execute("SELECT userID FROM registereduser WHERE email = %s", (session["email"],))
        userID = c.fetchone()
        if type == 'reminder':
            reminder_date = request.form['reminder_date']
            c.execute("INSERT INTO reminder (title, description, creationDate, reminderDate, creatorID, ID) VALUES (%s, %s, %s, %s, %s, %s)",
                      (title, description, creation_date, reminder_date, userID, board_id))
        elif type == 'task':
            default = "0"
            deadline = request.form['deadline']
            c.execute("INSERT INTO task (title, description, creationDate, deadline, creatorID, type, status, ID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                      (title, description, creation_date, deadline, userID, default, default, board_id))
        elif type == 'note':
            body = request.form['body']
            c.execute("INSERT INTO note (title, body, creationDate, creatorID, ID) VALUES (%s, %s, %s, %s, %s)",
                      (title, body, creation_date, userID, board_id))
        mysql.connection.commit()
        c.close()
        return redirect(url_for('boards'))
    return render_template('additem.html', type=type)

@app.route('/share/<type>/<int:item_id>', methods=['GET', 'POST'])
def share_item(type, item_id):
    if request.method == 'GET':
        if 'email' in session:
            email = session['email']
            c = mysql.connection.cursor()
            c.execute("SELECT userID FROM registereduser WHERE email = %s", (email,))
            user_id = c.fetchone()[0]
            c.execute("SELECT user2ID, name, surname, email FROM registereduser "
                      "JOIN friends ON registereduser.userID = friends.user2ID WHERE friends.user1ID = %s", (user_id,))
            friends = [{'userID': row[0], 'name': row[1], 'surname': row[2], 'email': row[3]} for row in c.fetchall()]
            return render_template('share.html', type=type, temp=[item_id], friends=friends)
        else:
            return redirect(url_for('login'))
    elif request.method == 'POST':
        if 'email' in session:
            selected_friends = request.form.getlist('friends')
            table_map = {'note': 'noteaccess', 'reminder': 'reminderaccess', 'task': 'taskaccess'}
            if type not in table_map:
                return "Invalid item type", 400
            table = table_map[type]
            default = '0'
            c = mysql.connection.cursor()
            for friend_id in selected_friends:
                if table == 'notaccess':
                    print(table)
                    c.execute("INSERT INTO notaccess (noteID, userID, accesstype) VALUES (%s, %s, %s)", (item_id, friend_id, default))
                    
                elif table == 'reminderaccess':
                    print(table)
                    c.execute("INSERT INTO reminderaccess (reminderID, userID, accesstype) VALUES (%s, %s, %s)", (item_id, friend_id, default))
                else: 
                    print(table)
                    c.execute("INSERT INTO taskaccess (taskID, userID, accesstype, individualStatus) VALUES (%s, %s, %s, %s)", (item_id, friend_id, default, default))
            mysql.connection.commit()
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))



    
if __name__ == '__main__':
    app.debug = True
    app.run()