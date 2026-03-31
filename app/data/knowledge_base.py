from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class Discipline:
    name: str
    professor: str
    summary: str
    topics: list[str]


@dataclass(frozen=True)
class ServiceInfo:
    topic: str
    guidance: str
    deadline: str
    amount: str | None = None


@dataclass(frozen=True)
class IntentDefinition:
    name: str
    description: str
    examples: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


class AcademicKnowledgeBase:
    """Centraliza os dados usados pelo motor do chatbot."""

    def __init__(self) -> None:
        self.disciplines = {
            "ia aplicada": Discipline(
                name="IA Aplicada",
                professor="Profa. Carla Mendes",
                summary=(
                    "A disciplina apresenta aprendizado de maquina, NLP, visao computacional "
                    "e integracao de modelos em produtos reais."
                ),
                topics=[
                    "classificacao de textos",
                    "representacao vetorial",
                    "transformers",
                    "avaliacao de modelos",
                ],
            ),
            "redes de computadores": Discipline(
                name="Redes de Computadores",
                professor="Prof. Renato Silveira",
                summary=(
                    "Estuda arquiteturas de rede, protocolos, roteamento, seguranca e "
                    "monitoramento de servicos."
                ),
                topics=[
                    "modelo TCP/IP",
                    "enderecamento",
                    "roteamento",
                    "camada de aplicacao",
                ],
            ),
            "processamento de linguagem natural": Discipline(
                name="Processamento de Linguagem Natural",
                professor="Prof. Helena Rocha",
                summary=(
                    "Explora pipeline de texto, classificacao, embeddings, analise semantica "
                    "e uso de transformers em linguagem."
                ),
                topics=[
                    "limpeza textual",
                    "tf-idf",
                    "bert",
                    "avaliacao",
                ],
            ),
        }

        self.services = {
            "historico": ServiceInfo(
                topic="Historico escolar",
                guidance=(
                    "A solicitacao pode ser feita no portal da secretaria em Servicos "
                    "> Documentos > Historico escolar. Depois, confirme os dados e gere o protocolo."
                ),
                deadline="Prazo medio de emissao: 3 dias uteis.",
                amount="Taxa de emissao: R$ 15,00.",
            ),
            "boleto": ServiceInfo(
                topic="Boleto e financeiro",
                guidance=(
                    "O boleto fica disponivel no portal financeiro do aluno. Caso esteja vencido, "
                    "o sistema gera automaticamente a segunda via com juros atualizados."
                ),
                deadline="Vencimento padrao todo dia 10 de cada mes.",
                amount="A multa simulada usada neste exemplo e de 2% mais juros diarios.",
            ),
            "matricula": ServiceInfo(
                topic="Matricula",
                guidance=(
                    "A matricula e feita no portal academico em Matricula online. O aluno escolhe "
                    "as disciplinas, valida os pre-requisitos e confirma a grade."
                ),
                deadline="Periodo academico simulado: de 10/02 a 20/02.",
                amount="Taxa administrativa simulada: R$ 80,00.",
            ),
        }

        self.intents = [
            IntentDefinition(
                name="saudacao",
                description="Cumprimentar o usuario no inicio da conversa.",
                examples=["ola", "oi", "bom dia", "boa tarde", "boa noite"],
                keywords=["ola", "oi", "bom dia", "boa tarde", "boa noite"],
            ),
            IntentDefinition(
                name="despedida",
                description="Encerrar a conversa.",
                examples=["tchau", "ate mais", "valeu", "ate logo"],
                keywords=["tchau", "ate", "valeu", "encerrar"],
            ),
            IntentDefinition(
                name="agradecimento",
                description="Responder agradecimentos.",
                examples=["obrigado", "muito obrigado", "valeu pela ajuda"],
                keywords=["obrigado", "obrigada", "valeu"],
            ),
            IntentDefinition(
                name="secretaria",
                description="Orientar sobre servicos da secretaria.",
                examples=[
                    "como solicito meu historico",
                    "onde peco declaracao",
                    "como funciona a matricula",
                    "preciso do historico escolar",
                ],
                keywords=["historico", "declaracao", "secretaria", "matricula"],
            ),
            IntentDefinition(
                name="financeiro",
                description="Responder sobre pagamentos e boletos.",
                examples=[
                    "qual o prazo do boleto",
                    "boleto venceu",
                    "segunda via do boleto",
                    "qual o valor da matricula",
                ],
                keywords=["boleto", "mensalidade", "financeiro", "valor", "pagamento"],
            ),
            IntentDefinition(
                name="disciplina_info",
                description="Explicar o que se aprende em uma disciplina.",
                examples=[
                    "o que vou aprender em ia aplicada",
                    "me fale de pln",
                    "conteudo de redes de computadores",
                ],
                keywords=["disciplina", "conteudo", "aprender", "ementa", "pln"],
            ),
            IntentDefinition(
                name="professor_info",
                description="Informar o professor responsavel por uma disciplina.",
                examples=[
                    "quem e o professor de redes",
                    "quem ministra ia aplicada",
                    "qual professora de pln",
                ],
                keywords=["professor", "professora", "docente", "ministra"],
            ),
            IntentDefinition(
                name="follow_up",
                description="Pergunta de continuidade baseada no contexto.",
                examples=["e qual o valor", "e o prazo", "como faco isso", "e depois"],
                keywords=["valor", "prazo", "depois", "isso", "qual"],
            ),
        ]

    def iter_intents(self) -> Iterable[IntentDefinition]:
        return self.intents

    def detect_discipline(self, text: str) -> Discipline | None:
        aliases = {
            "ia aplicada": "ia aplicada",
            "inteligencia artificial aplicada": "ia aplicada",
            "redes": "redes de computadores",
            "redes de computadores": "redes de computadores",
            "pln": "processamento de linguagem natural",
            "processamento de linguagem natural": "processamento de linguagem natural",
        }
        for alias, key in aliases.items():
            if alias in text:
                return self.disciplines[key]
        return None

    def detect_service(self, text: str) -> ServiceInfo | None:
        aliases = {
            "historico": "historico",
            "boleto": "boleto",
            "financeiro": "boleto",
            "mensalidade": "boleto",
            "matricula": "matricula",
        }
        for alias, key in aliases.items():
            if alias in text:
                return self.services[key]
        return None
