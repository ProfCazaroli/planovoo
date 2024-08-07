# Definir Atributos de Geometria
# PlanoVoo_AtributosGeom.py

projeto = QgsProject.instance()
camada = projeto.mapLayersByName('Pontos_reprojetados')[0]

# Adicione novos campos para X, Y e Z
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

