def generate_csv():
    import psycopg
    import pandas as pd

    DBNAME = '###'
    HOST = '###'
    PORT = '###'
    USER = '###'
    PASSWORD = '###'

    connection = psycopg.connect(
        dbname=DBNAME,
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD
    )
    query = """SELECT
                    DISTINCT ON (mov_ordem_magistrado.coddocumento, cc.codcumprimento)
                    mov_ordem_magistrado.coddocumento mov_ordem_coddocumento,
                    mov_ordem_magistrado.numerounico numero_processo,
                    mov_ordem_magistrado.datarecebimento mov_ordem_datarecebimento,
                    mov_ordem_magistrado.login mov_ordem_login,
                    ad_mov_ordem_magistrado.caminho ad_mov_ordem_magistrado_caminho,
                    ad_mov_ordem_magistrado.descricao ad_mov_ordem_magistrado_descricao,
                    mov_ordem_magistrado.cod_vara,
                    mov_ordem_magistrado.nome_vara,
                    mov_ordem_magistrado.competencia_vara,
                    nm.codnaturezamandado cod_natureza_mandado,
                    nm.descricao desc_natureza_mandado,
                    mov_exped_mandado.datarecebimento mov_exped_datarecebimento,
                    ad_mov_exped_mandado.caminho ad_mov_exped_mandado_caminho,
                    ad_mov_exped_mandado.descricao ad_mov_exped_mandado_descricao,
                    pt.nome as parte_nome,
                    CASE pp.tipoparte
                        WHEN 0 THEN 'PROMOVENTE'
                        WHEN 1 THEN 'PROMOVIDO'
                        WHEN 2 THEN 'VITIMA'
                        WHEN 3 THEN 'TESTEMUNHA'
                        WHEN 4 THEN 'TERCEIRO'
                        WHEN 5 THEN 'SENTENCIADO'
                        WHEN 6 THEN 'JURADO'
                    END AS parte_tipo,
                    1 as i			
                FROM (
                    SELECT
                        movimentacao.*,
                        processo.numerounico,
                        vara_competencia.cod_vara AS cod_vara,
                        vara_competencia.descricao AS nome_vara,
                        vara_competencia.competencia AS competencia_vara
                    FROM movimentacao
                    INNER JOIN logon ON movimentacao.login=logon.login
                    INNER JOIN processo ON processo.numeroprocesso=movimentacao.numeroprocesso
                    INNER JOIN (
                        SELECT 
                            cod_vara, replace(replace(descricao, ' - Competência Criminal', ''), ' - Competência Cível', '') as descricao,
                            CASE 
                                WHEN cod_vara IN (1017046) THEN 'JESPCrim'
                                WHEN cod_vara IN (6017044,6017146,6017145,6017043) THEN 'JVD'
                                WHEN cod_vara IN (1086073,1086016) THEN 'VarFam'
                                WHEN cod_vara IN (6017026,6017025,6017027) THEN 'VarCrim'
                                WHEN cod_vara IN (1001049,16,1001056,1001064,6017022,6017023) THEN 'VarCiv'
                                WHEN cod_vara IN (1017037,1017011,1017029) THEN 'JESPCiv'
                            ELSE 'OUTRA' END competencia
                        FROM vara
                        WHERE cod_vara IN (
                            1017046, -- JESP Criminal
                            6017044,6017146,6017145,6017043, -- Juizado Violencia Domestica
                            1086073,1086016, -- Varas de Familia
                            6017026,6017025,6017027, -- Varas Criminais
                            1001049,16,1001056,1001064,6017022,6017023, -- Varas Civeis
                            1017037,1017011,1017029, -- JESP Civel
                            -1
                        )
                    ) AS vara_competencia ON movimentacao.codvaraserealizou=vara_competencia.cod_vara
                    WHERE movimentacao.status=0
                    AND logon.grupo=10
                    AND processo.codclasseprocessual NOT IN (261) -- Remove Carta Precatoria
                    AND movimentacao.datarecebimento BETWEEN '2017-01-01 00:00:00' AND '2021-12-31 23:59:59'
                ) AS mov_ordem_magistrado
                INNER JOIN movimentacao_arquivo_documento mad_mov_ordem_magistrado ON mad_mov_ordem_magistrado.coddocumento = mov_ordem_magistrado.coddocumento AND mad_mov_ordem_magistrado.situacao = 0
                INNER JOIN arquivo_documento ad_mov_ordem_magistrado ON ad_mov_ordem_magistrado.codarquivo=mad_mov_ordem_magistrado.codarquivo
                LEFT JOIN cumprimento_cartorio cc ON mov_ordem_magistrado.coddocumento= cc.coddocumento AND tipocumprimento=7
                LEFT JOIN natureza_mandado nm ON cc.codnaturezamandado=nm.codnaturezamandado
                LEFT JOIN movimentacao mov_exped_mandado ON mov_exped_mandado.coddocumento = cc.codmovimentoexpedicao AND mov_exped_mandado.status=0
                LEFT JOIN movimentacao_arquivo_documento mad_mov_exped_mandado ON mad_mov_exped_mandado.coddocumento = mov_exped_mandado.coddocumento AND mad_mov_exped_mandado.situacao = 0
                LEFT JOIN arquivo_documento ad_mov_exped_mandado ON ad_mov_exped_mandado.codarquivo=mad_mov_exped_mandado.codarquivo
                LEFT JOIN cumprimento_cartorio_parte_processo ccpp ON ccpp.codcumprimentocartorio=cc.codcumprimento
                LEFT JOIN partes_processo pp ON ccpp.codparteprocesso=pp.codparteprocesso
                LEFT JOIN parte pt ON pp.codparte=pt.codparte
                WHERE TRUE
                ORDER BY mov_ordem_magistrado.coddocumento, cc.codcumprimento
            """

    data = pd.read_sql_query(query, connection)
    connection.close()

    data.to_csv('dados/amostra.csv', index=False)

generate_csv()




# def generate_chart_tendencia():
#    import matplotlib.pyplot as plt
#    import numpy as np
#    import pandas as pd
#
#     data = pd.read_csv('./data.csv')
#
#     x = np.arange(1, len(data) + 1, 1)
#     y = data['quantidade'].to_numpy()
#     print(x)
#     print(y)
#
#     plt.plot(x, y)
#     plt.show()
#
# generate_chart_tendencia()