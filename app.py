import streamlit as st
import pandas as pd

st.title("Conversor de Leads para Meetime")

uploaded_file = st.file_uploader("Faça upload da planilha Excel com as abas 'Empresas' e 'Contatos'", type=["xlsx"])

if uploaded_file:
    try:
        empresas = pd.read_excel(uploaded_file, sheet_name="Empresas")
        contatos = pd.read_excel(uploaded_file, sheet_name="Contatos")

        empresas['CNPJ'] = empresas['CNPJ'].astype(str)
        contatos['CNPJ'] = contatos['CNPJ'].astype(str)

        contatos['Contato_Formatado'] = contatos.apply(
            lambda row: f"{row.get('Nome completo', '')} | {row.get('Cargo atual', '')} | {row.get('Departamento', '')} | {row.get('URL contact page', '')}", axis=1
        )
        anotações_por_cnpj = contatos.groupby('CNPJ')['Contato_Formatado'].apply(lambda x: '\n'.join(x)).reset_index()
        primeiros_contatos = contatos.groupby('CNPJ').first().reset_index()

        resultado = empresas.merge(primeiros_contatos[['CNPJ', 'Nome completo', 'E-mail corporativo', 'Perfil do linkedin']], on='CNPJ', how='left')
        resultado = resultado.merge(anotações_por_cnpj, on='CNPJ', how='left')

        resultado['PRIMEIRO NOME'] = resultado['Nome completo'].apply(lambda x: str(x).split()[0] if pd.notnull(x) else '')

        df_final = pd.DataFrame({
            'CNPJ': resultado['CNPJ'],
            'EMPRESA': resultado.get('Nome Fantasia', ''),
            'RAZAO SOCIAL': resultado.get('Nome da empresa', ''),
            'ESTADO': resultado.get('UF', ''),
            'CIDADE': resultado.get('Município', ''),
            'NUMERO DE LOJAS': resultado.get('Total de filiais', ''),
            'SITE': resultado.get('Domínio', ''),
            'TELEFONE': resultado.get('Telefone principal', ''),
            'EMAIL': resultado.get('Email principal', ''),
            'INSTAGRAM': resultado.get('Perfil do instagram', ''),
            'LINKEDIN': resultado.get('Perfil do linkedin', ''),
            'SEGMENTO': resultado.get('Segmento', ''),
            'FUNCIONARIOS': resultado.get('Total de funcionários', ''),
            'FATURAMENTO': resultado.get('Faixa de faturamento', ''),
            'PRIMEIRO NOME': resultado['PRIMEIRO NOME'],
            'NOME COMPLETO': resultado['Nome completo'],
            'EMAIL DO PROSPECT': resultado['E-mail corporativo'],
            'LINKEDIN DO PROSPECT': resultado['Perfil do linkedin_y'] if 'Perfil do linkedin_y' in resultado else resultado['Perfil do linkedin'],
            'ANOTAÇÕES DO LEAD': resultado['Contato_Formatado']
        })

        st.success("Planilha processada com sucesso! 🎉")
        st.dataframe(df_final)

        csv = df_final.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 Baixar CSV", csv, file_name="leads_meetime.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, envie um arquivo Excel para começar.")
