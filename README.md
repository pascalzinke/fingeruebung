## Usage

Das analyze.py Script scannt alle XML-Dateien die im Ordner 'data' abgelegt
wurden und erstellt entsprechende CSV-Dateien für Statistiken im 'output' Ordner,
sowieso ein JPG mit einer Grafik für die Satzlängen.

Das visualize.py Script scannt die Bicylces.xml und
Highlights_of_the_Prado_Museum.xml Dateien, sofern sich diese irgendwo im
'data' Ordner befinden, und erstellt jeweils ein JPG im 'output' Ordner.
SPATIAL_ENTITIES werden blau dargestellt, PLACES gelb, QSLINKS grün und
OLINKS rot.