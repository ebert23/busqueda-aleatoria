from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///servicios.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Bootstrap(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nombre = db.Column(db.String(100))
    es_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    cliente = db.Column(db.String(100))
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    kilometraje = db.Column(db.Float)
    filtro_aceite = db.Column(db.String(20))
    precio_filtro_aceite = db.Column(db.Float)
    filtro_aire = db.Column(db.String(20))
    precio_filtro_aire = db.Column(db.Float)
    filtro_petroleo = db.Column(db.String(20))
    precio_filtro_petroleo = db.Column(db.Float)
    aceite_motor = db.Column(db.String(50))
    precio_aceite_motor = db.Column(db.Float)
    otros_1 = db.Column(db.String(100))
    precio_otros_1 = db.Column(db.Float)
    otros_2 = db.Column(db.String(100))
    precio_otros_2 = db.Column(db.Float)
    otros_3 = db.Column(db.String(100))
    precio_otros_3 = db.Column(db.Float)
    otros_4 = db.Column(db.String(100))
    precio_otros_4 = db.Column(db.Float)
    total = db.Column(db.Float)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    usuario = db.relationship('Usuario', backref=db.backref('servicios', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Has iniciado sesión exitosamente', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 500
    pagination = Servicio.query.order_by(Servicio.fecha.desc()).paginate(page=page, per_page=per_page, error_out=False)
    servicios = pagination.items
    return render_template('index.html', servicios=servicios, pagination=pagination)

@app.route('/buscar')
@login_required
def buscar():
    placa = request.args.get('placa', '')
    page = request.args.get('page', 1, type=int)
    per_page = 500
    if placa:
        pagination = Servicio.query.filter(Servicio.placa.ilike(f'%{placa}%')).order_by(Servicio.fecha.desc()).paginate(page=page, per_page=per_page, error_out=False)
        servicios = pagination.items
    else:
        servicios = []
        pagination = None
    return render_template('index.html', servicios=servicios, pagination=pagination, placa=placa)

@app.route('/servicio/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_servicio():
    if request.method == 'POST':
        try:
            servicio = Servicio(
                placa=request.form['placa'],
                fecha=datetime.strptime(request.form['fecha'], '%Y-%m-%d'),
                cliente=request.form['cliente'],
                marca=request.form['marca'],
                modelo=request.form['modelo'],
                kilometraje=float(request.form['kilometraje']) if request.form['kilometraje'] else None,
                filtro_aceite=request.form['filtro_aceite'],
                precio_filtro_aceite=float(request.form['precio_filtro_aceite']) if request.form['precio_filtro_aceite'] else None,
                filtro_aire=request.form['filtro_aire'],
                precio_filtro_aire=float(request.form['precio_filtro_aire']) if request.form['precio_filtro_aire'] else None,
                filtro_petroleo=request.form['filtro_petroleo'],
                precio_filtro_petroleo=float(request.form['precio_filtro_petroleo']) if request.form['precio_filtro_petroleo'] else None,
                aceite_motor=request.form['aceite_motor'],
                precio_aceite_motor=float(request.form['precio_aceite_motor']) if request.form['precio_aceite_motor'] else None,
                otros_1=request.form['otros_1'],
                precio_otros_1=float(request.form['precio_otros_1']) if request.form['precio_otros_1'] else None,
                otros_2=request.form['otros_2'],
                precio_otros_2=float(request.form['precio_otros_2']) if request.form['precio_otros_2'] else None,
                otros_3=request.form['otros_3'],
                precio_otros_3=float(request.form['precio_otros_3']) if request.form['precio_otros_3'] else None,
                otros_4=request.form['otros_4'],
                precio_otros_4=float(request.form['precio_otros_4']) if request.form['precio_otros_4'] else None,
                usuario_id=current_user.id
            )
            
            # Calcular el total
            total = 0
            for attr in ['precio_filtro_aceite', 'precio_filtro_aire', 'precio_filtro_petroleo',
                        'precio_aceite_motor', 'precio_otros_1', 'precio_otros_2',
                        'precio_otros_3', 'precio_otros_4']:
                valor = getattr(servicio, attr)
                if valor is not None:
                    total += valor
            servicio.total = total

            db.session.add(servicio)
            db.session.commit()
            flash('Servicio registrado exitosamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error al registrar el servicio: {str(e)}', 'danger')
            return redirect(url_for('nuevo_servicio'))
    return render_template('form_servicio.html')

@app.route('/servicio/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    if request.method == 'POST':
        try:
            servicio.placa = request.form['placa']
            servicio.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
            servicio.cliente = request.form['cliente']
            servicio.marca = request.form['marca']
            servicio.modelo = request.form['modelo']
            servicio.kilometraje = float(request.form['kilometraje']) if request.form['kilometraje'] else None
            servicio.filtro_aceite = request.form['filtro_aceite']
            servicio.precio_filtro_aceite = float(request.form['precio_filtro_aceite']) if request.form['precio_filtro_aceite'] else None
            servicio.filtro_aire = request.form['filtro_aire']
            servicio.precio_filtro_aire = float(request.form['precio_filtro_aire']) if request.form['precio_filtro_aire'] else None
            servicio.filtro_petroleo = request.form['filtro_petroleo']
            servicio.precio_filtro_petroleo = float(request.form['precio_filtro_petroleo']) if request.form['precio_filtro_petroleo'] else None
            servicio.aceite_motor = request.form['aceite_motor']
            servicio.precio_aceite_motor = float(request.form['precio_aceite_motor']) if request.form['precio_aceite_motor'] else None
            servicio.otros_1 = request.form['otros_1']
            servicio.precio_otros_1 = float(request.form['precio_otros_1']) if request.form['precio_otros_1'] else None
            servicio.otros_2 = request.form['otros_2']
            servicio.precio_otros_2 = float(request.form['precio_otros_2']) if request.form['precio_otros_2'] else None
            servicio.otros_3 = request.form['otros_3']
            servicio.precio_otros_3 = float(request.form['precio_otros_3']) if request.form['precio_otros_3'] else None
            servicio.otros_4 = request.form['otros_4']
            servicio.precio_otros_4 = float(request.form['precio_otros_4']) if request.form['precio_otros_4'] else None

            # Recalcular el total
            total = 0
            for attr in ['precio_filtro_aceite', 'precio_filtro_aire', 'precio_filtro_petroleo',
                        'precio_aceite_motor', 'precio_otros_1', 'precio_otros_2',
                        'precio_otros_3', 'precio_otros_4']:
                valor = getattr(servicio, attr)
                if valor is not None:
                    total += valor
            servicio.total = total

            db.session.commit()
            flash('Servicio actualizado exitosamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error al actualizar el servicio: {str(e)}', 'danger')
    return render_template('form_servicio.html', servicio=servicio)

@app.route('/servicio/eliminar/<int:id>')
@login_required
def eliminar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    try:
        db.session.delete(servicio)
        db.session.commit()
        flash('Servicio eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el servicio: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/importar', methods=['GET', 'POST'])
@login_required
def importar_excel():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'danger')
            return redirect(request.url)

        try:
            df = pd.read_excel(file)
            
            # Verificar si existen las columnas requeridas
            columnas_requeridas = ['FECHA', 'PLACA']
            for columna in columnas_requeridas:
                if columna not in df.columns:
                    raise ValueError(f'La columna {columna} no existe en el archivo Excel')

            for _, row in df.iterrows():
                try:
                    # Manejo específico de la fecha
                    fecha_raw = row['FECHA']
                    if pd.isna(fecha_raw):
                        raise ValueError('La fecha no puede estar vacía')
                    
                    try:
                        fecha = pd.to_datetime(fecha_raw).date()
                    except Exception as fecha_error:
                        raise ValueError(f'Error al procesar la fecha "{fecha_raw}": {str(fecha_error)}')

                    servicio = Servicio(
                        placa=str(row['PLACA']) if pd.notna(row['PLACA']) else None,
                        fecha=fecha,
                        cliente=str(row['CLIENTE']) if pd.notna(row.get('CLIENTE')) else None,
                        marca=str(row['MARCA']) if pd.notna(row.get('MARCA')) else None,
                        modelo=str(row['MODELO']) if pd.notna(row.get('MODELO')) else None,
                        kilometraje=float(row['KM']) if pd.notna(row.get('KM')) else None,
                        filtro_aceite=str(row['FILTRO DE ACEITE']) if pd.notna(row.get('FILTRO DE ACEITE')) else None,
                        precio_filtro_aceite=float(row['PRECIO FILTRO ACEITE']) if pd.notna(row.get('PRECIO FILTRO ACEITE')) else None,
                        filtro_aire=str(row['FILTRO FILTRO DE AIRE']) if pd.notna(row.get('FILTRO FILTRO DE AIRE')) else None,
                        precio_filtro_aire=float(row['PRECIO AIRE']) if pd.notna(row.get('PRECIO AIRE')) else None,
                        filtro_petroleo=str(row['FILTRO DE PETROLEO ']) if pd.notna(row.get('FILTRO DE PETROLEO ')) else None,
                        precio_filtro_petroleo=float(row['PRECIO FILTRO PETROLEO']) if pd.notna(row.get('PRECIO FILTRO PETROLEO')) else None,
                        aceite_motor=str(row['    ACEITE MOTOR']) if pd.notna(row.get('    ACEITE MOTOR')) else None,
                        precio_aceite_motor=float(row['PRECIO ACEITE MOTOR']) if pd.notna(row.get('PRECIO ACEITE MOTOR')) else None,
                        otros_1=str(row['OTROS 1']) if pd.notna(row.get('OTROS 1')) else None,
                        precio_otros_1=float(row['PRECIO OTROS 1']) if pd.notna(row.get('PRECIO OTROS 1')) else None,
                        otros_2=str(row['OTROS 2']) if pd.notna(row.get('OTROS 2')) else None,
                        precio_otros_2=float(row['PRECIO OTROS 2']) if pd.notna(row.get('PRECIO OTROS 2')) else None,
                        otros_3=str(row['OTROS 3']) if pd.notna(row.get('OTROS 3')) else None,
                        precio_otros_3=float(row['PRECIO OTROS 3']) if pd.notna(row.get('PRECIO OTROS 3')) else None,
                        otros_4=str(row['OTROS 4']) if pd.notna(row.get('OTROS 4')) else None,
                        precio_otros_4=float(row['PRECIO OTROS 4']) if pd.notna(row.get('PRECIO OTROS 4')) else None,
                        usuario_id=current_user.id
                    )

                    # Calcular el total
                    total = 0
                    for attr in ['precio_filtro_aceite', 'precio_filtro_aire', 'precio_filtro_petroleo',
                                'precio_aceite_motor', 'precio_otros_1', 'precio_otros_2',
                                'precio_otros_3', 'precio_otros_4']:
                        valor = getattr(servicio, attr)
                        if valor is not None:
                            total += valor
                    servicio.total = total
                    
                    db.session.add(servicio)
                except Exception as row_error:
                    db.session.rollback()
                    raise ValueError(f'Error en la fila {_ + 2}: {str(row_error)}')
            
            db.session.commit()
            flash('Datos importados exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al importar datos: {str(e)}', 'danger')
        
        return redirect(url_for('index'))
    
    return render_template('importar.html')

@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not current_user.es_admin:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('index'))
    usuarios = Usuario.query.all()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuario/crear', methods=['POST'])
@login_required
def crear_usuario():
    if not current_user.es_admin:
        flash('No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('index'))
    
    try:
        username = request.form['username']
        password = request.form['password']
        nombre = request.form['nombre']
        es_admin = 'es_admin' in request.form
        
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'danger')
            return redirect(url_for('admin_usuarios'))
        
        usuario = Usuario(username=username, nombre=nombre, es_admin=es_admin)
        usuario.set_password(password)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Usuario creado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al crear el usuario: {str(e)}', 'danger')
    
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuario/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_usuario(id):
    if not current_user.es_admin:
        flash('No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('index'))
    
    if id == current_user.id:
        flash('No puedes eliminar tu propio usuario', 'danger')
        return redirect(url_for('admin_usuarios'))
    
    try:
        usuario = Usuario.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el usuario', 'danger')
    
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/borrar-todos-registros', methods=['POST'])
@login_required
def borrar_todos_registros():
    if not current_user.es_admin:
        flash('No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Contar registros antes de eliminar
        total_registros = Servicio.query.count()
        
        # Eliminar todos los registros de servicios
        Servicio.query.delete()
        db.session.commit()
        
        flash(f'Se han eliminado exitosamente {total_registros} registros del sistema', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar los registros. Por favor, inténtelo de nuevo.', 'danger')
    
    return redirect(url_for('admin_usuarios'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Crear usuario admin por defecto si no existe
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(username='admin', nombre='Administrador', es_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')