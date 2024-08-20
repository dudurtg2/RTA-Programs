import sys
import winsound
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QComboBox
import firebase_admin
from firebase_admin import credentials, firestore
from PyQt5.QtCore import Qt
import json
import textwrap

with open('service-account-credentials.json') as json_file:
    data = json.load(json_file)
    firebase_credentials = data['firebase']

cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

base = [
    "ROTAS", "FEIRA DE SANTANA", "TRANSFERENCIA", "DIRECIONADO"
]
cidades_feira = [
    "IPIRA", "BAIXA GRANDE", "MAIRI", "VARZEA DA ROÇA", "MORRO DO CHAPEU", "IRECE",
    "ITABERABA", "IAÇU", "ITATIM", "CASTRO ALVES", "SANTA TEREZINHA", "SANTO ESTEVÃO",
    "ANTONIO CARDOSO", "IPECAETA", "SÃO GONÇALO DOS CAMPOS", "CACHOEIRA", "SÃO FELIX",
    "CONCEIÇÃO DA FEIRA", "AMELIA RODRIGUES", "CONCEIÇÃO DO JACUIPE", "CORAÇÃO DE MARIA",
    "TEODORO SAMPAIO", "IRARA", "SANTANOPOLIS", "MURITIBA", "SAPEAÇU", "CRUZ DAS ALMAS",
    "GOVERNADOR MANGABEIRA", "CABACEIRA DO PARAGUAÇU", "SÃO FELIPE",
    "MARAGOGIPE", "TANQUINHO", "CANDEAL", "ICHU", "SERRINHA", "BIRITINGA", "BARROCAS",
    "ARACI", "TEOFILANDIA", "SANTA BARBARA", "LAMARÃO", "AGUA FRIA", "CONCEIÇÃO DO COITÉ",
    "VALENTE", "RETIROLANDIA", "SANTA LUZ", "CANSANÇÃO", "QUEIMADAS", "SÃO DOMINGOS",
    "RIACHÃO DO JACUIPE", "NOVA FATIMA", "PE DE SERRA", "CIPÓ", "BANZAÊ", "FATIMA",
    "CICERO DANTAS", "NOVA SOURE", "TUCANO", "RIBEIRA DO AMPARO", "SITIO DO QUINTO",
    "CORONEL JOÃO SÁ", "HELIOPOLIS", "RIBEIRA DO POMBAL", "ANGUERA", "SERRA PRETA",
    "RAFAEL JAMBEIRO", "FEIRA DE SANTANA", "BAIXA GRANDE"
]
tranferencia = [
    "TRANSFERENCIA PARA FEIRA", "TRANSFERENCIA PARA ALAGOINHAS", "TRANSFERENCIA PARA JACOBINA", "TRANSFERENCIA PARA SANTO ANTONIO DE JESUS"
]
rotas = [
    "001", "002", "003", "004", "005", "008"
]
status = [
    "Direcionado" , "Recusado", "Retirado", "Finalizado", "Ocorrencia"
]
morotista = [
    
]
tipo = "Rota"
class FirebaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("RTA controler")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout(self.central_widget)
        
        self.layout_base = QHBoxLayout()
        self.base_label = QLabel("Região de destino:")
        self.layout_base.addWidget(self.base_label)
        self.base_combo_box = QComboBox()
        self.base_combo_box.addItems(base)
        self.layout_base.addWidget(self.base_combo_box)
        layout.addLayout(self.layout_base)
        self.base_combo_box.currentIndexChanged.connect(self.on_base_selected)
        
        self.layout_cidade = QHBoxLayout()
        self.cidade_label = QLabel("Cidade:")
        self.layout_cidade.addWidget(self.cidade_label)
        self.combo_box = QComboBox()
        self.combo_box.addItems(rotas)
        self.layout_cidade.addWidget(self.combo_box)
        layout.addLayout(self.layout_cidade)
        self.combo_box.currentIndexChanged.connect(self.on_cidade_selected)

        self.label = QLabel("Documentos na coleção:")
        layout.addWidget(self.label)

        self.search_layout = QHBoxLayout()
        layout.addLayout(self.search_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o ID do documento ou uma chave de pesquisa...")
        self.search_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Pesquisar")
        self.search_button.clicked.connect(self.search_documents)
        self.search_layout.addWidget(self.search_button)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.list_widget)

        self.delete_button = QPushButton("Deletar Documentos Selecionados")
        self.delete_button.clicked.connect(self.delete_documents)
        layout.addWidget(self.delete_button)

        self.layout_entregador = QHBoxLayout()
        self.entregador_label = QLabel("Motoristas:")
        self.layout_entregador.addWidget(self.entregador_label)
        self.combo_box_entregador = QComboBox()
        self.layout_entregador.addWidget(self.combo_box_entregador)
        layout.addLayout(self.layout_entregador)
        self.combo_box_entregador.currentIndexChanged.connect(self.on_cidade_selected)
        
        tempo_layout_base = QHBoxLayout()
        layout.addLayout(tempo_layout_base)
        
        self.direciona_button = QPushButton("Distribuir para motoristas")
        self.direciona_button.clicked.connect(self.direciona_pacotes)
        tempo_layout_base.addWidget(self.direciona_button)
        
        self.libera_button = QPushButton("Liberar ocorrência")
        self.libera_button.clicked.connect(self.liberar)
        tempo_layout_base.addWidget(self.libera_button)

        self.remover_direciona_button = QPushButton("Remover do motorista")
        self.remover_direciona_button.clicked.connect(self.remover_direciona_pacotes)
        tempo_layout_base.addWidget(self.remover_direciona_button)

        # Novo campo de texto para inserir o doc_id
        self.doc_id_input = QLineEdit()
        self.doc_id_input.setPlaceholderText("Digite / Bipe o RTX e pressione Enter")
        self.doc_id_input.returnPressed.connect(self.direciona_pacote_por_doc_id)
        layout.addWidget(self.doc_id_input)

        self.ceos_label_layout = QHBoxLayout()
        self.Ceos = QLabel("Github.com/dudurtg2 - Versão Prototipo 0.0.1.3")
        self.Ceos.setStyleSheet("color: gray;")
        self.ceos_label_layout.addWidget(self.Ceos)
        self.ceos_label_layout.setAlignment(Qt.AlignRight)
        layout.addLayout(self.ceos_label_layout)
        
        self.remover_direciona_button.setEnabled(False)
        self.libera_button.setEnabled(False)
        self.direciona_button.setEnabled(True)
        self.load_documents()
        self.users()
    
    def users(self):
        users_ref = db.collection('usuarios')
        documents = users_ref.stream()
        for doc in documents:
            morotista.append(f"{doc.to_dict()['nome']}")
        self.combo_box_entregador.addItems(morotista)


    def on_cidade_selected(self, index):
        global tipo
        if tipo == "Status":
            self.remove_documents()
        else:
            self.load_documents()

    def on_base_selected(self, index):
        global tipo  
        base_selecionada = self.base_combo_box.currentText()
        self.remover_direciona_button.setEnabled(False)
        self.libera_button.setEnabled(False)
        self.direciona_button.setEnabled(True)
        if base_selecionada == "FEIRA DE SANTANA":
            self.atualizar_cidades(sorted(cidades_feira))
            self.remover_direciona_button.setEnabled(False)
            self.libera_button.setEnabled(False)
            self.direciona_button.setEnabled(True)
            self.cidade_label.setText("Cidade:")
            tipo = "Local" 
        elif base_selecionada == "TRANSFERENCIA":
            self.atualizar_cidades(sorted(tranferencia))
            self.cidade_label.setText("Local:")
            self.remover_direciona_button.setEnabled(False)
            self.libera_button.setEnabled(False)
            self.direciona_button.setEnabled(True)
            tipo = "Local"
        elif base_selecionada == "ROTAS":
            self.atualizar_cidades(rotas)
            self.remover_direciona_button.setEnabled(False)
            self.libera_button.setEnabled(False)
            self.direciona_button.setEnabled(True)
            self.cidade_label.setText("Rota:")
            tipo = "Rota"
        elif base_selecionada == "DIRECIONADO":
            self.atualizar_cidades(status)
            self.remover_direciona_button.setEnabled(True)
            self.libera_button.setEnabled(False)
            self.direciona_button.setEnabled(False)
            self.cidade_label.setText("Status:")
            tipo = "Status"
        self.on_cidade_selected(self)

    def atualizar_cidades(self, lista_cidades):
        global tipo  
        self.combo_box.clear()
        self.combo_box.addItems(lista_cidades)
    
        
    def load_documents(self):
        global tipo  
        self.list_widget.clear()
        query_text = self.combo_box.currentText()
        
        if query_text:
            collection_ref = db.collection('bipagem')
            query_ref = collection_ref.where(tipo, '==', query_text).where('Status', '==', 'aguardando')
            docs = query_ref.stream()
        else:
            collection_ref = db.collection('bipagem')
            docs = collection_ref.where('Status', '==', 'aguardando').stream()
        
        for doc in docs:
            data = doc.to_dict()
            quantidade = data.get('Quantidade', 'Campo não encontrado')
            cidade = data.get('Local', 'Campo não encontrado')
            hora_dia = data.get('Hora_e_Dia', 'Campo não encontrado')
            campo_valor = f"Quantidade: {quantidade}, Local: {cidade}, Data e Hora: {hora_dia}"
            self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")

    def documents(self):
        global tipo  
        self.list_widget.clear()
    
        collection_ref = db.collection('bipagem')
        docs = collection_ref.stream()
        
        for doc in docs:
            data = doc.to_dict()
            quantidade = data.get('Quantidade', 'Campo não encontrado')
            cidade = data.get('Local', 'Campo não encontrado')
            hora_dia = data.get('Hora_e_Dia', 'Campo não encontrado')
            campo_valor = f"Quantidade: {quantidade}, Local: {cidade}, Data e Hora: {hora_dia}"
            self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")
            
    def liberar(self):

        selected_items = self.list_widget.selectedItems()
        if selected_items:
            motorista = self.combo_box_entregador.currentText()

            motorista_ref = db.collection('usuarios').where('nome', '==', motorista).limit(1).stream()
            motorista_doc = next(motorista_ref, None)

            if motorista_doc:
                motorista_uid = motorista_doc.id
                doc_ids = [item.text().split(',')[0].split(':')[1].strip() for item in selected_items]

                for doc_id in doc_ids:
                
                    db.collection('rota').document(motorista_uid).collection('pacotes').document(doc_id).update({
                        'Status': "Finalizado"
                    })


            global tipo
            if tipo == "Status":
                self.remove_documents()  # Implemente sua lógica para remover documentos conforme necessário
            else:
                self.load_documents()  # Método para recarregar documentos na lista

        else:
            # Tratar caso nenhum item esteja selecionado
            print("Nenhum documento selecionado para liberar.")
    
    
    def remove_documents(self):
        global tipo
        query_text = self.combo_box.currentText() 
        self.list_widget.clear()
        motorista = self.combo_box_entregador.currentText()
        motorista_ref = db.collection('usuarios').where('nome', '==', motorista).limit(1).stream()
        motorista_doc = next(motorista_ref, None)
        motorista_uid = motorista_doc.id
        if query_text == "Direcionado":
            self.remover_direciona_button.setEnabled(True)
            self.libera_button.setEnabled(False)
            self.direciona_button.setEnabled(False)
            collection_ref = db.collection('direcionado').document(motorista_uid).collection('pacotes')
            docs = collection_ref.where('Status', '==', 'aguardando').stream()
            for doc in docs:
                data = doc.to_dict()
                quantidade = data.get('Quantidade', 'Campo não encontrado')
                cidade = data.get('Local', 'Campo não encontrado')
                hora_dia = data.get('Hora_e_Dia', 'Campo não encontrado')
                campo_valor = f"Quantidade: {quantidade}, Local: {cidade}, Data e Hora: {hora_dia}"
                self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")
        elif query_text == "Ocorrencia":
            self.remover_direciona_button.setEnabled(False)
            self.libera_button.setEnabled(True)
            self.direciona_button.setEnabled(False)
            collection_ref = db.collection('rota').document(motorista_uid).collection('pacotes')
            docs = collection_ref.where('Status', '==', query_text).stream()
            for doc in docs:
                data = doc.to_dict()
                ocorrencia = data.get('Ocorrencia', 'Campo não encontrado')
                cidade = data.get('Local', 'Campo não encontrado')
                hora_dia = data.get('Hora_e_Dia', 'Campo não encontrado')
                campo_valor = f"Local: {cidade}, Data e Hora: {hora_dia}\nOcorrencia: "
                campo_valor += '\n'.join(textwrap.wrap(ocorrencia, width=80))
                self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")
        else:
            if query_text == "Finalizado":
                self.remover_direciona_button.setEnabled(False)
                self.libera_button.setEnabled(False)
                self.direciona_button.setEnabled(False)
            else:
                self.remover_direciona_button.setEnabled(True)
                self.libera_button.setEnabled(False)
                self.direciona_button.setEnabled(False)
            collection_ref = db.collection('rota').document(motorista_uid).collection('pacotes')
            docs = collection_ref.where('Status', '==', query_text).stream()
            for doc in docs:
                data = doc.to_dict()
                quantidade = data.get('Quantidade', 'Campo não encontrado')
                cidade = data.get('Local', 'Campo não encontrado')
                hora_dia = data.get('Hora_e_Dia', 'Campo não encontrado')
                campo_valor = f"Quantidade: {quantidade}, Local: {cidade}, Data e Hora: {hora_dia}"
                self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")

    def search_documents(self):
        global tipo  
        query_text = self.search_input.text()
        self.list_widget.clear()

        if query_text:
            try:
                doc_ref = db.collection('bipagem').document(query_text)
                doc = doc_ref.get()

                if doc.exists:
                    data = doc.to_dict()
                    quantidade = data.get('Quantidade', 'Campo não encontrado')
                    cidade = data.get('Local', 'Campo não encontrado')
                    hora_dia = data.get('Hora_e_Dia', 'Campo não encontrado')
                    campo_valor = f"Quantidade: {quantidade}, Local: {cidade}, Data e Hora: {hora_dia}"
                    self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")
                else:
                    print(f"Documento com ID {query_text} não encontrado.")
            except Exception as e:
                print(f"Erro ao buscar documento: {e}")
        else:
            self.documents()
    def direciona_pacote_por_doc_id(self):
        doc_id = self.doc_id_input.text()
        if doc_id:
            motorista = self.combo_box_entregador.currentText()
            motorista_ref = db.collection('usuarios').where('nome', '==', motorista).limit(1).stream()
            motorista_doc = next(motorista_ref, None)
            if motorista_doc:
                motorista_uid = motorista_doc.id
                try:    
                    original_doc_ref = db.collection('bipagem').document(doc_id)
                    original_doc_snapshot = original_doc_ref.get()

                    if not original_doc_snapshot.exists:
                        winsound.Beep(855, 350)
                        self.doc_id_input.clear() 
                        return

                    original_doc_data = original_doc_snapshot.to_dict()
                    new_doc_ref = db.collection('direcionado').document(motorista_uid).collection('pacotes').document(doc_id)
                    new_doc_ref.set(original_doc_data)
                    db.collection('direcionado').document(motorista_uid).collection('pacotes').document(doc_id).update({'Motorista': motorista_uid})
                    original_doc_ref.delete()
                    winsound.Beep(1755, 150)
                    self.doc_id_input.clear() 
                    global tipo
                    if tipo == "Status":
                        self.remove_documents()
                    else:
                        self.load_documents()

                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao direcionar pacotes: {e}")
            else:
                QMessageBox.warning(self, "Atenção", "Motorista não encontrado.")
        else:
            QMessageBox.warning(self, "Atenção", "Por favor, insira um ID de documento para direcionar.")
        self.doc_id_input.clear()
    def direciona_pacotes(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            motorista = self.combo_box_entregador.currentText()
            motorista_ref = db.collection('usuarios').where('nome', '==', motorista).limit(1).stream()
            motorista_doc = next(motorista_ref, None)
            if motorista_doc:
                motorista_uid = motorista_doc.id
                doc_ids = [item.text().split(',')[0].split(':')[1].strip() for item in selected_items]
                try:
                    for doc_id in doc_ids:
                        original_doc_ref = db.collection('bipagem').document(doc_id)
                        original_doc_snapshot = original_doc_ref.get()
                        if original_doc_snapshot.exists:
                            original_doc_data = original_doc_snapshot.to_dict()
                            new_doc_ref = db.collection('direcionado').document(motorista_uid).collection('pacotes').document(doc_id)
                            new_doc_ref.set(original_doc_data)
                            db.collection('direcionado').document(motorista_uid).collection('pacotes').document(doc_id).update({'Motorista': motorista_uid})
                            original_doc_ref.delete()

                    QMessageBox.information(self, "Sucesso", f"Pacotes direcionados com sucesso para {motorista}.")
                    global tipo
                    if tipo == "Status":
                        self.remove_documents()
                    else:
                        self.load_documents()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao direcionar pacotes: {e}")
            else:
                QMessageBox.warning(self, "Atenção", "Motorista não encontrado.")
        else:
            QMessageBox.warning(self, "Atenção", "Por favor, selecione pelo menos um pacote para direcionar.")

    def remover_direciona_pacotes(self):
        global tipo
        if tipo == "Status":
            local = "rota"
        else:
            local = "direcionado"
        if self.combo_box.currentText() == "Direcionado":
            local = "direcionado"
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            motorista = self.combo_box_entregador.currentText()
            motorista_ref = db.collection('usuarios').where('nome', '==', motorista).limit(1).stream()
            motorista_doc = next(motorista_ref, None)
            if motorista_doc:
                motorista_uid = motorista_doc.id
                doc_ids = [item.text().split(',')[0].split(':')[1].strip() for item in selected_items]
                try:
                    for doc_id in doc_ids:
                        original_doc_ref = db.collection(local).document(motorista_uid).collection('pacotes').document(doc_id)
                        original_doc_snapshot = original_doc_ref.get()
                        if original_doc_snapshot.exists:
                            original_doc_data = original_doc_snapshot.to_dict()
                            new_doc_ref = db.collection('bipagem').document(doc_id) 
                            new_doc_ref.set(original_doc_data)
                            db.collection('bipagem').document(doc_id).update({'Motorista': "aguardando"})
                            original_doc_ref.delete()

                    QMessageBox.information(self, "Sucesso", f"Pacotes removidos com sucesso de {motorista}.")
                    if tipo == "Status":
                        self.remove_documents()
                    else:
                        self.load_documents()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao remover pacotes: {e}")
            else:
                QMessageBox.warning(self, "Atenção", "Motorista não encontrado.")
        else:
            QMessageBox.warning(self, "Atenção", "Por favor, selecione pelo menos um pacote para remover.")
            

    def delete_documents(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            doc_ids = [item.text().split(',')[0].split(':')[1].strip() for item in selected_items]
            try:
                for doc_id in doc_ids:
                    db.collection('bipagem').document(doc_id).delete()
                QMessageBox.information(self, "Sucesso", f"Documentos deletados com sucesso.")
                global tipo
                if tipo == "Status":
                    self.remove_documents()
                else:
                    self.load_documents()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao deletar os documentos: {e}")
        else:
            QMessageBox.warning(self, "Atenção", "Por favor, selecione pelo menos um documento para deletar.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FirebaseApp()
    window.show()
    sys.exit(app.exec_())
