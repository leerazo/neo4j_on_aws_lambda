import json
import sys
sys.path.append('lib') 
import neo4j

# Replace values below with your instance's credentials
db_creds = {
    'uri': 'neo4j+s://XXXXXXXX.databases.neo4j.io',
    'username': 'neo4j',
    'password': 'YOUR PASSWORD',
}


def connect_neo4j(db_creds):

    from neo4j import GraphDatabase
    #import neo4j
   
    uri = db_creds['uri']
    username = db_creds['username']
    password = db_creds['password']

    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    # Test database connectivity
    # connectivity = driver.verify_connectivity()

    return driver

def get_actors(tx, movie): # (1)
    import json

    result = tx.run("""
        MATCH (p:Person)-[:ACTED_IN]->(:Movie {title: $title})
        RETURN p
    """, title=movie)
 
    # Convert the results into a list of names
    actor_list = []
    for record in result:
        actor_list.append(record['p']['name'])

    if len(actor_list) == 0:
        # Movie not found in the database
        actor_json = None
    else:
        # Convert list to JSON and return
        actor_json = json.dumps(actor_list)
    return actor_json

def neo4jManager(movie_title, db_creds):
    # Connect to Neo4j instance and create driver
    driver = connect_neo4j(db_creds) 

    # Query function with movie title and return list of actors
    with driver.session() as session:
        actor_list = session.read_transaction(get_actors, movie=movie_title)
    session.close()
    return actor_list
    
def getTitle(event):
    target_key = 'movie_title'
    if target_key in event:
        movie_title = event['movie_title']
    elif ('queryStringParameters'in event) and target_key in event['queryStringParameters']:
        movie_title = event['queryStringParameters']['movie_title']
    else:
        movie_title = None
    return movie_title    
    
def lambda_handler(event, context):
    movie_title = getTitle(event)
    if movie_title:
        results = neo4jManager(movie_title, db_creds)
        if not results:
            return str("\"" + movie_title + "\"" + " not found in database.")
        else:
            return results
    else:
        return "No movie title provided"

