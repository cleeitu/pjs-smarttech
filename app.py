import streamlit as st
import datetime
import calendar
import pandas as pd

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def format_currency(value):
    """Formata valor float para o padrão monetário brasileiro (Ex: R$ 1.500,50)"""
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"

def get_quinto_dia_util(year, month):
    """Retorna a data do 5º dia útil do mês informado (considerando Seg-Sex)"""
    dia = 1
    dias_uteis = 0
    while dias_uteis < 5:
        dt = datetime.date(year, month, dia)
        if dt.weekday() < 5:  # 0 a 4 são Segunda a Sexta
            dias_uteis += 1
        if dias_uteis < 5:
            dia += 1
    return datetime.date(year, month, dia)

def get_primeiro_dia_util(year, month):
    """Retorna o 1º dia útil do mês informado"""
    dia = 1
    while True:
        dt = datetime.date(year, month, dia)
        if dt.weekday() < 5:
            return dt
        dia += 1

def add_months(sourcedate, months):
    """Adiciona meses a uma data de forma segura"""
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Gestão PJ - Contratações e Distratos", layout="wide")
st.title("Gestão de Prestadores (PJ)")

# Criando as abas
tab1, tab2 = st.tabs(["Novas Contratações", "Distratos"])

# ==========================================
# ABA 1: NOVAS CONTRATAÇÕES
# ==========================================
with tab1:
    st.header("Cálculo para Novas Contratações")
    
    col1, col2 = st.columns(2)
    with col1:
        valor_contrato = st.number_input("Valor Mensal do Contrato (R$)", min_value=0.0, value=4500.0, step=100.0, key="val_contrato")
    with col2:
        data_entrada = st.date_input("Data de Entrada", value=datetime.date.today(), format="DD/MM/YYYY", key="dt_entrada")
    
    if st.button("Calcular Cenários", type="primary"):
        diaria = valor_contrato / 30
        
        # --- LÓGICA CENÁRIO 1 ---
        # Mês 1
        dt_corte_c1_m1 = datetime.date(data_entrada.year, data_entrada.month, 15)
        if data_entrada.day > 15:
            dt_corte_c1_m1 = add_months(dt_corte_c1_m1, 1)
            
        dias_c1_m1 = (dt_corte_c1_m1 - data_entrada).days + 1
        valor_c1_m1 = dias_c1_m1 * diaria
        dt_pagamento_c1_m1 = get_quinto_dia_util(add_months(dt_corte_c1_m1, 1).year, add_months(dt_corte_c1_m1, 1).month)
        
        # Mês 2
        dt_inicio_c1_m2 = dt_corte_c1_m1 + datetime.timedelta(days=1)
        dt_corte_c1_m2 = add_months(dt_corte_c1_m1, 1)
        valor_c1_m2 = valor_contrato
        dt_pagamento_c1_m2 = get_quinto_dia_util(add_months(dt_corte_c1_m2, 1).year, add_months(dt_corte_c1_m2, 1).month)
        
        # --- LÓGICA CENÁRIO 2 ---
        # Fração 1
        ultimo_dia_mes_entrada = calendar.monthrange(data_entrada.year, data_entrada.month)[1]
        dt_fim_c2_f1 = datetime.date(data_entrada.year, data_entrada.month, ultimo_dia_mes_entrada)
        dias_c2_f1 = (dt_fim_c2_f1 - data_entrada).days + 1
        valor_c2_f1 = dias_c2_f1 * diaria
        
        dt_envio_nota_c2_f1 = get_primeiro_dia_util(add_months(dt_fim_c2_f1, 1).year, add_months(dt_fim_c2_f1, 1).month)
        dt_pagamento_c2_f1 = dt_envio_nota_c2_f1 + datetime.timedelta(days=15)
        
        # Fração 2
        dt_inicio_c2_f2 = datetime.date(add_months(data_entrada, 1).year, add_months(data_entrada, 1).month, 1)
        dt_fim_c2_f2 = datetime.date(dt_inicio_c2_f2.year, dt_inicio_c2_f2.month, 15)
        dias_c2_f2 = (dt_fim_c2_f2 - dt_inicio_c2_f2).days + 1
        valor_c2_f2 = dias_c2_f2 * diaria
        dt_pagamento_c2_f2 = get_quinto_dia_util(add_months(dt_fim_c2_f2, 1).year, add_months(dt_fim_c2_f2, 1).month)

        # Texto Final para Copiar
        texto_contratacao = f"""Olá! Tudo bem?

Seja muito bem-vindo(a)! Para organizarmos o seu fluxo financeiro conosco, apresento abaixo as informações e cenários para o faturamento dos seus primeiros meses de prestação de serviços.

Como a nossa data de corte padrão é todo dia 15, estruturamos duas opções de cenários iniciais. Dessa forma, você pode avaliar qual delas se adequa melhor ao seu fluxo de caixa neste início:

OPÇÕES DE FATURAMENTO INICIAL

CENÁRIO 1: Ciclo de faturamento contínuo

1º MÊS (Referente a {dias_c1_m1} dias)
- Período: {data_entrada.strftime('%d/%m/%Y')} a {dt_corte_c1_m1.strftime('%d/%m/%Y')}
- Valor a faturar: {format_currency(valor_c1_m1)}
- Envio da nota: Até dia {dt_corte_c1_m1.strftime('%d/%m/%Y')}
- Data de pagamento: {dt_pagamento_c1_m1.strftime('%d/%m/%Y')} (5º dia útil)

2º MÊS EM DIANTE (Ciclo padrão)
- Período: {dt_inicio_c1_m2.strftime('%d/%m/%Y')} a {dt_corte_c1_m2.strftime('%d/%m/%Y')}
- Valor a faturar: {format_currency(valor_c1_m2)}
- Envio da nota: Até dia {dt_corte_c1_m2.strftime('%d/%m/%Y')}
- Data de pagamento: {dt_pagamento_c1_m2.strftime('%d/%m/%Y')} (5º dia útil)


CENÁRIO 2: Ciclo fracionado na virada do mês

1º MÊS - FRAÇÃO 1 (Referente a {dias_c2_f1} dias)
- Período: {data_entrada.strftime('%d/%m/%Y')} a {dt_fim_c2_f1.strftime('%d/%m/%Y')}
- Valor a faturar: {format_currency(valor_c2_f1)}
- Envio da nota: {dt_envio_nota_c2_f1.strftime('%d/%m/%Y')} (1º dia útil)
- Data de pagamento: {dt_pagamento_c2_f1.strftime('%d/%m/%Y')} (Prazo de 15 dias)

1º MÊS - FRAÇÃO 2 (Referente a {dias_c2_f2} dias)
- Período: {dt_inicio_c2_f2.strftime('%d/%m/%Y')} a {dt_fim_c2_f2.strftime('%d/%m/%Y')}
- Valor a faturar: {format_currency(valor_c2_f2)}
- Envio da nota: Até dia {dt_fim_c2_f2.strftime('%d/%m/%Y')}
- Data de pagamento: {dt_pagamento_c2_f2.strftime('%d/%m/%Y')} (5º dia útil)


**Informações Importantes sobre o Fluxo:**
1. Período de Transição: Esses cenários diferenciados aplicam-se apenas aos meses iniciais para o correto alinhamento do cronograma de pagamentos.
2. Fluxo Recorrente (Padrão Definitivo): Após esse período de ajuste, seu faturamento seguirá o modelo padrão definitivo. Isso significa que o envio da sua Nota Fiscal deverá ocorrer até o dia 15 de cada mês (referente ao período do dia 16 do mês anterior ao dia 15 do mês atual), com o pagamento sendo realizado sempre no 5º dia útil do mês seguinte.
3. Aprovação e Faturamento: Por favor, analise as opções acima e nos retorne informando qual dos dois cenários você prefere adotar. Emitiremos a Ordem de Compra (OC) somente após a sua escolha. A sua Nota Fiscal só deverá ser faturada após a emissão dessa OC.
4. Envio da Nota: O envio das notas fiscais deve ser realizado para o e-mail: nf.ti@bioritmo.com.br.

Dados Cadastrais para Emissão da Nota Fiscal
Para a emissão da nota, favor utilizar rigorosamente os dados abaixo:
* Razão Social: SMARTFIT ESCOLA DE GINÁSTICA E DANÇA S.A.
* CNPJ: 07.594.978/0001-78

Se tiver qualquer dúvida, estou à disposição para ajudar!

Abraços,"""
        
        st.success("Cálculos realizados com sucesso!")
        st.text_area("Copie o texto abaixo para enviar ao prestador:", value=texto_contratacao, height=600)


