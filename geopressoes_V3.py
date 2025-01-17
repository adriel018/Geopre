import io
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from streamlit_pdf_viewer import pdf_viewer
from streamlit_option_menu import option_menu

#  Configurações da página web
logo = 'logo.png'
img_logo = Image.open(logo)
cab = 'logo_syng.png'
img_cab = Image.open(cab)
arquivo = 'logo.png'
image = Image.open(arquivo)
PAGE_CONFIG = {"page_title": "Geopressões",
               "page_icon": image,
               "layout": "wide",
               "initial_sidebar_state": "auto",
               }
st.set_page_config(**PAGE_CONFIG)

c1, c2, c3 = st.columns((0.1, 1, 0.1))
with c2:
    st.image(img_cab, use_column_width=True)  # Inserindo a logo no site

if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = "Home"

# Página inicial do menu do site
def home_page():
    st.title('Syngular Solutions Web Application')
    st.divider()
    st.markdown('''Bem-vindo ao aplicativo web desenvolvido pela ***Syngular Solutions***! Nossa ferramenta foi criada 
    com o intuito de ajudar os profissionais do ramo da perfuração a compreenderem melhor o ***cálculo de geopressões***, 
    um dos ***pilares da segurança*** e eficiência nas operações de subsuperfície.''')
    st.divider()
    st.header('📘 Do que se trata?')
    st.markdown('''Este aplicativo é um recurso didático e prático que aborda os conceitos de geopressões, simula cálculos 
    essenciais e fornece orientações sobre como utilizá-los nas diversas etapas do planejamento e execução de um poço. Ao 
    entender os perfis de pressão em formações geológicas, você estará mais preparado para lidar com desafios como 
    ***estabilidade do poço***, ***controle de kick*** e ***prevenção de blowouts***.''')
    st.divider()
    st.header("🎯 Quando usar este aplicativo?")
    st.write('''O cálculo correto das geopressões é crucial para a segurança e o sucesso de uma operação de perfuração.
    Nosso aplicativo foi projetado para:''')
    st.markdown('''
    - **Reduzir riscos:** Apoiar no controle de pressões anormais;
    - **Otimizar custos:** Identificar janelas operacionais ideais para reduzir custos associados a trincas ou perdas de fluido;
    - **Apoiar decisões:** Oferecer informações confiáveis para a tomada de decisão em tempo real.
    ''')
    st.divider()
    st.markdown('Com este aplicativo, Syngular Solutions reafirma seu compromisso em fornecer soluções inovadoras e acessíveis'
                ' para a indústria de petróleo e gás. Prepare-se para explorar os fundamentos das geopressões e fortalecer '
                'seus conhecimentos em perfuração de poços!')
    st.divider()

