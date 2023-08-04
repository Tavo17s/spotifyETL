# PROYECTO ETL (SPOTIFY)

Proyecto creado con el proposito de utilizar Docker para guardar en una base de datos (postgres) la información sobre las reproduciones del dia anterior del usuario en Spotify.

### Librerias utilizadas
<ul>
  <li>spotipy</li>
  <li>psycopg2</li>
  <li>pandas</li>
  <li>sqlalchemy</li>
  <li>datetime</li>
</ul>

Las cuales te dejo en el requirements.txt, asegurate de correr el siguiente comando: pip install --no-cache-dir --upgrade -r requirements.txt

### Tecnologias utilizadas
<ul>
  <li>Python</li>
  <li>Docker</li>
  <li>PostgreSQL</li>
  <li>PgAdmin</li>
</ul>

### Video con el paso a paso (me dio flojera escribirlo y el video es mejor)

https://youtu.be/TrE8qd41QhU

### Comentarios extras

+ Al crear la app en spotify, el campo de redirect URI debe ser el mismo al que aparece en el metodo spotipy_conn, puedes colocar el que quieras o dejar el mismo

+ Las credenciales de PgAdmin como las de Postgres las encuentras en el docker-compose, cambialas a tu gusto

+ El token se guarda en el .cache, pero expira cada hora (asi lo maneja spotify), por lo que si no ha expirado puedes correr el algoritmo sin problemas, pero si expira, te toca copiar el url de nuevo y pegarlo en la consola, como hago la primera vez.