# -*- coding: utf-8 -*-
"""
Aplicação Flask principal para o simulador Park Security.
"""

import os
import uuid # Necessário para gerar IDs de sessão únicos
from typing import Optional

from flask import (Flask, jsonify, redirect, render_template, request,
                   session, url_for)
from supabase import Client, create_client # Importa o cliente Supabase
from dotenv import load_dotenv
import jwt  # Adicionado para debug do token Supabase

# Importa os cenários e a função de emoji do módulo local
from scenarios import SCENARIOS, get_emoji

load_dotenv()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Configura uma chave secreta para gerenciar sessões de forma segura.
# É crucial trocar esta chave por um valor seguro em produção!
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

# --- Configuração do Supabase ---

SUPABASE_URL: str | None = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str | None = os.environ.get("SUPABASE_KEY")
supabase: Client | None = None # Inicializa como None

# Validação básica das credenciais e inicialização do cliente
if not SUPABASE_URL or not SUPABASE_KEY:
    app.logger.warning("Credenciais SUPABASE_URL ou SUPABASE_KEY não configuradas. A integração com Supabase estará desativada.")
else:
    try:
        # Configura o cliente Supabase com headers adicionais para forçar o uso do role "anon"
        # Em algumas versões mais recentes do supabase-py, podemos usar os parâmetros diretamente
        # Verificando versão do supabase-py para fornecer a configuração apropriada
        try:
            from importlib.metadata import version
            supabase_version = version("supabase")
            app.logger.debug(f"Versão do supabase-py: {supabase_version}")
        except:
            supabase_version = "desconhecida"
            app.logger.debug("Não foi possível determinar a versão do supabase-py")
        
        # Tenta criar o cliente com headers explícitos para forçar o role "anon"
        headers = {
            "apikey": SUPABASE_KEY,
            # Forçando o role como anon nas requisições
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        # Criação do cliente tentando diferentes formas dependendo da versão
        try:
            # Primeiro tenta a forma com headers explícitos
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY, headers=headers)
            app.logger.info("Cliente Supabase inicializado com headers personalizados.")
        except TypeError:
            # Se falhar, tenta a forma padrão
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            # E tenta definir os headers depois
            if hasattr(supabase, '_client') and hasattr(supabase._client, 'headers'):
                supabase._client.headers.update(headers)
                app.logger.info("Cliente Supabase inicializado com headers atualizados após criação.")
            else:
                app.logger.info("Cliente Supabase inicializado com configuração padrão.")
                
    except Exception as e:
        app.logger.error(f"Falha ao inicializar o cliente Supabase: {e}")
        supabase = None # Garante que seja None em caso de erro
