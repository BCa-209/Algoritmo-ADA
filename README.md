# Algoritmo-ADA

alg.py (núcleo)
    ↑
main.py (flujo completo) → genera → archivos CSV
    ↑
select_quartile.py (herramienta auxiliar) ← lee ← archivos CSV

Algoritmo-ADA/
│
├── __pycache__/
│   ├── alg.cpython-312.pyc
│   └── analizar_datasets.cpython-312.pyc
│
├── data/
│   ├── B2C.csv
│   ├── B4C.csv
│   ├── B8C.csv
│   ├── B16C.csv
│   ├── W2C.csv
│   ├── W4C.csv
│   ├── W8C.csv
│   ├── W16C.csv
│   ├── df_discretizado.csv
│   └── df_original.csv
│
├── graficas_correlacion/
│   ├── correlaciones_B4C.png
│   ├── correlaciones_W4C.png
│   ├── matriz_correlacion_B4C.png
│   ├── matriz_correlacion_W4C.png
│   └── resumen_correlaciones.csv
│
├── grafos/
│   ├── datos_grafo_B4C_mixto.csv
│   ├── datos_grafo_W4C_mixto.csv
│   ├── datos_grafos_consolidado.csv
│   ├── grafo_B4C_mixto.gexf
│   ├── grafo_W4C_mixto.gexf
│   ├── grafo_B4C_mixto.png
│   ├── grafo_W4C_mixto.png
│   ├── metricas_grafo_W4C_mixto.csv
│   ├── metricas_grafos_consolidado.csv
│   └── metricas_grafo_B4C_mixto.csv
│
├── mst_resultados/
│   ├── aristas_importantes_B4C_mixto.csv
│   ├── aristas_importantes_W4C_mixto.csv
│   ├── mst_B4C_mixto.csv
│   ├── mst_W4C_mixto.csv
│   ├── mst_B4C_mixto.png
│   └── mst_W4C_mixto.png
│
├── resultado_correlacion/
│   ├── B4C_mixto.npz
│   └── W4C_mixto.npz
│
├── .gitattributes
├── .gitignore
├── README.md
├── requirements.txt
│
├── alg.py
├── analizar_correlacion.py
├── analizar_datasets.py
├── correlacion.py
├── grafo.py
├── main.py
├── mst_kruskal.py
└── select_quartile.py
