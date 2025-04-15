# -*- coding: utf-8 -*-
"""
Aplicação Flask principal para o simulador Park Security.
"""

import os
from typing import Optional # Revisar

from flask import (Flask, jsonify, redirect, render_template, request,
                   session, url_for)

# Importa os cenários e a função de emoji do módulo local
from scenarios import SCENARIOS, get_emoji

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configura uma chave secreta para gerenciar sessões de forma segura.
# É crucial trocar esta chave por um valor seguro em produção!
# Você pode gerar uma usando: python -c 'import os; print(os.urandom(24))'

app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "uma-chave-secreta-padrao-insegura")

# Define o número total de cenários
TOTAL_SCENARIOS = len(SCENARIOS)

@app.route("/")
def index() -> str:
    """
    Rota principal. Exibe o cenário atual ou o resumo final.

    Gerencia o estado do jogo na sessão do usuário.
    """
    # Inicializa o estado na sessão se não existir
    if "current_index" not in session:
        session["current_index"] = 0
    if "decisions" not in session:
        # Armazena decisões como {scenario_id: boolean}
        session["decisions"] = {}

    current_index: int = session["current_index"]
    decisions: dict[int, bool] = session["decisions"]

    # Verifica se todos os cenários foram concluídos
    if current_index >= TOTAL_SCENARIOS:
        # Renderiza a página de resumo
        return render_template(
            "summary.html",
            scenarios=SCENARIOS,
            decisions=decisions,
            get_emoji=get_emoji # Passa a função para o template
        )
    else:
        # Obtém o cenário atual
        current_scenario = SCENARIOS[current_index]
        # Calcula o progresso
        progress = (current_index / TOTAL_SCENARIOS) * 100

        # Renderiza a página do cenário atual
        return render_template(
            "scenario.html",
            scenario=current_scenario,
            progress=progress,
            current_scenario_number=current_index + 1,
            total_scenarios=TOTAL_SCENARIOS,
            get_emoji=get_emoji # Passa a função para o template
        )

@app.route("/decision", methods=["POST"])
def handle_decision() -> str:
    """
    Processa a decisão do usuário (Sim/Não) para o cenário atual.

    Atualiza o estado na sessão e redireciona para o próximo cenário ou resumo.
    """
    if "current_index" not in session or "decisions" not in session:
        # Se a sessão foi perdida, redireciona para o início
        return redirect(url_for("index"))

    current_index: int = session["current_index"]

    # Garante que ainda estamos dentro dos limites dos cenários
    if current_index < TOTAL_SCENARIOS:
        # Obtém a decisão do formulário ('yes' ou 'no')
        decision_str: Optional[str] = request.form.get("decision")
        # Obtém o ID do cenário atual
        scenario_id: int = SCENARIOS[current_index]["id"]

        # Converte a decisão para booleano e armazena na sessão
        if decision_str == "yes":
            session["decisions"][str(scenario_id)] = True # Convertido para string
        elif decision_str == "no":
            session["decisions"][str(scenario_id)] = False # Convertido para string
        # Se decision_str for None ou inválido, não faz nada (poderia adicionar tratamento de erro)

        # Avança para o próximo cenário
        session["current_index"] = current_index + 1

        # Marca a sessão como modificada para garantir que seja salva
        session.modified = True

    # Verifica se todos os cenários foram concluídos
    if current_index >= TOTAL_SCENARIOS:
        # Retorna um sinal de conclusão e a URL do resumo
        return jsonify({
            'is_complete': True,
            'summary_url': url_for('index') # A rota index lida com o resumo
        })
    else:
        # Obtém os dados do próximo cenário
        next_scenario = SCENARIOS[current_index]
        # Calcula o progresso
        progress = (current_index / TOTAL_SCENARIOS) * 100
        # Obtém o emoji correspondente
        emoji = get_emoji(next_scenario['image'])

        # Retorna os dados do próximo cenário em formato JSON
        return jsonify({
            'is_complete': False,
            'scenario': next_scenario,
            'progress': progress,
            'current_scenario_number': current_index + 1,
            'total_scenarios': TOTAL_SCENARIOS,
            'emoji': emoji
        })

@app.route("/reset")
def reset() -> str:
    """
    Reinicia o jogo limpando o estado da sessão.
    """
    # Remove as chaves relevantes da sessão
    session.pop("current_index", None)
    session.pop("decisions", None)
    session.modified = True # Garante que a limpeza seja salva
    # Redireciona para o início
    return redirect(url_for("index"))

# Bloco para executar a aplicação em modo de desenvolvimento
if __name__ == "__main__":
    # debug=True ativa o recarregamento automático e mensagens de erro detalhadas
    # host='0.0.0.0' torna o servidor acessível na rede local
    app.run(debug=True, host='0.0.0.0', port=5001) # Usando porta 5001 para evitar conflitos comuns
