# Reprojetar Camada Pontos (Fotos) de 31983 para 4326
# PlanoVoo_ReprojetarCoord.py

camada = QgsProject.instance().mapLayersByName('Pontos')[0]

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
QgsProject.instance().addMapLayer(camadaReproj)

