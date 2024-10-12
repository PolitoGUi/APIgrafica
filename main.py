from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import traceback

app = FastAPI()

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

class MovePedido(BaseModel):
    rfid: str

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
        print(traceback.format_exc())  # Exibir o traceback do erro
        raise HTTPException(status_code=500, detail="Erro ao inserir dados no banco de dados")
    finally:
        cursor.close()
        connection.close()

@app.post("/mover_pedidos/")
def mover_pedidos(mover_pedido: MovePedido):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Selecionar o nome do produto pelo RFID
        cursor.execute("SELECT nome_produto FROM produtos WHERE rfid = %s", (mover_pedido.rfid,))
        produto = cursor.fetchone()

        if not produto:
            return {"message": "Nenhum produto encontrado para o RFID fornecido."}

        nome_produto = produto[0]

        # Selecionar os pedidos correspondentes ao nome do produto
        cursor.execute("""
            SELECT id, quantidade, preco, hora
            FROM pedidos
            WHERE nome_produto = %s
        """, (nome_produto,))
        pedidos = cursor.fetchall()

        if not pedidos:
            return {"message": "Nenhum pedido encontrado para o produto correspondente."}

        for pedido in pedidos:
            # Inserir o pedido na tabela pedidos_feitos
            cursor.execute("""
                INSERT INTO pedidos_feitos (nome, nome_produto, preco, quantidade, hora)
                VALUES (%s, %s, %s, %s, %s)
            """, (pedido[1], nome_produto, pedido[2], 1, pedido[3]))  # Ajuste na quantidade

            # Excluir o pedido da tabela pedidos
            cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido[0],))
        
        connection.commit()
        return {"message": "Pedidos movidos com sucesso"}
    except Exception as e:
        connection.rollback()
        print(f"Erro ao mover pedidos: {e}")
        print(traceback.format_exc())  # Exibir o traceback do erro
        raise HTTPException(status_code=500, detail="Erro ao mover pedidos no banco de dados")
    finally:
        cursor.close()
        connection.close()

@app.post("/mover_pedidos/")
def mover_pedidos(mover_pedido: MovePedido):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Selecionar o nome do produto pelo RFID
        cursor.execute("SELECT nome_produto FROM produtos WHERE rfid = %s", (mover_pedido.rfid,))
        produto = cursor.fetchone()

        # Verificar se o produto foi encontrado
        if not produto:
            return {"message": "Nenhum produto encontrado para o RFID fornecido."}

        nome_produto = produto[0]

        # Selecionar os pedidos correspondentes ao nome do produto
        cursor.execute("""
            SELECT id, quantidade, preco, hora
            FROM pedidos
            WHERE nome_produto = %s
        """, (nome_produto,))
        pedidos = cursor.fetchall()

        # Verificar se pedidos foram encontrados
        if not pedidos:
            return {"message": "Nenhum pedido encontrado para o produto correspondente."}

        for pedido in pedidos:
            # Inserir o pedido na tabela pedidos_feitos
            cursor.execute("""
                INSERT INTO pedidos_feitos (nome, nome_produto, preco, quantidade, hora)
                VALUES (%s, %s, %s, %s, %s)
            """, (pedido[1], nome_produto, pedido[2], 1, pedido[3]))  # Ajuste na quantidade

            # Excluir o pedido da tabela pedidos
            cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido[0],))
        
        connection.commit()
        return {"message": "Pedidos movidos com sucesso"}
    except Exception as e:
        connection.rollback()
        print(f"Erro ao mover pedidos: {e}")
        print(traceback.format_exc())  # Exibir o traceback do erro
        raise HTTPException(status_code=500, detail="Erro ao mover pedidos no banco de dados")
    finally:
        cursor.close()
        connection.close()
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