# --- Fim Configuração do Supabase ---

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
    # Garante que a sessão tenha um UUID persistente
    if 'user_session_uuid' not in session:
        session['user_session_uuid'] = str(uuid.uuid4())
        session.modified = True # Marca como modificada ao adicionar o UUID

    current_index: int = session["current_index"]
    decisions: dict[str, bool] = session["decisions"] # Chave é string agora

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
def handle_decision(): # Removido -> str para retornar Response ou Json
    """
    Processa a decisão do usuário (Sim/Não) para o cenário atual.

    Armazena a decisão na sessão e envia para o Supabase.
    Retorna dados do próximo cenário ou sinal de conclusão em JSON.
    """
    if "current_index" not in session or "decisions" not in session or 'user_session_uuid' not in session:
        # Se a sessão estiver incompleta, redireciona para o início para reinicializar
        app.logger.warning("Sessão incompleta encontrada em /decision. Redirecionando para /.")
        # Retornar um erro JSON pode ser melhor para chamadas fetch
        return jsonify({"error": "Session invalid, please reload.", "redirect": url_for("index")}), 400


    current_index: int = session["current_index"]
    session_modified_flag = False # Flag para marcar se a sessão foi modificada

    # Garante que ainda estamos dentro dos limites dos cenários
    if current_index < TOTAL_SCENARIOS:
        decision_str: Optional[str] = request.form.get("decision")
        scenario_id: int = SCENARIOS[current_index]["id"]
        decision_bool: bool | None = None

        # Converte a decisão para booleano e armazena na sessão
        if decision_str == "yes":
            decision_bool = True
            session["decisions"][str(scenario_id)] = True
            session_modified_flag = True
        elif decision_str == "no":
            decision_bool = False
            session["decisions"][str(scenario_id)] = False
            session_modified_flag = True
        # Se decision_str for None ou inválido, não faz nada e não avança

        # --- Integração Supabase ---
        if supabase and decision_bool is not None: # Verifica se o cliente foi inicializado e a decisão é válida
            try:
                # user_session_uuid já deve existir por causa da rota index
                user_uuid = session['user_session_uuid']

                vote_data = {
                    'scenario_id': scenario_id,
                    'decision': decision_bool,
                    'session_uuid': user_uuid
                }
                app.logger.debug(f"[DEBUG] vote_data: {vote_data}")

                # Debugging do token/cliente Supabase
                try:
                    # Tenta decodificar a chave SUPABASE_KEY para verificar as claims
                    decoded_key = jwt.decode(SUPABASE_KEY, options={"verify_signature": False})
                    app.logger.debug(f"[DEBUG] Decoded SUPABASE_KEY: {decoded_key}")
                    
                    # Tenta acessar as propriedades do cliente Supabase para debug
                    if hasattr(supabase, 'auth') and hasattr(supabase.auth, 'session'):
                        session_info = supabase.auth.session()
                        app.logger.debug(f"[DEBUG] Supabase auth session: {session_info}")
                    
                    # Tentativa de verificar o tipo de chave (anon vs. service_role)
                    if SUPABASE_KEY and SUPABASE_KEY.startswith("eyJ"):
                        app.logger.debug("[DEBUG] SUPABASE_KEY parece ser um token JWT válido")
                    else:
                        app.logger.debug("[DEBUG] SUPABASE_KEY não parece ser um token JWT")
                        
                except Exception as decode_err:
                    app.logger.error(f"[DEBUG] Erro ao decodificar SUPABASE_KEY ou acessar session: {decode_err}")

                # Tenta acessar os headers que serão enviados para entender o role
                try:
                    # Acessa o método interno para obter headers (se disponível)
                    if hasattr(supabase, '_client'):
                        headers = getattr(supabase._client, 'headers', {})
                        app.logger.debug(f"[DEBUG] Supabase client headers: {headers}")
                except Exception as headers_err:
                    app.logger.error(f"[DEBUG] Erro ao acessar headers do cliente: {headers_err}")

                # Assume que sua tabela se chama 'votes'
                # Cria headers explícitos para garantir que o role "anon" seja aplicado na requisição
                insert_headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "X-Client-Info": "supabase-py/debug"
                }
                
                # Tenta o insert com headers explícitos
                try:
                    # Primeiro tenta usar o método .headers() para definir headers para esta operação específica
                    if hasattr(supabase.table('votes'), 'headers'):
                        data, count = supabase.table('votes').headers(insert_headers).insert(vote_data).execute()
                    else:
                        # Se não tiver o método headers(), usa o método padrão
                        data, count = supabase.table('votes').insert(vote_data).execute()
                    
                    app.logger.debug(f"Voto registrado no Supabase para session_uuid {user_uuid}, scenario_id {scenario_id}")

                    # --- Contagem de Votos ---
                    yes_votes = 0
                    no_votes = 0
                    try:
                        # Contagem de votos 'sim' (usando count='exact')
                        yes_count_res = supabase.table('votes').select('id', count='exact').eq('scenario_id', scenario_id).eq('decision', True).execute()
                        yes_votes = yes_count_res.count if yes_count_res.count is not None else 0

                        # Contagem de votos 'não'
                        no_count_res = supabase.table('votes').select('id', count='exact').eq('scenario_id', scenario_id).eq('decision', False).execute()
                        no_votes = no_count_res.count if no_count_res.count is not None else 0

                        app.logger.debug(f"Contagem de votos para scenario {scenario_id}: Sim={yes_votes}, Não={no_votes}")

                    except Exception as agg_err:
                        app.logger.error(f"Erro ao buscar contagem de votos para scenario {scenario_id}: {agg_err}")
                        # Mantém yes_votes e no_votes como 0 (fallback)
                    # --- Fim Contagem de Votos ---

                    # Retorna os resultados para exibição no frontend
                    # NÃO avança o cenário aqui
                    return jsonify({
                        'show_results': True,
                        'scenario_id': scenario_id,
                        'your_decision': decision_bool,
                        'yes_votes': yes_votes,
                        'no_votes': no_votes,
                        'next_scenario_url': url_for('next_scenario') # URL para o próximo passo
                    })

                except Exception as insert_err:
                    # Se falhar, tenta uma abordagem alternativa - usando a API diretamente (se disponível)
                    app.logger.warning(f"Falha no método padrão de insert: {insert_err}")
                    
                    if hasattr(supabase, 'postgrest'):
                        try:
                            # Tenta usar o client postgrest diretamente
                            data, count = supabase.postgrest.from_('votes').insert(vote_data, headers=insert_headers).execute()
                            app.logger.debug(f"Voto registrado via postgrest para session_uuid {user_uuid}, scenario_id {scenario_id}")
                        except Exception as postgrest_err:
                            raise Exception(f"Falha também no insert via postgrest: {postgrest_err}")
                    else:
                        # Se não tiver acesso ao postgrest, reraise a exceção original
                        raise insert_err

            except Exception as e:
                app.logger.error(f"Erro ao salvar voto no Supabase para scenario_id {scenario_id}: {e}")
                # Considerar estratégia de fallback aqui se necessário
                # Por enquanto, apenas logamos o erro, a decisão ainda está na sessão.
                # Se houve erro no Supabase, podemos decidir avançar sem mostrar resultados
                # ou retornar um erro específico. Por ora, vamos deixar avançar.
        # --- Fim Integração Supabase ---

        # Se a decisão foi inválida (None), retorna erro
        if decision_bool is None:
             app.logger.warning("Decisão inválida recebida (None).")
             return jsonify({"error": "Invalid decision provided."}), 400

        # Se chegou aqui, significa que a decisão foi válida, mas ou o Supabase não está ativo
        # ou houve um erro ao salvar/contar votos. Neste caso, avançamos o cenário sem mostrar resultados.
        # (Comportamento original)
        session["current_index"] = current_index + 1
        session.modified = True # Marca a sessão como modificada

        # Recalcula o índice atual após incremento
        current_index = session["current_index"]

        # Verifica se todos os cenários foram concluídos
        if current_index >= TOTAL_SCENARIOS:
            # Retorna um sinal de conclusão e a URL do resumo
            return jsonify({
                'is_complete': True,
                'summary_url': url_for('index') # A rota index lida com o resumo
            })
        else:
            # Obtém os dados do próximo cenário (agora com o índice atualizado)
            next_scenario = SCENARIOS[current_index]
            progress = (current_index / TOTAL_SCENARIOS) * 100
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
    else:
        # Se current_index >= TOTAL_SCENARIOS (já completou)
        app.logger.warning("Recebida decisão quando todos os cenários já foram completados.")
        return jsonify({
            'is_complete': True,
            'summary_url': url_for('index')
        })

