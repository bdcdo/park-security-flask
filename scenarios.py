# -*- coding: utf-8 -*-
"""
Define os cenários para a aplicação Park Security.

Cada cenário é um dicionário com:
- id: Identificador único.
- title: Título curto do cenário.
- scenario: Descrição da situação para o usuário decidir.
- image: Uma chave para identificar o emoji/imagem associado.
"""

SCENARIOS = [
    {
        "id": 1,
        "title": "Skate",
        "scenario": "Um adolescente se aproxima da entrada do parque andando de skate. Você permitiria que ele entrasse no parque com o skate?",
        "image": "skateboard",
    },
    {
        "id": 2,
        "title": "Cadeira de Rodas",
        "scenario": "Uma pessoa usando cadeira de rodas quer entrar no parque. Você permitiria a entrada dela?",
        "image": "wheelchair",
    },
    {
        "id": 3,
        "title": "Carrinho de Bebê",
        "scenario": "Um pai com um carrinho de bebê está na entrada do parque. Você permitiria que ele entrasse com o carrinho?",
        "image": "baby-carriage",
    },
    {
        "id": 4,
        "title": "Memorial de Guerra",
        "scenario": "Há uma proposta para instalar um jipe militar desativado como memorial de guerra dentro do parque. Você aprovaria esta instalação apesar da regra 'Proibido Veículos'?",
        "image": "jeep",
    },
    {
        "id": 5,
        "title": "Bicicleta",
        "scenario": "Um ciclista quer atravessar o parque em sua bicicleta. Você permitiria que ele entrasse com a bicicleta?",
        "image": "bicycle",
    },
    {
        "id": 6,
        "title": "Patinete Elétrico",
        "scenario": "Alguém em um patinete elétrico quer entrar no parque. Você permitiria a entrada com o patinete?",
        "image": "scooter",
    },
    {
        "id": 7,
        "title": "Carrinho de Brinquedo",
        "scenario": "Uma criança com um carrinho de controle remoto quer brincar com ele no parque. Você permitiria o carrinho de brinquedo no parque?",
        "image": "toy-car",
    },
    {
        "id": 8,
        "title": "Drone",
        "scenario": "Uma pessoa quer voar com um drone recreativo sobre o parque sem que ele toque o solo. Você permitiria esta atividade no parque?",
        "image": "drone",
    },
    {
        "id": 9,
        "title": "Patins",
        "scenario": "Uma pessoa usando patins quer patinar pelos caminhos do parque. Você permitiria a entrada dela com os patins?",
        "image": "skates",
    },
    {
        "id": 10,
        "title": "Cavalo",
        "scenario": "Alguém montado em um cavalo quer passar pelos caminhos do parque. Você permitiria o cavalo no parque?",
        "image": "horse",
    },
    {
        "id": 11,
        "title": "Simulador de Direção",
        "scenario": "Um simulador de direção será instalado temporariamente para uma campanha de segurança no trânsito. Você permitiria esta instalação no parque?",
        "image": "simulator",
    },
    {
        "id": 12,
        "title": "Barco a Remo",
        "scenario": "Alguém quer usar um barco a remo em um lago dentro do parque. Você permitiria o barco no lago do parque?",
        "image": "rowboat",
    },
    {
        "id": 13,
        "title": "Ambulância",
        "scenario": "Uma ambulância precisa entrar no parque para atender uma emergência médica. Você permitiria a entrada da ambulância?",
        "image": "ambulance",
    },
    {
        "id": 14,
        "title": "Carro Fúnebre",
        "scenario": "Um carro fúnebre precisa entrar para um funeral em uma capela dentro do parque. Você permitiria a entrada do carro fúnebre?",
        "image": "hearse",
    },
    {
        "id": 15,
        "title": "Robô de Entrega",
        "scenario": "Um robô de entrega autônomo quer passar pelo parque para fazer uma entrega. Você permitiria a entrada do robô?",
        "image": "robot",
    },
    {
        "id": 16,
        "title": "Trenó com Cães",
        "scenario": "Uma pessoa quer usar um trenó puxado por cães no parque durante o inverno. Você permitiria o trenó no parque?",
        "image": "sled",
    },
    {
        "id": 17,
        "title": "Exoesqueleto Motorizado",
        "scenario": "Uma pessoa usando um exoesqueleto motorizado por razões médicas quer entrar no parque. Você permitiria a entrada dela com o exoesqueleto?",
        "image": "exoskeleton",
    },
]

EMOJI_MAP: dict[str, str] = {
    "skateboard": "🛹",
    "wheelchair": "♿",
    "baby-carriage": "👶🏼🧸",
    "jeep": "🪖🚙",
    "bicycle": "🚲",
    "scooter": "🛴",
    "toy-car": "🧸🚗",
    "drone": "🚁",
    "skates": "⛸️",
    "horse": "🐎",
    "simulator": "🎮🚗",
    "rowboat": "🚣",
    "ambulance": "🚑",
    "hearse": "⚰️🚙",
    "robot": "🤖📦",
    "sled": "🐕🛷",
    "exoskeleton": "🦾👨",
}

def get_emoji(image_key: str) -> str:
    """Retorna o emoji correspondente à chave da imagem."""
    return EMOJI_MAP.get(image_key, "❓")
