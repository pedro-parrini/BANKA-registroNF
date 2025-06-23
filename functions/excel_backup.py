import smtplib
from email.message import EmailMessage
from datetime import datetime

def backup_planilha(planilha="Banka l Planilha Gerencial.xlsx"):

    email_origem = "pedro.parrini@equityrio.com.br"
    senha_do_email = 'upvz ljbh zszn kipb'
    msg = EmailMessage()
    msg['From'] = email_origem
    msg['Subject']  = f'Backup Planilha Gerencial {datetime.now().strftime("%d/%m/%Y")}'
    msg['To'] = ['pedro.parrini@equityrio.com.br', 'brunodnpeniche@gmail.com', 'financeiro.banka@gmail.com', 'vqf.banka@gmail.com']

    mensagem = f''' 

Segue a Planilha salva no dia {datetime.now().strftime("%d/%m/%Y")}.

'''

    msg.set_content(mensagem, 'html')

    try:

        with open(planilha, 'rb') as content_file:
            content = content_file.read()
            msg.add_attachment(content, maintype='application', subtype='xlsx', filename="Banka l Planilha Gerencial.xlsx")  

    except:
        pass

    try:

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_origem, senha_do_email)
            smtp.send_message(msg)
    
    except:
        pass

