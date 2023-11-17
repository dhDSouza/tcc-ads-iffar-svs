from flask import Blueprint, render_template, url_for, request, jsonify, session, redirect, Response
from models.camera_model import Camera
from json import dumps
from utils.deteccao_pessoas import detectar_pessoas
import os

camera_bp = Blueprint('camera', __name__, url_prefix='/camera')

@camera_bp.route('/listar')
def listar_cameras():
    from app import verificar_login
    if verificar_login():
        
        cameras = Camera().list_cameras()

        if cameras:
            return render_template('list_cameras.html', cameras=cameras)
        else:

            return render_template('list_cameras.html')

    return redirect(url_for('auth.login'))

@camera_bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_camera():
    from app import verificar_login
    if verificar_login():

        if request.method == 'GET':
            return render_template('add_camera.html')

        else:

            name = request.form.get('name')
            ip = request.form.get('ip')

            exist_camera = Camera().get_camera_by_ip(ip)

            if exist_camera:
                data = 'Já existe câmera regitrada com este IP!'
                return render_template('add_camera.html', data=data)

            new_camera = Camera().add_camera(name, ip)

            return redirect(url_for('camera.listar_cameras'))

    return redirect(url_for('auth.login'))


@camera_bp.route('/editar/<id>', methods=['GET', 'POST'])
def editar_camera(id):
    from app import verificar_login
    if verificar_login():

        camera = Camera().get_camera_by_id(id)

        if not camera:
            return redirect(url_for('camera.listar_cameras'))

        if request.method == 'GET':
            return render_template('edit_camera.html', camera=camera)

        else:

            name = request.form.get('name')
            ip = request.form.get('ip')

            exist_ip = Camera().get_camera_by_ip(ip)

            if exist_ip and camera.get('ip') != ip:
                data = 'Já existe câmera regitrada com este IP!'
                return render_template('edit_camera.html', camera=camera, data=data)

            new_camera = Camera().update_camera(id, name, ip)

            return redirect(url_for('camera.listar_cameras'))

    return redirect(url_for('auth.login'))

@camera_bp.route('/excluir/<id>', methods=['GET'])
def excluir_camera(id):
    from app import verificar_login
    if verificar_login():

        camera = Camera().get_camera_by_id(id)

        if not camera:
            return redirect(url_for('camera.listar_cameras'))

        else:

            Camera().delete_camera(id)

            return redirect(url_for('camera.listar_cameras'))

    return redirect(url_for('auth.login'))

@camera_bp.route('/visualizar/<camera_id>')
def visualizar_camera(camera_id):
    from app import verificar_login

    if verificar_login():
        camera = Camera().get_camera_by_id(camera_id)

        if not camera:
            return redirect(url_for('camera.listar_cameras'))

        return render_template('visualizar_camera.html', camera_id=camera_id)

    return redirect(url_for('auth.login'))

@camera_bp.route('/video_feed/<camera_id>')
def video_feed(camera_id):

    return Response(detectar_pessoas(Camera().get_camera_by_id(camera_id)['ip']),
                    mimetype='multipart/x-mixed-replace; boundary=frame')