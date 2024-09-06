import sys
import winsound
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QComboBox,
)
import firebase_admin
from firebase_admin import credentials, firestore
from PyQt5.QtCore import Qt
import json
import textwrap


with open("service-account-credentials.json") as json_file:
    data = json.load(json_file)
    firebase_credentials = data["firebase"]

cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

json_file_path = "Data/data.json"

with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

rota_01 = data.get("rota_01", [])
rota_02 = data.get("rota_02", [])
rota_03 = data.get("rota_03", [])
rota_04 = data.get("rota_04", [])
rota_05 = data.get("rota_05", [])
rota_06 = data.get("rota_06", [])
rota_07 = data.get("rota_07", [])

cidades_algoinhas = data.get("cidades_algoinhas", [])
cidades_jacobina = data.get("cidades_jacobina", [])
cidades_saj = data.get("cidades_saj", [])
cidades_feira = rota_01 + rota_02 + rota_03 + rota_04 + rota_05 + rota_06 + rota_07

barrios_saj = data.get("barrios_saj", [])
barrios_feria = data.get("barrios_feria", [])
barrios_alagoinhas = data.get("barrios_alagoinhas", [])
barrios_jacobina = data.get("barrios_jacobina", [])

devolucaos = data.get("devolucaos", [])
empresa = data.get("empresa", [])
base = ["ROTAS", "FEIRA DE SANTANA", "TRANSFERENCIA", "DIRECIONADO"]
tranferencia = data.get("tranferencia", [])

allLocate = (
    barrios_feria
    + barrios_alagoinhas
    + barrios_jacobina
    + cidades_feira
    + cidades_algoinhas
    + cidades_jacobina
    + cidades_saj
    + barrios_saj
    + devolucaos
    + tranferencia
)

rota_dict = {city: "001" for city in rota_01}
rota_dict.update({city: "002" for city in rota_02})
rota_dict.update({city: "003" for city in rota_03})
rota_dict.update({city: "004" for city in rota_04})
rota_dict.update({city: "005" for city in rota_05})
rota_dict.update({city: "006" for city in rota_06})
rota_dict.update({city: "008" for city in tranferencia})

cidades = cidades_feira

rotas = ["001", "002", "003", "004", "005", "006", "008"]
status = ["Direcionado", "Recusado", "Retirado", "Finalizado", "Ocorrencia"]
campo = ["Direcionar", "Roterizar"]
morotista = []
tipo = "Rota"


class FirebaseApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RTA controler")
        self.setGeometry(100, 100, 800, 600)

        # Central Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Base Selection
        self.layout_base = QHBoxLayout()
        self.base_label = QLabel("Região de destino:")
        self.layout_base.addWidget(self.base_label)
        self.base_combo_box = QComboBox()
        self.base_combo_box.addItems(base)
        self.layout_base.addWidget(self.base_combo_box)
        layout.addLayout(self.layout_base)
        self.base_combo_box.currentIndexChanged.connect(self.on_base_selected)

        # City Selection
        self.layout_cidade = QHBoxLayout()
        self.cidade_label = QLabel("Cidade:")
        self.layout_cidade.addWidget(self.cidade_label)
        self.combo_box = QComboBox()
        self.combo_box.addItems(rotas)
        self.layout_cidade.addWidget(self.combo_box)
        layout.addLayout(self.layout_cidade)
        self.combo_box.currentIndexChanged.connect(self.on_cidade_selected)

        # Document Search
        self.label = QLabel("Documentos na coleção:")
        layout.addWidget(self.label)
        self.search_layout = QHBoxLayout()
        layout.addLayout(self.search_layout)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Digite o ID do documento ou uma chave de pesquisa..."
        )
        self.search_layout.addWidget(self.search_input)
        self.search_button = QPushButton("Pesquisar")
        self.search_button.clicked.connect(self.search_documents)
        self.delete_button = QPushButton("Deletar selecionados")
        self.delete_button.setStyleSheet("color: red;")
        self.delete_button.clicked.connect(self.delete_documents)
        self.search_layout.addWidget(self.search_button)
        self.search_layout.addWidget(self.delete_button)

        # Document List
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.list_widget)

        # Delivery Details
        self.layout_entregador = QHBoxLayout()
        self.Tipo = QLabel("Tipo:")
        self.layout_entregador.addWidget(self.Tipo)
        self.combo_box_Tipo = QComboBox()
        self.layout_entregador.addWidget(self.combo_box_Tipo)
        self.campo_label = QLabel("Campo de bipagem:")
        self.layout_entregador.addWidget(self.campo_label)
        self.doc_id_input = QLineEdit()
        self.doc_id_input.setPlaceholderText("Digite ou bipe o codigo de ficha.")
        self.doc_id_input.returnPressed.connect(self.direciona_pacote_por_doc_id)
        self.layout_entregador.addWidget(self.doc_id_input)
        self.entregador_label = QLabel("Motoristas:")
        self.layout_entregador.addWidget(self.entregador_label)
        self.combo_box_entregador = QComboBox()
        self.layout_entregador.addWidget(self.combo_box_entregador)
        layout.addLayout(self.layout_entregador)
        self.combo_box_entregador.currentIndexChanged.connect(self.on_cidade_selected)

        # Buttons
        tempo_layout_base = QHBoxLayout()
        layout.addLayout(tempo_layout_base)
        self.direciona_button = QPushButton("Distribuir para motoristas")
        self.direciona_button.clicked.connect(self.direciona_pacotes)
        tempo_layout_base.addWidget(self.direciona_button)
        self.libera_button = QPushButton("Liberar ocorrência")
        self.libera_button.clicked.connect(self.liberar)
        tempo_layout_base.addWidget(self.libera_button)
        self.remover_direciona_button = QPushButton("Remover do motorista")
        self.remover_direciona_button.setStyleSheet("color: red;")
        self.remover_direciona_button.clicked.connect(self.remover_direciona_pacotes)
        tempo_layout_base.addWidget(self.remover_direciona_button)

        # Footer
        self.ceos_label_layout = QHBoxLayout()
        self.Ceos = QLabel("Github.com/dudurtg2 - Versão Prototipo 0.0.1.3")
        self.Ceos.setStyleSheet("color: gray;")
        self.ceos_label_layout.addWidget(self.Ceos)
        self.ceos_label_layout.setAlignment(Qt.AlignRight)
        layout.addLayout(self.ceos_label_layout)

        # Initial State
        self.remover_direciona_button.setEnabled(False)
        self.libera_button.setEnabled(False)
        self.direciona_button.setEnabled(True)
        self.load_documents()
        self.users()

    def users(self):
        users_ref = db.collection("usuarios")
        documents = users_ref.stream()
        for doc in documents:
            morotista.append(f"{doc.to_dict()['nome']}")
        self.combo_box_entregador.addItems(morotista)
        self.combo_box_Tipo.addItems(campo)

    def on_cidade_selected(self, index):
        global tipo
        if tipo == "Status":
            if self.combo_box.currentText() == "Finalizado":
                self.load_documents()
            else:
                self.remove_documents()
        else:
            self.load_documents()

    def on_base_selected(self, index):
        base_selecionada = self.base_combo_box.currentText()
        settings = {
            "FEIRA DE SANTANA": {
                "cities": sorted(cidades_feira),
                "label": "Cidade:",
                "tipo": "Local",
                "direciona_enabled": True,
                "remover_direciona_enabled": False,
                "libera_enabled": False,
            },
            "TRANSFERENCIA": {
                "cities": sorted(tranferencia),
                "label": "Local:",
                "tipo": "Local",
                "direciona_enabled": True,
                "remover_direciona_enabled": False,
                "libera_enabled": False,
            },
            "ROTAS": {
                "cities": rotas,
                "label": "Rota:",
                "tipo": "Rota",
                "direciona_enabled": True,
                "remover_direciona_enabled": False,
                "libera_enabled": False,
            },
            "DIRECIONADO": {
                "cities": status,
                "label": "Status:",
                "tipo": "Status",
                "direciona_enabled": False,
                "remover_direciona_enabled": True,
                "libera_enabled": False,
            },
        }
        settings_for_base = settings.get(base_selecionada, {})

        self.atualizar_cidades(settings_for_base.get("cities", []))
        self.cidade_label.setText(settings_for_base.get("label", ""))
        self.direciona_button.setEnabled(
            settings_for_base.get("direciona_enabled", False)
        )
        self.remover_direciona_button.setEnabled(
            settings_for_base.get("remover_direciona_enabled", False)
        )
        self.libera_button.setEnabled(settings_for_base.get("libera_enabled", False))
        global tipo
        tipo = settings_for_base.get("tipo", "")

        self.on_cidade_selected(self)

    def atualizar_cidades(self, lista_cidades):
        global tipo
        self.combo_box.clear()
        self.combo_box.addItems(lista_cidades)

    def search_documents(self):
        query_text = self.search_input.text()
        self.search_input.clear()
        self.list_widget.clear()

        if query_text:
            try:
                usuarios_collection = db.collection("usuarios")
                motorista_docs = usuarios_collection.stream()
                motorista_ids = [motorista_doc.id for motorista_doc in motorista_docs]

                collections = [
                    db.collection("bipagem"),
                    db.collection("rota"),
                    db.collection("direcionado"),
                ]

                found = False
                for collection in collections:
                    if collection.id in ["rota", "direcionado"]:
                        for motorista_id in motorista_ids:
                            pacotes_collection = collection.document(
                                motorista_id
                            ).collection("pacotes")
                            doc_ref = pacotes_collection.document(query_text)
                            doc = doc_ref.get()
                            if doc.exists:
                                data = doc.to_dict()
                                quantidade = data.get(
                                    "Quantidade", "Campo não encontrado"
                                )
                                cidade = data.get("Local", "Campo não encontrado")
                                hora_dia = data.get(
                                    "Hora_e_Dia", "Campo não encontrado"
                                )
                                status = data.get("Status", "Campo não encontrado")
                                motorista_doc = usuarios_collection.document(
                                    motorista_id
                                ).get()
                                motorista_nome = motorista_doc.to_dict().get(
                                    "nome", "Nome não encontrado"
                                )
                                campo_valor = f"Local: {cidade}  \n{quantidade}\nData e Hora: {hora_dia}\nStatus: {status}\nMotorista: {motorista_nome}"
                                self.list_widget.addItem(
                                    f"ID: {doc.id} \n{campo_valor}"
                                )
                                found = True
                                break
                    else:
                        doc_ref = collection.document(query_text)
                        doc = doc_ref.get()
                        if doc.exists:
                            data = doc.to_dict()
                            quantidade = data.get("Quantidade", "Campo não encontrado")
                            cidade = data.get("Local", "Campo não encontrado")
                            hora_dia = data.get("Hora_e_Dia", "Campo não encontrado")
                            campo_valor = f"     Local: {cidade}  \n{quantidade}         Data e Hora: {hora_dia}\n"
                            self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")
                            found = True
                            break

                if not found:
                    self.list_widget.addItem(
                        "Documento não encontrado em nenhuma coleção."
                    )
            except Exception as e:
                print(f"Erro ao buscar documento: {e}")
        else:
            self.load_documents()

    def load_documents(self):
        global tipo
        self.list_widget.clear()
        query_text = self.combo_box.currentText()
        motorista = self.combo_box_entregador.currentText()
        motorista_ref = (
            db.collection("usuarios").where("nome", "==", motorista).limit(1).stream()
        )
        motorista_doc = next(motorista_ref, None)

        if self.combo_box.currentText() == "Finalizado":
            motorista_uid = motorista_doc.id
            doc_ref = db.collection("finalizados").document(motorista_uid)
            doc = doc_ref.get()
            data = doc.to_dict()
            for key, value in data.items():
                self.list_widget.addItem(f"{key}: {value}")

        if self.combo_box.currentText() == "Retirado":
            motorista_uid = motorista_doc.id
            collection_ref = (
                db.collection("rota").document(motorista_uid).collection("pacotes")
            )
            docs = collection_ref.stream()
            for doc in docs:
                data = doc.to_dict()
                quantidade = data.get("Quantidade", "Campo não encontrado")
                cidade = data.get("Local", "Campo não encontrado")
                hora_dia = data.get("Hora_e_Dia", "Campo não encontrado")
                campo_valor = (
                    f"Local: {cidade} \n{quantidade}         Data e Hora: {hora_dia}\n"
                )
                self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")

        elif query_text:
            collection_ref = db.collection("bipagem")
            query_ref = collection_ref.where(tipo, "==", query_text)
            docs = query_ref.stream()

            for doc in docs:
                data = doc.to_dict()
                quantidade = data.get("Quantidade", "Campo não encontrado")
                cidade = data.get("Local", "Campo não encontrado")
                hora_dia = data.get("Hora_e_Dia", "Campo não encontrado")
                campo_valor = (
                    f"Local: {cidade} \n{quantidade}         Data e Hora: {hora_dia}\n"
                )
                self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")

        else:
            collection_ref = db.collection("bipagem")
            docs = collection_ref.where("Status", "==", "aguardando").stream()

            for doc in docs:
                data = doc.to_dict()
                quantidade = data.get("Quantidade", "Campo não encontrado")
                cidade = data.get("Local", "Campo não encontrado")
                hora_dia = data.get("Hora_e_Dia", "Campo não encontrado")
                campo_valor = (
                    f"Local: {cidade} \n{quantidade}         Data e Hora: {hora_dia}\n"
                )
                self.list_widget.addItem(f"ID: {doc.id}, {campo_valor}")

    def liberar(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            motorista = self.combo_box_entregador.currentText()
            motorista_ref = (
                db.collection("usuarios")
                .where("nome", "==", motorista)
                .limit(1)
                .stream()
            )
            motorista_doc = next(motorista_ref, None)
            if motorista_doc:
                motorista_uid = motorista_doc.id
                doc_ids = [
                    item.text().split(",")[0].split(":")[1].strip()
                    for item in selected_items
                ]
                for doc_id in doc_ids:
                    db.collection("rota").document(motorista_uid).collection(
                        "pacotes"
                    ).document(doc_id).update({"Status": "Finalizado"})
            global tipo
            if tipo == "Status":
                self.remove_documents()
            else:
                self.load_documents()

    def remove_documents(self):

        global tipo
        query_text = self.combo_box.currentText()
        self.list_widget.clear()
        motorista = self.combo_box_entregador.currentText()

        motorista_ref = (
            db.collection("usuarios").where("nome", "==", motorista).limit(1).stream()
        )
        motorista_doc = next(motorista_ref, None)

        if not motorista_doc:
            self.list_widget.addItem("Motorista não encontrado.")
            return

        motorista_uid = motorista_doc.id
        status_map = {
            "Direcionado": {
                "button_enabled": (True, False, False),
                "collection": "direcionado",
                "filter": "aguardando",
            },
            "Ocorrencia": {
                "button_enabled": (False, True, False),
                "collection": "rota",
                "filter": "Ocorrencia",
            },
            "Finalizado": {
                "button_enabled": (False, False, False),
                "collection": "rota",
                "filter": "Finalizado",
            },
        }

        def adicionar_documento(data, doc_id):

            cidade = data.get("Local", "Campo não encontrado")
            hora_dia = data.get("Hora_e_Dia", "Campo não encontrado")
            quantidade = data.get("Quantidade", "Campo não encontrado")
            ocorrencia = data.get("Ocorrencia", "Campo não encontrado")

            campo_valor = f"Local: {cidade}  \n{quantidade if query_text != 'Ocorrencia' else ''}         Data e Hora: {hora_dia}\n"
            if query_text == "Ocorrencia":
                campo_valor += "\n".join(textwrap.wrap(ocorrencia, width=80))

            self.list_widget.addItem(f"ID: {doc_id}, {campo_valor}")

        if query_text in status_map:
            buttons_state = status_map[query_text]["button_enabled"]
            self.remover_direciona_button.setEnabled(buttons_state[0])
            self.libera_button.setEnabled(buttons_state[1])
            self.direciona_button.setEnabled(buttons_state[2])

            collection_ref = (
                db.collection(status_map[query_text]["collection"])
                .document(motorista_uid)
                .collection("pacotes")
            )
            docs = collection_ref.where(
                "Status", "==", status_map[query_text]["filter"]
            ).stream()

            for doc in docs:
                data = doc.to_dict()
                adicionar_documento(data, doc.id)

        else:
            self.remover_direciona_button.setEnabled(True)
            self.libera_button.setEnabled(False)
            self.direciona_button.setEnabled(False)

            collection_ref = (
                db.collection("rota").document(motorista_uid).collection("pacotes")
            )
            docs = collection_ref.where("Status", "==", query_text).stream()

            for doc in docs:
                data = doc.to_dict()
                adicionar_documento(data, doc.id)

    def direciona_pacote_por_doc_id(self):
        doc_id = self.doc_id_input.text()
        if doc_id:
            motorista = self.combo_box_entregador.currentText()
            motorista_ref = (
                db.collection("usuarios")
                .where("nome", "==", motorista)
                .limit(1)
                .stream()
            )
            motorista_doc = next(motorista_ref, None)
            if motorista_doc:
                motorista_uid = motorista_doc.id
                try:
                    original_doc_ref = db.collection("bipagem").document(doc_id)
                    original_doc_snapshot = original_doc_ref.get()

                    if not original_doc_snapshot.exists:
                        winsound.Beep(855, 350)
                        self.doc_id_input.clear()
                        return
                    original_doc_data = original_doc_snapshot.to_dict()
                    if self.combo_box_Tipo.currentText() == "Direcionar":
                        new_doc_ref = (
                            db.collection("rota")
                            .document(motorista_uid)
                            .collection("pacotes")
                            .document(doc_id)
                        )
                        new_doc_ref.set(original_doc_data)
                        db.collection("rota").document(motorista_uid).collection(
                            "pacotes"
                        ).document(doc_id).update({"Motorista": motorista_uid})
                        db.collection("rota").document(motorista_uid).collection(
                            "pacotes"
                        ).document(doc_id).update({"Status": "Retirado"})
                        original_doc_ref.delete()
                    else:
                        new_doc_ref = (
                            db.collection("direcionado")
                            .document(motorista_uid)
                            .collection("pacotes")
                            .document(doc_id)
                        )
                        new_doc_ref.set(original_doc_data)
                        db.collection("direcionado").document(motorista_uid).collection(
                            "pacotes"
                        ).document(doc_id).update({"Motorista": motorista_uid})
                        db.collection("direcionado").document(motorista_uid).collection(
                            "pacotes"
                        ).document(doc_id).update({"Status": "aguardando retirada"})
                        original_doc_ref.delete()
                    winsound.Beep(1755, 350)
                    self.doc_id_input.clear()
                    global tipo
                    if tipo == "Status":
                        self.remove_documents()
                    else:
                        self.load_documents()
                except Exception as e:
                    winsound.Beep(855, 450)
            else:
                winsound.Beep(855, 450)
        else:
            winsound.Beep(855, 450)
        self.doc_id_input.clear()

    def direciona_pacotes(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            motorista = self.combo_box_entregador.currentText()
            motorista_ref = (
                db.collection("usuarios")
                .where("nome", "==", motorista)
                .limit(1)
                .stream()
            )
            motorista_doc = next(motorista_ref, None)
            if motorista_doc:
                motorista_uid = motorista_doc.id
                doc_ids = [
                    item.text().split(",")[0].split(":")[1].strip()
                    for item in selected_items
                ]
                try:
                    for doc_id in doc_ids:
                        original_doc_ref = db.collection("bipagem").document(doc_id)
                        original_doc_snapshot = original_doc_ref.get()
                        if original_doc_snapshot.exists:
                            original_doc_data = original_doc_snapshot.to_dict()
                            new_doc_ref = (
                                db.collection("rota")
                                .document(motorista_uid)
                                .collection("pacotes")
                                .document(doc_id)
                            )
                            new_doc_ref.set(original_doc_data)
                            db.collection("rota").document(motorista_uid).collection(
                                "pacotes"
                            ).document(doc_id).update({"Motorista": motorista_uid})
                            db.collection("rota").document(motorista_uid).collection(
                                "pacotes"
                            ).document(doc_id).update({"Status": "Retirado"})
                            original_doc_ref.delete()

                    QMessageBox.information(
                        self,
                        "Sucesso",
                        f"Pacotes direcionados com sucesso para {motorista}.",
                    )
                    global tipo
                    if tipo == "Status":
                        self.remove_documents()
                    else:
                        self.load_documents()
                except Exception as e:
                    QMessageBox.critical(
                        self, "Erro", f"Erro ao direcionar pacotes: {e}"
                    )
            else:
                QMessageBox.warning(self, "Atenção", "Motorista não encontrado.")
        else:
            QMessageBox.warning(
                self,
                "Atenção",
                "Por favor, selecione pelo menos um pacote para direcionar.",
            )

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
            motorista_ref = (
                db.collection("usuarios")
                .where("nome", "==", motorista)
                .limit(1)
                .stream()
            )
            motorista_doc = next(motorista_ref, None)
            if motorista_doc:
                motorista_uid = motorista_doc.id
                doc_ids = [
                    item.text().split(",")[0].split(":")[1].strip()
                    for item in selected_items
                ]
                try:
                    for doc_id in doc_ids:
                        original_doc_ref = (
                            db.collection(local)
                            .document(motorista_uid)
                            .collection("pacotes")
                            .document(doc_id)
                        )
                        original_doc_snapshot = original_doc_ref.get()
                        if original_doc_snapshot.exists:
                            original_doc_data = original_doc_snapshot.to_dict()
                            new_doc_ref = db.collection("bipagem").document(doc_id)
                            new_doc_ref.set(original_doc_data)
                            db.collection("bipagem").document(doc_id).update(
                                {"Motorista": "aguardando"}
                            )
                            db.collection("bipagem").document(doc_id).update(
                                {"Status": "aguardando"}
                            )
                            original_doc_ref.delete()

                    QMessageBox.information(
                        self,
                        "Sucesso",
                        f"Pacotes removidos com sucesso de {motorista}.",
                    )
                    if tipo == "Status":
                        self.remove_documents()
                    else:
                        self.load_documents()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao remover pacotes: {e}")
            else:
                QMessageBox.warning(self, "Atenção", "Motorista não encontrado.")
        else:
            QMessageBox.warning(
                self,
                "Atenção",
                "Por favor, selecione pelo menos um pacote para remover.",
            )

    def delete_documents(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            doc_ids = [
                item.text().split(",")[0].split(":")[1].strip()
                for item in selected_items
            ]
            try:
                for doc_id in doc_ids:
                    db.collection("bipagem").document(doc_id).delete()
                QMessageBox.information(
                    self, "Sucesso", f"Documentos deletados com sucesso."
                )
                global tipo
                if tipo == "Status":
                    self.remove_documents()
                else:
                    self.load_documents()
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao deletar os documentos: {e}"
                )
        else:
            QMessageBox.warning(
                self,
                "Atenção",
                "Por favor, selecione pelo menos um documento para deletar.",
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FirebaseApp()
    window.show()
    sys.exit(app.exec_())
