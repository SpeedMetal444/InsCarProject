import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox, QMessageBox, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from app.patient_manager import (
    buscar_paciente,
    buscar_pacientes,
    agregar_paciente,
    obtener_pbs_vencidos,
    actualizar_paciente,
    eliminar_paciente,
    renovar_pbs
)
from datetime import date
import os
import configparser
import subprocess

if sys.platform == 'win32':
    myappid = 'com.inscar.gestiondepacientes.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configuración de la base de datos")
        self.setGeometry(100, 100, 400, 350)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        label_db_name = QLabel("Nombre de la base de datos:")
        label_db_name.setFont(QFont("Open Sans", 12))
        self.entry_db_name = QLineEdit()
        self.entry_db_name.setFixedHeight(30)
        self.entry_db_name.setPlaceholderText("Ingrese el nombre de la base de datos")
        self.entry_db_name.setText("inscar_db")

        label_db_host = QLabel("Host de la base de datos:")
        label_db_host.setFont(QFont("Open Sans", 12))
        self.entry_db_host = QLineEdit()
        self.entry_db_host.setFixedHeight(30)
        self.entry_db_host.setPlaceholderText("Ingrese el host de la base de datos")
        self.entry_db_host.setText("localhost")

        label_db_port = QLabel("Puerto de la base de datos:")
        label_db_port.setFont(QFont("Open Sans", 12))
        self.entry_db_port = QLineEdit()
        self.entry_db_port.setFixedHeight(30)
        self.entry_db_port.setPlaceholderText("Ingrese el puerto de la base de datos")
        self.entry_db_port.setText("5432")

        label_db_user = QLabel("Usuario de la base de datos:")
        label_db_user.setFont(QFont("Open Sans", 12))
        self.entry_db_user = QLineEdit()
        self.entry_db_user.setFixedHeight(30)
        self.entry_db_user.setPlaceholderText("Ingrese el usuario de la base de datos")

        label_db_password = QLabel("Contraseña de la base de datos:")
        label_db_password.setFont(QFont("Open Sans", 12))
        self.entry_db_password = QLineEdit()
        self.entry_db_password.setFixedHeight(30)
        self.entry_db_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry_db_password.setPlaceholderText("Ingrese la contraseña de la base de datos")

        self.check_save_credentials = QCheckBox("Guardar datos de inicio de sesión")

        self.check_create_db = QCheckBox("Crear base de datos")
        self.check_create_tables = QCheckBox("Crear tabla")

        button_login = QPushButton("Iniciar")
        button_login.setFixedHeight(30)
        button_login.clicked.connect(self.login)

        layout.addWidget(label_db_name)
        layout.addWidget(self.entry_db_name)
        layout.addWidget(label_db_host)
        layout.addWidget(self.entry_db_host)
        layout.addWidget(label_db_port)
        layout.addWidget(self.entry_db_port)
        layout.addWidget(label_db_user)
        layout.addWidget(self.entry_db_user)
        layout.addWidget(label_db_password)
        layout.addWidget(self.entry_db_password)
        layout.addWidget(self.check_save_credentials)
        layout.addWidget(self.check_create_db)
        layout.addWidget(self.check_create_tables)
        layout.addWidget(button_login)

        self.setLayout(layout)

        if getattr(sys, 'frozen', False):
            config_file = os.path.join(os.path.dirname(sys.executable), '_internal', 'config.ini')
        else:
            config_file = 'config.ini'

        if os.path.exists(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)
            self.entry_db_name.setText(config['database']['database'])
            self.entry_db_host.setText(config['database']['host'])
            self.entry_db_port.setText(config['database']['port'])
            if config['database']['user'] and config['database']['password']:
                self.entry_db_user.setText(config['database']['user'])
                self.entry_db_password.setText(config['database']['password'])
                self.check_save_credentials.setChecked(True)

    def login(self):
        db_name = self.entry_db_name.text()
        db_user = self.entry_db_user.text()
        db_password = self.entry_db_password.text()
        db_host = self.entry_db_host.text()
        db_port = self.entry_db_port.text()

        config = configparser.ConfigParser()
        config['database'] = {
            'database': db_name,
            'user': db_user if self.check_save_credentials.isChecked() else '',
            'password': db_password if self.check_save_credentials.isChecked() else '',
            'host': db_host,
            'port': db_port
        }

        if getattr(sys, 'frozen', False):
            config_file = os.path.join(os.path.dirname(sys.executable), '_internal', 'config.ini')
        else:
            config_file = 'config.ini'

        with open(config_file, 'w') as f:
            config.write(f)


        def ejecutar_script(nombre_script):
            directorios = ['./_internal', './']
            for directorio in directorios:
                ruta_script = os.path.join(directorio, nombre_script)
                if os.path.exists(ruta_script):
                    try:
                        resultado = subprocess.check_output(['python', ruta_script], stderr=subprocess.STDOUT, text=True)
                        return resultado.strip()
                    except subprocess.CalledProcessError as e:
                        raise Exception(f"Error al ejecutar {nombre_script}: {e.output.strip()}")
            raise Exception(f"No se encontró el script {nombre_script} en ninguno de los directorios")

        if self.check_create_db.isChecked():
            try:
                resultado = ejecutar_script('create_database.py')
                QMessageBox.information(self, "Base de datos", resultado)
            except Exception as e:
                QMessageBox.warning(self, "Error al crear la base de datos", str(e))

        if self.check_create_tables.isChecked():
            try:
                resultado = ejecutar_script('create_tables.py')
                QMessageBox.information(self, "Tabla", resultado)
            except Exception as e:
                QMessageBox.warning(self, "Error al crear la tabla", str(e))

        self.close()
        self.main_window = PacientesApp()
        self.main_window.container.show()