def geo_page():

    st.title('Cálculo de Geopressões')

    tabs = st.tabs(['Importaçao de Dados', 'Gradiente de Sobrecarga', 'Gradiente de Pressão de Poros', 'Gradiente de Fratura', 'Geral', 'Relatório'])

    # Carregar Dados
    with tabs[0]:
        c1, c2, c3 = st.columns((1, 1, 1))
        with c1:
            container = st.container(border=True)  # Criando um container com borda
            with container:
                st.markdown('#### Basic Well Info')
                st.text_input('Nome do Usuário', max_chars=None, key='user_name', type="default")
                st.text_input('País', max_chars=None, key='country_name', type="default")
                st.text_input('Nome da Companhia', max_chars=None, key='company_name', type="default")
                st.text_input('Nome do Campo', max_chars=None, key='field_name', type="default")
                st.text_input('Nome do Poço', max_chars=None, key='well_name', type="default")

                st.text_input('Coordenadas do Poço UTM(m): N/S E/W', max_chars=None, key='coordinate', type="default")
                st.text_input('Datum', key='date')
                st.text_area('Objetivo do Poço', max_chars=None, key='comments')
        with c2:
            container = st.container(border = True)
            with container:
                # Permitir upload do arquivo
                uploaded_file = st.file_uploader("***Envie o seu arquivo Excel***", type=["xlsx", "xls"])
                if uploaded_file:
                    try:
                        with c3:
                            container = st.container(border=True)
                            with container:
                                # Lê o arquivo Excel e mostra uma lista de abas
                                excel_data = pd.ExcelFile(uploaded_file)

                                # Selecionar a aba desejada
                                sheet_name = st.selectbox("Selecione a aba para visualizar", excel_data.sheet_names)

                                # Carregar os dados da aba selecionada
                                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

                                # Mostrar a tabela original
                                st.write("Dados Importados:")
                                st.dataframe(df, use_container_width=True)

                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo: {e}")

                c1, c2, c3 = st.columns((1, 0.4, 1))
                with c1:
                    st.checkbox('Poço Onshore', key="onshore", value=True)
                with c3:
                    st.checkbox('Extrapolação', key="ex", value=True)

                st.selectbox('Perfil', ['Perfil Sônico', 'Perfil de Densidade'], key="perfil")

    # Gradiente de Sobrecarga
    with tabs[1]:
        if uploaded_file:
            aux = 0
            if st.session_state.perfil == 'Perfil Sônico':
                while True:
                    dt = []
                    dd = []
                    dm = []

                    # Cálculo de densidade total (sônico)
                    for i in df['Perfil sônico (µs/pé)']:
                        dt.append(0.23 * ((10 ** 6 / i) ** 0.25))
                    df['Densidade total (g/cm³)'] = dt

                    # Cálculo de ΔD (m)
                    dd.append(df['Profundidade (m)'].iloc[0])
                    for i in range(1, len(df)):
                        dd.append(df['Profundidade (m)'].iloc[i] - df['Profundidade (m)'].iloc[i - 1])
                    df['ΔD (m)'] = dd

                    # Cálculo da Densidade
                    if st.session_state.onshore == True:
                        df['Densidade total (g/cm³)'][1] = df['Densidade total (g/cm³)'][1] - aux
                        prof = [df['Profundidade (m)'][1], df['Profundidade (m)'][2]]
                    else:
                        df['Densidade total (g/cm³)'][1] = 1.03
                        df['Densidade total (g/cm³)'][2] = df['Densidade total (g/cm³)'][2] - aux
                        prof = [df['Profundidade (m)'][2], df['Profundidade (m)'][3]]

                    # Cálculo de Densidade x ΔD x 1,422 (psi)
                    for i in range(len(df)):
                        dm.append(df['Densidade total (g/cm³)'].iloc[i] * df['ΔD (m)'].iloc[i] * 1.422)

                    df['Densidade x ΔD x 1,422 (psi)'] = dm
                    df['Soma (psi)'] = df['Densidade x ΔD x 1,422 (psi)'].cumsum()
                    df['Gradiente de Sobrecarga (lb/gal)'] = df['Soma (psi)'] / (0.1704 * df['Profundidade (m)'])

                    if st.session_state.onshore == True:
                        press = [df['Soma (psi)'][1], df['Soma (psi)'][2]]
                    else:
                        press = [df['Soma (psi)'][2], df['Soma (psi)'][3]]

                    # Extrapolação
                    grad = []
                    for i in range(1, int(df['Profundidade (m)'][1])):
                        prof.insert(0, prof[0] - 1)
                        press.insert(0, (((press[1]-press[0])/(prof[2]-prof[1]))*(prof[0]-prof[1])+press[0]))
                    for i, value in enumerate(press):
                        grad.append(max(value/(0.1704*prof[i]), 0))

                    if max(grad) > 21:
                        aux += 0.1
                    else:
                        break

                prof_f = list(df['Profundidade (m)'])
                grad_f = list(df['Gradiente de Sobrecarga (lb/gal)'])

                prof_s = prof + prof_f
                grad_s = grad + grad_f

                graf = pd.DataFrame()
                graf['Profundidade (m)'] = prof_s
                graf['Gradiente de Sobrecarga (lb/gal)'] = grad_s

                c1, c2, c3, c4 = st.columns((0.1, 1, 0.8, 0.1))
                with c2:
                    st.dataframe(df, use_container_width=True)

                with c3:
                    container = st.container(border=True)  # Criando um container com borda
                    with container:
                        # Ajuste da figura
                        plt.figure(figsize=(8, 10))
                        plt.plot(df['Gradiente de Sobrecarga (lb/gal)'], df['Profundidade (m)'],
                                 color='black', linestyle='-', linewidth=2, label="G. de Sobrecarga")
                        if st.session_state.ex == True:
                            plt.plot(grad, prof, color='black', linewidth=2, linestyle='-')
                        # Configurações do gráfico
                        plt.title('Gradiente de Sobrecarga (lb/gal)', fontsize=14, fontweight='bold')
                        plt.xlabel('Gradiente (ppg)', fontsize=12)
                        plt.ylabel('Profundidade (m)', fontsize=12)
                        plt.gca().invert_yaxis()  # Profundidade crescente para baixo
                        # Define os limites do eixo X e Y com base nos dados
                        max_depth = int(df['Profundidade (m)'].max()) + 100
                        margin = 20  # Espaço adicional acima do 0
                        plt.yticks(range(0, max_depth + margin, 200))
                        plt.ylim(max_depth, -margin)
                        plt.xticks(range(7, 21, 1))
                        plt.xlim(7, 21)  # Ajusta o eixo X conforme a imagem
                        plt.grid(True, linestyle='--', alpha=0.5)
                        plt.legend(loc='best')

                        # Exibe o gráfico no Streamlit
                        st.pyplot(plt)

            elif st.session_state.perfil == 'Perfil de Densidade':

                while True:
                    dd = []
                    dm = []

                    # Cálculo de ΔD (m)
                    dd.append(df['Profundidade (m)'].iloc[0])
                    for i in range(1, len(df)):
                        dd.append(df['Profundidade (m)'].iloc[i] - df['Profundidade (m)'].iloc[i - 1])

                    # Adiciona as novas colunas ao DataFrame
                    df['ΔD (m)'] = dd

                    df['Perfil de densidade (g/cm³)'][1] = df['Perfil de densidade (g/cm³)'][1] - aux

                    # cálculo de Densidade x ΔD x 1,422 (psi)
                    for i in range(len(df)):
                        dm.append(df['Perfil de densidade (g/cm³)'].iloc[i] * df['ΔD (m)'].iloc[i] * 1.422)

                    df['Densidade x ΔD x 1,422 (psi)'] = dm
                    df['Soma (psi)'] = df['Densidade x ΔD x 1,422 (psi)'].cumsum()
                    df['Gradiente de Sobrecarga (lb/gal)'] = df['Soma (psi)'] / (0.1704 * df['Profundidade (m)'])

                    prof = [df['Profundidade (m)'][1], df['Profundidade (m)'][2]]
                    press = [df['Soma (psi)'][1], df['Soma (psi)'][2]]
                    grad = []
                    for i in range(1, int(df['Profundidade (m)'][1])):
                        prof.insert(0, prof[0] - 1)
                        press.insert(0, (((press[1]-press[0])/(prof[2]-prof[1]))*(prof[0]-prof[1])+press[0]))
                    for i, value in enumerate(press):
                        grad.append(max(value/(0.1704*prof[i]), 0))

                    if max(grad) > 21 or min(grad) > 1:
                        aux += 0.01
                    else:
                        break

                prof_f = list(df['Profundidade (m)'])
                grad_f = list(df['Gradiente de Sobrecarga (lb/gal)'])

                prof_s = prof + prof_f
                grad_s = grad + grad_f

                graf = pd.DataFrame()
                graf['Profundidade (m)'] = prof_s
                graf['Gradiente de Sobrecarga (lb/gal)'] = grad_s

                c1, c2, c3, c4 = st.columns((0.1, 1, 0.8, 0.1))
                with c2:
                    st.dataframe(df, use_container_width=True)

                with c3:
                    container = st.container(border=True)  # Criando um container com borda
                    with container:
                        # Ajuste da figura
                        plt.figure(figsize=(8, 10))
                        plt.plot(df['Gradiente de Sobrecarga (lb/gal)'], df['Profundidade (m)'],
                                 color='black', linestyle='-', linewidth=2, label="G. de Sobrecarga")
                        if st.session_state.ex == True:
                            plt.plot(grad, prof, color='black', linewidth=2, linestyle='-')
                        # Configurações do gráfico
                        plt.title('Gradiente de Sobrecarga (lb/gal)', fontsize=14, fontweight='bold')
                        plt.xlabel('Gradiente (ppg)', fontsize=12)
                        plt.ylabel('Profundidade (m)', fontsize=12)
                        plt.gca().invert_yaxis()  # Profundidade crescente para baixo
                        # Define os limites do eixo X e Y com base nos dados
                        max_depth = int(df['Profundidade (m)'].max()) + 100
                        margin = 20  # Espaço adicional acima do 0
                        plt.yticks(range(0, max_depth + margin, 150))
                        plt.ylim(max_depth, -margin)
                        plt.xticks(range(7, 21, 1))
                        plt.xlim(7, 21)  # Ajusta o eixo X conforme a imagem
                        plt.grid(True, linestyle='--', alpha=0.5)
                        plt.legend(loc='best')

                        # Exibe o gráfico no Streamlit
                        st.pyplot(plt)

        else:
            st.error('Por favor, insira um documento!', icon="🚨")

    # Gradiente de Pressão de Poros
    with (tabs[2]):
        if uploaded_file:
            c1, c2, c3, c4 = st.columns((0.1, 1, 1, 0.1))
            with c2:
                container = st.container(border=True)  # Criando um container com borda
                with container:
                    st.selectbox('Métodos para Calcular Pressão de Poros', ['Pressão Normal','Método de Eaton'], key = 'mp')
                    if st.session_state.mp == 'Pressão Normal':
                        st.number_input('Insira o valor do ***Nível Freático***',help='Valor em metros',
                                        step=1.0, format='%f', key='nf', min_value=0.0)
                        # Obter a profundidade máxima do dataframe
                        max_depth = df['Profundidade (m)'].max()

                        # Cria uma lista de profundidades de 0 até a profundidade máxima
                        depths = list(range(0, int(max_depth) + 1, 1))

                        # Exibir a tabela de profundidades
                        depth_data = {'Profundidade (m)': depths}
                        df_pp = pd.DataFrame(depth_data)

                        # Mostrar a tabela com as profundidades
                        st.write("Tabela de Profundidades:")

                        ff = []
                        for i in df_pp['Profundidade (m)']:
                            if i <= 7:
                                ff.append(0)  # Se a profundidade for menor ou igual a 7, 'Fluido  da formação' é 0
                            else:
                                ff.append((i + 19200) / 2305.8823529)  # Caso contrário, calcula com a fórmula original

                        df_pp['Fluido da formação (ppg)'] = ff

                        pp = [0]
                        for i in range(1,len(df_pp)):
                            if df_pp['Profundidade (m)'][i] <= st.session_state.nf:
                                pp.append(0)
                            else:
                                # Calcula a pressão com base nos valores da profundidade e do fluido da formação
                                pp.append((0.1704 * df_pp['Fluido da formação (ppg)'][i] * (df_pp['Profundidade (m)'][i] - df_pp['Profundidade (m)'][i - 1])) + pp[-1])

                        # Ajustando o comprimento de pp para corresponder ao tamanho do DataFrame
                        if len(pp) < len(df_pp):  # Caso o vetor tenha menos elementos que o número de linhas
                            pp += [0] * (len(df_pp) - len(pp))  # Preencher com zeros até ter o mesmo comprimento

                        df_pp['Pressão (psi)'] = pp

                        gpp = [0]
                        for i in range(1,len(df_pp)):
                            gpp.append(df_pp['Pressão (psi)'][i] / (0.1704 * df_pp['Profundidade (m)'][i]))
                        df_pp['Gradiente de Pressão de Poros (lb/gal)'] = gpp

                        # Atualizando `graf` para considerar somente profundidades correspondentes
                        graf['Closest Depth'] = graf['Profundidade (m)'].apply(
                            lambda x: min(df_pp['Profundidade (m)'], key=lambda d: abs(d - x))
                        )

                        # Mapeando os valores correspondentes de gradiente de pressão de poros
                        mapped_gpp = []
                        for depth in graf['Closest Depth']:
                            # Encontrar o índice correspondente na tabela `df_pp`
                            matching_row = df_pp[df_pp['Profundidade (m)'] == depth]
                            if not matching_row.empty:
                                mapped_gpp.append(matching_row['Gradiente de Pressão de Poros (lb/gal)'].iloc[0])
                            else:
                                mapped_gpp.append(np.nan)  # Caso não encontre uma correspondência, adicione NaN

                        # Adicionar a coluna filtrada ao DataFrame `graf`
                        graf['Gradiente de Pressão de Poros (lb/gal)'] = mapped_gpp

                        # Remover colunas desnecessárias e ajustar para visualização
                        graf = graf[['Profundidade (m)', 'Gradiente de Sobrecarga (lb/gal)',
                                     'Gradiente de Pressão de Poros (lb/gal)']]

                        st.dataframe(df_pp)

                    if st.session_state.mp == 'Método de Eaton' and st.session_state.perfil == 'Perfil de Densidade':
                        st.error('Este método precisa de dados do perfil Sônico, selecione outro método ou outra planilha', icon="🚨")

                    if st.session_state.mp == 'Método de Eaton' and st.session_state.perfil == 'Perfil Sônico':
                        col1, col2 = st.columns((1, 1))

                        with col1:
                            st.number_input('Profundidade 1', help='Valor em metros',
                                            step=1.0, format='%f', key='pp1', min_value=0.0)
                            st.number_input('Profundidade 2', help='Valor em metros',
                                            step=1.0, format='%f', key='pp2', min_value=0.0)
                        with col2:
                            st.number_input('Leitura 1 do Sônico', help='Valor em µs/pé',
                                            step=1.0, format='%f', key='s1', min_value=0.0)
                            st.number_input('Leitura 2 do Sônico', help='Valor em µs/pé',
                                            step=1.0, format='%f', key='s2', min_value=0.0)
                        df_pp = pd.DataFrame()
                        df_pp['Profundidade (m)'] = df['Profundidade (m)']
                        df_pp['Perfil sônico (µs/pé)'] = df['Perfil sônico (µs/pé)']

                        if st.session_state.s1 != 0 and st.session_state.s2 != 0 and st.session_state.pp1 != 0 and st.session_state.pp2 != 0:
                            # Cálculo da inclinação (a) e do intercepto (b)
                            a = (st.session_state.pp2 - st.session_state.pp1) / (st.session_state.s2 - st.session_state.s1)
                            b = st.session_state.pp1 - a * st.session_state.s1

                            rn = []
                            for i in range(len(df_pp)):
                                if pd.isnull(df_pp['Perfil sônico (µs/pé)'].iloc[i]):
                                    rn.append(None)
                                else:
                                    rn.append((df_pp['Profundidade (m)'].iloc[i] - b) / a)

                            df_pp['Perfil sônico (µs/pé) Reta Normal'] = rn

                            df_pp['Gradiente de Sobrecarga (lb/gal)'] = df['Gradiente de Sobrecarga (lb/gal)']

                            gp = []
                            for i in range(len(df_pp)):
                                if pd.isnull(df_pp['Perfil sônico (µs/pé)'].iloc[i]):
                                    gp.append(None)
                                elif df_pp['Perfil sônico (µs/pé)'].iloc[i] <= df_pp['Perfil sônico (µs/pé) Reta Normal'].iloc[i]:
                                    gp.append(8.5)
                                elif df_pp['Profundidade (m)'].iloc[i]< st.session_state.pp2:
                                    gp.append(8.5)
                                else:
                                    gp.append(df_pp['Gradiente de Sobrecarga (lb/gal)'].iloc[i] - ((df_pp['Gradiente de Sobrecarga (lb/gal)'].iloc[i] - 8.5)*
                                              ((df_pp['Perfil sônico (µs/pé)'].iloc[i] / df_pp['Perfil sônico (µs/pé) Reta Normal'].iloc[i])**(-3))))

                            df_pp['Gradiente de Pressão de Poros (lb/gal)'] = gp

                            st.dataframe(df_pp, use_container_width=True)

                        else:
                            st.error('Por favor, insira os dados corretamente', icon="🚨")

            with c3:
                if uploaded_file:
                    if st.session_state.mp == 'Pressão Normal':
                        container = st.container(border=True)  # Criando um container com borda
                        with container:
                            # Ajuste da figura
                            plt.figure(figsize=(8, 10))
                            if st.session_state.nf != 0:
                                plt.plot(df_pp['Gradiente de Pressão de Poros (lb/gal)'], df_pp['Profundidade (m)'],
                                         color='orange', linestyle='-', linewidth=2, label="G. de Pressão de Poros")
                            else:
                                pass
                            # Configurações do gráfico
                            plt.title('Gradiente de Pressão de Poros (lb/gal)', fontsize=14, fontweight='bold')
                            plt.xlabel('Gradiente (ppg)', fontsize=12)
                            plt.ylabel('Profundidade (m)', fontsize=12)
                            plt.gca().invert_yaxis()  # Profundidade crescente para baixo
                            # Define os limites do eixo X e Y com base nos dados
                            max_depth = int(df['Profundidade (m)'].max()) + 100
                            margin = 20
                            plt.yticks(range(0, max_depth + margin, 150))
                            plt.ylim(max_depth, -margin)  # Inclui espaço antes do 0
                            plt.xticks(range(7, 20, 1))
                            plt.xlim(7, 20)  # Ajusta o eixo X conforme a imagem
                            plt.grid(True, linestyle='--', alpha=0.5)
                            plt.legend(loc='best')

                            # Exibe o gráfico no Streamlit
                            st.pyplot(plt)

                    else:
                        container = st.container(border=True)  # Criando um container com borda
                        with container:
                            # Ajuste da figura
                            plt.figure(figsize=(8, 10))
                            if st.session_state.s1 != 0 and st.session_state.s2 != 0 and st.session_state.pp1 != 0 and st.session_state.pp2 != 0:
                                plt.plot(df_pp['Gradiente de Pressão de Poros (lb/gal)'], df_pp['Profundidade (m)'],
                                         color='orange', linestyle='-', linewidth=2, label="G. de Pressão de Poros")
                            # Configurações do gráfico
                            plt.title('Gradiente de Pressão de Poros (lb/gal)', fontsize=14, fontweight='bold')
                            plt.xlabel('Gradiente (ppg)', fontsize=12)
                            plt.ylabel('Profundidade (m)', fontsize=12)
                            plt.gca().invert_yaxis()  # Profundidade crescente para baixo
                            # Define os limites do eixo X e Y com base nos dados
                            max_depth = int(df['Profundidade (m)'].max()) + 100
                            margin = 20
                            plt.yticks(range(0, max_depth + margin, 200))
                            plt.ylim(max_depth, -margin)  # Inclui espaço antes do 0
                            plt.xticks(range(7, 21, 1))
                            plt.xlim(7, 21)  # Ajusta o eixo X conforme a imagem
                            plt.grid(True, linestyle='--', alpha=0.5)
                            plt.legend(loc='best')

                            # Exibe o gráfico no Streamlit
                            st.pyplot(plt)

        else:
            st.error('Por favor, insira um documento!', icon="🚨")

    # Gradiente de Fratura
    with tabs[3]:
        if uploaded_file:
            c1, c2, c3, c4 = st.columns((0.1, 1, 1, 0.1))
            with c2:
                container = st.container(border=True)  # Criando um container com borda
                with container:

                    if 'add' not in st.session_state:
                        st.session_state.add = []
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button('Add :heavy_plus_sign:', key='add_bt', use_container_width=True):
                            st.session_state.add.append(1)
                    with c2:
                        if st.button('Delete :x:', key='delete_bt', use_container_width=True):
                            try:
                                st.session_state.add.pop(-1)
                            except:
                                st.toast('There are no action to delete!')
                    col1, col2, col3 = st.columns((1, 1, 1))
                    with col1:
                        st.number_input('Revestimento 1', help='Valor em in',
                                        step=1.0, format='%f', key='r1', min_value=0.0)
                        st.number_input('Revestimento 2', help='Valor em in',
                                        step=1.0, format='%f', key='r2', min_value=0.0)
                        for i in range(len(st.session_state.add)):
                            st.number_input(f'Revestimento {i + 3}', help='Valor em in',
                                            step=1.0, format='%f', min_value=0.0, key=f'r_{i + 3}')

                    with col2:
                        st.number_input('Profundidade 1', help='Valor em metros',
                                        step=1.0, format='%f', key='p1_prof', min_value=0.0)
                        st.number_input('Profundidade 2', help='Valor em metros',
                                        step=1.0, format='%f', key='p2_prof', min_value=0.0)
                        for i in range(len(st.session_state.add)):
                            st.number_input(f'Profundidade {i + 3}', help='Valor em in',
                                            step=1.0, format='%f', min_value=0.0, key=f'p{i + 3}_prof')

                    with col3:
                        st.number_input('LOT 1', help='Valor em ppg',
                                        step=1.0, format='%f', key='l1_leak', min_value=0.0)
                        st.number_input('LOT 2', help='Valor em ppg',
                                        step=1.0, format='%f', key='l2_leak', min_value=0.0)
                        for i in range(len(st.session_state.add)):
                            st.number_input(f'LOT {i + 3}', help='Valor em in',
                                            step=1.0, format='%f', min_value=0.0, key=f'l{i + 3}_leak')

                lt = []
                pp = []

                for i in st.session_state:
                    if i.endswith('_prof'):
                        pp.append(st.session_state[i])
                        pp.sort()

                    if i.endswith('_leak'):
                        lt.append(st.session_state[i])
                        lt.sort()

                prof_keys = [key for key in st.session_state.keys() if
                             key.startswith("p") and key.endswith("_prof")]

                if st.session_state.mp == 'Pressão Normal':

                    gf = pd.DataFrame()

                    gf['Profundidade (m)'] = pp

                    ppf = []

                    for i, val in enumerate(pp):
                        if i == 0:
                            ppf.append(0)
                        else:
                            ppf.append(0.1704 * pp[i] * 8.5)

                    gf['P. Poros (psi)'] = ppf

                    pa = []
                    for i, val in enumerate(lt):
                        if i == 0:
                            pa.append(0)
                        else:
                            pa.append(0.1704 * lt[i] * gf['Profundidade (m)'][i])

                    gf['P. Absorção (psi)'] = pa

                    gf.loc[0, 'Gradiente de Sobrecarga (lb/gal)'] = 0


                    def get_closest_depth_value(df, target_depth):
                        closest_index = (df['Profundidade (m)'] - target_depth).abs().argmin()
                        return df.iloc[closest_index]['Gradiente de Sobrecarga (lb/gal)']

                    grad_p1 = get_closest_depth_value(graf, st.session_state.p1_prof)
                    grad_p2 = get_closest_depth_value(graf, st.session_state.p2_prof)

                    gf.loc[gf['Profundidade (m)'] == st.session_state.p1_prof, 'Gradiente de Sobrecarga (lb/gal)'] = grad_p1
                    gf.loc[gf['Profundidade (m)'] == st.session_state.p2_prof, 'Gradiente de Sobrecarga (lb/gal)'] = grad_p2

                    ps = []
                    for i in range(len(gf)):
                        if i == 0:
                            ps.append(0)
                        else:
                            ps.append(0.1704 * gf['Profundidade (m)'][i] * gf['Gradiente de Sobrecarga (lb/gal)'][i])

                    gf['P. Sobrecarga (psi)'] = ps

                    k = []
                    for i in range(len(gf)):
                        if i == 0:
                            k.append(0.1)
                        else:
                            k.append((gf['P. Absorção (psi)'][i] - gf['P. Poros (psi)'][i]) /
                                     (gf['P. Sobrecarga (psi)'][i] - gf['P. Poros (psi)'][i]))

                    gf['K'] = k

                    if st.session_state.p1_prof != 0 and st.session_state.p2_prof != 0:
                        x = gf['K']
                        y = gf['Profundidade (m)']
                        log_y = np.log(y)
                        b, log_a = np.polyfit(x, log_y, 1)
                        a = np.exp(log_a)

                        grf = []
                        for i in range(len(graf)):
                            grf.append((np.log(graf['Profundidade (m)'][i]) - np.log(a)) / b)
                        graf['K'] = grf

                        fra = []
                        for i in range(len(graf)):
                            fra.append(graf['Gradiente de Pressão de Poros (lb/gal)'][i] + graf['K'][i] *
                                       (graf['Gradiente de Sobrecarga (lb/gal)'][i] -
                                        graf['Gradiente de Pressão de Poros (lb/gal)'][i]))
                        graf['Gradiente de Fratura (lb/gal)'] = fra

                    else:
                        pass

                    x_values = []
                    y_values = []
                    for i in range(1, len(lt) + 1):
                        # Gera dinamicamente as chaves para profundidade e gradiente
                        profundidade_key = f"p{i}_prof"
                        gradiente_key = f"grad_p{i}"
                        leak_key = f"l{i}_leak"  # Adiciona o valor de leak correspondente

                        # Calcula o gradiente mais próximo usando a função get_closest_depth_value
                        st.session_state[gradiente_key] = get_closest_depth_value(df,
                                                                                  st.session_state[profundidade_key])

                        # Atualiza o DataFrame com o valor calculado
                        gf.loc[
                            gf['Profundidade (m)'] == st.session_state[profundidade_key],
                            'P. Sobrecarga (psi)'
                        ] = st.session_state[gradiente_key]

                        # Adiciona os valores às listas de coordenadas para o gráfico
                        x_values.append(st.session_state[leak_key])
                        y_values.append(st.session_state[profundidade_key])

                    container = st.container(border=True)  # Criando um container com borda
                    with container:
                        st.dataframe(gf)

                    container = st.container(border=True)  # Criando um container com borda
                    with container:
                        st.dataframe(graf)

                else:
                    df_gf = pd.DataFrame()
                    df_gf['Profundidade (m)'] = df['Profundidade (m)']
                    df_gf['Gradiente de Sobrecarga (lb/gal)'] = df['Gradiente de Sobrecarga (lb/gal)']

                    if st.session_state.s1 and st.session_state.s2 != 0:
                        df_gf['Gradiente de Pressão de Poros (lb/gal)'] = df_pp['Gradiente de Pressão de Poros (lb/gal)']

                        gf = pd.DataFrame()

                        gf['Profundidade (m)'] = pp

                        def get_closest_depth(df, target_depth):
                            closest_index = (df['Profundidade (m)'] - target_depth).abs().argmin()
                            return df.iloc[closest_index]['Gradiente de Pressão de Poros (lb/gal)']

                        for i in range(1,len(pp)+1):
                            # Recupera a profundidade de cada ponto a partir do session_state
                            profundidade_key = f"p{i}_prof"
                            gradiente_key = f"grad_p{i}"

                            # Calcula o gradiente de pressão de poros mais próximo
                            st.session_state[gradiente_key] = get_closest_depth(df_pp, st.session_state[profundidade_key])

                            # Atualiza o DataFrame gf com os valores calculados
                            gf.loc[gf['Profundidade (m)'] == st.session_state[profundidade_key], 'P. de poros (psi)'] = \
                            st.session_state[gradiente_key]

                        ppf = []

                        for i, value in enumerate(gf['P. de poros (psi)']):

                            ppf.append(0.1704 * gf['Profundidade (m)'][i] * value)

                        gf['P. Poros (psi)'] = ppf

                        print(gf)

                        pa = []
                        for i, val in enumerate(lt):
                            pa.append(0.1704 * lt[i] * gf['Profundidade (m)'][i])

                        gf['P. Absorção (psi)'] = pa

                        gf.loc[0, 'P. Sobrecarga (psi)'] = 0

                        def get_closest_depth_value(df, target_depth):
                            closest_index = (df['Profundidade (m)'] - target_depth).abs().argmin()
                            return df.iloc[closest_index]['Soma (psi)']

                        for i in range(1,len(pp)+1):
                            # Gera dinamicamente as chaves para profundidade e gradiente
                            profundidade_key = f"p{i}_prof"
                            gradiente_key = f"grad_p{i}"

                            # Calcula o gradiente mais próximo usando a função get_closest_depth_value
                            st.session_state[gradiente_key] = get_closest_depth_value(df,st.session_state[profundidade_key])

                            # Atualiza o DataFrame com o valor calculado
                            gf.loc[
                                gf['Profundidade (m)'] == st.session_state[profundidade_key],
                                'P. Sobrecarga (psi)'
                            ] = st.session_state[gradiente_key]

                        k = []
                        for i in range(len(gf)):
                            k.append((gf['P. Absorção (psi)'][i] - gf['P. Poros (psi)'][i]) /
                                     (gf['P. Sobrecarga (psi)'][i] - gf['P. Poros (psi)'][i]))

                        gf['K'] = k



                        # Checar se todas as profundidades são diferentes de 0
                        if all(st.session_state[key] != 0 for key in prof_keys):
                            # Realizar o cálculo
                            try:
                                x = gf['K']
                                y = gf['Profundidade (m)']
                                log_y = np.log(y)
                                b, log_a = np.polyfit(x, log_y, 1)
                                a = np.exp(log_a)
                            except Exception as e:
                                st.error(f"Erro no cálculo: {e}")

                            grf = []
                            for i in range(len(df_gf)):
                                grf.append((np.log(df_gf['Profundidade (m)'][i]) - np.log(a)) / b)
                            df_gf['K'] = grf

                            fra = []
                            for i in range(len(df_gf)):
                                fra.append(df_gf['Gradiente de Pressão de Poros (lb/gal)'][i] + df_gf['K'][i] *
                                           (df_gf['Gradiente de Sobrecarga (lb/gal)'][i] -
                                            df_gf['Gradiente de Pressão de Poros (lb/gal)'][i]))
                            df_gf['Gradiente de Fratura (lb/gal)'] = fra


                        else:
                            pass
                            # st.warning("Por favor, preencha todas as profundidades antes de realizar o cálculo.")

                        x_values = []
                        y_values = []
                        for i in range(1, len(lt)+1):
                            # Gera dinamicamente as chaves para profundidade e gradiente
                            profundidade_key = f"p{i}_prof"
                            gradiente_key = f"grad_p{i}"
                            leak_key = f"l{i}_leak"  # Adiciona o valor de leak correspondente

                            # Calcula o gradiente mais próximo usando a função get_closest_depth_value
                            st.session_state[gradiente_key] = get_closest_depth_value(df,st.session_state[profundidade_key])

                            # Atualiza o DataFrame com o valor calculado
                            gf.loc[
                                gf['Profundidade (m)'] == st.session_state[profundidade_key],
                                'P. Sobrecarga (psi)'
                            ] = st.session_state[gradiente_key]

                            # Adiciona os valores às listas de coordenadas para o gráfico
                            x_values.append(st.session_state[leak_key])
                            y_values.append(st.session_state[profundidade_key])

                        container = st.container(border=True)  # Criando um container com borda
                        with container:
                            st.dataframe(gf)

                        container = st.container(border=True)  # Criando um container com borda
                        with container:
                            st.dataframe(df_gf)

                    else:
                        pass

            with c3:
                container = st.container(border=True)  # Criando um container com borda
                with container:
                    plt.figure(figsize=(8, 10))
                    if st.session_state.mp == 'Pressão Normal':
                        if 'Gradiente de Fratura (lb/gal)' in graf.columns:
                            plt.plot(graf['Gradiente de Fratura (lb/gal)'], graf['Profundidade (m)'],
                                     color='brown', linestyle='-', linewidth=2, label="Gradiente de Fratura")

                    if all(st.session_state[key] != 0 for key in prof_keys):
                        plt.plot(df_gf['Gradiente de Fratura (lb/gal)'], df_gf['Profundidade (m)'],
                                 color='brown', linestyle='-', linewidth=2, label="Gradiente de Fratura")
                        plt.scatter(x_values, y_values, color='red', label="LOT's", zorder=5)
                    else:
                        pass
                    plt.title('Gradiente de Fratura (lb/gal)', fontsize=14, fontweight='bold')
                    plt.xlabel('Gradiente (ppg)', fontsize=12)
                    plt.ylabel('Profundidade (m)', fontsize=12)
                    plt.xticks(range(7, 20, 1))
                    plt.gca().invert_yaxis()
                    max_depth = int(df['Profundidade (m)'].max()) + 100
                    margin = 20
                    plt.yticks(range(0, max_depth + margin, 200))
                    plt.ylim(max_depth, -margin)
                    plt.xticks(range(7, 21, 1))
                    plt.xlim(7, 21)
                    plt.grid(True, linestyle='--', alpha=0.5)
                    plt.legend(loc='best')

                    st.pyplot(plt)

        else:
            st.error('Por favor, insira um documento!', icon="🚨")

    # Gráfico de Geopressões
    with tabs[4]:

        col1, col2, col3, col4 = st.columns((0.1, 1, 1, 0.1))
        with col2:
            container = st.container(border=True)  # Criando um container com borda
            with container:
                st.selectbox('Selecione o gráfico que deseja plotar: ', ['Geopressões','Profundidade x Sônico'], key = 'gra')

        with col3:
            if uploaded_file:
                container = st.container(border=True)  # Criando um container com borda
                with container:
                    if st.session_state.gra == 'Geopressões':
                        # Ajuste da figura
                        plt.figure(figsize=(8, 10))
                        if st.session_state.ex == True:
                            plt.plot(grad, prof, color='black', linewidth=2, linestyle='-')
                        plt.plot(df['Gradiente de Sobrecarga (lb/gal)'], df['Profundidade (m)'],
                                 color='black', linestyle='-', linewidth=2, label="G. de Sobrecarga")
                        if st.session_state.mp == 'Pressão Normal':
                            if st.session_state.nf != 0:
                                plt.plot(df_pp['Gradiente de Pressão de Poros (lb/gal)'], df_pp['Profundidade (m)'],
                                         color='orange', linestyle='-', linewidth=2, label="G. de Pressão de Poros")
                            else:
                                pass
                        else:
                            pass
                        if st.session_state.mp == 'Método de Eaton' and st.session_state.perfil == 'Perfil Sônico' and st.session_state.pp2 != 0:
                            plt.plot(df_pp['Gradiente de Pressão de Poros (lb/gal)'], df_pp['Profundidade (m)'],
                                     color='orange', linestyle='-', linewidth=2, label="G. de Pressão de Poros")
                        else:
                            pass
                        if st.session_state.mp == 'Pressão Normal':
                            if 'Gradiente de Fratura (lb/gal)' in graf.columns:
                                plt.plot(graf['Gradiente de Fratura (lb/gal)'], graf['Profundidade (m)'],
                                         color='brown', linestyle='-', linewidth=2, label="Gradiente de Fratura")
                        if all(st.session_state[key] != 0 for key in prof_keys):
                            plt.plot(df_gf['Gradiente de Fratura (lb/gal)'], df_gf['Profundidade (m)'],
                                     color='brown', linestyle='-', linewidth=2, label="Gradiente de Fratura")
                            plt.scatter(x_values, y_values, color='red', label="LOT's", zorder=5)
                        # Configurações do gráfico
                        plt.title('Curva de Geopressões', fontsize=14, fontweight='bold')
                        plt.xlabel('Gradiente (ppg)', fontsize=12)
                        plt.ylabel('Profundidade (m)', fontsize=12)
                        plt.gca().invert_yaxis()  # Profundidade crescente para baixo
                        max_depth = int(df['Profundidade (m)'].max()) + 100
                        margin = 20
                        plt.yticks(range(0, max_depth + margin, 200))
                        plt.ylim(max_depth, -margin)  # Inclui espaço antes do 0
                        plt.xticks(range(7, 21, 1))
                        plt.xlim(7, 21)  # Ajusta o eixo X conforme a imagem
                        plt.grid(True, linestyle='--', alpha=0.5)
                        plt.legend(loc='best')

                        # Exibe o gráfico no Streamlit
                        st.pyplot(plt)

                    else:
                        plt.figure(figsize=(8, 10))
                        plt.plot(df['Perfil sônico (µs/pé)'], df['Profundidade (m)'],
                                 color='red', linestyle='-', linewidth=2, label="Sônico x Profundidade")
                        plt.plot(df_pp['Perfil sônico (µs/pé) Reta Normal'], df['Profundidade (m)'],
                                color='green', linestyle='--', linewidth=2, label="Linha de Tendência")
                        plt.title('Sônico x Profundidade (m)', fontsize=14, fontweight='bold')
                        plt.xlabel('Perfil sônico (µs/pé)', fontsize=12)
                        plt.ylabel('Profundidade (m)', fontsize=12)
                        plt.xticks(range(7, 20, 1))
                        plt.gca().invert_yaxis()
                        max_depth = int(df['Profundidade (m)'].max()) + 100
                        margin = 20
                        plt.yticks(range(0, max_depth + margin, 200))
                        plt.ylim(max_depth, -margin)
                        plt.xticks(range(0, 250, 20))
                        plt.xlim(0, 250)
                        plt.grid(True, linestyle='--', alpha=0.5)
                        plt.legend(loc='best')

                        st.pyplot(plt)
            else:
                st.error('Por favor, insira um documento!', icon="🚨")

    # Relatório
    with tabs[5]:

        if uploaded_file:

            hora_now = datetime.now() + timedelta(hours=-3)

            st.title("Relatório Final")

            # Criação de um buffer em memória para armazenar o PDF em binário
            pdf_buffer = io.BytesIO()

            # Definição do PDF usando o reportlab
            c = canvas.Canvas(pdf_buffer, pagesize=letter)

            width, height = letter

            c.drawImage(logo, 230, height - 100, width=150, height=100)

            c.setFont("Helvetica-Bold", 25)
            c.drawString(235, height - 320, "Geopressões")
            c.drawString(228, height - 350, "Relatório Final")
            well_name = f" {st.session_state.well_name}"
            user_name = f" {st.session_state.user_name}"

            # Obter a largura do texto
            text_width = c.stringWidth(well_name, "Helvetica-Bold", 20)
            text_width2 = c.stringWidth("Responsável Técnico:" + user_name, "Helvetica", 15)

            # Calcular a posição X para centralizar o texto
            x_position = (width - text_width) / 2
            x2_position = (width - text_width2) / 2

            # Desenhar o texto na posição calculada
            c.setFont("Helvetica-Bold", 18)
            c.drawString(x_position, height - 375, well_name)
            c.setFont("Helvetica", 15)
            c.drawString(x2_position, height - 530, "Responsável Técnico:" f'{user_name}')


            c.setFont("Helvetica", 12)
            c.line(30, height - 690, width - 30, height - 690)
            c.drawString(40, height - 710, 'Syngular Solutions')
            c.drawString(40, height - 730, 'Houston, TX 77077')
            c.drawString(40, height - 750, 'info@syngularsolutions.com')
            c.drawString(380, height - 710,f"Data do Relatório: {datetime.today().strftime('%d/%m/%Y')} {hora_now.strftime('%H:%M')}")

            c.showPage()

            c.drawImage(logo, 230, height - 100, width=150, height=100)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(30, height - 80, "Dados do Poço")
            c.line(30, height - 90, width - 30, height - 90)
            c.line(30, height - 765, width - 30, height - 765)
            c.setFont("Helvetica", 12)
            c.drawString(30, height - 110, f"Nome do Usuário: {st.session_state.user_name}")
            c.drawString(30, height - 130, f"Perfil Utilizado: {st.session_state.perfil}")
            c.drawString(30, height - 150, f"Nome do Poço: {st.session_state.well_name}")
            c.drawString(30, height - 170, f"Nome do Campo: {st.session_state.field_name}")
            c.drawString(300, height - 110, f"Nome da Companhia: {st.session_state.company_name}")
            c.drawString(300, height - 130, f"País: {st.session_state.country_name}")
            c.drawString(300, height - 150, f"Coordenadas do Poço UTM(m): {st.session_state.coordinate}")
            c.drawString(300, height - 170, f"Datum: {st.session_state.date}")
            comments = st.session_state.comments
            max_length_per_line = 85  # Defina o comprimento máximo por linha conforme necessário
            comment_lines = [comments[i:i + max_length_per_line] for i in
                             range(0, len(comments), max_length_per_line)]
            c.setFont("Helvetica", 12)
            c.drawString(30, height - 190, "Objetivo do Poço:")
            y_position = height - 190
            for line in comment_lines:
                c.drawString(125, y_position, line)
                y_position -= 15
            c.setFont("Helvetica-Bold", 20)
            c.drawString(30, height - 230, "Gradiente de Sobrecarga")
            c.line(30, height - 240, width - 30, height - 240)

            c.showPage()

            # c.drawImage(logo, 230, height - 100, width=150, height=100)
            # c.setFont("Helvetica-Bold", 20)
            # c.drawString(30, height - 100, "Gradiente de Pressão de Poros")
            # c.line(30, height - 110, width - 30, height - 110)
            # c.line(30, height - 765, width - 30, height - 765)
            # c.setFont("Helvetica", 12)
            # c.drawString(30, height - 130, f"Nível Freático : {st.session_state.nf} metros")
            #
            # c.showPage()
            #
            # c.drawImage(logo, 230, height - 100, width=150, height=100)
            # c.setFont("Helvetica-Bold", 20)
            # c.drawString(30, height - 100, "Gradiente de Fratura")
            # c.line(30, height - 110, width - 30, height - 110)
            # c.line(30, height - 765, width - 30, height - 765)
            # c.setFont("Helvetica", 12)
            # c.drawString(30, height - 130, f"Revestimento 1: {st.session_state.r1} in")
            # c.drawString(30, height - 150, f"Revestimento 2: {st.session_state.r2} in")
            # c.drawString(30, height - 170, f"Profundidade 1: {st.session_state.p1} metros")
            # c.drawString(30, height - 190, f"Profundidade 1: {st.session_state.p2} metros")
            # c.drawString(30, height - 210, f"LOT 1: {st.session_state.l1} lb/gal")
            # c.drawString(30, height - 230, f"LOT 2: {st.session_state.l2} lb/gal")
            #
            # c.showPage()
            #
            # c.drawImage(logo, 230, height - 100, width=150, height=100)
            # c.setFont("Helvetica-Bold", 20)
            # c.drawString(30, height - 100, "Gráfico de Geopressões")
            # c.line(30, height - 110, width - 30, height - 110)
            # c.line(30, height - 765, width - 30, height - 765)
            #
            # c.showPage()

            # Finaliza o PDF
            c.save()

            # Recupera o conteúdo do buffer como um valor binário
            pdf_binary = pdf_buffer.getvalue()

            col_pdf1, col_pdf2, col_pdf3, col_pdf4, col_pdf5 = st.columns((0.4, 0.2, 1, 0.2, 0.3))

            with col_pdf1:

                if st.session_state.well_name == '':
                    report_name = 'Relatorio_Final.pdf'

                else:
                    report_name = f'{st.session_state.well_name}.pdf'

                view = st.button(':bookmark_tabs: Ver Relatório', key='pdf_view_bt', use_container_width=True)
                st.download_button(
                    label="⬇️ Baixar Relatório",
                    data=pdf_binary,
                    file_name=report_name,
                    mime="application/pdf",
                    use_container_width=True
                )

                with col_pdf3:

                    if view:
                        container_pdf = st.container(border=True, height=900)
                        with container_pdf:
                            pdf_bytes = pdf_buffer.getvalue()
                            pdf_viewer(input=pdf_bytes,
                                       width=700, pages_vertical_spacing=20)

menu_option = ["Home", "Geopressões"]
menu_icons = ["house", "list-task"]

# Criando menu principal
selected = option_menu(
    menu_title=None,
    options=menu_option,
    icons=menu_icons,
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    key='option_menu'
)

# Condições para entrar em cada página do site
if selected == 'Home':
    home_page()

else:
    geo_page()