@app.route("/next_scenario")
def next_scenario():
    """
    Avança para o próximo cenário na sessão e retorna seus dados.
    Chamado pelo frontend após o usuário visualizar os resultados da votação.
    """
    if "current_index" not in session:
        app.logger.warning("Sessão sem current_index acessando /next_scenario. Redirecionando.")
        # Retornar erro ou redirecionar? Retornar erro é melhor para fetch API.
        return jsonify({"error": "Session invalid, please reload.", "redirect": url_for("index")}), 400

    # Incrementa o índice do cenário
    current_index = session.get("current_index", -1) # Pega o índice atual
    current_index += 1
    session["current_index"] = current_index
    session.modified = True

    app.logger.debug(f"Avançando para o cenário índice: {current_index}")

    # Verifica se todos os cenários foram concluídos
    if current_index >= TOTAL_SCENARIOS:
        app.logger.debug("Todos os cenários concluídos. Retornando is_complete=True.")
        # Retorna um sinal de conclusão e a URL do resumo
        return jsonify({
            'is_complete': True,
            'summary_url': url_for('index') # A rota index lida com o resumo
        })
    else:
        # Obtém os dados do próximo cenário (agora com o índice atualizado)
        try:
            next_scenario_data = SCENARIOS[current_index]
            progress = (current_index / TOTAL_SCENARIOS) * 100
            emoji = get_emoji(next_scenario_data['image'])

            app.logger.debug(f"Retornando dados para o cenário {current_index + 1}")
            # Retorna os dados do próximo cenário em formato JSON
            return jsonify({
                'is_complete': False,
                'scenario': next_scenario_data,
                'progress': progress,
                'current_scenario_number': current_index + 1,
                'total_scenarios': TOTAL_SCENARIOS,
                'emoji': emoji
            })
        except IndexError:
            app.logger.error(f"Erro: Índice {current_index} fora dos limites para SCENARIOS.")
            # Se o índice estiver fora do alcance por algum motivo, trata como completo
            return jsonify({
                'is_complete': True,
                'summary_url': url_for('index')
            })
        except Exception as e:
            app.logger.error(f"Erro inesperado ao preparar próximo cenário: {e}")
            return jsonify({"error": "Internal server error loading next scenario."}), 500


