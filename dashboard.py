import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os

# Dados originais (tempo em HH:MM:SS)
data = [
    ["Módulo 1", "Linux", "06:49:11", "03:10:00"],
    ["Módulo 1", "Scratch", "03:12:21", "03:12:00"],
    ["Módulo 1", "Introdução a Web", "12:28:23", "03:25:00"],
    ["Módulo 1", "No Code", "05:36:37", "02:51:00"],
    ["Módulo 1", "Python", "15:41:33", "03:00:00"],
    ["Módulo 2", "JavaScript", "09:32:53", "04:20:00"],
    ["Módulo 2", "POO", "09:03:40", "03:40:00"],
    ["Módulo 2", "Python II", "12:57:25", "04:00:00"],
    ["Módulo 2", "Banco de Dados", "07:15:00", "03:50:00"],
    ["Módulo 3", "Fundamentos de Interface", "07:11:01", "03:00:00"],
    ["Módulo 3", "React JS", "07:14:08", "03:00:00"],
    ["Módulo 3", "Web com mentalidade ágil", "07:08:56", "03:00:00"],
    ["Módulo 3", "Frameworks Front-End", "06:55:52", "03:00:00"],
    ["Módulo 3", "React Native", "06:20:19", "03:00:00"],
    ["Módulo 3", "Flutter", "04:21:00", "03:00:00"],
    # NOVAS MATÉRIAS ADICIONADAS AQUI NO MÓDULO 4 (TEMPOS COMO PLACEHOLDER)
    ["Módulo 4", "Desenvolvimento Android", "00:00:00", "00:00:00"],
    ["Módulo 4", "Desenvolvimento FullStack", "00:00:00", "00:00:00"],
    ["Módulo 4", "Fundamentos das APIs RESTful", "00:00:00", "00:00:00"],
    ["Módulo 4", "NoSQL", "00:00:00", "00:00:00"],
    ["Módulo 4", "Teste de Software para Android", "00:00:00", "00:00:00"],
    ["Módulo 4", "Teste de Software para Web", "00:00:00", "00:00:00"],
    ["Módulo 4", "Padrão de Projeto", "00:00:00", "00:00:00"], # NOVO CURSO
]

def time_to_seconds(t):
    h, m, s = map(int, t.split(':'))
    return h*3600 + m*60 + s

def seconds_to_time(s):
    h = s // 3600
    s %= 3600
    m = s // 60
    s %= 60
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

df = pd.DataFrame(data, columns=["Módulo", "Curso", "Antes", "Depois"])
df["Antes_seg"] = df["Antes"].apply(time_to_seconds)
df["Depois_seg"] = df["Depois"].apply(time_to_seconds)
df["Reducao_seg"] = df["Antes_seg"] - df["Depois_seg"]
# Previne divisão por zero se "Antes_seg" for 0
df["% Redução"] = (df["Reducao_seg"] / df["Antes_seg"] * 100).replace([float('inf'), -float('inf')], 0).round(1)
df["Antes_fmt"] = df["Antes"]
df["Depois_fmt"] = df["Depois"]
df["Reducao_fmt"] = df["Reducao_seg"].apply(seconds_to_time)

st.title("Dashboard de Redução de Carga Horária")

# --- Definição das Abas Principais ---
tab_geral, tab_detalhamento, tab_ementas, tab_exercicios = st.tabs(["Visão Geral por Módulo", "Detalhamento por Curso", "Ementas dos Cursos", "Exercícios"])

