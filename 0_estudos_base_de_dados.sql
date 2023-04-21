ROLLBACK TO active_records;

ROLLBACK; -- drops the temp table
BEGIN; -- start transaction

--Classifica as competencias das Varas
CREATE TEMPORARY TABLE vara_competencia
  ON COMMIT DROP 
AS
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
);
--Extrai todas as movimentacoes do periodo selecionado 2017 a 2021
CREATE TEMPORARY TABLE movimentacao_periodo
  ON COMMIT DROP 
AS
SELECT
	movimentacao.*,
	processo.numerounico,
	vara_competencia.cod_vara AS cod_vara,
	vara_competencia.descricao AS nome_vara,
	vara_competencia.competencia AS competencia_vara
FROM movimentacao
INNER JOIN logon ON movimentacao.login=logon.login
INNER JOIN processo ON processo.numeroprocesso=movimentacao.numeroprocesso
INNER JOIN vara_competencia ON movimentacao.codvaraserealizou=vara_competencia.cod_vara
WHERE movimentacao.status=0
AND logon.grupo=10
AND processo.codclasseprocessual NOT IN (261) -- Remove Carta Precatoria
AND movimentacao.datarecebimento BETWEEN '2017-01-01 00:00:00' AND '2021-12-31 23:59:59';
SAVEPOINT active_records


-- ####################
-- ## INICIO DOS ESTUDOS
-- ####################

-- Quantidade de Mandados por Competencia
SELECT
	vara_competencia.competencia,
	COUNT(*) AS qtd
FROM cumprimento_cartorio
INNER JOIN vara_competencia ON vara_competencia.cod_vara=codvaraserealizou
WHERE tipocumprimento=7
AND DATE_PART('YEAR', cumprimento_cartorio.datadistribuicaooficialjustica) BETWEEN 2017 AND 2021
GROUP BY 1
ORDER BY qtd DESC;

-- Quantidade de Mandados por Vara
SELECT
	vara_competencia.descricao,
	COUNT(*) AS qtd
FROM cumprimento_cartorio
INNER JOIN vara_competencia ON vara_competencia.cod_vara=codvaraserealizou
WHERE tipocumprimento=7
AND DATE_PART('YEAR', cumprimento_cartorio.datadistribuicaooficialjustica) BETWEEN 2017 AND 2021
GROUP BY 1
ORDER BY qtd DESC;


-- Quantidade de Manifestacao do Juiz por Vara
SELECT vara_competencia.descricao,
	count(*) as qtd,
	round(count(*) * 0.05) as cinco_por_cento,
	round(count(*) * 0.01) as um_por_cento
FROM movimentacao_periodo
INNER JOIN vara_competencia ON movimentacao_periodo.codvaraserealizou=vara_competencia.cod_vara
GROUP BY 1
ORDER BY qtd DESC;

SELECT COUNT(*) FROM movimentacao_periodo

--Selecao da amostra
SELECT COUNT(*) FROM (

	SELECT
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
	FROM movimentacao_periodo mov_ordem_magistrado
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
	
) X


COMMIT; -- drops the temp table







SELECT
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
	LIMIT 10
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
