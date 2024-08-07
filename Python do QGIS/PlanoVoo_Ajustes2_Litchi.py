# Adicionar o novo campo 'Alt. AGL [m]'
# PlanoVoo_Ajustes2_Litchi.py

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
        
