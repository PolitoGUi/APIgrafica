from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

# Diretório onde o gráfico será salvo
STATIC_DIR = 'static'
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# Conectar ao banco de dados PostgreSQL
def get_db_connection():
    try:
        connection = psycopg2.connect(
            dbname="tcc_mlul",
            user="guilherme",
            password="UHnP3RoMsq3qcWMJVPHQ7LtFq4zbD9yQ",
            host="dpg-crvgsa08fa8c739a75l0-a.oregon-postgres.render.com",
            port="5432"
        )
        print("Conectado ao banco de dados.")
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados")

# Modelo de dados usando Pydantic
class SensorData(BaseModel):
    esp_id: str
    rfid: str
    peso: float
    preco: float
    nome: str

@app.post("/sensor_data/")
def insert_sensor_data(sensor_data: SensorData):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO sensor_data (esp_id, rfid, peso, preco, nome)
            VALUES (%(esp_id)s, %(rfid)s, %(peso)s, %(preco)s, %(nome)s)
        """, sensor_data.dict())
        connection.commit()
        return {"message": "Dados inseridos com sucesso"}
    except Exception as e:
        connection.rollback()
        print(f"Erro ao inserir dados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao inserir dados no banco de dados")
    finally:
        cursor.close()
        connection.close()

@app.post("/mover_pedidos_em_ordem/")
def mover_pedidos_em_ordem():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Selecionar todos os pedidos em ordem de ID
        cursor.execute("SELECT * FROM pedidos ORDER BY id ASC")
        pedidos = cursor.fetchall()

        if not pedidos:
            return {"message": "Nenhum pedido a ser movido"}

        for pedido in pedidos:
            # Inserir o pedido na tabela pedidos_feitos
            cursor.execute("""
                INSERT INTO pedidos_feitos (nome, nome_produto, preco, quantidade, hora)
                VALUES (%s, %s, %s, %s, %s)
            """, (pedido[1], pedido[2], pedido[3], pedido[4], pedido[5]))
            
            # Excluir o pedido da tabela pedidos
            cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido[0],))
        
        connection.commit()
        return {"message": "Todos os pedidos foram movidos com sucesso"}
    except Exception as e:
        connection.rollback()
        print(f"Erro ao mover pedidos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao mover pedidos no banco de dados")
    finally:
        cursor.close()
        connection.close()

@app.get("/sensor_data/{sensor_id}")
def get_sensor_data(sensor_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM sensor_data WHERE id = %s", (sensor_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "esp_id": row[1],
                "rfid": row[2],
                "peso": row[3],
                "preco": row[4],
                "nome": row[5]
            }
        else:
            raise HTTPException(status_code=404, detail="Dados não encontrados")
    except Exception as e:
        print(f"Erro ao consultar dados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao consultar dados no banco de dados")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
