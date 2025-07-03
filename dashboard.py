import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os
# base64 não é mais necessário
# import base64 

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
df["% Redução"] = (df["Reducao_seg"] / df["Antes_seg"] * 100).round(1)
df["Antes_fmt"] = df["Antes"]
df["Depois_fmt"] = df["Depois"]
df["Reducao_fmt"] = df["Reducao_seg"].apply(seconds_to_time)

st.title("Dashboard de Redução de Carga Horária")

# --- Definição das Abas Principais ---
tab_geral, tab_detalhamento, tab_ementas = st.tabs(["Visão Geral por Módulo", "Detalhamento por Curso", "Ementas dos Cursos"])

# =============================================================================
# Conteúdo da Aba "Visão Geral por Módulo"
# =============================================================================
with tab_geral:
    st.subheader("Visão Geral do Tempo por Módulo")

    # Resumo por módulo
    resumo_modulo = df.groupby("Módulo").agg({
        "Antes_seg": "sum",
        "Depois_seg": "sum"
    }).reset_index()
    resumo_modulo["Reducao_seg"] = resumo_modulo["Antes_seg"] - resumo_modulo["Depois_seg"]
    resumo_modulo["% Redução"] = (resumo_modulo["Reducao_seg"] / resumo_modulo["Antes_seg"] * 100).round(1)
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
# Conteúdo da Aba "Detalhamento por Curso"
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
# Conteúdo da Aba "Ementas dos Cursos" - USANDO GOOGLE DRIVE COM IDs
# =============================================================================
with tab_ementas:
    st.subheader("Acessar Ementas dos Cursos")

    # DICIONÁRIO DE MAPEAMENTO: Curso -> Google Drive File ID
    # Estes IDs foram extraídos dos links de compartilhamento que você forneceu.
    google_drive_pdf_ids = {
        "Linux": "1LO6ef6nBfqu7mi2m2_6K2zGJVVCNoNhR",
        "Scratch": "1ptQTvQxs_KgYa7dXwKC8lEq3snzZAsy9",
        "Introdução a Web": "1NxyAv9iLlzGIPNUhVPdd8PehOiFNySnO",
        "No Code": "14DYBFTAhBDnkL5QYAoWUEjAl4hdquaJ4",
        "Python": "1IBvSgpp0l83rgxzE3UfOXY-RRzAsqnw5",
        "JavaScript": "1KEhBynKcG1FnmdGbGvi60CeCIIuEXJfa", # ID de arquivo corrigido para JavaScript
        "POO": "1IEGCznbmPAjdL5o5A1G86q5pp5oHD2sc",
        "Python II": "1ieUHBoaYAmRvEcX2kOvqC5bGiFRO4pB6",
        "Banco de Dados": "1-BLddbRgJaBvJJHZCi6g9ezAqmkQZKAM",
        "Fundamentos de Interface": "1Kwzlg4zi7XPxk3PmziGugRNYPapEJ3qf",
        "React JS": "1F9-Al3-56QGUdlY3fd-R8yvMvFevFD1A",
        "Web com mentalidade ágil": "1Mfvqg_p5y6UnYGF79w-K1fUxWKJxajlM",
        "Frameworks Front-End": "1CKK6oZ3cGXcLmxxrwBV6fTLssOAN1_Is",
        "React Native": "1R2fno9IohbpDisR2743dGN-oU8ZYkjqw",
        "Flutter": "1gpSctdd8Uf6rsmNTmp-eltq5-DxXa-hO",
    }

    # Base URL para links de download direto do Google Drive
    GOOGLE_DRIVE_DOWNLOAD_BASE_URL = "https://drive.google.com/uc?export=download&id="

    # Selecionar o curso
    cursos_para_ementa = sorted(df["Curso"].unique())
    curso_selecionado_ementa = st.selectbox("Escolha o curso para acessar a ementa:", cursos_para_ementa)

    if curso_selecionado_ementa in google_drive_pdf_ids:
        file_id = google_drive_pdf_ids[curso_selecionado_ementa]
        pdf_url = f"{GOOGLE_DRIVE_DOWNLOAD_BASE_URL}{file_id}"
        
        st.markdown(f"**[{curso_selecionado_ementa} - Clique para abrir/baixar a Ementa]({pdf_url})**", unsafe_allow_html=True)
        
        # Botão secundário para abrir em nova aba (opcional)
        st.markdown(f'<a href="{pdf_url}" target="_blank" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-align: center; text-decoration: none; border-radius: 5px; margin-top: 10px;">Abrir Ementa de {curso_selecionado_ementa} em Nova Aba</a>', unsafe_allow_html=True)

        st.success("Clique no link ou botão acima para acessar a ementa.")
        st.caption("A ementa será aberta/baixada diretamente do Google Drive. Certifique-se de que o PDF está configurado para 'Qualquer pessoa com o link' no Google Drive.")
    else:
        st.warning(f"ID do Google Drive para '{curso_selecionado_ementa}' não encontrado no mapeamento.")
        st.caption("Por favor, verifique se o curso e seu ID correspondente estão corretos no dicionário do código.")
