import os
import atexit
from dotenv import load_dotenv
from flask import jsonify, Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from psycopg2 import OperationalError, pool
from psycopg2.pool import PoolError

load_dotenv()
connection_pool = pool.SimpleConnectionPool(1, 10, os.getenv('DATABASE_URL'))

def close_connection():
    try:
        connection_pool.closeall()
    except PoolError as e:
        print(f"Error closing connection pool: {e}")

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["JWT_SECRET_KEY"] = os.getenv('SECRETKEY')
    jwt = JWTManager(app)
    atexit.register(close_connection)

    @app.route('/login', methods=['POST'])
    def login():
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        print(username,password)

        if username == os.getenv('USER') and password == os.getenv('PASSWORD'):
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    #Default route
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({"Message":"Welcome to Soluciones-IT API"})
    
    #Gets clients information from the database, returns a dictionary of database information
    @app.route('/clients', methods=['GET'])
    @jwt_required()
    def get_clients():
        try:
            get_jwt_identity()
            conn = connection_pool.getconn()
            cur = conn.cursor()

            cur.execute("SELECT * FROM Clients;")
            data_clients = cur.fetchall()

            response = {"data":[]}

            for client in data_clients:
                response["data"].append({
                    "id":client[0],
                    "name":client[1],
                    "identification":client[2],
                    "phone":client[3],
                    "direction":client[4],
                    "description":client[5],
                    "iptv":client[6],
                    "amount":client[7],
                    "paid":client[8],
                    "gigabytes":client[9]
                    })
                
            return jsonify(response),200
        except OperationalError as db_error:
            print(f"DB Error: {db_error}")
            return jsonify({"Database error":db_error}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error":e}), 400
        finally:
            if cur:
                cur.close()
            if conn:
                connection_pool.putconn(conn)
    
    #Gets paids information from the database, returns a dictionary of database information
    @app.route('/paids', methods=['GET'])
    @jwt_required()
    def get_paids():
        try:
            get_jwt_identity()
            conn = connection_pool.getconn()
            cur = conn.cursor()

            cur.execute("SELECT * FROM paids;")
            data_clients = cur.fetchall()

            response = {"data":[]}

            for client in data_clients:
                response["data"].append({
                    "id":client[0],
                    "name":client[1],
                    "identification":client[2],
                    "phone":client[3],
                    "amount":client[4],
                    "date_payment":client[5],
                    "type":client[6]
                    })
                
            return jsonify(response),200
        except OperationalError as db_error:
            print(f"DB Error: {db_error}")
            return jsonify({"Database error":db_error}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error":e}), 400
        finally:
            if cur:
                cur.close()
            if conn:
                connection_pool.putconn(conn)
        
    #Updates client information from the database, returns message of error or confirmation
    @app.route('/update_client', methods=['POST'])
    @jwt_required()
    def update_client():
        try:
            get_jwt_identity()
            data_client = request.get_json()
            id = data_client.get("id")
            name = data_client.get("name")
            identification = data_client.get("identification")
            phone = data_client.get("phone")
            direction = data_client.get("direction")
            description = data_client.get("description")
            iptv = data_client.get("iptv")
            amount = data_client.get("amount")
            paid = data_client.get("paid")
            gigabytes = data_client.get("gigabytes")

            conn = connection_pool.getconn()
            cur = conn.cursor()

            cur.execute("SELECT update_client(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);", (id, name, identification, phone, direction, description, iptv, amount, paid, gigabytes))
            conn.commit()
            
            response = {"Message":"Client updated successfully"}

            return jsonify(response), 200
        except OperationalError as db_error:
            print(f"DB Error: {db_error}")
            return jsonify({"Database error":db_error}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error":e}), 400
        finally:
            if cur:
                cur.close()
            if conn:
                connection_pool.putconn(conn)
        
    #Inserts client from the database, returns message of error or confirmation
    @app.route('/insert_client', methods=['POST'])
    @jwt_required()
    def insert_client():
        try:
            get_jwt_identity()
            data_client = request.get_json()
            name = data_client.get("name")
            identification = data_client.get("identification")
            phone = data_client.get("phone")
            direction = data_client.get("direction")
            description = data_client.get("description")
            iptv = data_client.get("iptv")
            amount = data_client.get("amount")
            paid = data_client.get("paid")
            gigabytes = data_client.get("gigabytes")

            conn = connection_pool.getconn()
            cur = conn.cursor()

            cur.execute("SELECT insert_client(%s,%s,%s,%s,%s,%s,%s,%s,%s);", (name, identification, phone, direction, description, iptv, amount, paid, gigabytes))
            conn.commit()
            
            response = {"Message":"Client inserted successfully"}

            return jsonify(response), 200
        except OperationalError as db_error:
            print(f"DB Error: {db_error}")
            return jsonify({"Database error":db_error}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error":e}), 400
        finally:
            if cur:
                cur.close()
            if conn:
                connection_pool.putconn(conn)

    #Delete client from the database, returns message of error or confirmation
    @app.route('/delete_client', methods=['DELETE'])
    @jwt_required()
    def delete_client():
        try:
            get_jwt_identity()
            data_client = request.get_json()
            id = data_client.get("id")

            conn = connection_pool.getconn()
            cur = conn.cursor()

            cur.execute("SELECT delete_client(%s);", (id))
            conn.commit()
            
            response = {"Message":"Client deleted successfully"}

            return jsonify(response), 200
        except OperationalError as db_error:
            print(f"DB Error: {db_error}")
            return jsonify({"Database error":db_error}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error":e}), 400
        finally:
            if cur:
                cur.close()
            if conn:
                connection_pool.putconn(conn)
        
    #Inserts payment from the database, returns message of error or confirmation
    @app.route('/insert_payment', methods=['POST'])
    @jwt_required()
    def insert_payment():
        try:
            get_jwt_identity()
            data_payment = request.get_json()
            id_client = data_payment.get("id_client")
            date = data_payment.get("date")
            type = data_payment.get("type") #'Sinpe movil', 'Efectivo'



            conn = connection_pool.getconn()
            cur = conn.cursor()

            cur.execute("SELECT insert_payment(%s,%s,%s);", (id_client, date, type))
            conn.commit()
            

            response = {"Message":"Payment inserted successfully"}

            return jsonify(response), 200
        except OperationalError as db_error:
            print(f"DB Error: {db_error}")
            return jsonify({"Database error":db_error}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error":e}), 400
        finally:
            if cur:
                cur.close()
            if conn:
                connection_pool.putconn(conn)
        
    #Clean payments from the database, returns message of error or confirmation
    @app.route('/clean_payments', methods=['GET'])
    @jwt_required()
    def clean_payments():
        try:
            get_jwt_identity()

            conn = connection_pool.getconn()
            cur = conn.cursor()

            cur.execute("SELECT delete_all_payments();")
            conn.commit()

            response = {"Message":"Clean payments successfully"}

            return jsonify(response), 200
        except OperationalError as db_error:
            print(f"DB Error: {db_error}")
            return jsonify({"Database error":db_error}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error":e}), 400
        finally:
            if cur:
                cur.close()
            if conn:
                connection_pool.putconn(conn)
    
    @app.route('/reset_paids', methods=['GET'])
    @jwt_required()
    def reset_paids():
        try:
            get_jwt_identity()

            conn = connection_pool.getconn()
            cur = conn.cursor()

            # Actualiza el estado 'paid' del cliente
            cur.execute("UPDATE Clients SET paid = FALSE;")
            conn.commit()
            
            response = {"Message": "Paids status updated successfully"}

            return jsonify(response), 200
        except OperationalError as db_error:
            print(f"DB Error: {db_error}")
            return jsonify({"Database error": db_error}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error": str(e)}), 400
        finally:
            if cur:
                cur.close()
            if conn:
                connection_pool.putconn(conn)

        #Update paid status of a client, returns message of error or confirmation
    @app.route('/update_paid_status', methods=['POST'])
    @jwt_required()
    def update_paid_status():
        try:
            get_jwt_identity()
            data_client = request.get_json()
            id = data_client.get("id")
            paid = data_client.get("paid")

            conn = connection_pool.getconn()
            cur = conn.cursor()

            # Actualiza el estado 'paid' del cliente
            cur.execute("UPDATE Clients SET paid = %s WHERE id = %s;", (paid, id))
            conn.commit()
            
            response = {"Message": "Paid status updated successfully"}

            return jsonify(response), 200
        except OperationalError as db_error:
            print(f"DB Error: {db_error}")
            return jsonify({"Database error": db_error}), 500
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"Error": str(e)}), 400
        finally:
            if cur:
                cur.close()
            if conn:
                connection_pool.putconn(conn)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=7500, debug=True)