@app.route("/reset")
def reset() -> str:
    """
    Reinicia o jogo limpando o estado da sessão.
    """
    # Remove as chaves relevantes da sessão
    session.pop("current_index", None)
    session.pop("decisions", None)
    session.pop("user_session_uuid", None) # Limpa também o UUID
    session.modified = True # Garante que a limpeza seja salva
    # Redireciona para o início
    return redirect(url_for("index"))

@app.route("/supabase-policy")
def supabase_policy():
    """
    Rota que exibe a política SQL recomendada para a tabela "votes", incluindo permissão de leitura.
    """
    policy_sql = """
-- 1. Criar tabela de votos (se não existir)
CREATE TABLE IF NOT EXISTS public.votes (
  id BIGSERIAL PRIMARY KEY, -- Usar BIGSERIAL é comum no Supabase
  session_uuid UUID NOT NULL, -- Coluna para o UUID da sessão Flask
  scenario_id INTEGER NOT NULL,
  decision BOOLEAN NOT NULL, -- Nome da coluna igual ao enviado pelo Python
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  -- Removido updated_at, pois não é atualizado
  -- Removido user_id e a referência à tabela users
  -- Adicionada restrição UNIQUE para session_uuid e scenario_id
  -- UNIQUE(session_uuid, scenario_id) -- Descomente se quiser impedir votos duplicados da mesma sessão para o mesmo cenário
);

-- Primeiro desativa RLS para evitar conflitos durante a atualização
ALTER TABLE public.votes DISABLE ROW LEVEL SECURITY;

-- Remove políticas antigas que possam estar em conflito
DROP POLICY IF EXISTS "Allow anonymous inserts" ON public.votes;
DROP POLICY IF EXISTS "Allow specific inserts" ON public.votes;
DROP POLICY IF EXISTS "Allow debug inserts" ON public.votes;

-- Cria uma política mais específica que permite inserções para qualquer usuário (anon ou authenticated)
-- com a condição de que os campos obrigatórios estejam presentes
CREATE POLICY "Allow votes inserts"
ON public.votes
FOR INSERT
TO anon, authenticated
WITH CHECK (
    session_uuid IS NOT NULL AND 
    scenario_id IS NOT NULL AND 
    decision IS NOT NULL
);

-- 2. Desativar RLS temporariamente para aplicar políticas
ALTER TABLE public.votes DISABLE ROW LEVEL SECURITY;

-- 3. Remover políticas antigas (se existirem) para evitar conflitos
DROP POLICY IF EXISTS "Allow anonymous inserts" ON public.votes;
DROP POLICY IF EXISTS "Allow specific inserts" ON public.votes;
DROP POLICY IF EXISTS "Allow debug inserts" ON public.votes;
DROP POLICY IF EXISTS "Allow votes inserts" ON public.votes; -- Remove a política de insert antiga se existir
DROP POLICY IF EXISTS "Allow public read access" ON public.votes; -- Remove a política de select antiga se existir

-- 4. Criar política de INSERT (Permite que usuários anônimos/autenticados insiram votos válidos)
CREATE POLICY "Allow votes inserts"
ON public.votes
FOR INSERT
TO anon, authenticated
WITH CHECK (
    session_uuid IS NOT NULL AND
    scenario_id IS NOT NULL AND
    decision IS NOT NULL
);

-- 5. Criar política de SELECT (Permite que usuários anônimos/autenticados leiam dados)
-- IMPORTANTE: Esta política permite ler TODAS as colunas. Se houver dados sensíveis, restrinja as colunas ou adicione condições.
-- Para a funcionalidade de contagem de votos (agregação), esta política é necessária.
CREATE POLICY "Allow public read access"
ON public.votes
FOR SELECT
TO anon, authenticated
USING (true); -- Permite a leitura de todas as linhas por qualquer pessoa

-- 6. Reativar e Forçar RLS na tabela
ALTER TABLE public.votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.votes FORCE ROW LEVEL SECURITY; -- Garante que as políticas sejam aplicadas imediatamente

-- Opcional: Adicionar índices para otimizar consultas de contagem
CREATE INDEX IF NOT EXISTS idx_votes_scenario_decision ON public.votes (scenario_id, decision);
CREATE INDEX IF NOT EXISTS idx_votes_session_scenario ON public.votes (session_uuid, scenario_id); -- Para a restrição UNIQUE (se usada)
"""
    return render_template("sql_policy.html", policy_sql=policy_sql)

