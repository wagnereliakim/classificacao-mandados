import logging
import csv
import os
from shutil import copyfile

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

PATH_CSV = []
SAMPLES = 50
COLUMN_PATH = 4
PATH_CSV_SAMPLE = '../dados/amostra.sample'
PATH_ROOT_ORIGIN = '/mnt/sistema-judicial/processos'
PATH_ROOT_TARGET = '/media/destino/amostra-samples'
CHECK_SIZE = False
ALLOW_OVERRIDE = False


def copiar_por_indice(arquivos):
    index = 0
    total_arquivos = len(arquivos)
    for path in arquivos:
        index = index + 1
        arquivo_origem = "{}{}".format(PATH_ROOT_ORIGIN, path)
        arquivo_pronunciamento = os.path.basename(path)
        diretorio_destino_pronunciamento = "{}{}".format(PATH_ROOT_TARGET, os.path.dirname(path))

        os.makedirs(diretorio_destino_pronunciamento, exist_ok=True)
        arquivo_destino = os.path.join(diretorio_destino_pronunciamento, arquivo_pronunciamento)

        if not os.path.exists(arquivo_destino) or ALLOW_OVERRIDE:
            try:
                copyfile(arquivo_origem, arquivo_destino)
                logger.info('Copiando o arquivo {}/{} - {}'.format(index, total_arquivos, arquivo_origem))
            except OSError as exc:
                logger.exception('Erro ao copiar o arquivo {}/{} - {}'.format(index, total_arquivos, arquivo_origem))
        else:
            logger.warning('Ignorando arquivo {}/{} que já existe em {}'.format(index, total_arquivos, arquivo_destino))


def calcular_tamanho_total(arquivos):
    total_bytes = 0
    index = 0
    for arquivo in arquivos:
        index = index + 1
        arquivo_origem = "{}{}".format(PATH_ROOT_ORIGIN, arquivo)
        try:
            size = os.path.getsize(arquivo_origem)
        except FileNotFoundError as exc:
            size = 0
        total_bytes = total_bytes + size
        logger.info(
            "Tamanho do arquivo {}/{} ({}): {}. Total: {}".format(index, len(arquivos), arquivo, formatar_tamanho(size),
                                                                  formatar_tamanho(total_bytes)))

    return total_bytes


def formatar_tamanho(total_bytes, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(total_bytes) < 1024.0:
            return f"{total_bytes:3.1f}{unit}{suffix}"
        total_bytes /= 1024.0
    return f"{total_bytes:.1f}Yi{suffix}"


# Início execução
for i in range(29, SAMPLES):
    file = "{}.{}.csv".format(PATH_CSV_SAMPLE, i + 1)
    PATH_CSV.append(file)

arquivos = list()

for path in PATH_CSV:
    with open(path, newline='') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            arquivos.append(row[COLUMN_PATH])

if CHECK_SIZE:
    total_bytes = calcular_tamanho_total(arquivos)
    logger.info("#" * 100)
    logger.info("Copiando {} arquivos totalizando {}".format(len(arquivos), formatar_tamanho(total_bytes)))
    logger.info("#" * 100)

if len(arquivos) > 0:
    copiar_por_indice(arquivos)