# =============================================================================
# Conteúdo da Aba "Visão Geral por Módulo" (Sem Alterações na lógica, apenas dados)
# =============================================================================
with tab_geral:
    st.subheader("Visão Geral do Tempo por Módulo")

    # Resumo por módulo
    resumo_modulo = df.groupby("Módulo").agg({
        "Antes_seg": "sum",
        "Depois_seg": "sum"
    }).reset_index()
    resumo_modulo["Reducao_seg"] = resumo_modulo["Antes_seg"] - resumo_modulo["Depois_seg"]
    resumo_modulo["% Redução"] = (resumo_modulo["Reducao_seg"] / resumo_modulo["Antes_seg"] * 100).replace([float('inf'), -float('inf')], 0).round(1)
    resumo_modulo["Antes"] = resumo_modulo["Antes_seg"].apply(seconds_to_time)
    resumo_modulo["Depois"] = resumo_modulo["Depois_seg"].apply(seconds_to_time)
    resumo_modulo["Reducao"] = resumo_modulo["Reducao_seg"].apply(seconds_to_time)

    # Gráfico geral empilhado: Depois em azul, Antes em amarelo
    fig_geral = go.Figure()

    fig_geral.add_trace(go.Bar(
        x=resumo_modulo["Módulo"],
        y=resumo_modulo["Depois_seg"],
        name="Tempo Depois",
        marker_color="royalblue",
        text=resumo_modulo["Depois"],
        textposition="inside",
    ))

    fig_geral.add_trace(go.Bar(
        x=resumo_modulo["Módulo"],
        y=resumo_modulo["Antes_seg"],
        name="Tempo Antes",
        marker_color="goldenrod",
        text=resumo_modulo["Antes"],
        textposition="inside",
    ))

    for i, row in resumo_modulo.iterrows():
        # Adiciona anotação de redução apenas se o tempo "Antes" for maior que 0
        if row["Antes_seg"] > 0:
            fig_geral.add_annotation(
                x=row["Módulo"],
                y=row["Antes_seg"] + row["Depois_seg"],
                text=f"{row['% Redução']}% ↓",
                showarrow=False,
                font=dict(color="red", size=14, weight="bold"),
                align="center",
                yshift=10
            )

    fig_geral.update_layout(
        barmode="stack",
        yaxis_title="Tempo (segundos)",
        legend_title_text="Legenda",
        height=450,
        margin=dict(t=50, b=100),
        xaxis_tickangle=-30,
    )

    st.plotly_chart(fig_geral, use_container_width=True)
    st.table(resumo_modulo[["Módulo", "Antes", "Depois", "Reducao", "% Redução"]].set_index("Módulo"))

# =============================================================================
# Conteúdo da Aba "Detalhamento por Curso" (Sem Alterações na lógica, apenas dados)
# =============================================================================
with tab_detalhamento:
    st.subheader("Detalhamento do Tempo por Curso")

    # Seleção do módulo para detalhamento
    modulo_escolhido = st.selectbox("Selecione o módulo para detalhamento:", sorted(df["Módulo"].unique()))
    df_mod = df[df["Módulo"] == modulo_escolhido]

    st.subheader(f"Cursos do {modulo_escolhido}")

    # Gráfico detalhado empilhado: Depois azul embaixo, Antes laranja em cima (tempo total antes)
    fig_det = go.Figure()

    fig_det.add_trace(go.Bar(
        x=df_mod["Curso"],
        y=df_mod["Depois_seg"],
        name="Tempo Depois",
        marker_color="royalblue",
        text=df_mod["Depois_fmt"],
        textposition="inside",
    ))

    fig_det.add_trace(go.Bar(
        x=df_mod["Curso"],
        y=df_mod["Antes_seg"],
        name="Tempo Antes",
        marker_color="orange",
        text=df_mod["Antes_fmt"],
        textposition="inside",
    ))

    for i, row in df_mod.iterrows():
        # Adiciona anotação de redução apenas se o tempo "Antes" for maior que 0
        if row["Antes_seg"] > 0:
            fig_det.add_annotation(
                x=row["Curso"],
                y=row["Antes_seg"] + row["Depois_seg"],
                text=f"{row['% Redução']}% ↓",
                showarrow=False,
                font=dict(color="red", size=12, weight="bold"),
                align="center",
                yshift=10
            )

    fig_det.update_layout(
        barmode="stack",
        xaxis_tickangle=-45,
        yaxis_title="Tempo (segundos)",
        legend_title_text="Legenda",
        height=600,
        margin=dict(t=50, b=150),
    )

    st.plotly_chart(fig_det, use_container_width=True)

    # Tabela detalhada por curso
    st.dataframe(df_mod[["Curso", "Antes_fmt", "Depois_fmt", "Reducao_fmt", "% Redução"]].rename(columns={
        "Antes_fmt": "Antes (HH:MM:SS)",
        "Depois_fmt": "Depois (HH:MM:SS)",
        "Reducao_fmt": "Redução (HH:MM:SS)",
        "% Redução": "% Redução"
    }).set_index("Curso"))

