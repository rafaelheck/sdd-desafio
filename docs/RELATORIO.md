# Relatório — Desafio SDD

**Aluno:** Rafael Heck · **Repositório:** https://github.com/rafaelheck/sdd-desafio · **Data:** 31/07/2026

> Isto não é redação. São **evidências**. Toda afirmação deve vir acompanhada de
> arquivo, hash de commit ou trecho de sessão exportada. Um parágrafo bonito sem
> evidência vale menos que uma frase curta com um hash.
>
> Vale 20 dos 100 pontos, e é a seção que mais separa notas.

---

## Delegação

*O que você fez, o que o Claude fez, e por que dividiu assim.*

**A divisão:**

| Atividade | Quem | Por quê |
|---|---|---|
| Identificar ambiguidades | Ambos | Fiz a identificação inicial das ambiguidades repassando as decisões iniciais. Utilizei IA para revisar as que encontrei e buscar novas ambiguidades |
| Decidir as ambiguidades | Eu | Para garantir que a resolução de cada ambiguidade esteja coerente com o meu planejamento de como o produto deve funcionar |
| Escrever a spec | Ambos | Eu oriento, a IA aplica. O texto bruto foi escrito pela IA, porém eu guio o que deve ser escrito, indico quais as regras do produto e exemplos, reviso o que foi feito e se não estiver de acordo, oriento o que deve ser ajustado e como |
| Desenhar a arquitetura | Ambos | Por se tratar de um projeto relativamente simples, defini apenas regras básicas como tratamento de regras bem definidas em funções separadas para facilitar code review e funções de calculos separadas para reuso e validação, mas sem definir uma arquitetura de código ou de sistema em específico |
| Implementar | IA | Não toquei em código, apenas testei e revisei. Precisando de ajustes, refiz o passo de spec, plan, task e a IA implementa a diferença |
| Escrever testes | IA | Testes foram escritos baseados nas regras de negócio da spec, com o numero da regra no nome do teste, facilitando a revisão |
| Absorver o envelope | Ambos | Definição inicial de regras de negócio e decisões de ambiguidades que encontrei tomadas por mim. IA revisa o que orientei, aponta novas ambiguidades e eu decido as ações a serem tomadas a partir dai. |

**Onde deleguei e me arrependi:**
Não me recordo de nada que tenha delegado e me arrependido. Para sistemas mais robustos, provavelmente gostaria de estar mais presente nas definições de arquitetura.

**Onde não deleguei e deveria ter delegado:**
Como estou utilizando o speckit, poderia ter utilizado melhor as funcionalidades de analyze e checklist, utilizei apenas no fim do projeto, acredito que teria ajudado nas revisões iniciais.

**Usei subagentes / skills / MCP / hooks?** <se sim: o quê, como configurou,
valeu a pena. Se não: por que não.>
Utilizei apenas o speckit, para testar o toolkit fora de projetos do cliente e agilizar o processo.
Configuração basica especificada na própria doc do speckit, apenas inclui os templates de spec, plan e task no .specify/template/overrides para que ele siga os templates do desafio.

---

## Descrição

*Como você transformou requisito ambíguo em requisito verificável.*

Pegue **um** requisito ambíguo da política do RH e mostre a evolução:

**Versão 1 (minha primeira escrita):**
> ```
> <cole>
> ```

**Versão final:**
> ```
> <cole>
> ```

**O que estava ambíguo:**

**Como percebi:** <testando? o Claude perguntou? bateu o olho no JSON de exemplo
e não soube dizer qual era a resposta certa?>

**Commit da mudança:** `<hash>`

---

## Discernimento

*Onde o Claude errou e você pegou.*

> **Sem um caso concreto e verificável, esta seção vale zero.** Não existe projeto
> de dois dias em que o modelo acertou tudo. A ausência do caso não prova que o
> modelo foi perfeito — prova que ninguém estava conferindo.

### Caso 1

**O que ele propôs:**
No inicio do projeto, propus que existiam apenas 3 categorias fixas
 - hospedagem
 - alimentacao
 - transporte_urbano

