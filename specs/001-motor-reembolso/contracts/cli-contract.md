# Contrato da CLI — `calcular`

Interface pública do sistema. É o único ponto de contato com o usuário.

## Invocação

```
calcular --input <arquivo.json> --output <arquivo.json> [--em-viagem]
```

Em desenvolvimento (sem instalar o console script):

```
python -m src --input <arquivo.json> --output <arquivo.json> [--em-viagem]
```

## Argumentos

| Argumento | Obrigatório | Tipo | Default | Significado |
|---|---|---|---|---|
| `--input` | sim | caminho | — | Arquivo JSON de entrada com colaborador, período e despesas |
| `--output` | sim | caminho | — | Arquivo JSON a ser escrito com o resultado |
| `--em-viagem` | não | flag booleana | `false` | Se presente, aplica limites ampliados em 50% (RN-009) a todas as despesas do input |

- `--em-viagem` é `store_true`: presença = `true`, ausência = `false`. Não recebe valor.
- O valor de `--em-viagem` sobrepõe/define `em_viagem`; se o input também trouxer
  `em_viagem`, a flag da CLI é a fonte de verdade (o usuário informa em viagem —
  AMB-008). *(Decisão de plano; se preferir que o campo do JSON vença, é troca de 1 linha.)*

## Entrada (arquivo `--input`)

Estrutura conforme `exemplos/despesas-exemplo.json` e Seção 4 da spec:
`colaborador{id,nome,centro_custo}`, `periodo{competencia,inicio,fim}`,
`despesas[]{id,data,categoria,descricao,fornecedor,valor,tem_nota_fiscal}`.
O campo de topo `em_viagem` é opcional.

## Saída (arquivo `--output`)

JSON conforme o exemplo da Seção 4 da spec. Contrato resumido:

```json
{
  "colaborador": { "id": "…", "nome": "…", "centro_custo": "…" },
  "competencia": "YYYY-MM",
  "periodo": { "inicio": "YYYY-MM-DD", "fim": "YYYY-MM-DD" },
  "em_viagem": false,
  "categorias": {
    "alimentacao":       { "total_despesas": 0.00, "total_aceito": 0.00, "total_reembolso": 0.00, "reprovadas": [ { "id": "…", "motivo": "…" } ] },
    "transporte_urbano": { "total_despesas": 0.00, "total_aceito": 0.00, "total_reembolso": 0.00, "reprovadas": [] },
    "hospedagem":        { "total_despesas": 0.00, "total_aceito": 0.00, "total_reembolso": 0.00, "reprovadas": [] }
  },
  "reprovadas_sem_categoria": [ { "id": "…", "categoria_informada": "…", "motivo": "…" } ],
  "total_reembolso_geral": 0.00
}
```

- Todos os valores monetários com **exatamente 2 casas decimais**.
- Acentos preservados (UTF-8, sem escape).
- As três categorias válidas sempre presentes, mesmo com totais zerados.
- Motivos possíveis: `categoria não aplicável`, `data fora da competência`,
  `registro duplicado`, `sem nota fiscal obrigatória`, `valor inválido`,
  `registro inválido`.

## Códigos de saída

| Código | Situação |
|---|---|
| `0` | Sucesso: resultado escrito em `--output` (mesmo que haja despesas reprovadas) |
| `2` | Erro de uso: argumento obrigatório ausente/ inválido (padrão do `argparse`) |
| `1` | Erro irrecuperável de entrada: arquivo `--input` inexistente, JSON de topo inparseável, ou campos de topo obrigatórios ausentes (RN-013). Mensagem em `stderr`, nada escrito em `--output` |

- Registro de despesa malformado **não** aborta: vira `registro inválido` em
  `reprovadas_sem_categoria` e a execução termina com código `0` (RN-013).
- Erros e mensagens vão para `stderr`; `stdout` fica livre (a saída de dados vai
  para o arquivo `--output`).
