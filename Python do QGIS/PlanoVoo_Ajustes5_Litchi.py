# Trocar Coluna X e Y de lugar
# PlanoVoo_Ajustes5_Litchi.py

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

