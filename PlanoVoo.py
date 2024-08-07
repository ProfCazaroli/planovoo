from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from .resources import *
from .PlanoVoo_dialog import PlanoVooDialog
import os.path
import processing
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsVectorLayer, QgsFeature, QgsField, QgsFields, 
    QgsGeometry, QgsPoint, QgsPointXY, QgsRaster, QgsWkbTypes, edit, QgsCoordinateReferenceSystem,
    QgsVectorFileWriter, QgsCoordinateTransform
)
from PyQt5.QtCore import QVariant

class PlanoVoo:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PlanoVoo_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&PlanoVoo')

        self.first_start = None

    def tr(self, message):
        return QCoreApplication.translate('PlanoVoo', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        icon_path = ':/plugins/PlanoVoo/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PlanoVoo'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PlanoVoo'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        if self.first_start == True:
            self.first_start = False
            self.dlg = PlanoVooDialog()

        self.dlg.show()
        
        result = self.dlg.exec_()
        
        if result:
            projeto = QgsProject.instance()

            # ===OpenTopography=========================================================
            # Obter as coordenadas extremas da área
            camada = self.dlg.cmbArea.currentText()
            camada = projeto.mapLayersByName(camada)[0]

            pontoN = float('-inf')  # coordenada máxima (Norte) / inf de inifito
            pontoS = float('inf')   # coordenada mínima (Sul)
            pontoW = float('inf')   # coordenada mínima (Oeste)
            pontoE = float('-inf')  # coordenada máxima (Leste)
            
            for feature in camada.getFeatures():
                geom = feature.geometry()
                bounds = geom.boundingBox() # Obtém os limites da geometria

                pontoN = max(pontoN, bounds.yMaximum())
                pontoS = min(pontoS, bounds.yMinimum())
                pontoW = min(pontoW, bounds.xMinimum())
                pontoE = max(pontoE, bounds.xMaximum())

            ajuste_lat = (pontoN - pontoS) * 0.70
            ajuste_long = (pontoE - pontoW) * 0.70
            
            pontoN += ajuste_lat
            pontoS -= ajuste_lat
            pontoW -= ajuste_long
            pontoE += ajuste_long    

            # obter o MDE da área
            src = projeto.crs()              # [EPSG:<QgsCoordinateReferenceSystem: EPSG:31983>]
            src = src.authid().split(":")[1] # 31983
            coordenadas = f'{pontoW},{pontoE},{pontoS},{pontoN}'
            area = f"{coordenadas}[EPSG:{src}]"
            apiKey = 'd0fd2bf40aa8a6225e8cb6a4a1a5faf7'

            result = processing.run(
                    "OTDEMDownloader:OpenTopography DEM Downloader", {
                        'DEMs': 7,
                        'Extent': area,
                        'API_key': apiKey,
                        'OUTPUT': 'TEMPORARY_OUTPUT'})

            output_path = result['OUTPUT']
            camadaMDE = QgsRasterLayer(output_path, "DEM")
            
            projeto.addMapLayer(camadaMDE)

            # ==================================================================================
            # === Reprojetar Camada Pontos (Fotos) de 31983 para 4326===========================
            camada = self.dlg.cmbFotos.currentText()
            camada = projeto.mapLayersByName(camada)[0]
            #camada = QgsProject.instance().mapLayersByName('Pontos')[0]

            src = camada.crs() # EPSG:31983
            srcDestino = QgsCoordinateReferenceSystem(4326) # EPSG:4326

            # Configuração do transformador
            transform_context = QgsProject.instance().transformContext()
            transform = QgsCoordinateTransform(src, srcDestino, transform_context)

            # Crie uma nova camada para os dados reprojetados
            camadaReproj = QgsVectorLayer("Point?crs=EPSG:4326", "Pontos_reprojetados", "memory")
            camadaReproj.startEditing()
            camadaReproj.dataProvider().addAttributes(camada.fields())
            camadaReproj.updateFields()

            # Reprojetar os pontos
            for f in camada.getFeatures():
                geom = f.geometry()
                geom.transform(transform)
                reprojFeature = QgsFeature()
                reprojFeature.setGeometry(geom)
                reprojFeature.setAttributes(f.attributes())
                camadaReproj.addFeature(reprojFeature)

            # Adiciona a camada ao projeto
            camadaReproj.commitChanges()
            
            projeto.addMapLayer(camadaReproj)
            
            # ==================================================================================
            # ====Obter Cota Z - Pontos e DEM ==================================================
            alturaVoo = self.dlg.spbAlturaVoo.value() # 120m altura de Voo

            # Obter a camada MDE e a camada de fotos do projeto
            camadaMDE = projeto.mapLayersByName("DEM")[0]
            camada = projeto.mapLayersByName("Pontos_reprojetados")[0]

            # Adicionar o campo "Z" na camada de pontos se ainda não existir
            if camada.fields().indexFromName('Z') == -1:
                camada.dataProvider().addAttributes([QgsField('Z', QVariant.Double)])
                camada.updateFields()

            camada.startEditing()

            # definir o valor de Z
            for f in camada.getFeatures():
                point = f.geometry().asPoint()
                x, y = point.x(), point.y()
                
                # Obter o valor de Z do MDE
                mde = camadaMDE.dataProvider().identify(QgsPointXY(x, y), QgsRaster.IdentifyFormatValue)
                z_value = mde.results()[1]  # O valor de Z está no índice 1
                
                # Atualizar o campo "Z" da feature
                f['Z'] = z_value + alturaVoo
                camada.updateFeature(f)

            camada.commitChanges()

            projeto.addMapLayer(camada)
            
            # ==================================================================================
            # ===Exportar para o Google Earth Pro (kml)=========================================
            # caminho = r'C:\Users\profcazaroli\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\planovoo\Arquivos_Gerados'
            # camArq = caminho + '\Fotos.kml'
            
            camArq = self.dlg.arqKml.filePath()

            camada = projeto.mapLayersByName("Pontos_reprojetados")[0]
            
            # Configure as opções para o escritor de arquivos
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.fileEncoding = 'UTF-8'
            options.driverName = 'KML'
            options.crs = QgsCoordinateReferenceSystem('EPSG:4326')
            options.layerOptions = ['ALTITUDE_MODE=absolute'] 

            # Crie o escritor de arquivos
            #writer = QgsVectorFileWriter(camArq, 'UTF-8', camada.fields(), QgsWkbTypes.Point, src, 'KML')
            writer = QgsVectorFileWriter.writeAsVectorFormat(camada, camArq, options)
            
            # ==================================================================================
            # ===Definir Atributos de Geometria=================================================

            camada = projeto.mapLayersByName("Pontos_reprojetados")[0]
            
            camada.dataProvider().addAttributes([QgsField("xcoord", QVariant.Double),
                                                QgsField("ycoord", QVariant.Double)])
            camada.updateFields()

            # Obtenha o índice dos novos campos
            idx_x = camada.fields().indexFromName('xcoord')
            idx_y = camada.fields().indexFromName('ycoord')

            # Inicie a edição da camada
            camada.startEditing()

            # Itere sobre todas as features e atualize os novos campos
            for f in camada.getFeatures():
                geom = f.geometry()
                if geom.isEmpty():
                    continue

                # Supondo que a geometria seja um ponto
                point = geom.asPoint()
                x = point.x()
                y = point.y()

                # Atualize os valores de xcoord e ycoord
                f.setAttribute(idx_x, x)
                f.setAttribute(idx_y, y)

                # Atualize a feature na camada
                camada.updateFeature(f)

            camada.commitChanges()
            
            # ==================================================================================
            # ===Mapeamento dos campos antigos para os novos nomes==============================
            campos = camada.fields()
                    
            novos_nomes = {
                'id': 'Waypoint Number',
                'latitude': 'Y [m]',
                'longitude': 'X [m]',
                'Z': 'Alt. ASL [m]',
                'xcoord': 'xcoord',
                'ycoord': 'ycoord'}

            # Adicionar novos campos à camada
            novoCampos = QgsFields()
            for f in campos:
                novoNome = novos_nomes.get(f.name(), f.name())
                novoCampo = QgsField(novoNome, f.type())
                novoCampos.append(novoCampo)

            # Criar uma nova camada com os campos renomeados
            novaCamada = QgsVectorLayer(f'Point?crs={camada.crs().authid()}', 'Pontos_renomeados', 'memory')
            provider = novaCamada.dataProvider()
            provider.addAttributes(novoCampos)
            novaCamada.updateFields()

            # Copiar os recursos da camada original para a nova camada
            with edit(novaCamada):
                for f in camada.getFeatures():
                    novaFeature = QgsFeature(novaCamada.fields())
                    novaFeature.setGeometry(f.geometry())
                    
                    novaFeature.setAttributes(f.attributes())
                    novaCamada.dataProvider().addFeature(novaFeature)
                
            # Adicionar a nova camada ao projeto
            projeto.addMapLayer(novaCamada)
            
            # resultado = novaCamada que é Pontos_renomeados
            
            # ==================================================================================
            # ===Adicionar o novo campo 'Alt. AGL [m]'==========================================
            camada = projeto.mapLayersByName('Pontos_renomeados')[0]
            campos = camada.fields()

            novoCampo = QgsField('Alt. AGL [m]', QVariant.Double) # QVariant.Double p/valores numéricos
            camada.dataProvider().addAttributes([novoCampo])
            camada.updateFields()

            i = len(campos)

            with edit(camada):
                for f in camada.getFeatures():
                    f.setAttribute(i, None)  # Definir como NaN
                    camada.updateFeature(f)
            
            # ==================================================================================
            # ====Multiplicar por -1 as latitudes e longitudes==================================
            camada = projeto.mapLayersByName('Pontos_renomeados')[0]

            camada.startEditing()

            for f in camada.getFeatures():
                xcoord = f['xcoord']
                x = f['X [m]']
                
                ycoord = f['ycoord']
                y = f['Y [m]']
                
                # Se 'xcoord' for negativo, multiplica 'X [m]' por -1
                if xcoord < 0:
                    x = x * 
                    
                    f.setAttribute(f.fieldNameIndex('X [m]'), x)
                    camada.updateFeature(f)
                    
                if ycoord < 0:
                    y = y * -1
                    
                    f.setAttribute(f.fieldNameIndex('Y [m]'), y)
                    camada.updateFeature(f)

            camada.commitChanges()
            
            # ==================================================================================
            # ====Renumerar a coluna de IDs - Waypoint Number==================================
            camada = projeto.mapLayersByName('Pontos_renomeados')[0]

            camada.startEditing()
                
            n = 1

            for f in camada.getFeatures():
                f['Waypoint Number'] = n
                camada.updateFeature(f)
                n += 1

            camada.commitChanges()
            
            # ==================================================================================
            # ====Trocar Coluna X e Y de lugar==================================================
            camada = projeto.mapLayersByName('Pontos_renomeados')[0]

            # Definindo a nova ordem dos campos
            novaOrdem = ['Waypoint Number', 'X [m]', 'Y [m]', 'Alt. ASL [m]', 'Alt. AGL [m]', 'xcoord', 'ycoord']

            # Criando uma nova camada de memória com a nova ordem de campos
            novaCamada = QgsVectorLayer(f'Point?crs={camada.crs().authid()}', 'Pontos_reordenados', 'memory')
            provider = novaCamada.dataProvider()

            # Adicionando os campos na nova ordem
            novosCampos = QgsFields()
            for field_name in novaOrdem:
                field = camada.fields().field(field_name)
                novosCampos.append(field)
                
            provider.addAttributes(novosCampos)
            novaCamada.updateFields()

            # Copiando os registros da camada original para a nova camada
            for f in camada.getFeatures():
                n = QgsFeature(novaCamada.fields())
                n.setGeometry(f.geometry())
                
                for field_name in novaOrdem:
                    n.setAttribute(field_name, f[field_name])
                
                provider.addFeature(n)

            # Adicionando a nova camada ao projeto
            QgsProject.instance().addMapLayer(novaCamada)
            
            # ==================================================================================
            # ====Colocar a cota Z em 120m (altura do Voo)======================================
            camada = projeto.mapLayersByName('Pontos_reordenados')[0]

            camada.startEditing()

            for f in camada.getFeatures():
                f['Alt. ASL [m]'] = 120.00
                camada.updateFeature(f)

            camada.commitChanges()
            
            # ==================================================================================
            # ====Mudar Sistema numérico - ponto no lugar de vírgula para separa a parte decimal
            camada = projeto.mapLayersByName('Pontos_reordenados')[0]

            def addCampo(camada, field_name, field_type):
                # Verificar se o campo já existe
                if field_name not in [field.name() for field in camada.fields()]:
                    camada.dataProvider().addAttributes([QgsField(field_name, field_type)])
                    camada.updateFields()

            def delCampo(camada, campo):
                # Remover o campo se ele existir
                if campo in [f.name() for f in camada.fields()]:
                    camada.dataProvider().deleteAttributes([camada.fields().indexOf(campo)])
                    camada.updateFields()
                    
            camada.startEditing()

            # Adicionar campos de texto
            addCampo(camada, 'X [m] ', QVariant.String)
            addCampo(camada, 'Y [m] ', QVariant.String)
            addCampo(camada, 'Alt. ASL [m] ', QVariant.String)
            addCampo(camada, 'Alt. AGL [m] ', QVariant.String)
            addCampo(camada, 'xcoord ', QVariant.String)
            addCampo(camada, 'ycoord ', QVariant.String)

            for f in camada.getFeatures():
                x1 = str(f['X [m]']).replace(',', '.')
                x2 = str(f['Y [m]']).replace(',', '.')
                x3 = str(f['Alt. ASL [m]']).replace(',', '.')
                x4 = 'nan'
                x5 = str(f['xcoord']).replace(',', '.')
                x6 = str(f['ycoord']).replace(',', '.')

                # Formatar os valores como strings com ponto como separador decimal
                x1 = "{:.6f}".format(float(x1))
                x2 = "{:.6f}".format(float(x2))
                x3 = "{:.6f}".format(float(x3))
                x4 = x4
                x5 = "{:.6f}".format(float(x5))
                x6 = "{:.6f}".format(float(x6))

                # Atualizar os valores dos campos de texto
                f['X [m] '] = x1
                f['Y [m] '] = x2
                f['Alt. ASL [m] '] = x3
                f['Alt. AGL [m] '] = x4
                f['xcoord '] = x5
                f['ycoord '] = x6

                camada.updateFeature(f)

            camada.commitChanges()

            camada.startEditing()

            # Lista de campos Double a serem removidos
            fields_to_remove = ['X [m]', 'Y [m]', 'Alt. ASL [m]', 'Alt. AGL [m]', 'xcoord', 'ycoord']
            for f in fields_to_remove:
                delCampo(camada, f)

            camada.commitChanges()
            
            # ==================================================================================
            # ====Exportar para o Litich (csv preparado)========================================

            # caminho = r'C:\Users\profcazaroli\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\planovoo\Arquivos_Gerados'
            # camArq = caminho + '\Fotos.csv'

            camArq = self.dlg.arqCSV.filePath()
            
            camada = projeto.mapLayersByName('Pontos_reordenados')[0]
            
            src = QgsCoordinateReferenceSystem('EPSG:4326')  # CRS padrão para KML (WGS84)

            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = 'CSV'
            options.fileEncoding = 'UTF-8'
            options.crs = src

            writer = QgsVectorFileWriter.writeAsVectorFormat(camada, camArq, options)
            
            # ==================================================================================
            # ====Mensagem de Encerramento======================================================
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Plugin Plano de Voo")
            msg.setText("Plugin executado com sucesso.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            pass
