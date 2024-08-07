# Multiplicar por -1 as latitudes e longitudes
# PlanoVoo_Ajustes3_Litchi.py

camada = projeto.mapLayersByName('Pontos_renomeados')[0]

camada.startEditing()

for f in camada.getFeatures():
    xcoord = f['xcoord']
    x = f['X [m]']
    
    ycoord = f['ycoord']
    y = f['Y [m]']
    
    # Se 'xcoord' for negativo, multiplica 'X [m]' por -1
    if xcoord < 0:
        x = x * -1
        
        f.setAttribute(f.fieldNameIndex('X [m]'), x)
        camada.updateFeature(f)
        
    if ycoord < 0:
        y = y * -1
        
        f.setAttribute(f.fieldNameIndex('Y [m]'), y)
        camada.updateFeature(f)

camada.commitChanges()
