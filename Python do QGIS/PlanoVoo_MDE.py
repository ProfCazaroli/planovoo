# OpenTopography
# PlanoVoo_MDE.py

projeto = QgsProject.instance()
camada = projeto.mapLayersByName('Terreno')[0]

pontoN = float('-inf')  # coordenada máxima (Norte) / inf de inifito
pontoS = float('inf')   # coordenada mínima (Sul)
pontoW = float('inf')   # coordenada mínima (Oeste)
pontoE = float('-inf')  # coordenada máxima (Leste)

for feature in camada.getFeatures():
    geom = feature.geometry()
    bounds = geom.boundingBox() # Obtém os limites da geometria
    
    pontoN = max(pontoN, bounds.yMaximum())
    pontoS = min(pontoS, bounds.yMinimum())
    pontoW = min(pontoW, bounds.xMinimum())
    pontoE = max(pontoE, bounds.xMaximum())

ajuste_lat = (pontoN - pontoS) * 0.50
ajuste_long = (pontoE - pontoW) * 0.50

pontoN += ajuste_lat
pontoS -= ajuste_lat
pontoW -= ajuste_long
pontoE += ajuste_long

src = projeto.crs() #[EPSG:<QgsCoordinateReferenceSystem: EPSG:31983>]
src = src.authid().split(":")[1] # 31983
coordenadas = f'{pontoW},{pontoE},{pontoS},{pontoN}'
area = f"{coordenadas}[EPSG:{src}]"
apiKey = 'd0xxxxxxxxxxxxxxxxxxxxxxxxxxxxx7'

result = processing.run(
    "OTDEMDownloader:OpenTopography DEM Downloader", {
        'DEMs': 7,
        'Extent': area,
        'API_key': apiKey,
        'OUTPUT': 'TEMPORARY_OUTPUT'})

output_path = result['OUTPUT']
camadaTemp = QgsRasterLayer(output_path, "DEM")

projeto.addMapLayer(camadaTemp)

