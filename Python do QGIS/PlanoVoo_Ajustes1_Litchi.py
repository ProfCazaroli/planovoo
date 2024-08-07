# Mapeamento dos campos antigos para os novos nomes
# PlanoVoo_Ajustes1_Litchi.py

projeto = QgsProject.instance()
camada = projeto.mapLayersByName('Pontos_reprojetados')[0]

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