# ==========================================
# ABA 2: DISTRATOS
# ==========================================
with tab2:
    st.header("Cálculo de Distrato")
    
    col1, col2 = st.columns(2)
    with col1:
        val_mensal_distrato = st.number_input("Valor Mensal do Contrato (R$)", min_value=0.0, value=4500.0, step=100.0, key="val_distrato")
        data_distrato = st.date_input("Data do Distrato", value=datetime.date.today(), format="DD/MM/YYYY", key="dt_distrato")
        solicitante = st.radio("Quem solicitou o distrato?", ["Empresa", "Prestador"])
    
    with col2:
        horas_extras = st.number_input("Horas Extras (R$)", min_value=0.0, value=0.0, step=50.0)
        valores_adicionais = st.number_input("Valores Adicionais / Férias (R$)", min_value=0.0, value=0.0, step=50.0)
        tera_mediacao = st.checkbox("Terá mediação? (Marque se houver)")
        somar_mes_anterior = st.checkbox("Incluir ciclo anterior (Nota não emitida)?")

    st.subheader("Notas Pendentes de Pagamento")
    st.write("Insira as informações das notas já emitidas que ainda serão pagas.")
    
    # Tabela editável para notas pendentes
    df_notas = pd.DataFrame(columns=["Número da Nota", "Valor (R$)", "Descrição/Período", "Data de Pagto Programada"])
    edited_df = st.data_editor(df_notas, num_rows="dynamic", use_container_width=True)
    
    st.subheader("Equipamentos para Devolução")
    equipamentos = st.text_area("Liste os equipamentos (um por linha):", "1 Macbook com carregador - Apple\n1 Adaptador Anker")

    if st.button("Gerar Resumo de Distrato", type="primary"):
        diaria = val_mensal_distrato / 30
        
        # Encontrar o último dia 16
        if data_distrato.day >= 16:
            dt_ultimo_16 = datetime.date(data_distrato.year, data_distrato.month, 16)
        else:
            dt_ultimo_16 = datetime.date(add_months(data_distrato, -1).year, add_months(data_distrato, -1).month, 16)
            
        # Regra nova: Retroceder 1 mês se o ciclo anterior não foi faturado
        if somar_mes_anterior:
            dt_ultimo_16 = datetime.date(add_months(dt_ultimo_16, -1).year, add_months(dt_ultimo_16, -1).month, 16)
            
        dias_trabalhados = (data_distrato - dt_ultimo_16).days + 1
        valor_dias_trabalhados = dias_trabalhados * diaria
        
        # Soma de Horas Extras ao mês trabalhado
        total_servicos_mes = valor_dias_trabalhados + horas_extras
        
        # Multa/Aviso
        valor_aviso = val_mensal_distrato if solicitante == "Empresa" else 0.0
        
        # Total da Última Nota
        valor_ultima_nota = total_servicos_mes + valor_aviso + valores_adicionais
        
        # --- MONTAR TEXTO ---
        texto_distrato = f"Pagamentos\n\n"
        
        texto_distrato += f"Serviços prestados de {dt_ultimo_16.strftime('%d/%m/%Y')} a {data_distrato.strftime('%d/%m/%Y')}: {format_currency(total_servicos_mes)}\n"
        
        if valor_aviso > 0:
            texto_distrato += f"30 dias previsto em contrato: {format_currency(valor_aviso)}\n"
            
        if valores_adicionais > 0:
            texto_distrato += f"Serviços adicionais: {format_currency(valores_adicionais)}\n"
            
        # Adicionar Notas Pendentes ao texto
        for index, row in edited_df.iterrows():
            if pd.notna(row['Número da Nota']) and pd.notna(row['Valor (R$)']):
                val_nota_pendente = float(row['Valor (R$)'])
                texto_distrato += f"Pagamento da nota fiscal nº {row['Número da Nota']} no valor de {format_currency(val_nota_pendente)}, referente a {row['Descrição/Período']}, que já está programada para pagamento dia {row['Data de Pagto Programada']}\n"
                
        texto_distrato += f"Emitir uma última nota com o valor total de {format_currency(valor_ultima_nota)}. O pagamento será realizado em até 20 dias após emissão e envio da nota para o e-mail nf.ti@bioritmo.com.br.\n\n"
        
        texto_distrato += f"Equipamentos\n\nNosso time de ativos irá entrar em contato para devolução dos seguintes equipamentos:\n{equipamentos}\n\n"
        
        # Regra da Mediação
        if not tera_mediacao:
            texto_distrato += f"Documentação\n\nO nosso jurídico está elaborando o distrato que conterá as informações acima, com encerramento do contrato para o dia {data_distrato.strftime('%d/%m/%Y')}. Você receberá um e-mail da nossa plataforma de assinatura (DocuSign), para validar e assinar o distrato."
            
        st.success("Resumo de distrato gerado com sucesso!")
        st.text_area("Copie o texto abaixo para enviar ao departamento ou prestador:", value=texto_distrato, height=450)
