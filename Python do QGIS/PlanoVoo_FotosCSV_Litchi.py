# Exportar para o Litich (csv preparado)
# PlanoVoo_FotosCSV_Litchi.py

projeto = QgsProject.instance()
camada = projeto.mapLayersByName('Pontos_reordenados')[0]

caminho = r'C:\Users\profcazaroli\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\planovoo\Arquivos_Gerados'
camArq = caminho + '\Fotos.csv'

src = QgsCoordinateReferenceSystem('EPSG:4326')  # CRS padrão para KML (WGS84)

options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = 'CSV'
options.fileEncoding = 'UTF-8'
options.crs = src

writer = QgsVectorFileWriter.writeAsVectorFormat(camada, camArq, options)