# =============================================================================
# Conteúdo da Aba "Ementas dos Cursos" - IDs de Ementas (Atualizados e com seleção por Módulo)
# =============================================================================
with tab_ementas:
    st.subheader("Acessar Ementas dos Cursos")

    # DICIONÁRIO DE MAPEAMENTO: Curso -> Google Drive File ID para Ementas
    google_drive_ementa_ids = {
        "Linux": "1LO6ef6nBfqu7mi2m2_6K2zGJVVCNoNhR",
        "Scratch": "1ptQTvQxs_KgYa7dXwKC8lEq3snzZAsy9",
        "Introdução a Web": "1NxyAv9iLlzGIPNUhVPdd8PehOiFNySnO",
        "No Code": "14DYBFTAhBDnkL5QYAoWUEjAl4hdquaJ4",
        "Python": "1IBvSgpp0l83rgxzE3UfOXY-RRzAsqnw5",
        "JavaScript": "1KEhBynKcG1FnmdGbGvi60CeCIIuEXJfa",
        "POO": "1IEGCznbmPAjdL5o5A1G86q5pp5oHD2sc",
        "Python II": "1ieUHBoaYAmRvEcX2kOvqC5bGiFRO4pB6",
        "Banco de Dados": "1-BLddbRgJaBvJJHZCi6g9ezAqmkQZKAM",
        "Fundamentos de Interface": "1Kwzlg4zi7XPxk3PmziGugRNYPapEJ3qf",
        "React JS": "1F9-Al3-56QGUdlY3fd-R8yvMvFevFD1A",
        "Web com mentalidade ágil": "1Mfvqg_p5y6UnYGF79w-K1fUxWKJxajlM",
        "Frameworks Front-End": "1CKK6oZ3cGXcLmxxrwBV6fTLssOAN1_Is",
        "React Native": "1R2fno9IohbpDisR2743dGN-oU8ZYkjqw",
        "Flutter": "1gpSctdd8Uf6rsmNTmp-eltq5-DxXa-hO",
        "Desenvolvimento Android": "1wZTlwX7X1k3q54Nh13Z8E9NMrR6G3uZ1",
        "Desenvolvimento FullStack": "1VnBbJFECntcAaC9YAUu2RkZbiW_egVbq",
        "Fundamentos das APIs RESTful": "1P5y5Sh7lHysqA2pBFSd2Fwm9V6ZRCw2F",
        "NoSQL": "1fhkY-z0c_JniaWBWbeuW3KB3BxnXSEqb",
        "Teste de Software para Android": "1iwFF3aDlBiNPd1k1fbUPH9XAq9jl1ojS",
        "Teste de Software para Web": "1YArR5qwgVEQv84r7Fs1AQt-YkgulBhcO",
        "Padrão de Projeto": "14Uj3i7BuvmXeL-aTh2R4-uDaMKArhJ1W", # NOVO CURSO
    }

    # Base URL para links de download direto do Google Drive
    GOOGLE_DRIVE_DOWNLOAD_BASE_URL = "https://drive.google.com/uc?export=download&id="

    # Seleção do módulo para ementas
    modulos_ementa = sorted(df["Módulo"].unique())
    modulo_selecionado_ementa = st.selectbox("Selecione o Módulo para a Ementa:", modulos_ementa, key="mod_ementa_sel")

    # Filtra os cursos baseados no módulo selecionado
    cursos_do_modulo_ementa = sorted(df[df["Módulo"] == modulo_selecionado_ementa]["Curso"].unique())
    
    # Selecionar o curso dentro do módulo
    if cursos_do_modulo_ementa:
        curso_selecionado_ementa = st.selectbox("Escolha o curso para acessar a ementa:", cursos_do_modulo_ementa, key="curso_ementa_sel")

        if curso_selecionado_ementa in google_drive_ementa_ids:
            file_id = google_drive_ementa_ids[curso_selecionado_ementa]
            pdf_url = f"{GOOGLE_DRIVE_DOWNLOAD_BASE_URL}{file_id}"
            
            
            st.markdown(f'<a href="{pdf_url}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-align: center; text-decoration: none; border-radius: 5px; margin-top: 10px;">Abrir Ementa de {curso_selecionado_ementa} em Nova Aba</a>', unsafe_allow_html=True)

        else:
            st.warning(f"Ementa para '{curso_selecionado_ementa}' não encontrada no mapeamento. Por favor, adicione o ID do Google Drive para este curso.")
    else:
        st.info(f"Nenhum curso encontrado no {modulo_selecionado_ementa} para exibir ementas.")

