# Importando bibliotecas necessárias
import os
from flask import Blueprint, render_template, url_for, request, jsonify, session, redirect, Response
from models.camera_model import Camera
from utils.deteccao_pessoas import realizar_contagem, realizar_heatmap
from datetime import datetime

# Criando uma blueprint para as rotas relacionadas à câmera
camera_bp = Blueprint('camera', __name__, url_prefix='/camera')

# Rota para listar câmeras, permitindo apenas o método GET
@camera_bp.route('/listar')
def listar_cameras():
    # Verificando se o usuário está autenticado
    from app import verificar_login
    if verificar_login():
        
        # Obtendo a lista de câmeras
        cameras = Camera().list_cameras()

        # Verificando se há câmeras para exibir
        if cameras:
            # Renderiza a página com a lista de câmeras
            return render_template('list_cameras.html', cameras=cameras)
        else:
            # Renderiza a página informando que não há câmeras registradas
            return render_template('list_cameras.html')

    # Se o usuário não estiver autenticado, redireciona para a página de login
    return redirect(url_for('auth.login'))


# Rota para adicionar câmera, permitindo métodos GET e POST
@camera_bp.route('/adicionar', methods=['GET', 'POST'])
def adicionar_camera():
    # Verificando se o usuário está autenticado
    from app import verificar_login
    if verificar_login():
        # Se o método da requisição for GET, renderiza o formulário para adicionar câmera
        if request.method == 'GET':
            return render_template('add_camera.html')
        else:
            # Obtendo dados do formulário
            name = request.form.get('name')
            ip = request.form.get('ip')
            contagem_checkbox = request.form.get('contagem')

            # Verificando se câmera com mesmo IP já existe
            exist_camera = Camera().get_camera_by_ip(ip)

            if exist_camera:
                # Se já existir câmera com o mesmo IP, retorna mensagem de erro
                data = 'Já existe câmera registrada com este IP!'
                return render_template('add_camera.html', data=data)

            if contagem_checkbox:
                # Se a opção de contagem estiver marcada, verifica e processa as informações de linha e entrada
                linha_form = request.form.get('linha')
                entrada = request.form.get('entrada')

                if linha_form is not None and entrada is not None:
                    linha = list(map(int, linha_form.split(',')))

                    # Verifica se a linha é vertical ou horizontal
                    if not (linha[0] == linha[2] or linha[1] == linha[3]):
                        data = 'A linha precisa ser vertical ou horizontal!'
                        return render_template('add_camera.html', data=data)

                    elif linha[0] == linha[2]:

                        if linha[1] == linha[3]:
                            data = 'Para uma linha na vertical os valores do eixo Y devem ser diferentes'
                            return render_template('add_camera.html', data=data)

                        # Verifica se a entrada é válida para uma linha vertical
                        if entrada == 'cima' or entrada == 'baixo':
                            data = 'A entrada precisa ser esquerda ou direita!'
                            return render_template('add_camera.html', data=data)

                    elif linha[1] == linha[3]:

                        if linha[0] == linha[2]:
                            data = 'Para uma linha na horizontal os valores do eixo X devem ser diferentes'
                            return render_template('add_camera.html', data=data)

                        # Verifica se a entrada é válida para uma linha horizontal
                        if entrada == 'esquerda' or entrada == 'direita':
                            data = 'A entrada precisa ser cima ou baixo!'
                            return render_template('add_camera.html', data=data)
                
                    # Adiciona a câmera com informações de contagem
                    new_camera = Camera().add_camera(name, ip, linha=linha, entrada=entrada)

            else:
                # Adiciona a câmera sem informações de contagem
                new_camera = Camera().add_camera(name, ip)

            # Redireciona para a lista de câmeras após adicionar
            return redirect(url_for('camera.listar_cameras'))

    # Se o usuário não estiver autenticado, redireciona para a página de login
    return redirect(url_for('auth.login'))

# Rota para editar câmera, permitindo métodos GET e POST
@camera_bp.route('/editar/<id>', methods=['GET', 'POST'])
def editar_camera(id):
    # Verificando se o usuário está autenticado
    from app import verificar_login
    if verificar_login():

        # Obtendo informações da câmera pelo ID
        camera = Camera().get_camera_by_id(id)

        # Verificando se a câmera existe
        if not camera:
            return redirect(url_for('camera.listar_cameras'))

        # Se o método da requisição for GET, renderiza o formulário de edição
        if request.method == 'GET':
            return render_template('edit_camera.html', camera=camera)
        else:
            # Inicializando variáveis de linha e entrada
            linha = None
            entrada = None

            # Obtendo dados do formulário
            name = request.form.get('name')
            ip = request.form.get('ip')
            contagem_checkbox = request.form.get('contagem')

            # Verificando se a opção de contagem está marcada
            if contagem_checkbox:
                # Processando informações de linha e entrada, se fornecidas
                linha_form = request.form.get('linha')
                entrada = request.form.get('entrada')

                if linha_form is not None and entrada is not None:
                    linha = list(map(int, linha_form.split(',')))

                    # Verificando se a linha é vertical ou horizontal
                    if not (linha[0] == linha[2] or linha[1] == linha[3]):
                        data = 'A linha precisa ser vertical ou horizontal!'
                        return render_template('add_camera.html', data=data)

                    elif linha[0] == linha[2]:

                        if linha[1] == linha[3]:
                            data = 'Para uma linha na vertical os valores do eixo Y devem ser diferentes'
                            return render_template('add_camera.html', data=data)

                        # Verificando a validade da entrada para uma linha vertical
                        if entrada == 'cima' or entrada == 'baixo':
                            data = 'A entrada precisa ser esquerda ou direita!'
                            return render_template('add_camera.html', data=data)

                    elif linha[1] == linha[3]:

                        if linha[0] == linha[2]:
                            data = 'Para uma linha na horizontal os valores do eixo X devem ser diferentes'
                            return render_template('add_camera.html', data=data)

                        # Verificando a validade da entrada para uma linha horizontal
                        if entrada == 'esquerda' or entrada == 'direita':
                            data = 'A entrada precisa ser cima ou baixo!'
                            return render_template('add_camera.html', data=data)

            else:
                # Se a opção de contagem não estiver marcada, linha e entrada permanecem como None
                linha = None
                entrada = None

            # Verificando se já existe uma câmera com o IP fornecido
            exist_ip = Camera().get_camera_by_ip(ip)

            if exist_ip and camera.get('ip') != ip:
                data = 'Já existe câmera registrada com este IP!'
                return render_template('edit_camera.html', camera=camera, data=data)

            # Atualizando informações da câmera
            new_camera = Camera().update_camera(id, name, ip, new_linha=linha, new_entrada=entrada)

            # Redireciona para a lista de câmeras após a edição
            return redirect(url_for('camera.listar_cameras'))

    # Se o usuário não estiver autenticado, redireciona para a página de login
    return redirect(url_for('auth.login'))