Para se adequar a nova regra de categorias por centro de custo, na sessão 06-nova-regra-centro-de-custo.md, foi especificado que as categorias a serem consideradas agora estariam dispostas no arquivo politica-v4.json.

Quase toda a spec foi atualizada de acordo, porém as 3 regras de negócio especificas para hospedagem, alimentacao e transporte_urbano ainda estavam na spec.

**Por que estava errado:**
Não foram removidas referencias a regras que anteriormente eram fixas, citando diretamente categorias que o sistema não deve ter conhecimento e que podem ser atualizadas a qualquer momento, deixando a spec defasada e com o risco do sistema fixar em código informações que deveriam ser volateis.

**Como eu detectei:** <li o diff? o teste quebrou? só percebi dias depois?
"como detectei" é a informação mais útil deste relatório inteiro>
Detectei durante a revisão da spec após rodar a sessão 06-nova-regra-centro-de-custo.md

**O que eu fiz:**
No inicio da sessão 07-spec-plan-tasks-novas-regras.md, especifiquei que as regras RN-002, RN-003 e RN-004 precisavam ser ajustadas, especificando que o sistema é agnostico as categorias e que toda informação sobre categorias existentes virá do arquivo externo politica-v4.json 

**Onde está a evidência:** `docs/sessions/<arquivo>`, trecho `<...>`
Primeiro prompt de docs/session/07-spec-plan-tasks-novas-regras.md

### Caso 2 *(opcional)*

**Padrão que eu notei:** <em que tipo de tarefa ele erra mais? teve um sinal
recorrente que passou a te deixar em alerta?>

---

## Diligência

*O que você verificou antes de aceitar.*

**Meu procedimento de verificação:** <o que você de fato fazia — não o que
deveria ter feito>
Para spec/plan/task, revisei através do diff, checando se estava de acordo com as minhas decisões.
Utilizei clarify do speckit para tentar encontrar novas ambiguidades após a minha revisão.
No fim do projeto, utilizei também analyze para validar se as informações estavam consistentes.

**Li o diff inteiro em que porcentagem das entregas?** <seja honesto; a
honestidade aqui vale ponto e a maquiagem custa>
Gastei mais tempo revisando principalmente spec e plan.
Tasks revisei pontualmente.
Código revisei muito pouco.

**O que aceitei sem verificar direito, e o que me custou:**
Aceitei toda a implementação de código revisando muito pouco. O que me custa é não ter um conhecimento mais a fundo do código em si. Um conhecimento mais profundo poderia ser necessário em um cenário onde precise resolver algum bug que a IA não está resolvendo.

**Testes: quem escreveu, e como você sabe que eles testam a coisa certa?**
<teste escrito pelo mesmo agente que escreveu o código passa com muita facilidade>
Teste escrito pela IA, cada teste está atrelado a uma regra de negócio da spec, o que facilita comparar o que está sendo testado com a regra de negócio definida.
Testes não foram feitos em um contexto e agente separado, pode ter impactado negativamente na confiabilidade dos testes.

---

## O envelope

*A mudança de requisito do Dia 2.*

**Quantos arquivos toquei na mão:** `<0>`
**Quanto tempo levou:** `<...>`
**Diff de absorção:** `<n> arquivos, +<n>/-<n> linhas` (`git diff <hash-antes> HEAD --stat`)

**Absorveu de graça:** <o que a arquitetura já suportava e por quê>

**Resistiu:** <o que teve que ser quebrado e por quê>

**Ordem em que fiz:** <spec → tasks → código? ou código → spec? seja honesto:
a correção vê os timestamps dos commits de qualquer forma>

**Se eu tivesse escrito a spec original sabendo desta mudança:**

**O que a spec me poupou, em concreto:**

---

## Fechamento

**Para qual tamanho de projeto isto valeu a pena?**

**Para qual não valeria?**

**O que eu faria diferente:**

**A coisa mais desconfortável que aprendi sobre como eu trabalho com IA:**
