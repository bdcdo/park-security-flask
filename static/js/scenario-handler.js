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
    // Seletores para a seção de resultados e botão Próximo
    const voteResultsDiv = document.getElementById('vote-results');
    const buttonNext = document.getElementById('button-next');
    // Não precisamos mais de decisionButtonsContainer


    // Verifica se todos os elementos essenciais do cenário foram encontrados
    // A verificação dos elementos de resultado será feita dentro da função handleDecision
    if (!progressBar || !scenarioCounter || !scenarioTitle || !scenarioEmoji || !scenarioDescription || !buttonNo || !buttonYes || !voteResultsDiv || !buttonNext) {
        console.error('Erro: Um ou mais elementos essenciais do DOM do cenário não foram encontrados. Verifique os IDs no HTML.');
        return; // Interrompe a execução se algum elemento estiver faltando
    }
    // Removemos a leitura da versão do layout

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
            // Garante estado inicial correto ao carregar novo cenário
            voteResultsDiv.classList.add('hidden'); // Esconde resultados
            buttonNext.classList.add('hidden'); // Esconde botão próximo
            // Mostra os botões de decisão diretamente
            buttonNo.classList.remove('hidden');
            buttonYes.classList.remove('hidden');


            // Reabilita botões Sim/Não
            buttonNo.disabled = false;
            buttonNo.classList.remove('opacity-50', 'cursor-not-allowed');
            buttonYes.disabled = false;
            buttonYes.classList.remove('opacity-50', 'cursor-not-allowed');
            // Reabilita botão Próximo (será escondido logo em seguida se não houver erro)
            buttonNext.disabled = false;
            buttonNext.classList.remove('opacity-50', 'cursor-not-allowed');


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

            // Verifica se a resposta indica para mostrar resultados
            if (data.show_results) {
                // Esconde os botões Sim/Não diretamente
                buttonNo.classList.add('hidden');
                buttonYes.classList.add('hidden');


                // Seleciona os novos elementos das barras e contagens DENTRO deste bloco
                const yourVoteText = document.getElementById('your-vote-text');
                const yesBar = document.getElementById('yes-bar');
                const noBar = document.getElementById('no-bar');
                const yesPercentageSpan = document.getElementById('yes-percentage');
                const noPercentageSpan = document.getElementById('no-percentage');
                const yesCountSpan = document.getElementById('yes-count');
                const noCountSpan = document.getElementById('no-count');

                // Verifica se os elementos da barra de votação foram encontrados
                if (!yourVoteText || !yesBar || !noBar || !yesPercentageSpan || !noPercentageSpan || !yesCountSpan || !noCountSpan) {
                    console.error("Erro: Elementos da barra de votação não encontrados no DOM. Verifique os IDs em scenario.html.");
                    // Tenta reabilitar botões Sim/Não para evitar travamento, mesmo que escondidos
                    buttonNo.disabled = false;
                    buttonYes.disabled = false;
                    buttonNo.classList.remove('opacity-50', 'cursor-not-allowed');
                    buttonYes.classList.remove('opacity-50', 'cursor-not-allowed');
                    // Mostra os botões Sim/Não novamente se a UI de resultados falhar
                    buttonNo.classList.remove('hidden');
                    buttonYes.classList.remove('hidden');
                    alert('Ocorreu um erro ao exibir os resultados. Por favor, tente recarregar.');
                    return; // Interrompe se elementos cruciais faltarem
                }

                // Atualiza o texto do voto do usuário
                yourVoteText.textContent = `Você votou ${data.your_decision ? 'Sim 👍' : 'Não 👎'}. Veja como os outros votaram:`;

                const totalVotes = data.yes_votes + data.no_votes;
                let yesPercentage = 0;
                let noPercentage = 0;

                if (totalVotes > 0) {
                    yesPercentage = Math.round((data.yes_votes / totalVotes) * 100);
                    noPercentage = 100 - yesPercentage; // Garante que some 100%
                } else {
                    // Caso especial: primeiro voto (ou nenhum voto ainda)
                    // Define a barra correspondente ao voto do usuário como 100% visualmente
                    if (data.your_decision) {
                        yesPercentage = 100;
                        noPercentage = 0;
                    } else {
                        yesPercentage = 0;
                        noPercentage = 100;
                    }
                }


                // Atualiza a largura das barras
                yesBar.style.width = `${yesPercentage}%`;
                noBar.style.width = `${noPercentage}%`;

                // Atualiza o texto das porcentagens (mostra apenas se for > 10%)
                yesPercentageSpan.textContent = yesPercentage > 10 ? `${yesPercentage}%` : '';
                noPercentageSpan.textContent = noPercentage > 10 ? `${noPercentage}%` : '';

                // Atualiza a contagem de votos
                yesCountSpan.textContent = `Sim: ${data.yes_votes}`;
                noCountSpan.textContent = `Não: ${data.no_votes}`;

                // Mostra a div de resultados e o botão Próximo
                voteResultsDiv.classList.remove('hidden');
                buttonNext.classList.remove('hidden');
                buttonNext.dataset.nextUrl = data.next_scenario_url; // Armazena a URL

                // Reabilita os botões Sim/Não (eles estão escondidos, mas redefine o estado para o próximo cenário)
                buttonNo.disabled = false;
                buttonYes.disabled = false;
                buttonNo.classList.remove('opacity-50', 'cursor-not-allowed');
                buttonYes.classList.remove('opacity-50', 'cursor-not-allowed');

                // Removemos a lógica de scroll

            } else if (data.redirect) {
                 // Se a sessão for inválida, o backend pode pedir redirecionamento
                 window.location.href = data.redirect;
            } else {
                // Se não for para mostrar resultados, atualiza para o próximo cenário diretamente
                // Garante que a div de resultados e o botão próximo estejam escondidos
                voteResultsDiv.classList.add('hidden');
                buttonNext.classList.add('hidden');
                // Mostra os botões Sim/Não novamente
                buttonNo.classList.remove('hidden');
                buttonYes.classList.remove('hidden');
                updateScenarioUI(data); // Atualiza a UI e reabilita botões Sim/Não
            }

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
            // Garante que a seção de resultados e o botão próximo estejam escondidos em caso de erro
            voteResultsDiv.classList.add('hidden');
            buttonNext.classList.add('hidden');
            // Garante que os botões Sim/Não estejam visíveis em caso de erro
            buttonNo.classList.remove('hidden');
            buttonYes.classList.remove('hidden');
        }
    }

    // Função assíncrona para buscar o próximo cenário
    async function fetchNextScenario() {
        const nextUrl = buttonNext.dataset.nextUrl;
        if (!nextUrl) {
            console.error("URL do próximo cenário não encontrada no dataset do botão.");
            alert('Erro interno: Não foi possível encontrar a URL para o próximo cenário.');
            return;
        }

        // Desabilita o botão Próximo para evitar cliques múltiplos
        buttonNext.disabled = true;
        buttonNext.classList.add('opacity-50', 'cursor-not-allowed');

        try {
            const response = await fetch(nextUrl); // Método GET é o padrão
            if (!response.ok) {
                // Tenta ler a resposta de erro se possível
                let errorBody = await response.text();
                console.error("Erro HTTP:", response.status, errorBody);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            // A função updateScenarioUI já lida com esconder/mostrar os elementos corretos
            updateScenarioUI(data); // Esta função já lida com is_complete e reabilita botões

        } catch (error) {
            console.error('Erro ao buscar próximo cenário:', error);
            alert('Ocorreu um erro ao carregar o próximo cenário. Por favor, recarregue a página.');
            // Reabilita o botão Próximo em caso de erro para permitir nova tentativa
            buttonNext.disabled = false;
            buttonNext.classList.remove('opacity-50', 'cursor-not-allowed');
            // Garante que a div de resultados esteja escondida em caso de erro
             voteResultsDiv.classList.add('hidden');
             // Garante que os botões Sim/Não estejam visíveis se o carregamento falhar
             buttonNo.classList.remove('hidden');
             buttonYes.classList.remove('hidden');
        }
    }


    // Adiciona os event listeners aos botões "Não" e "Sim"
    buttonNo.addEventListener('click', () => handleDecision('no'));
    buttonYes.addEventListener('click', () => handleDecision('yes'));
    // Adiciona listener ao botão "Próximo"
    buttonNext.addEventListener('click', fetchNextScenario);
});
