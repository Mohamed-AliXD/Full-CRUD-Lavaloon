import pymysql


def get_connection():
    
    connection = pymysql.connect(
        host="localhost",       
        user="root",          
        password="rootroot",
        database="crud_api",    
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
