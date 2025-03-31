from flask import Flask, request, render_template
import pandas as pd
import re

app = Flask(__name__)

def controller_tags(colonna,tipologia,pattern):
    lista = []
    for row in colonna:
        row = str(row).replace('_', '-')
        if tipologia in row:
            riga = row.split(',')
            if len(riga)>1:
                for parola in riga:
                    parola = str(parola).replace("R410-", "")
                    if re.match(pattern, str(parola)):
                        lista.append(parola)
    return lista

def crea_lista(colonna,pattern):
    lista = []
    for row in colonna:
        row = str(row).replace("R410-", "")
        row = str(row).replace('_', '-')
        if re.match(pattern, str(row)):
            lista.append(row)
    return lista

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file1 = request.files['file1']
    file2 = request.files['file2']

    opzione = request.form.get('opzione')
    CT1 = request.form.get('CT1')
    CT2 = request.form.get('CT2')
    nr_colonna1 = request.form.get('colonna1')
    nr_colonna2 = request.form.get('colonna2')
    nr_colonna3 = request.form.get('colonna3')
    tipologia1 = request.form.get('type1')
    tipologia2 = request.form.get('type2')
    tipologia = request.form.get('tipologia')
    priorita = request.form.get('scelta')

    pattern = r'^[A-Za-z0-9]+-[A-Za-z0-9]+$'

    if 'file1' not in request.files:
        return render_template('output.html', data='Nessun file1 selezionato'), 400
    
    if file1 and file1.filename.endswith('.csv'):
#----------------------------------------------------------------------------------------------------------------------------------------
        if opzione == 'opzione1':
            if 'file2' not in request.files:
                return render_template('output.html', data='Nessun file2 selezionato'), 400
            
            if file2 and file2.filename.endswith('.csv'):
                if  priorita:
                    try:
                        fileA = pd.read_csv(file1, sep=';', header=None)
                    except pd.errors.ParserError as e:
                        return render_template('output.html', data='Errore nella lettura del primo file CSV:'), e
                    try:
                        fileB = pd.read_csv(file2, sep=';', header=None)
                    except pd.errors.ParserError as e:
                        return render_template('output.html', data='Errore nella lettura del secondo file CSV:'), e
                    
                    colonna1 = fileA.iloc[:, int(nr_colonna1)]
                    colonna2 = fileB.iloc[:, int(nr_colonna2)]

                    if CT1=='CT1':#1
                        lista1 = controller_tags(colonna1,tipologia1,pattern)
                    else:
                        lista1 = crea_lista(colonna1,pattern)

                    if CT2=='CT2':#2
                        lista2 = controller_tags(colonna2,tipologia2,pattern)
                    else:
                        lista2 = crea_lista(colonna2,pattern)

                    if  priorita == 'scelta1': #3
                        out = list(set(lista1) - set(lista2))
                        out.sort()
                    elif priorita == 'scelta2': #4
                        out = list(set(lista2) - set(lista1))
                        out.sort()

                    if len(out)==0:
                        return render_template('output.html', data='Tutti i valori sono presenti')
                    else:
                        return render_template('output.html', data=out)
                else:
                    return render_template('output.html', data='Errore priorità non scelta')
            else:
                return render_template('output.html', data='Il file2 non è un CSV valido'), 400
#----------------------------------------------------------------------------------------------------------------------------------------
        elif opzione == 'opzione2':
            try:
                file = pd.read_csv(file1, sep=';', header=None)
            except pd.errors.ParserError as e:
                return render_template('output.html', data='Errore nella lettura del primo file CSV:'), e
            
            colonna = file.iloc[:, int(nr_colonna3)]

            if CT1=='CT1':
                lista = controller_tags(colonna,tipologia,pattern)
            else:
                lista = crea_lista(colonna,pattern)

            lista.sort()
            return render_template('output.html', data=lista)
#----------------------------------------------------------------------------------------------------------------------------------------                        
        else:
            return render_template('output.html', data='Devi selezionare una funzione!')
    else:
        return render_template('output.html', data='Il file1 non è un CSV valido'), 400
    
if __name__ == '__main__':
    app.run(debug=True)