import streamlit as st
import altair as alt
import os
from sqlalchemy import create_engine, VARCHAR, Float, Date, text
import pandas as pd
from datetime import datetime
import datetime as dti

st.set_page_config(
    page_title='Spy App',
    page_icon='🔎',
    layout='wide'
)

@st.cache_data
# Query data
def load_data():
    # Replace 'your_username', 'your_password', and 'your_database' with your actual credentials
    username = 'lucca_brandao'
    password = st.secrets['db_password']
    database = 'spy_dpdh'
    host = 'dpg-coq36rkf7o1s73ea52eg-a.ohio-postgres.render.com'

    # Create a connection string
    connection_string = f'postgresql://{username}:{password}@{host}/{database}'

    # Create the engine
    engine = create_engine(connection_string)

    # Test the connection
    try:
        connection = engine.connect()
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed! Error: {e}")

    # Close the connection
    engine.dispose()

    query = text('select * from test')
    df_ = pd.read_sql(query, con=connection)
    return df_

df = load_data()

####### Creating app

# Sidebar com os filtros
st.sidebar.subheader("Filtre aqui :sunglasses:")

start_date = st.sidebar.date_input(label="Data Inicial", value=dti.date(2024,1,1))
end_date = st.sidebar.date_input("Data Final")

selected_products = st.sidebar.multiselect("Selecione o Produto", df['product'].unique())
select_all_products = st.sidebar.checkbox("Selecione todos os produtos")
if select_all_products:
    selected_products =  df['product'].unique().tolist()


selected_stores = st.sidebar.multiselect("Selecione a Loja", df['store_name'].unique())
select_all_stores = st.sidebar.checkbox("Selecione todas as lojas")
if select_all_stores:
    selected_stores =  df['store_name'].unique().tolist()


# Converte as datas de string para datetime
df['created_at'] = pd.to_datetime(df['created_at'])

# Aplica os filtros
filtered_df = df.copy()
if start_date and end_date:
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())
    filtered_df = filtered_df[(filtered_df['created_at'] >= start_date) & (filtered_df['created_at'] <= end_date)]
if selected_products:
    filtered_df = filtered_df[filtered_df['product'].isin(selected_products)]
if selected_stores:
    filtered_df = filtered_df[filtered_df['store_name'].isin(selected_stores)]

# Calcula estatísticas
mean_price = filtered_df['price'].mean()
median_price = filtered_df['price'].median()
price_percentile_75 = filtered_df['price'].quantile(0.75)
price_percentile_25 = filtered_df['price'].quantile(0.25)
std_dev_price = filtered_df['price'].std()  # Desvio padrão

st.markdown('# Spy App 🔎')
st.write('Descubra o preço dos concorrentes em segundos! 💰💸')
st.write('')
# Mostra os cards com as estatísticas
st.markdown("## Análise de Preço")

# Cria uma grade de colunas para exibir os cards lado a lado
col1, col2, col3, col4, col5 = st.columns(5)

# Exibe os cards dentro das colunas
with col1:
    st.metric(label="Preço Médio", value=f"R$ {mean_price:.2f}")
with col2:
    st.metric(label="Preço no Percentil 25", value=f"R$ {price_percentile_25:.2f}")
with col3:
    st.metric(label="Preço Mediana", value=f"R$ {median_price:.2f}")
with col4:
    st.metric(label="Preço no Percentil 75", value=f"R$ {price_percentile_75:.2f}")
with col5:
    st.metric(label="Desvio Padrão", value=f"R$ {std_dev_price:.2f}")

################################################
# Sidebar com as opções de visualização
visualization_option = st.radio("Tipo de visão gráfico de linhas:", ["Diária", "Semanal"])

# Verifica a opção selecionada
if visualization_option == "Diária":
    col1, col2 = st.columns(2)
    with col1:
        # Gráfico de linhas por produto
        line_chart_products = alt.Chart(filtered_df).mark_line().encode(
            x=alt.X('created_at:T', axis=alt.Axis(title='Data')),
            y=alt.Y('mean(price):Q', axis=alt.Axis(title='Preço Médio')),
            color='product:N',
            tooltip=['created_at', 'product', alt.Tooltip('mean(price)', format='.2f', title='Preço Médio')]
        ).properties(
            width=600,
            height=300
        )
        st.markdown("#### Preço médio de Produto por dia")
        st.altair_chart(line_chart_products)

    with col2:
        # Gráfico de linhas por loja
        line_chart_stores = alt.Chart(filtered_df).mark_line().encode(
            x=alt.X('created_at:T', axis=alt.Axis(title='Data')),
            y=alt.Y('mean(price):Q', axis=alt.Axis(title='Preço Médio')),
            color='store_name:N',
            tooltip=['created_at', 'store_name', alt.Tooltip('mean(price)', format='.2f', title='Preço Médio')]
        ).properties(
            width=600,
            height=300
        )
        st.markdown("#### Preço médio de Loja por dia")
        st.altair_chart(line_chart_stores)

