# Exportar para o Google Earth Pro (kml)
# PlanoVoo_FotosKML.py

projeto = QgsProject.instance()
camada = projeto.mapLayersByName('Pontos_reprojetados')[0]

caminho = r'C:\Users\profcazaroli\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\planovoo\Arquivos_Gerados'
camArq = caminho + '\Fotos.kml'

src = QgsCoordinateReferenceSystem('EPSG:4326')  # CRS padrão para KML (WGS84)

# Configure as opções para o escritor de arquivos
options = QgsVectorFileWriter.SaveVectorOptions()
options.fileEncoding = 'UTF-8'
options.driverName = 'KML'
options.crs = src
options.layerOptions = ['ALTITUDE_MODE=absolute'] 

# Crie o escritor de arquivos
#writer = QgsVectorFileWriter(camArq, 'UTF-8', camada.fields(), QgsWkbTypes.Point, src, 'KML')
writer = QgsVectorFileWriter.writeAsVectorFormat(camada, camArq, options)
