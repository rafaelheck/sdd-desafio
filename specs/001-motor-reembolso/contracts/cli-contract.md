# Contrato da CLI — `calcular`

Interface pública do sistema (spec 1.4). Único ponto de contato com o usuário.
Mudanças desde 1.1: **removido `--em-viagem`** (viagem é por registro, RN-009);
**adicionados** `--politica`/`--cambio` (opcionais); a saída **não** tem mais `em_viagem`;
o câmbio ausente/inválido **aborta**.

## Invocação

```
calcular --input <arquivo.json> --output <arquivo.json> [--politica <arquivo.json>] [--cambio <arquivo.json>]
```

Em desenvolvimento (sem instalar o console script):

```
python -m src --input <arquivo.json> --output <arquivo.json> [--politica ...] [--cambio ...]
```

## Argumentos

| Argumento | Obrigatório | Tipo | Default | Significado |
|---|---|---|---|---|
| `--input` | sim | caminho | — | JSON de entrada: colaborador, período e despesas |
| `--output` | sim | caminho | — | JSON a ser escrito com o resultado |
| `--politica` | não | caminho | `src/informacoes_externas/politica-v4.json` | Política externa de categorias/limites por CC (RN-015) |
| `--cambio` | não | caminho | `src/informacoes_externas/cambio.json` | Tabela de câmbio: `moeda_base` + `taxas` por data (RN-018) |

- Sem regra de negócio na CLI. Os defaults resolvem os arquivos empacotados relativos ao pacote `src`.
- Não há mais flag `--em-viagem`; a condição de viagem é derivada por registro pela `moeda` (RN-009).

## Entrada (arquivo `--input`)

Conforme `exemplos/despesas-exemplo.json`, `exemplos/despesas-envelope.json` e Seção 4:
`colaborador{id,nome,centro_custo}`, `periodo{competencia,inicio,fim}`,
`despesas[]{id,data,categoria,descricao,fornecedor,valor,tem_nota_fiscal, moeda?}`.
O campo `despesas[].moeda` é **opcional** (ausente/`null`/vazio = moeda base, sem conversão).
**Não** há mais campo de topo `em_viagem`.

## Saída (arquivo `--output`)

JSON conforme os exemplos das Seções 4 da spec. Contrato resumido (categorias **dinâmicas** por CC):

```json
{
  "colaborador": { "id": "…", "nome": "…", "centro_custo": "…" },
  "competencia": "YYYY-MM",
  "periodo": { "inicio": "YYYY-MM-DD", "fim": "YYYY-MM-DD" },
  "categorias": {
    "<categoria válida do CC com ≥1 despesa>": {
      "total_despesas": 0.00, "total_aceito": 0.00, "total_reembolso": 0.00,
      "reprovadas": [ { "id": "…", "motivo": "…" } ]
    }
  },
  "reprovadas_sem_categoria": [ { "id": "…", "categoria_informada": "…", "motivo": "…" } ],
  "total_reembolso_geral": 0.00
}
```

- **Sem** campo `em_viagem`.
- Todos os valores monetários com **exatamente 2 casas decimais**, na **moeda base** (BRL) já convertida.
- Acentos preservados (UTF-8, sem escape).
- O bloco `categorias` lista **só** as categorias válidas do CC com ≥1 despesa (AMB-015), na ordem das
  chaves do CC resolvido na política (DT-011). Categorias configuradas sem despesas não aparecem.
- Motivos possíveis: `categoria não aplicável`, `data fora da competência`, `registro duplicado`,
  `sem nota fiscal obrigatória`, `valor inválido`, `registro inválido`, `cambio não identificado`, ou a
  `observacao` da categoria (limite ≤ 0).

## Códigos de saída

| Código | Situação |
|---|---|
| `0` | Sucesso: resultado escrito em `--output` (mesmo com despesas reprovadas) |
| `2` | Erro de uso: argumento obrigatório ausente/inválido (padrão do `argparse`) |
| `1` | Erro irrecuperável: `--input`, `--politica` ou `--cambio` inexistente ou com JSON inparseável; JSON de topo do input inválido; ou campos de topo obrigatórios ausentes (RN-013, RN-018). Mensagem em `stderr`, nada escrito em `--output` |

- Registro de despesa malformado **não** aborta: vira `registro inválido` em `reprovadas_sem_categoria`,
  execução termina com `0` (RN-013).
- Uma `moeda` sem taxa em todo o câmbio **não** aborta: vira `cambio não identificado` por registro
  (RN-020). Já o **arquivo** de câmbio ausente/inparseável aborta com `1` (RN-018).
- Erros vão para `stderr`; `stdout` fica livre (dados vão para `--output`).
