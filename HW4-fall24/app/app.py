
import re  
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__) 

app.secret_key = 'abcdefgh'
  
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'cs353hw4db'
  
mysql = MySQL(app)  

@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        if user:              
            session['loggedin'] = True
            session['userid'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return redirect(url_for('tasks'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)


@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            message = 'Choose a different username!'
  
        elif not username or not password or not email:
            message = 'Please fill out the form!'

        else:
            cursor.execute('INSERT INTO User (id, username, email, password) VALUES (NULL, % s, % s, % s)', (username, email, password,))
            mysql.connection.commit()
            message = 'User successfully created!'

    elif request.method == 'POST':

        message = 'Please fill all the fields!'
    return render_template('register.html', message = message)

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():

    if "loggedin" not in session:
        return redirect(url_for("login")) # user stay in the login page.
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) # u can create many functions with these.

    message =" "

    if request.method == "POST": # the method is post = inserting is going to happen or updating.
        action = request.form.get("action") # get the action of the post method

        if action == "add_task": # add a task method.
            title = request.form.get("title")
            description = request.form.get("description")
            status = request.form.get("status")
            deadline = request.form.get("deadline")
            creation_time = request.form.get("creation_time") or None
            completion_time = request.form.get("completion_time") or None
            user_id = session["userid"]
            task_type = request.form.get("task_type")
            
            # Insert the new task if no duplicate title is found
            cursor.execute("""INSERT INTO Task (title, description, status, deadline, creation_time, completion_time, user_id, task_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (title, description, status, deadline, creation_time, completion_time, user_id, task_type ),)
            mysql.connection.commit()
            last_inserted_id = cursor.lastrowid
            message = f"Task with ID: {last_inserted_id} added successfully."

        if action == "delete_task": # delete a task method.
            task_id = request.form.get("task_id")
            user_id = session["userid"]
            
            if task_id: # Check if the task belongs to the user before deleting
                cursor.execute("SELECT * FROM Task WHERE id = %s AND user_id = %s", (task_id, user_id))
                deleteTask = cursor.fetchone()

                if deleteTask:  # If the task exists, delete it
                    cursor.execute("DELETE FROM Task WHERE id = %s", (task_id,))
                    mysql.connection.commit()
                    message = f"Task with id: {task_id} deleted successfully."
                else:
                    message = f"Task with id: {task_id} doesn't exist for the current user."

        if action == "edit_task":
            taskId = request.form.get("taskId")
        
            if taskId:
                cursor.execute("SELECT * FROM Task WHERE id = %s",(taskId,))
                updateTask = cursor.fetchone()

                if updateTask:
                    title = request.form.get("title")
                    description = request.form.get("description")
                    status = request.form.get("status")
                    deadline = request.form.get("deadline")
                    creation_time = request.form.get("creation_time") or None
                    completion_time = request.form.get("completion_time") or None
                    user_id = session["userid"]
                    task_type = request.form.get("task_type")

                    cursor.execute ("""UPDATE Task SET title = %s , description = %s , status = %s , deadline = %s , 
                    creation_time = %s , completion_time = %s , task_type = %s
                    WHERE id = %s AND user_id = %s""",
                    (title, description, status, deadline, creation_time, completion_time, task_type, taskId , user_id))
                    mysql.connection.commit()
                    message = f"Task with ID: {taskId} edited successfully."
                else:
                    message = f"Task with ID: {taskId} doesn't exist to be edited."
        
        if action == "finish_task":
            finish_id = request.form.get("finish_id")

            if finish_id:
                cursor.execute("""
                SELECT id FROM Task 
                WHERE id = %s AND user_id = %s AND status = %s
                """, (finish_id, session["userid"], "Todo"))
                task = cursor.fetchone()

                if task:  # Task exists and is in 'Todo' status
                    cursor.execute("""
                    UPDATE Task 
                    SET status = %s, completion_time = NOW() 
                    WHERE id = %s AND user_id = %s
                    """, ("Done", finish_id, session["userid"]))
                    mysql.connection.commit()
                    message = f"Task with ID: {finish_id} is marked as Finished. Congrats!"
                else:
                    cursor.execute("""
                    SELECT id, status FROM Task 
                    WHERE id = %s AND user_id = %s
                    """, (finish_id, session["userid"]))
                    task_status = cursor.fetchone()

                    if task_status:
                        message = f"Task with ID: {finish_id} is already marked as 'Done'."
                    else:
                        message = f"Task with ID: {finish_id} does not exist for the current user."

    # Fetch the ongoing tasks for the user.
    cursor.execute("SELECT * FROM Task WHERE user_id = %s ORDER BY deadline ASC", (session['userid'],))
    tasks = cursor.fetchall()

    # Fetch the tasks which were done for the user.
    cursor.execute("SELECT * FROM Task WHERE user_id = %s ORDER BY completion_time ASC", (session['userid'],)) 
    doneTasks = cursor.fetchall()

   
    cursor.execute("SELECT type FROM TaskType") # Fetch TypeTasks
    task_types = cursor.fetchall()

    cursor.close()

    # Render the page with all the functions
    return render_template('tasks.html', tasks=tasks, doneTasks=doneTasks ,task_types=task_types ,message=message)


@app.route('/analysis', methods =['GET', 'POST'])
def analysis():
    if "loggedin" not in session:
        return redirect(url_for("login"))

    user_id = session['userid']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # All tasks of the user in increasing order of deadlines
    cursor.execute("""
    SELECT id, title, task_type, deadline, status FROM Task WHERE user_id = %s ORDER BY deadline ASC""", (user_id,))
    all_tasks = cursor.fetchall()

    # Completed tasks with completion time
    cursor.execute(""" SELECT id, title, completion_time, TIMESTAMPDIFF(HOUR, creation_time, completion_time) AS time_spent 
    FROM Task WHERE user_id = %s AND status = 'Done' ORDER BY completion_time ASC """, (user_id,)) 
    completed_tasks = cursor.fetchall()

    # Uncompleted tasks in increasing order of deadlines
    cursor.execute("""SELECT title, task_type, deadline FROM Task WHERE user_id = %s AND status != 'Done' ORDER BY deadline ASC"""
    , (user_id,))
    uncompleted_tasks = cursor.fetchall()

    # Tasks completed after their deadlines with latency
    cursor.execute("""SELECT id, title, TIMESTAMPDIFF(HOUR, deadline, completion_time) AS late_submission FROM Task
    WHERE user_id = %s AND status = 'Done' AND completion_time > deadline""", (user_id,))
    late_completed_tasks = cursor.fetchall()

    # Num. of completed tasks per task type in descending order
    cursor.execute("""
        SELECT task_type, COUNT(*) AS completed_count
        FROM Task
        WHERE user_id = %s AND status = 'Done'
        GROUP BY task_type
        ORDER BY completed_count DESC
    """, (user_id,))
    completed_tasks_by_type = cursor.fetchall()

    cursor.close()

    return render_template('analysis.html', all_tasks=all_tasks, completed_tasks=completed_tasks, uncompleted_tasks=uncompleted_tasks,
        late_completed_tasks=late_completed_tasks,completed_tasks_by_type=completed_tasks_by_type
    )

@app.route('/logout', methods=['GET', 'POST'])
def logout():

    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
