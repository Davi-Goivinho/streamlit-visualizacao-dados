import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler
from kmodes.kprototypes import KPrototypes
import time

response = requests.get("https://labdados.com/produtos")
df = pd.DataFrame(response.json())
df = df.dropna(subset=['Preço', 'Frete', 'Quantidade de parcelas', 'Avaliação da compra', 'Categoria do Produto', 'Tipo de pagamento'])

X_num = StandardScaler().fit_transform(df[['Preço', 'Frete', 'Quantidade de parcelas', 'Avaliação da compra']])
df_modelo = pd.DataFrame(X_num)
df_modelo['Categoria'] = df['Categoria do Produto'].values
df_modelo['Pagamento'] = df['Tipo de pagamento'].values

start = time.time()
costs = []
for k in range(2, 8):
    kproto = KPrototypes(n_clusters=k, init='Cao', n_init=1, n_jobs=-1)
    kproto.fit_predict(df_modelo.values, categorical=[4, 5])
    costs.append(kproto.cost_)
    print(f"k={k}, cost={kproto.cost_}, time={time.time() - start:.2f}s")
