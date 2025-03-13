import psycopg2

# Global connection
conn = None

# Postgres connection
def get_postgres_connection():
    try:
        conn = psycopg2.connect(
            dbname="ClaimRequest",
            user="postgres",
            password="12345",
            host="14.225.253.6",  
            port="5432"   
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None


def fetch_data():
    conn = get_postgres_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roles;")  
        rows = cursor.fetchall()
        
        for row in rows:
            print(row)
        
        cursor.close()
        conn.close()

def preview_table(table_name):
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.close()
    conn.close()

def close_connection():
    global conn
    if conn:
        conn.close()
        conn = None

def test_query():
  conn = get_postgres_connection()
  cursor = conn.cursor()
  # cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'claim' AND table_schema = 'public';")
  cursor.execute('SELECT * FROM claims;')
  result = cursor.fetchall()
  for row in result:
    print(row)
  cursor.close()
  conn.close()
  return result

# test_query()
fetch_data()
close_connection()
