# Definir o Valor de Z para as Fotos com o MDE obtido do OpenTopography
# PlanoVoo_CotaZ.py

alturaVoo = 120 # 120m altura de Voo

projeto = QgsProject.instance()

# Obter a camada MDE e a camada de fotos do projeto
camadaMDE = projeto.mapLayersByName("DEM")[0]
camadaPontos = projeto.mapLayersByName("Pontos_reprojetados")[0]

# Adicionar o campo "Z" na camada de pontos se ainda não existir
if camadaPontos.fields().indexFromName('Z') == -1:
    camadaPontos.dataProvider().addAttributes([QgsField('Z', QVariant.Double)])
    camadaPontos.updateFields()

camadaPontos.startEditing()

# definir o valor de Z
for f in camadaPontos.getFeatures():
    point = f.geometry().asPoint()
    x, y = point.x(), point.y()
    
    # Obter o valor de Z do MDE
    mde = camadaMDE.dataProvider().identify(QgsPointXY(x, y), QgsRaster.IdentifyFormatValue)
    z_value = mde.results()[1]  # O valor de Z está no índice 1
    
    # Atualizar o campo "Z" da feature
    f['Z'] = z_value + alturaVoo
    camadaPontos.updateFeature(f)

camadaPontos.commitChanges()

projeto.addMapLayer(camadaPontos)
    


