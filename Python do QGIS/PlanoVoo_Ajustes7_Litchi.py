# Mudar Sistema numérico
# ponto no lugar de vírgula para separa a parte decomal
# PlanoVoo_Ajustes7_Litchi.py

camada = projeto.mapLayersByName('Pontos_reordenados')[0]

def addCampo(camada, field_name, field_type):
    # Verificar se o campo já existe
    if field_name not in [field.name() for field in camada.fields()]:
        camada.dataProvider().addAttributes([QgsField(field_name, field_type)])
        camada.updateFields()

def delCampo(camada, campo):
    # Remover o campo se ele existir
    if campo in [f.name() for f in camada.fields()]:
        camada.dataProvider().deleteAttributes([camada.fields().indexOf(campo)])
        camada.updateFields()
        
camada.startEditing()

# Adicionar campos de texto
addCampo(camada, 'X [m] ', QVariant.String)
addCampo(camada, 'Y [m] ', QVariant.String)
addCampo(camada, 'Alt. ASL [m] ', QVariant.String)
addCampo(camada, 'Alt. AGL [m] ', QVariant.String)
addCampo(camada, 'xcoord ', QVariant.String)
addCampo(camada, 'ycoord ', QVariant.String)

for f in camada.getFeatures():
    x1 = str(f['X [m]']).replace(',', '.')
    x2 = str(f['Y [m]']).replace(',', '.')
    x3 = str(f['Alt. ASL [m]']).replace(',', '.')
    x4 = 'nan'
    x5 = str(f['xcoord']).replace(',', '.')
    x6 = str(f['ycoord']).replace(',', '.')

    # Formatar os valores como strings com ponto como separador decimal
    x1 = "{:.6f}".format(float(x1))
    x2 = "{:.6f}".format(float(x2))
    x3 = "{:.6f}".format(float(x3))
    x4 = x4
    x5 = "{:.6f}".format(float(x5))
    x6 = "{:.6f}".format(float(x6))

    # Atualizar os valores dos campos de texto
    f['X [m] '] = x1
    f['Y [m] '] = x2
    f['Alt. ASL [m] '] = x3
    f['Alt. AGL [m] '] = x4
    f['xcoord '] = x5
    f['ycoord '] = x6

    camada.updateFeature(f)

camada.commitChanges()

camada.startEditing()

# Lista de campos Double a serem removidos
fields_to_remove = ['X [m]', 'Y [m]', 'Alt. ASL [m]', 'Alt. AGL [m]', 'xcoord', 'ycoord']
for f in fields_to_remove:
    delCampo(camada, f)

camada.commitChanges()
