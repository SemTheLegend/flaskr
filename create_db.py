import mysql.connector

my_db = mysql.connector.connect(host="localhost",
                                user="root",
                                passwd = "Legend1240s26#"
                                )

my_cursor = my_db.cursor()

my_cursor.execute("CREATE DATABASE IF NOT EXISTS flask_blog_db")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)
    
my_cursor.close()
my_db.close()


# <!-- <a href="{{ url_for('delete_post', id=post.id) }}" class="btn btn-outline-danger btn-sm">Delete Post</a> -->