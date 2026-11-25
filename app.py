#Paso 1. La página.** Importa streamlit y pandas. Pon el nombre de la pestaña, la página a todo lo ancho, un título y una o dos frases con st.write: de qué son los datos y de qué fechas.

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pedidos a domicilio", page_icon="🛵", layout="wide")
st.title("¿Le compensa al bar La Consulta llevar pedidos a casa?")

st.write("Esta app enseña los pedidos a domicilio del bar La Consulta por Rayo, Mordisco y Teléfono, del 1 de septiembre al 15 de noviembre de 2026.")
st.write("Los datos salen de la base de datos del bar en TiDB Cloud, ya limpios en el cuaderno.")

#Paso 2. Los datos. Una función con @st.cache_data que lea pedidos_limpios.csv y la devuelva, y otra igual para platos.csv. Llama a las dos.

@st.cache_data
def cargar_pedidos():
    pedidos = pd.read_csv("pedidos_limpios.csv")
    return pedidos

@st.cache_data
def cargar_platos():
    platos = pd.read_csv("platos.csv")
    return platos

pedidos = cargar_pedidos()
platos = cargar_platos()
st.write("Tenemos", len(pedidos), "pedidos entregados.")

# Paso 3. Los filtros
# 3.1 En la barra de la izquierda (with st.sidebar:), al menos dos filtros:
#     un desplegable o unos botones para una columna de texto, con "Todos" al principio,
#     y una barra para una columna de números.
with st.sidebar:
    st.header("Filtros")

    plataformas = ["Todas"] + list(pedidos["plataforma"].value_counts().index)
    plataforma = st.selectbox("Plataforma", plataformas)

    barrios = ["Todos"] + list(pedidos["barrio"].value_counts().index)
    barrio = st.selectbox("Barrio", barrios)

    importe = st.slider("Importe del pedido (€)", 0, 100, (0, 100))

    # Paso 4. Filtrar
# 4.1 Empieza con filtrados = tu tabla, y después aplica un filtro por cada widget, como en los pisos.
filtrados = pedidos

if plataforma != "Todas":
    filtrados = filtrados[filtrados["plataforma"] == plataforma]

if barrio != "Todos":
    filtrados = filtrados[filtrados["barrio"] == barrio]

filtrados = filtrados[(filtrados["total"] >= importe[0]) & (filtrados["total"] <= importe[1])]

# Paso 5. Si no queda nada
# 5.1 Si filtrados está vacía, saca un aviso con st.warning y para el programa con st.stop().
if len(filtrados) == 0:
    st.warning("No hay ningún pedido con estos filtros. Prueba con otros.")
    st.stop()

# Paso 6. Las métricas
# 6.1 Tres métricas en columnas, con los números más importantes para tu pregunta.
col1, col2, col3 = st.columns(3)

col1.metric("Pedidos", len(filtrados))
col2.metric("Le queda al bar", f"{round(filtrados['neto'].sum())} €")
col3.metric("Minutos de media", round(filtrados["minutos"].mean(), 1),
            delta=round(filtrados["minutos"].mean() - pedidos["minutos"].mean(), 1),
            delta_color="inverse")

st.divider()
# Paso 7. Las pestañas
# 7.1 Al menos dos pestañas: una con la tabla filtrada y otra con dos gráficos.
# 7.2 Si tus datos tienen latitud y longitud, otra pestaña con el mapa.
tab1, tab2, tab3, tab4 = st.tabs(["Pedidos", "Gráficos", "Platos", "¿Cuánto tardará tu pedido?"])

with tab1:
    st.dataframe(filtrados)

with tab2:
    st.subheader("Cuántos pedidos hay cada semana")
    st.line_chart(filtrados.groupby("semana").size())

    st.subheader("Cuánto le deja al bar cada plataforma por pedido (€)")
    st.bar_chart(filtrados.groupby("plataforma")["neto"].mean())

    st.subheader("Cuántos minutos se tarda en llegar a cada barrio")
    st.bar_chart(filtrados.groupby("barrio")["minutos"].mean())

    st.subheader("A qué horas se pide")
    st.bar_chart(filtrados.groupby("hora").size())
    st.caption("Hay dos picos: a las 14 h y a las 21 h.")

with tab3:
    st.subheader("Los 10 platos que más se piden")
    st.bar_chart(platos.head(10).set_index("plato")["unidades"])

# Paso 8. Una pregunta para el usuario
# 8.1 Una última pestaña con una pregunta, como "¿Cuánto cobrarías por tu piso?" o "¿Te habrías salvado?":
#     el usuario elige algo y la app le contesta con lo que dicen los datos.
with tab4:
    st.subheader("¿Cuánto tardará tu pedido?")

    mi_barrio = st.selectbox("¿En qué barrio vives?", list(pedidos["barrio"].value_counts().index))
    lluvia = st.radio("¿Está lloviendo?", ["No", "Sí"])

    # Me quedo con los pedidos parecidos: del mismo barrio y con el mismo tiempo
    llueve = lluvia == "Sí"
    parecidos = pedidos[(pedidos["barrio"] == mi_barrio) & (pedidos["llueve"] == llueve)]

    # Si no hay ninguno, aviso. Si hay, digo cuántos son y cuánto tardaron
    if len(parecidos) == 0:
        st.warning("No hay pedidos parecidos para comparar.")
    else:
        minutos = round(parecidos["minutos"].mean())
        st.write("Hay", len(parecidos), "pedidos parecidos y tardaron de media", minutos, "minutos.")

        # Si tarda 35 minutos o menos, mensaje en verde. Si no, en rojo
        if minutos <= 35:
            st.success("Tu pedido llegará rápido.")
        else:
            st.error("Tu pedido puede tardar: mejor pedir con tiempo.")