# Renumerar a coluna de IDs - Waypoint Number
# PlanoVoo_Ajustes4_Litchi.py

camada = projeto.mapLayersByName('Pontos_renomeados')[0]

camada.startEditing()
    
n = 1

for f in camada.getFeatures():
    f['Waypoint Number'] = n
    camada.updateFeature(f)
    n += 1

camada.commitChanges()
