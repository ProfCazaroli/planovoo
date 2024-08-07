# Renumerar a coluna de IDs - Waypoint Number
# PlanoVoo_Ajustes6_Litchi.py

camada = projeto.mapLayersByName('Pontos_reordenados')[0]

camada.startEditing()

for f in camada.getFeatures():
    f['Alt. ASL [m]'] = 120
    camada.updateFeature(f)

camada.commitChanges()
