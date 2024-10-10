from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

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
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {e}")

# Modelo de dados
class ProdutoRFID(BaseModel):
    rfid: str

# Adicionar item à tabela 'pedidos' com base no RFID
@app.post("/adicionar_pedido/")
def adicionar_pedido(produto_rfid: ProdutoRFID):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Verificar se o RFID corresponde a um produto
        cursor.execute("""
            SELECT nome_produto, preco FROM produtos WHERE rfid = %s
        """, (produto_rfid.rfid,))
        produto = cursor.fetchone()

        if not produto:
            raise HTTPException(status_code=404, detail="Produto não encontrado para o RFID fornecido")

        nome_produto, preco = produto

        # Inserir na tabela de pedidos
        cursor.execute("""
            INSERT INTO pedidos (nome_produto, preco, quantidade, hora)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """, (nome_produto, preco, 1))  # Quantidade pode ser ajustada conforme necessário
        connection.commit()

        return {"message": f"Pedido de {nome_produto} adicionado com sucesso"}
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar pedido: {e}")
    finally:
        cursor.close()
        connection.close()

# Verificar um pedido com base no RFID
@app.get("/verificar_pedido/{rfid}")
def verificar_pedido(rfid: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Verificar pedido com base no RFID
        cursor.execute("""
            SELECT p.id, p.nome_produto, p.preco, p.quantidade, p.hora 
            FROM pedidos p
            JOIN produtos pr ON pr.nome_produto = p.nome_produto
            WHERE pr.rfid = %s
        """, (rfid,))
        pedido = cursor.fetchone()

        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido não encontrado para o RFID fornecido")

        return {
            "id": pedido[0],
            "nome_produto": pedido[1],
            "preco": pedido[2],
            "quantidade": pedido[3],
            "hora": pedido[4]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar pedido: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
