import streamlit as st
import pandas as pd

url = 'https://drive.google.com/uc?id=1N3Cb8X3QXWbzT7O_xXA05pcjFs4lx5Ci'

# Carregar o arquivo CSV em um DataFrame
df = pd.read_csv(url)

# Pré-processamento adicional
df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
df = df.dropna(subset=['genres', 'vote_average', 'release_year', 'overview', 'original_language'])

# Função para extrair gêneros e idiomas únicos
def extrair_generos(df):
    generos = set()
    for lista_generos in df['genres']:
        for genero in lista_generos.split(','):
            generos.add(genero.strip())
    return sorted(generos)

def extrair_idiomas(df):
    return sorted(df['original_language'].unique())

# Obter listas de gêneros e idiomas únicos
generos_unicos = extrair_generos(df)
idiomas_unicos = extrair_idiomas(df)

# Função para filtrar e sugerir filmes
def sugerir_filmes(generos, nota_minima, ano_minimo, idiomas, n_filmes=5):
    # Filtrar por nota mínima, ano mínimo e idiomas
    filmes_filtrados = df[
        (df['vote_average'] >= nota_minima) &
        (df['release_year'] >= ano_minimo) &
        (df['original_language'].isin(idiomas))
    ]

    # Filtrar por gêneros
    if generos:
        filmes_filtrados = filmes_filtrados[filmes_filtrados['genres'].apply(lambda x: all(g in x for g in generos))]

    if filmes_filtrados.empty:
        return pd.DataFrame(columns=['title', 'vote_average', 'release_date', 'genres', 'overview'])

    # Ordenar por nota e ano
    filmes_filtrados = filmes_filtrados.sort_values(by=['vote_average', 'release_year'], ascending=[False, False])

    return filmes_filtrados[['title', 'vote_average', 'release_date', 'genres', 'overview']].head(n_filmes)

# Interface do Streamlit
st.title('Recomendador de Filmes')

generos_selecionados1 = st.multiselect("Escolha os primeiros gêneros que você gostaria de ver:", generos_unicos)
idiomas_selecionados = st.multiselect("Escolha os idiomas dos filmes:", idiomas_unicos)
nota_minima_preferida = st.slider("Qual a nota mínima do IMDb você gostaria (vote_average)?", 0.0, 10.0, 5.0)
ano_minimo_preferido = st.slider("Qual o ano mínimo que você gostaria de filmes sugeridos?", 1900, 2024, 2000)

if st.button('Sugerir Filmes'):
    # Combine as duas listas de gêneros
    generos_preferidos = list(set(generos_selecionados1))
    sugestoes = sugerir_filmes(generos=generos_preferidos, nota_minima=nota_minima_preferida, ano_minimo=ano_minimo_preferido, idiomas=idiomas_selecionados)
    
    if sugestoes.empty:
        st.write("Não há filmes que correspondem aos seus critérios.")
    else:
        st.write("Filmes sugeridos:")
        for index, row in sugestoes.iterrows():
            st.write(f"**{row['title']}**")
            st.write(f"Nota: {row['vote_average']}")
            st.write(f"Data de lançamento: {row['release_date']}")
            st.write(f"Gêneros: {row['genres']}")
            st.write(f"Descrição: {row['overview']}")
            st.write("---")
