import spotipy
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta

from config import CLIENT_ID, CLIENT_SECRET, POSTGRES_USER, POSTRGRES_PASSWORD

def create_table_postgres():
    """
    SE CREA LA TABLA EN LA BASE DE DATOS DEL CONTENEDOR
    """

    try:
        conn = psycopg2.connect(database = "postgres", user = POSTGRES_USER, password = POSTRGRES_PASSWORD, host = "localhost", port = "5432")
    except:
        raise Exception("NO ME DEJA CONECTARME A LA BASE DE DATOS") 

    cur = conn.cursor()

    try:
        cur.execute("CREATE TABLE IF NOT EXISTS spotify_records( played_at TIMESTAMP PRIMARY KEY, artist TEXT NOT NULL, track TEXT NOT NULL);")
    except:
        raise Exception("NO PUDE CREAR LA TABLA EN LA BASE DE DATOS")

    conn.commit() # <--- makes sure the change is shown in the database
    conn.close()
    cur.close()

def spotipy_conn():

    scope = "user-read-recently-played"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID, 
        client_secret=CLIENT_SECRET,
        redirect_uri="https://example.com/callback/",
        scope=scope)
    )
    return sp

def postgres_upsert(table, conn, keys, data_iter):
    from sqlalchemy.dialects.postgresql import insert

    data = [dict(zip(keys, row)) for row in data_iter]

    insert_statement = insert(table.table).values(data)
    upsert_statement = insert_statement.on_conflict_do_update(
        constraint=f"{table.table.name}_pkey",
        set_={c.key: c for c in insert_statement.excluded},
    )
    conn.execute(upsert_statement)

def extract(date, sp, limit=50):
    """
    OBTENEMOS LAS CANCIONES REPRODUCIDAS RECIENTEMENTE UTILIZANDO LA LIBRERIA DE SPOTIPY
    QUE NOS CONECTA FACILMENTE A LA API WEB DE SPOTIFY.
    """
    ds = int(date.timestamp()) * 1000
    return sp.current_user_recently_played(limit=limit, after=ds)

def transform(raw_data, date):
    """
    MAS QUE TRANSFORMAR, VALIDA LA INFORMACION Y LA ORGANIZA EN LA ESTRUCTURA QUE SE NECESITA
    PARA LLENAR LA BASE DE DATOS
    """
    data = []

    for item in raw_data['items']:
        data.append({
            "played_at":  item['played_at'],
            "artist":  item['track']['artists'][0]['name'],
            "track":  item['track']['name']
        })
    
    df = pd.DataFrame(data)

    # Filtramos el dataframe para tener solo aquellas que la fecha concuerde con ayer
    #clean_df = df[pd.to_datetime(df["played_at"]).dt.date == date.date()]
    clean_df = df

    # Validamos que no venga algun valor nulo o vacio
    if df.isnull().values.any():
        raise Exception("Vino nulo o vacio algun valor de la API")

    return clean_df

def load(clean_df):

    conn_string = 'postgresql://postgres:123456@localhost:5432/postgres'
    db = create_engine(conn_string)
    clean_df.to_sql('spotify_records', db, index=False, if_exists='append', method=postgres_upsert)

if __name__ == "__main__":

    create_table_postgres()

    # date será la fecha de ayer
    date = datetime.today() - timedelta(days=1)
    
    sp = spotipy_conn()

    raw_data = extract(date, sp)
    
    clean_df = transform(raw_data, date)

    load(clean_df)