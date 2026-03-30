# BANKA — Resumo do Sistema v2.0

## Links importantes

| Recurso | Link |
|---|---|
| **App (Streamlit)** | *(cole aqui o link do seu app no share.streamlit.io)* |
| **Google Sheets (lançamentos auxiliares)** | https://docs.google.com/spreadsheets/d/1tz-vW9VnLyqpHn9fz8PiCnrKzrQSQxRlMkadrEu_TtI |
| **Google Drive (planilha gerencial)** | https://drive.google.com/drive/folders/0AMx_YQjS-FVIUk9PVA |

---

## O que o sistema faz

O app conecta os **funcionários das bancas** ao **financeiro (contas a pagar)**.

- Funcionários registram boletos e PIX diretamente pelo app, entre **13h e 20h**
- Cada registro gera um **código de identificação único** e dispara um **e-mail automático** com os anexos para todos os destinatários
- O financeiro acessa a área restrita para sincronizar, baixar e subir a planilha gerencial

---

## O que mudou na versão 2.0

### ✅ Problema de hibernação resolvido

**Antes:** o Streamlit desligava os servidores após ~8h sem acesso e todos os lançamentos feitos no período eram perdidos. A sincronização não encontrava nada.

**Agora:** os lançamentos são salvos em tempo real no **Google Sheets**, fora do servidor. A hibernação não afeta mais nada.

### ✅ Planilha gerencial no Google Drive

**Antes:** a planilha ficava no servidor do Streamlit e era apagada na hibernação.

**Agora:** a planilha fica salva no **Google Drive**. O app sempre busca e salva a versão mais recente de lá.

### ✅ Cálculo de data de vencimento do boleto corrigido

**Antes:** a data era calculada com a lógica antiga da FEBRABAN (data base 07/10/1997), que deixou de funcionar corretamente em fevereiro de 2025 quando o fator de 4 dígitos se esgotou.

**Agora:** o sistema reconhece automaticamente o novo padrão (fator reiniciado em 1000 a partir de 22/02/2025) e calcula a data corretamente.

### ✅ Bug de planilhas trocadas corrigido

**Antes:** registros da São Conrado iam para a planilha da Tijuca e vice-versa.

**Agora:** cada lançamento vai para a aba correta no Google Sheets.

---

## Guia rápido — Financeiro (Bruno)

### Sincronizar o sistema
1. Acesse o app e vá em **"Controle Operacional"**
2. Digite a senha
3. Clique em **"Sincronizar o Sistema"**
4. O app vai:
   - Baixar a planilha gerencial do Google Drive
   - Adicionar todos os lançamentos novos na aba *Controle de NFs Tomadas*
   - Subir a planilha atualizada de volta ao Google Drive
   - Limpar os lançamentos já processados do Google Sheets

### Baixar a planilha gerencial
1. Em **"Controle Operacional"**, após digitar a senha
2. Clique em **"Baixar Planilha Gerencial"**
3. O arquivo vem sempre da versão mais recente salva no Google Drive

### Salvar uma nova versão da planilha
1. Em **"Controle Operacional"**, após digitar a senha
2. Em **"Salvar Nova Planilha"**, selecione o arquivo `.xlsx` atualizado
3. O app salva no Google Drive **e** envia por e-mail como backup automático

---

## Guia rápido — Funcionários das bancas

1. Acesse o app entre **13h e 20h**
2. Selecione sua loja e o tipo de registro (Boleto ou PIX)
3. Preencha os campos — o número do boleto já preenche valor e vencimento automaticamente
4. Anexe a nota fiscal e o boleto
5. Clique em **"Registrar"**
6. Guarde o **código de identificação** exibido na tela — ele é usado caso precise cancelar o lançamento

### Para cancelar um lançamento
1. Vá em **"Cancelar Lançamento"**
2. Informe o código de identificação recebido no registro
3. O lançamento será removido na próxima sincronização

---

## Estrutura técnica resumida

```
Funcionário registra
       ↓
Google Sheets (lançamentos por banca)
       ↓
Bruno clica "Sincronizar"
       ↓
App baixa planilha gerencial do Google Drive
       ↓
App escreve lançamentos na aba "Controle de NFs Tomadas"
       ↓
App sobe planilha atualizada pro Google Drive
       ↓
Google Sheets é limpo para o próximo ciclo
```