@app.route("/debug")
def debug_info():
    """
    Rota de diagnóstico para mostrar informações de configuração e debug do Supabase.
    Útil para troubleshooting da integração com Supabase.
    """
    debug_data = {
        "supabase_configured": supabase is not None,
        "supabase_url_config": bool(SUPABASE_URL),  # Apenas indica se está configurado, sem expor o valor
        "supabase_key_config": bool(SUPABASE_KEY),  # Apenas indica se está configurado, sem expor o valor
    }
    
    # Verifica o tipo de chave e tenta decodificar se for JWT
    if SUPABASE_KEY:
        debug_data["key_type"] = "Parece ser JWT" if SUPABASE_KEY.startswith("eyJ") else "Não parece ser JWT"
        try:
            # Tenta decodificar a chave SUPABASE_KEY para verificar as claims
            decoded_key = jwt.decode(SUPABASE_KEY, options={"verify_signature": False})
            
            # Mostra informações importantes sem expor a chave completa
            safe_claims = {}
            # Lista de claims seguros para exibir
            for claim in ["aud", "role", "iss", "exp", "iat"]:
                if claim in decoded_key:
                    safe_claims[claim] = decoded_key[claim]
            
            debug_data["key_decoded_claims"] = safe_claims
        except Exception as e:
            debug_data["key_decode_error"] = str(e)
    
    # Verifica a existência e acesso ao cliente Supabase
    if supabase:
        # Tentativa de acessar informações do cliente
        try:
            if hasattr(supabase, '_client'):
                # Pega apenas os nomes das chaves dos headers para evitar expor informações sensíveis
                if hasattr(supabase._client, 'headers'):
                    headers = getattr(supabase._client, 'headers', {})
                    debug_data["client_headers_keys"] = list(headers.keys())
            
            # Verifica métodos disponíveis no cliente
            debug_data["has_auth"] = hasattr(supabase, 'auth')
            debug_data["has_auth_session"] = hasattr(supabase, 'auth') and hasattr(supabase.auth, 'session')
            
            # Tenta acessar a sessão se disponível
            if debug_data.get("has_auth_session"):
                try:
                    session_info = supabase.auth.session()
                    if session_info:
                        debug_data["auth_session_info"] = "Disponível (dados omitidos por segurança)"
                except Exception as session_err:
                    debug_data["auth_session_error"] = str(session_err)
        except Exception as client_err:
            debug_data["client_access_error"] = str(client_err)
    
    return jsonify(debug_data)

# Bloco para executar a aplicação em modo de desenvolvimento
if __name__ == "__main__":
    # debug=True ativa o recarregamento automático e mensagens de erro detalhadas
    # host='0.0.0.0' torna o servidor acessível na rede local
    app.run(debug=True, host='0.0.0.0', port=5001) # Usando porta 5001
