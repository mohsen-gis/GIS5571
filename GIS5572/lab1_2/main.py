import psycopg2
from flask import Flask, render_template, Response, request, redirect, url_for

app = Flask(__name__)

html = '''
<html>
<center>
<body>

<h1>Welcome!</h1>
<h3>Fetch Data From Our Database in GeoJSON format</h3>

<h3>----****US States****----</h3>
<br>
<p> Retrieve all states at once -->  <a href="https://gis5572-339101.uc.r.appspot.com/us_states" target="_blank" rel="noopener noreferrer">US States API call</a>.</p>

<br>   
<p> Retrieve states by region (NOT case sensitive) -->  <a href="https://gis5572-339101.uc.r.appspot.com/region/midwest" target="_blank" rel="noopener noreferrer">Midwest States API call</a>.</p>

<br>   
<p> Retrieve a single state by name (NOT case sensitive) -->  <a href="https://gis5572-339101.uc.r.appspot.com/state/minnesota" target="_blank" rel="noopener noreferrer">Minnesota State API call</a>.</p>

<br>   
<p> Retrieve a single state by abbreviation (NOT case sensitive) -->  <a href="https://gis5572-339101.uc.r.appspot.com/abbr/mn" target="_blank" rel="noopener noreferrer">MN API call</a>.</p>

<br> 
<br> 
<h3>----****/geojson_polygon Sample Assignment****----</h3>

<br>   
<p> Retrieve polygon by ID -->  <a href="https://gis5572-339101.uc.r.appspot.com/geojson_polygon" target="_blank" rel="noopener noreferrer">/geojson_polygon API call</a>.</p>
<p> This end point is created just for illustration and mee the assignment in Lab 1.2 </p>

<br>

<h3>----****About Us****----</h3>

<h4> This service is developed by <a href="https://mohsenahmadkhani.com" target="_blank" rel="noopener noreferrer">Mohsen Ahmadkhani</a></h4>

</body>
</center>
</html>
                '''

@app.route("/")
def index():
    return html


@app.route('/geojson_polygon')
def geojson_polygon():
                            
    q = f'''
    SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(feature)
    )
    FROM (
        SELECT jsonb_build_object(
        'type',       'Feature',
        'id',         id,
        'geometry',   ST_AsGeoJSON(geom)::jsonb,
                'properties', to_jsonb(inputs) - 'id' - 'geom'
    ) AS feature
            FROM (
            SELECT * FROM lab12poly 
                    ) inputs
                ) features;
    '''
    conn = psycopg2.connect("dbname='lab0' user='postgres' host='' password=''")
    cursor = conn.cursor()
    cursor.execute(q)
    data = cursor.fetchall()                                                                                                                     
    return data[0][0]

@app.route('/state/<sname>')
def state(sname):
    q = f'''
    SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(feature)
                    )
        FROM (
            SELECT jsonb_build_object(
            'type',       'Feature',
                'id',         geoid,
            'geometry',   ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb(inputs) - 'geoid' - 'geom')
    AS feature
    FROM (
    SELECT * FROM states WHERE lower(name) = '{sname.lower()}'
                            ) inputs
                        )features;
                            '''

    conn = psycopg2.connect("dbname='lab0' user='postgres' host='' password=''")
    cursor = conn.cursor()
    cursor.execute(q)
    data = cursor.fetchall()
                                                                                                                                                                                                                                                                         
    return data[0][0]


@app.route('/region/<rname>')
def region(rname):
    q = f'''
    SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(feature)
                    )
        FROM (
            SELECT jsonb_build_object(
            'type',       'Feature',
                'id',         geoid,
            'geometry',   ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb(inputs) - 'geoid' - 'geom')
    AS feature
    FROM (
    SELECT * FROM states WHERE lower(region) = '{rname.lower()}'
                            ) inputs
                        )features;
                            '''
    
    
    conn = psycopg2.connect("dbname='lab0' user='postgres' host='' password=''")
    cursor = conn.cursor()
    cursor.execute(q)
    data = cursor.fetchall()
                                                                                                                                                                                                                                                                         
    return data[0][0]


@app.route('/abbr/<stusps>')
def abbr(stusps):
    q = f'''
    SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(feature)
                    )
        FROM (
            SELECT jsonb_build_object(
            'type',       'Feature',
                'id',         geoid,
            'geometry',   ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb(inputs) - 'geoid' - 'geom')
    AS feature
    FROM (
    SELECT * FROM states WHERE lower(stusps) = '{stusps.lower()}'
                            ) inputs
                        )features;
                            '''

    conn = psycopg2.connect("dbname='lab0' user='postgres' host='' password=''")
    cursor = conn.cursor()
    cursor.execute(q)
    data = cursor.fetchall()
                                                                                                                                                                                                                                                                         
    return data[0][0]

@app.route('/us_states')
def us_states():
    q = f'''
    SELECT jsonb_build_object(
    'type',     'FeatureCollection',
    'features', jsonb_agg(feature)
                    )
        FROM (
            SELECT jsonb_build_object(
            'type',       'Feature',
                'id',         geoid,
            'geometry',   ST_AsGeoJSON(geom)::jsonb,
    'properties', to_jsonb(inputs) - 'geoid' - 'geom')
    AS feature
    FROM (
    SELECT * FROM states
                            ) inputs
                        )features;
                            '''

    conn = psycopg2.connect("dbname='lab0' user='postgres' host='' password=''")
    cursor = conn.cursor()
    cursor.execute(q)
    data = cursor.fetchall()
                                                                                                                                                                                                                                                                         
    return data[0][0]


if __name__ == "__main__":
    app.run()

    
    
    

