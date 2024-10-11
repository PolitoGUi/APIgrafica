from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

# Conectar ao banco de dados PostgreSQL
def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname="tcc_mlul",
            user="guilherme",
            password="UHnP3RoMsq3qcWMJVPHQ7LtFq4zbD9yQ",
            host="dpg-crvgsa08fa8c739a75l0-a.oregon-postgres.render.com",
            port="5432",
            sslmode="require" 
        )
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados")

# Modelo de dados usando Pydantic
class SensorData(BaseModel):
    rfid: str
    peso: float
    preco: float
    nome: str

# Função para verificar se o grupo está completo
def check_group_complete(cursor):
    # Por exemplo, se há um número fixo de 5 itens no grupo
    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE grupo_id = (SELECT MAX(grupo_id) FROM pedidos)")
    count = cursor.fetchone()[0]
    return count >= 5  # Definir condição para grupo completo

@app.post("/sensor_data/")
def insert_sensor_data(sensor_data: SensorData):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Adicionar dados à tabela de pedidos
        cursor.execute("""
            INSERT INTO pedidos (rfid, peso, preco, nome, grupo_id)
            VALUES (%(rfid)s, %(peso)s, %(preco)s, %(nome)s, (SELECT MAX(grupo_id) FROM pedidos))
        """, sensor_data.dict())
        connection.commit()

        # Verificar se o grupo está completo
        if check_group_complete(cursor):
            # Mover os pedidos do grupo para a tabela pedidos_feitos
            cursor.execute("""
                INSERT INTO pedidos_feitos (rfid, peso, preco, nome, grupo_id)
                SELECT rfid, peso, preco, nome, grupo_id FROM pedidos WHERE grupo_id = (SELECT MAX(grupo_id) FROM pedidos)
            """)
            cursor.execute("DELETE FROM pedidos WHERE grupo_id = (SELECT MAX(grupo_id) FROM pedidos)")
            connection.commit()
            return {"message": "Grupo completo e movido para pedidos_feitos"}

        return {"message": "Pedido inserido"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Erro ao inserir dados")
    finally:
        cursor.close()
        connection.close()