class PacientesApp(QTabWidget):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            QTabWidget {
                border: none;
            }
            QTabWidget::pane {
                border-top: none;
            }
        """)
        self.tab_buscar = QWidget()
        self.tab_registrar = QWidget()
        self.tab_pbs_vencido = QWidget()

        self.addTab(self.tab_buscar, "Buscar")
        self.addTab(self.tab_registrar, "Registrar paciente")
        self.addTab(self.tab_pbs_vencido, "PBS vencido")

        self.init_tab_buscar()
        self.init_tab_registrar()
        self.init_tab_pbs_vencido()

        self.link_cerrar_sesion = QLabel("<a href='#' style='color: grey; text-decoration: underline;'>Cerrar sesión</a>")
        self.link_cerrar_sesion.linkActivated.connect(self.cerrar_sesion)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self)
        main_layout.addWidget(self.link_cerrar_sesion)

        self.container = QWidget()
        self.container.setWindowTitle("InsCar - Gestión de Pacientes")
        self.container.setGeometry(100, 100, 500, 550)
        self.container.setLayout(main_layout)

    def cerrar_sesion(self):
        if getattr(sys, 'frozen', False):
            config_file = os.path.join(os.path.dirname(sys.executable), '_internal', 'config.ini')
        else:
            config_file = 'config.ini'

        config = configparser.ConfigParser()
        config.read(config_file)
        config['database']['user'] = ''
        config['database']['password'] = ''
        with open(config_file, 'w') as f:
            config.write(f)

        self.container.close()
        self.login_window = LoginWindow()
        self.login_window.show()

    def init_tab_buscar(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        label_dni = QLabel("Buscar por DNI:")
        label_dni.setFont(QFont("Open Sans", 12))
        self.entry_dni = QLineEdit()
        self.entry_dni.setFixedHeight(30)
        self.entry_dni.setPlaceholderText("Ingrese DNI")

        label_nombre = QLabel("Buscar por Nombre y Apellido:")
        label_nombre.setFont(QFont("Open Sans", 12))
        self.entry_nombre = QLineEdit()
        self.entry_nombre.setFixedHeight(30)
        self.entry_nombre.setPlaceholderText("Ingrese nombre")
        self.entry_apellido = QLineEdit()
        self.entry_apellido.setFixedHeight(30)
        self.entry_apellido.setPlaceholderText("Ingrese apellido")

        button_buscar = QPushButton("Buscar")
        button_buscar.setFixedHeight(30)
        button_buscar.clicked.connect(self.buscar_pacientes)

        self.list_resultado = QListWidget()
        self.list_resultado.setFixedHeight(150)
        self.list_resultado.itemSelectionChanged.connect(self.seleccionar_paciente)

        button_actualizar = QPushButton("Actualizar info de paciente")
        button_actualizar.setFixedHeight(30)
        button_actualizar.clicked.connect(self.actualizar_info_paciente)

        button_eliminar = QPushButton("Eliminar paciente")
        button_eliminar.setFixedHeight(30)
        button_eliminar.clicked.connect(self.eliminar_paciente_tab_buscar)

        button_renovar = QPushButton("Renovar PBS")
        button_renovar.setFixedHeight(30)
        button_renovar.clicked.connect(self.renovar_pbs)

        layout.addWidget(label_dni)
        layout.addWidget(self.entry_dni)
        layout.addWidget(label_nombre)
        layout.addWidget(self.entry_nombre)
        layout.addWidget(self.entry_apellido)
        layout.addWidget(button_buscar)
        layout.addWidget(self.list_resultado)
        layout.addWidget(button_actualizar)
        layout.addWidget(button_eliminar)
        layout.addWidget(button_renovar)

        self.tab_buscar.setLayout(layout)

    def init_tab_registrar(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        label_nombre = QLabel("Nombre:")
        label_nombre.setFont(QFont("Open Sans", 12))
        self.entry_reg_nombre = QLineEdit()
        self.entry_reg_nombre.setFixedHeight(30)
        self.entry_reg_nombre.setPlaceholderText("Ingrese nombre")

        label_apellido = QLabel("Apellido:")
        label_apellido.setFont(QFont("Open Sans", 12))
        self.entry_reg_apellido = QLineEdit()
        self.entry_reg_apellido.setFixedHeight(30)
        self.entry_reg_apellido.setPlaceholderText("Ingrese apellido")

        label_dni = QLabel("DNI:")
        label_dni.setFont(QFont("Open Sans", 12))
        self.entry_reg_dni = QLineEdit()
        self.entry_reg_dni.setFixedHeight(30)
        self.entry_reg_dni.setPlaceholderText("Ingrese DNI")

        label_direccion = QLabel("Dirección:")
        label_direccion.setFont(QFont("Open Sans", 12))
        self.entry_reg_direccion = QLineEdit()
        self.entry_reg_direccion.setFixedHeight(30)
        self.entry_reg_direccion.setPlaceholderText("Ingrese dirección")

        label_telefono = QLabel("Teléfono:")
        label_telefono.setFont(QFont("Open Sans", 12))
        self.entry_reg_telefono = QLineEdit()
        self.entry_reg_telefono.setFixedHeight(30)
        self.entry_reg_telefono.setPlaceholderText("Ingrese teléfono")

        self.check_pbs = QCheckBox("PBS (prepaga activa)")
        self.check_pbs.setFont(QFont("Open Sans", 12))

        button_registrar = QPushButton("Registrar paciente")
        button_registrar.setFixedHeight(30)
        button_registrar.clicked.connect(self.registrar_paciente)

        layout.addWidget(label_nombre)
        layout.addWidget(self.entry_reg_nombre)
        layout.addWidget(label_apellido)
        layout.addWidget(self.entry_reg_apellido)
        layout.addWidget(label_dni)
        layout.addWidget(self.entry_reg_dni)
        layout.addWidget(label_direccion)
        layout.addWidget(self.entry_reg_direccion)
        layout.addWidget(label_telefono)
        layout.addWidget(self.entry_reg_telefono)
        layout.addWidget(self.check_pbs)
        layout.addWidget(button_registrar)

        self.tab_registrar.setLayout(layout)

    def init_tab_pbs_vencido(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.entry_filtro = QLineEdit()
        self.entry_filtro.setPlaceholderText("Ingrese nombre, apellido o DNI")
        self.entry_filtro.textChanged.connect(self.filtrar_pbs_vencido)

        self.text_pbs_vencido = QTextEdit()
        self.text_pbs_vencido.setFixedHeight(300)

        button_actualizar = QPushButton("Actualizar lista")
        button_actualizar.setFixedHeight(30)
        button_actualizar.clicked.connect(self.mostrar_pbs_vencido)

        layout.addWidget(self.entry_filtro)
        layout.addWidget(self.text_pbs_vencido)
        layout.addWidget(button_actualizar)

        self.tab_pbs_vencido.setLayout(layout)

        self.pacientes_vencidos = []

    def filtrar_pbs_vencido(self):
        filtro = self.entry_filtro.text().lower()
        texto = ""
        for paciente in self.pacientes_vencidos:
             if filtro in str(paciente[1]).lower() or filtro in str(paciente[2]).lower() or filtro in str(paciente[3]).lower():
                texto += f"{paciente[1]} {paciente[2]} (DNI: {paciente[3]}) - Última renovación: {paciente[4]}\n"
        self.text_pbs_vencido.setText(texto)

    def eliminar_paciente_tab_buscar(self):
        dni = self.entry_dni.text().strip()
        paciente = buscar_paciente(dni=dni)
        if paciente:
            confirmacion = QMessageBox.question(self, "Confirmar eliminación", "¿Estás seguro de eliminar al paciente?")
            if confirmacion == QMessageBox.StandardButton.Yes:
                exito = eliminar_paciente(dni)
                if exito:
                    QMessageBox.information(self, "Paciente eliminado", "Paciente eliminado con éxito")
                    self.list_resultado.clear()
                else:
                    QMessageBox.critical(self, "Error", "Error al eliminar paciente")
        else:
            QMessageBox.critical(self, "Error", "Paciente no encontrado")

    def buscar_pacientes(self):
        dni = self.entry_dni.text().strip()
        nombre = self.entry_nombre.text().strip()
        apellido = self.entry_apellido.text().strip()

        self.list_resultado.clear()

        if dni:
            paciente = buscar_paciente(dni=dni)
            if paciente:
                resultado = f"""
