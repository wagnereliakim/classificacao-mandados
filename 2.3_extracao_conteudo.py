import csv
import logging
import pandas as pd
from well.pdf import extrair_texto

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

START = 1
SAMPLES = 10
BASE_PATH = '/media/destino/amostra-samples'

# Início execução
for sample in range(START, SAMPLES + 1):
    input_file = "../dados/amostra.sample.{}.csv".format(sample)
    output_file = "../dados/amostra.sample.{}.com_texto.sem_header.csv".format(sample)

    to_skip = []

    df = pd.read_csv(input_file)

    # df = df.sample(n=5, random_state=80, ignore_index=True)
    # data = ['/2021/ago/22/8/2280a179f0d3f298136c2ba7a0c7cc09.p7z'] # Possui margem diferente
    # data = ['/2020/fev/68/f/68fd7fec634e6e90f4ef48df9d317fdd.p7z'] # Está duplicando letras: ZZAAGGAALLLLOO, ttteeerrrmmmooosss
    # df = pd.DataFrame(data, columns=['ad_mov_ordem_magistrado_caminho'])

    amostra_size = len(df)
    df['texto'] = df \
        .query('ad_mov_ordem_magistrado_caminho not in @to_skip') \
        .apply(lambda path: (logger.info(f"Arquivo {sample} - {path.name + 1}/{amostra_size} - {path['ad_mov_ordem_magistrado_caminho']}"),
                             extrair_texto(BASE_PATH + path['ad_mov_ordem_magistrado_caminho'], lib='plumber')
                            )[1], axis=1)

    df.to_csv(output_file, index=False, encoding='utf-8', quotechar='"',
              quoting=csv.QUOTE_NONNUMERIC, escapechar='\\')
