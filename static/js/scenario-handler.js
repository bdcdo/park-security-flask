// Garante que o script só rode após o DOM estar completamente carregado
document.addEventListener('DOMContentLoaded', () => {
    // Seleciona os elementos do DOM que precisam ser atualizados ou interagir
    // É importante que os IDs no HTML correspondam exatamente a estes.
    const progressBar = document.getElementById('progress-bar');
    const scenarioCounter = document.getElementById('scenario-counter');
    const scenarioTitle = document.getElementById('scenario-title');
    const scenarioEmoji = document.getElementById('scenario-emoji');
    const scenarioDescription = document.getElementById('scenario-description');
    const buttonNo = document.getElementById('button-no');
    const buttonYes = document.getElementById('button-yes');

    // Verifica se todos os elementos essenciais foram encontrados
    if (!progressBar || !scenarioCounter || !scenarioTitle || !scenarioEmoji || !scenarioDescription || !buttonNo || !buttonYes) {
        console.error('Erro: Um ou mais elementos do DOM não foram encontrados. Verifique os IDs no HTML.');
        return; // Interrompe a execução se algum elemento estiver faltando
    }

    // Verifica se a URL da API foi definida no HTML
    if (typeof window.handleDecisionUrl === 'undefined') {
        console.error('Erro: A URL da API (window.handleDecisionUrl) não foi definida no template HTML.');
        return; // Interrompe a execução
    }

    // Função para atualizar a interface com os dados do novo cenário
    function updateScenarioUI(data) {
        if (data.is_complete) {
            // Se o jogo acabou, redireciona para a página de resumo
            // A URL é fornecida pelo backend
            window.location.href = data.summary_url;
        } else {
            // Atualiza os elementos da página com os novos dados vindos do JSON
            progressBar.style.width = data.progress + '%';
            scenarioCounter.textContent = `Cenário ${data.current_scenario_number} de ${data.total_scenarios}`;
            scenarioTitle.textContent = data.scenario.title;
            scenarioEmoji.textContent = data.emoji; // Usa o emoji vindo do JSON
            scenarioDescription.textContent = data.scenario.scenario;

            // Reabilita os botões após a atualização bem-sucedida
            buttonNo.disabled = false;
            buttonYes.disabled = false;
            // Opcional: Remover classes de 'loading' se foram adicionadas
            buttonNo.classList.remove('opacity-50', 'cursor-not-allowed');
            buttonYes.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    // Função assíncrona para lidar com a decisão do usuário
    async function handleDecision(decisionValue) {
        // Desabilita os botões para prevenir cliques múltiplos e dá feedback visual
        buttonNo.disabled = true;
        buttonYes.disabled = true;
        // Opcional: Adicionar classes de 'loading' (ex: opacidade)
        buttonNo.classList.add('opacity-50', 'cursor-not-allowed');
        buttonYes.classList.add('opacity-50', 'cursor-not-allowed');

        try {
            // Envia a requisição POST para o backend usando a URL definida no HTML
            const response = await fetch(window.handleDecisionUrl, {
                method: 'POST',
                headers: {
                    // Informa ao Flask que estamos enviando dados de formulário URL-encoded
                    // Isso corresponde ao que request.form espera no Flask
                    'Content-Type': 'application/x-www-form-urlencoded',
                    // NOTA: Se você estivesse usando Flask-WTF com CSRF, precisaria
                    // buscar o token CSRF (geralmente de um campo oculto ou meta tag)
                    // e adicioná-lo ao cabeçalho 'X-CSRFToken'.
                },
                // Envia a decisão como dados de formulário URL-encoded
                body: new URLSearchParams({
                    'decision': decisionValue
                })
            });

            // Verifica se a resposta da rede foi bem-sucedida
            if (!response.ok) {
                // Se a resposta não for OK (ex: 404, 500), lança um erro
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Converte a resposta do corpo para JSON
            const data = await response.json();
            // Atualiza a interface com os dados recebidos
            updateScenarioUI(data);

        } catch (error) {
            // Em caso de erro na requisição ou processamento, loga no console
            console.error('Erro ao processar decisão:', error);
            // Fornece um feedback básico ao usuário
            alert('Ocorreu um erro ao processar sua decisão. Por favor, tente novamente ou recarregue a página.');
            // Reabilita os botões em caso de erro para permitir nova tentativa
            buttonNo.disabled = false;
            buttonYes.disabled = false;
            // Opcional: Remover classes de 'loading'
            buttonNo.classList.remove('opacity-50', 'cursor-not-allowed');
            buttonYes.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    // Adiciona os event listeners aos botões "Não" e "Sim"
    // Quando clicados, eles chamarão a função handleDecision com o valor correspondente
    buttonNo.addEventListener('click', () => handleDecision('no'));
    buttonYes.addEventListener('click', () => handleDecision('yes'));
});