else:
    col1, col2 = st.columns(2)
    with col1:
        # Calcula a semana a partir da data
        filtered_df['week'] = filtered_df['created_at'] - pd.to_timedelta(filtered_df['created_at'].dt.dayofweek, unit='D')

        # Gráfico de linhas por produto (agrupado por semana)
        line_chart_products_weekly = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X('week:T', axis=alt.Axis(title='Semana')),
            y=alt.Y('mean(price):Q', axis=alt.Axis(title='Preço Médio')),
            color='product:N',
            tooltip=['week', 'product', alt.Tooltip('mean(price)', format='.2f', title='Preço Médio')]
        ).properties(
            width=600,
            height=300
        )
        st.markdown("#### Preço médio de Produto por semana")
        st.altair_chart(line_chart_products_weekly)
    with col2:
        # Gráfico de linhas por loja (agrupado por semana)
        line_chart_stores_weekly = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X('week:T', axis=alt.Axis(title='Semana')),
            y=alt.Y('mean(price):Q', axis=alt.Axis(title='Preço Médio')),
            color='store_name:N',
            tooltip=['week', 'store_name', alt.Tooltip('mean(price)', format='.2f', title='Preço Médio')]
        ).properties(
            width=600,
            height=300
        )
        st.markdown("#### Preço médio de Loja por semana")
        st.altair_chart(line_chart_stores_weekly)

# Adiciona os histogramas lado a lado com os percentis
if not filtered_df.empty:
    # Calcula os percentis
    percentiles_product = filtered_df['price'].quantile([0.25, 0.5, 0.75]).reset_index()

    # Histograma por produto
    hist_product = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X('price:Q', bin=alt.Bin(maxbins=20), axis=alt.Axis(title='Preço')),
        y=alt.Y('count():Q', axis=alt.Axis(title='Contagem')),
        # color='product:N'
    ).properties(
        width=450,
        height=300
    )

    # Adiciona as linhas verticais para os percentis
    lines_product = alt.Chart(percentiles_product).mark_rule(strokeDash=[3,3]).encode(
        x='price:Q',
        size=alt.value(2),
        color=alt.value('red')
    ).transform_calculate(
        value="datum.price"
    )

    # Adiciona as etiquetas estáticas para os percentis
    text_product = alt.Chart(percentiles_product).mark_text(align='left', baseline='middle', dx=5).encode(
        x='price:Q',
        y=alt.Y('value:Q', axis=alt.Axis(title='Preço')),
        text=alt.Text('value:Q', format=".2f")
    )

    hist_chart = hist_product + lines_product + text_product

    # Calcula o preço médio por produto
    mean_price_by_product = filtered_df.groupby('product')['price'].mean().reset_index()
    mean_price_by_product.columns = ['Produto', 'Preço Médio']

    # Ordena o DataFrame pelo preço médio de forma decrescente
    mean_price_by_product = mean_price_by_product.sort_values(by='Preço Médio', ascending=False)

    # Cria o gráfico de barras vertical usando Altair
    bar_chart_product = alt.Chart(mean_price_by_product).mark_bar().encode(
        y=alt.Y('Produto:N',sort='-x'),
        x=alt.X('Preço Médio:Q', axis=alt.Axis(title='Preço Médio')),
        tooltip=['Produto', 'Preço Médio']
    ).properties(
        width=450,
        height=300
    )

    # Calcula o preço médio por loja
    mean_price_by_store = filtered_df.groupby('store_name')['price'].mean().reset_index()
    mean_price_by_store.columns = ['Loja', 'Preço Médio']

    # Ordena o DataFrame pelo preço médio de forma decrescente
    mean_price_by_store = mean_price_by_store.sort_values(by='Preço Médio', ascending=False)

    # Cria o gráfico de barras vertical usando Altair
    bar_chart_store = alt.Chart(mean_price_by_store).mark_bar().encode(
        y=alt.Y('Loja:N', sort='-x'),
        x=alt.X('Preço Médio:Q', axis=alt.Axis(title='Preço Médio')),
        tooltip=['Loja', 'Preço Médio']
    ).properties(
        width=450,
        height=300
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("##### Histograma de preços")
        st.altair_chart(hist_chart)
    with col2:
        st.markdown('##### Ranking de preço médio por Produto')
        st.altair_chart(bar_chart_product)
    with col3:
        st.markdown('##### Ranking de preço médio por Loja')
        st.altair_chart(bar_chart_store)

# Mostra tabelas de dados
## Criando dataframe por dia
daily_df = (
    filtered_df[['created_at', 'product', 'store_name', 'price', 'total_discount', 'percentage_discount']]
    .rename(
        columns={
        'created_at': 'Dia',
        'product': 'Produto',
        'store_name': 'Loja',
        'price': 'Preço (R$)',
        'total_discount': 'Desconto (R$)',
        'percentage_discount': 'Desconto (%)'
        }
    )
)
daily_df['Desconto (%)'] = daily_df['Desconto (%)']*100
daily_df['Dia'] = daily_df['Dia'].dt.strftime('%Y-%m-%d')

# Criando dataframe semanal
filtered_df['created_at_week'] = filtered_df['created_at'].dt.strftime('%Y-%m-%d')
weekly_df = (
    filtered_df
    .groupby(by=['created_at_week', 'product', 'store_name'])
    .agg(
        {
            'price': 'mean',
            'total_discount': 'mean',
            'percentage_discount': 'mean'
        }
    )
    .reset_index()
    .rename(
        columns={
        'created_at_week': 'Semana',
        'product': 'Produto',
        'store_name': 'Loja',
        'price': 'Preço Médio (R$)',
        'total_discount': 'Desconto Médio (R$)',
        'percentage_discount': 'Desconto Médio (%)'
        }
    )
) 
weekly_df['Desconto Médio(%)'] = weekly_df['Desconto Médio (%)']*100

col1, col2 = st.columns(2)
with col1:
    st.markdown("##### Tabela com dados por dia")
    st.dataframe(daily_df)
with col2:
    st.markdown("##### Tabela com dados por semana")
    st.dataframe(weekly_df)