# =============================================================================
# NOVA ABA: Exercícios - IDs dos Exercícios (Atualizados e com seleção por Módulo)
# =============================================================================
with tab_exercicios:
    st.subheader("Acessar Exercícios dos Cursos")

    # DICIONÁRIO DE MAPEAMENTO: Curso -> Google Drive File ID para EXERCÍCIOS
    google_drive_exercicio_ids = {
        "Banco de Dados": "1_tGDhUvGPkfoAdXd8XHSlqTvC-Pw5wTi",
        "Flutter": "1RbtmNKfAGr0sXGpTmyJ-mGIJOoBNygRR",
        "Fundamentos de Interface": "1beD7viSPwJMD_Ye55pw4IZZxU5OEpd4D",
        "Introdução a Web": "1QHfTLurpFnmZZEKLRrV5r7VTIphWry4w", # Mapeado de "Introdução a HTML"
        "JavaScript": "1l8WbgIdY4IxemAxb-x_aMk0_BgQib1IM",
        "Linux": "1ubGMQYxrNyLmvjGhXvP_xz5HeHhp-12x",
        "Web com mentalidade ágil": "1FPjSt4WI6jWegKnw42j6TGGDOrWPDA4S", # Mapeado de "Mentalidade Agil"
        "No Code": "1sohrZ1g-uqdh78lY0GgXRC5MhQMMy3oA",
        "POO": "1kK7r5Sb5PI6E9s5JL-LRXJbBIcUC6JPw",
        "Python II": "1F8aEGb7fSEEJ2kpJBx-RKVuaALBeTb14",
        "Python": "1z1EhnDS_piueULzKjOY7ZvG1AwVd3THn", # Mapeado de "Python"
        "React JS": "1rmU9B8X7SR3zqbVwxyYgiXX8MeCMmHgA",
        "React Native": "15rCdwADCvMMA7Ezhz-lfJpyFTzbuyM-k",
        "Scratch": "1m8BWyOjwuVvYhpa-WZUxxbzFQq6xxhW0",
        "Frameworks Front-End": "1XZkk0CtpD3cGWV-iNCyQa6totLGdrSeN", # Mapeado de "framework de front-end"
        "Desenvolvimento Android": "1uFaem8hiN53Cl63a0rGNyBYBl8fzBfww",
        "Desenvolvimento FullStack": "1f8ohpsgyX9zq7ynDDlI4mlOoeogv2oWt",
        "Fundamentos das APIs RESTful": "1CJnMfJeRKmAsuqW5Gxd7gHrHFawDVFT7",
        "NoSQL": "1yNDXFcRu087khOjYAsaRFzv7lY1JCzKs",
        "Teste de Software para Android": "1kj9G8bRMR7_mQk6PyU8_y2J6BDkazYMk", # LINK CORRIGIDO!
        "Teste de Software para Web": "11gKzBXPu48yLmFNyhnpTACdze2eNCN48",
        "Padrão de Projeto": "1dskkjwfE-FABHryUKURgY5sIF9F7zodU", # NOVO CURSO
    }

    # Base URL para links de download direto do Google Drive (o mesmo)
    GOOGLE_DRIVE_DOWNLOAD_BASE_URL = "https://drive.google.com/uc?export=download&id="

    # Seleção do módulo para exercícios
    modulos_exercicio = sorted(df["Módulo"].unique())
    modulo_selecionado_exercicio = st.selectbox("Selecione o Módulo para o Exercício:", modulos_exercicio, key="mod_exerc_sel")

    # Filtra os cursos baseados no módulo selecionado
    cursos_do_modulo_exercicio = sorted(df[df["Módulo"] == modulo_selecionado_exercicio]["Curso"].unique())
    
    # Selecionar o curso dentro do módulo
    if cursos_do_modulo_exercicio:
        curso_selecionado_exercicio = st.selectbox("Escolha o curso para acessar os exercícios:", cursos_do_modulo_exercicio, key="curso_exerc_sel")

        if curso_selecionado_exercicio in google_drive_exercicio_ids:
            file_id_exercicio = google_drive_exercicio_ids[curso_selecionado_exercicio]
            exercicio_url = f"{GOOGLE_DRIVE_DOWNLOAD_BASE_URL}{file_id_exercicio}"
            
            
            st.markdown(f'<a href="{exercicio_url}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #28a745; color: white; text-align: center; text-decoration: none; border-radius: 5px; margin-top: 10px;">Abrir Exercícios de {curso_selecionado_exercicio} em Nova Aba</a>', unsafe_allow_html=True)

        else:
            st.warning(f"Exercícios para '{curso_selecionado_exercicio}' não encontrados no mapeamento. Por favor, adicione o ID do Google Drive para este curso.")
    else:
        st.info(f"Nenhum curso encontrado no {modulo_selecionado_exercicio} para exibir exercícios.")