ID: {paciente['id']}
Nombre: {paciente['nombre']} {paciente['apellido']}
DNI: {paciente['dni']}
Dirección: {paciente['direccion']}
Teléfono: {paciente['telefono']}
PBS: {'Sí' if paciente['pbs'] else 'No'}
Última renovación PBS: {paciente.get('pbs_ultima_renovacion', 'N/A')}
"""
                item = QListWidgetItem(resultado)
                item.setData(Qt.ItemDataRole.UserRole, paciente['dni'])
                self.list_resultado.addItem(item)
            else:
                self.list_resultado.addItem("Paciente no encontrado")
        elif nombre and apellido:
            pacientes = buscar_pacientes(nombre=nombre, apellido=apellido)
            if pacientes:
                for paciente in pacientes:
                    resultado = f"""
ID: {paciente['id']}
Nombre: {paciente['nombre']} {paciente['apellido']}
DNI: {paciente['dni']}
Dirección: {paciente['direccion']}
Teléfono: {paciente['telefono']}
PBS: {'Sí' if paciente['pbs'] else 'No'}
Última renovación PBS: {paciente.get('pbs_ultima_renovacion', 'N/A')}
"""
                    item = QListWidgetItem(resultado)
                    item.setData(Qt.ItemDataRole.UserRole, paciente['dni'])
                    self.list_resultado.addItem(item)
            else:
                self.list_resultado.addItem("Paciente no encontrado")
        else:
            QMessageBox.critical(self, "Error", "Por favor, complete los campos obligatorios")

    def seleccionar_paciente(self):
        selected_item = self.list_resultado.currentItem()
        if selected_item:
            dni = selected_item.data(Qt.ItemDataRole.UserRole)
            self.entry_dni.setText(dni)

    def registrar_paciente(self):
        nombre = self.entry_reg_nombre.text().strip()
        apellido = self.entry_reg_apellido.text().strip()
        dni = self.entry_reg_dni.text().strip()
        direccion = self.entry_reg_direccion.text().strip()
        telefono = self.entry_reg_telefono.text().strip()
        pbs = self.check_pbs.isChecked()

        if not (nombre and apellido and dni):
            QMessageBox.critical(self, "Error", "Por favor, complete todos los campos obligatorios")
            return

        paciente_existente = buscar_paciente(dni=dni)
        if paciente_existente:
            QMessageBox.information(self, "Paciente existente", "El paciente ya se encuentra registrado")
        else:
            exito = agregar_paciente(nombre, apellido, dni, direccion, telefono, pbs)
            if exito:
                QMessageBox.information(self, "Paciente registrado", "Paciente registrado con éxito")
                self.entry_reg_nombre.clear()
                self.entry_reg_apellido.clear()
                self.entry_reg_dni.clear()
                self.entry_reg_direccion.clear()
                self.entry_reg_telefono.clear()
                self.check_pbs.setChecked(False)
            else:
                QMessageBox.critical(self, "Error", "Error al registrar paciente")

    def renovar_pbs(self):
        dni = self.entry_dni.text().strip()
        paciente = buscar_paciente(dni=dni)
        if paciente:
            exito = renovar_pbs(dni)
            if exito:
                QMessageBox.information(self, "PBS renovado", "PBS renovado con éxito")
            else:
                QMessageBox.critical(self, "Error", "Error al renovar PBS")
        else:
            QMessageBox.critical(self, "Error", "Paciente no encontrado")

    def mostrar_pbs_vencido(self):
        self.pacientes_vencidos = obtener_pbs_vencidos()
        texto = ""
        for paciente in self.pacientes_vencidos:
            texto += f"{paciente[1]} {paciente[2]} (DNI: {paciente[3]}) - Última renovación: {paciente[4]}\n"
        self.text_pbs_vencido.setText(texto)
        self.entry_filtro.setText("")

    def actualizar_info_paciente(self):
        dni = self.entry_dni.text().strip()
        paciente = buscar_paciente(dni=dni)
        if paciente:
            # Actualizar paciente
            nombre = paciente['nombre']
            apellido = paciente['apellido']
            direccion = paciente['direccion']
            telefono = paciente['telefono']
            pbs = paciente['pbs']

            # Crear ventana de actualización
            ventana_actualizar = QWidget()
            layout = QVBoxLayout()

            label_nombre = QLabel("Nombre:")
            entry_nombre = QLineEdit(nombre)
            label_apellido = QLabel("Apellido:")
            entry_apellido = QLineEdit(apellido)
            label_direccion = QLabel("Dirección:")
            entry_direccion = QLineEdit(direccion)
            label_telefono = QLabel("Teléfono:")
            entry_telefono = QLineEdit(telefono)
            check_pbs = QCheckBox("PBS (prepaga activa)")
            check_pbs.setChecked(pbs)
            button_actualizar = QPushButton("Actualizar")

            layout.addWidget(label_nombre)
            layout.addWidget(entry_nombre)
            layout.addWidget(label_apellido)
            layout.addWidget(entry_apellido)
            layout.addWidget(label_direccion)
            layout.addWidget(entry_direccion)
            layout.addWidget(label_telefono)
            layout.addWidget(entry_telefono)
            layout.addWidget(check_pbs)
            layout.addWidget(button_actualizar)

            ventana_actualizar.setLayout(layout)

            def actualizar():
                paciente['nombre'] = entry_nombre.text()
                paciente['apellido'] = entry_apellido.text()
                paciente['direccion'] = entry_direccion.text()
                paciente['telefono'] = entry_telefono.text()
                paciente['pbs'] = check_pbs.isChecked()
                actualizar_paciente(paciente)
                ventana_actualizar.close()

            button_actualizar.clicked.connect(actualizar)
            ventana_actualizar.show()
        else:
            QMessageBox.critical(self, "Error", "Paciente no encontrado")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('InsCar.ico'))
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())