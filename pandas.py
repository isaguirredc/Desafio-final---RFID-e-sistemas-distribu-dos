import pandas as pd
import sqlite3

conn = sqlite3.connect("data.db")

logs = pd.read_sql_query("SELECT * FROM logs", conn)
users = pd.read_sql_query("SELECT * FROM funcionarios", conn)

conn.close()

if logs.empty or users.empty:
    print("Banco de dados vazio. Nenhum dado para processar.")
    exit()

df = logs.merge(users, left_on="user_id", right_on="id", suffixes=("_log", "_user"))

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])  # Remove timestamps inválidos
df["data"] = df["timestamp"].dt.date  # Criar coluna apenas com a data

entradas_por_dia = df[df["action"] == "ENTRADA"].groupby("data")["user_id"].count()

df = df.sort_values(["user_id", "timestamp"])

df["session"] = df.groupby("user_id")["action"].apply(lambda x: (x == "ENTRADA").cumsum())

entradas = df[df["action"] == "ENTRADA"][["user_id", "timestamp", "session"]].rename(columns={"timestamp": "entrada"})
saidas = df[df["action"] == "SAIDA"][["user_id", "timestamp", "session"]].rename(columns={"timestamp": "saida"})

tempo_na_sala = pd.merge(entradas, saidas, on=["user_id", "session"], how="left")

tempo_na_sala["tempo_na_sala_horas"] = (tempo_na_sala["saida"] - tempo_na_sala["entrada"]).dt.total_seconds() / 3600
tempo_na_sala["tempo_na_sala_horas"] = tempo_na_sala["tempo_na_sala_horas"].fillna(0)  # Define 0 para sessões sem saída

print("Acessos por dia:")
print(entradas_por_dia)

print("\nTempo de permanência na sala por usuário:")
print(tempo_na_sala[["user_id", "tempo_na_sala_horas"]])