# Rota para excluir câmera, permitindo apenas o método GET
@camera_bp.route('/excluir/<id>', methods=['GET'])
def excluir_camera(id):
    # Verificando se o usuário está autenticado
    from app import verificar_login
    if verificar_login():

        # Obtendo informações da câmera pelo ID
        camera = Camera().get_camera_by_id(id)

        # Verificando se a câmera existe
        if not camera:
            return redirect(url_for('camera.listar_cameras'))
        else:
            # Excluindo a câmera pelo ID
            Camera().delete_camera(id)

            # Redireciona para a lista de câmeras após excluir
            return redirect(url_for('camera.listar_cameras'))

    # Se o usuário não estiver autenticado, redireciona para a página de login
    return redirect(url_for('auth.login'))

# Rota para visualizar câmera, permitindo apenas o método GET
@camera_bp.route('/visualizar/<camera_id>/<tipo>')
def visualizar_camera(camera_id, tipo):
    # Verificando se o usuário está autenticado
    from app import verificar_login

    if verificar_login():
        # Obtendo informações da câmera pelo ID
        camera = Camera().get_camera_by_id(camera_id)

        # Verificando se a câmera existe
        if not camera:
            return redirect(url_for('camera.listar_cameras'))

        # Renderiza a página de visualização de câmera com o ID e tipo especificados
        return render_template('visualizar_camera.html', camera_id=camera_id, tipo=tipo)

    # Se o usuário não estiver autenticado, redireciona para a página de login
    return redirect(url_for('auth.login'))

# Rota para fornecer o feed de vídeo, permitindo apenas o método GET
@camera_bp.route('/video_feed/<camera_id>/<tipo>')
def video_feed(camera_id, tipo):
    # Obtendo informações da câmera pelo ID
    camera = Camera().get_camera_by_id(camera_id)
    # Obtendo o IP da câmera
    camera_ip = camera.get('ip')

    # Verificando o tipo de feed solicitado
    if tipo == 'contagem':
        # Verificando se a câmera existe
        if camera:
            # Obtendo informações de linha e entrada da câmera
            linha = camera.get('linha')
            entrada = camera.get('entrada')

            # Verificando se a câmera está configurada corretamente para contagem
            if linha and entrada:
                # Retornando o feed de vídeo com a realização da contagem
                return Response(realizar_contagem(camera_ip, linha, entrada),
                                mimetype='multipart/x-mixed-replace; boundary=frame')
            else:
                # Redireciona para a lista de câmeras se a configuração estiver ausente
                return redirect(url_for('camera.listar_cameras'))

    elif tipo == 'heatmap':
        # Retornando o feed de vídeo com a realização do heatmap
        return Response(realizar_heatmap(camera_ip),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

# Rota para gerar relatório, permitindo métodos GET e POST
@camera_bp.route('/relatorio', methods=['GET', 'POST'])
def gerar_relatorio():
    # Verificando se o usuário está autenticado e se sim, obtendo a instância do MongoDB
    from app import verificar_login, mongo

    if verificar_login():

        # Verificando o método da requisição
        if request.method == 'POST':

            # Obtendo informações do formulário para gerar o relatório
            camera_ip = request.form.get('camera_ip')
            data_inicio = request.form.get("data_inicio")
            data_fim = request.form.get("data_fim")

            # Convertendo as datas fornecidas para timestamps
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%dT%H:%M').timestamp()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%dT%H:%M').timestamp()

            # Contando o número total de entradas dentro do intervalo de datas especificado
            total_entradas = mongo.get_database().get_collection('registros').count_documents({
                'camera_ip': camera_ip,
                'entrada': {
                    '$gte': data_inicio,
                    '$lte': data_fim
                }
            })

            # Criando um dicionário com os resultados do relatório
            resultados = {
                'total_entradas': total_entradas
            }

            # Retornando os resultados em formato JSON
            return jsonify(resultados)

        # Obtendo a lista de câmeras configuradas para contagem
        cameras = Camera().list_cameras_contagem()

        # Renderizando o formulário de relatório com a lista de câmeras disponíveis
        return render_template('formulario_relatorio.html', cameras=cameras)

    # Se o usuário não estiver autenticado, redireciona para a página de login
    return redirect(url_for('auth.login'))
