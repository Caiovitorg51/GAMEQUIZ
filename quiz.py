import multiprocessing
import random
import time
import json

def jogar(jogador_id, perguntas, semaforos, pontuacao, evento_pronto, evento_nova_pergunta, evento_respostas_completas, respostas_jogadores, recompensas):
    # Simula o jogador se preparando
    time.sleep(random.uniform(1, 3))  # Simula tempo aleatório para estar pronto
    print(f"Jogador {jogador_id} está pronto.")
    evento_pronto.set()  # Informa que está pronto

    total_pontos = 0
    num_perguntas = len(perguntas)

    for idx in range(num_perguntas):
        evento_nova_pergunta.wait()  # Aguarda o servidor enviar uma nova pergunta
        print(f"Jogador {jogador_id} recebeu a pergunta {idx + 1} e está respondendo.")
        
        with semaforos[idx]:  # Garante acesso exclusivo à pergunta atual
            time.sleep(random.uniform(0.5, 2.0))  # Simula o tempo de resposta
            resposta = random.choice(perguntas[idx]['options'])  # Simula uma resposta aleatória
            if resposta == perguntas[idx]['answer']:
                ordem = len(respostas_jogadores[idx])
                if ordem == 0:
                    # Primeiro a acertar ganha o valor máximo da recompensa (40)
                    pontos_recebidos = recompensas[idx]  
                else:
                    # Os próximos jogadores a acertarem ganham menos pontos
                    pontos_recebidos = max(recompensas[idx] - 10 * ordem, 0)
                
                print(f"Jogador {jogador_id} respondeu certo e ganhou {pontos_recebidos} pontos!")
                total_pontos += pontos_recebidos
                
                # Atualiza a recompensa para os próximos jogadores
                recompensas[idx] = max(recompensas[idx] - 10, 0)
            else:
                print(f"Jogador {jogador_id} errou.")
        
        pontuacao[jogador_id] = total_pontos
        
        # Marca que o jogador respondeu
        with semaforos[idx]:  # Usa o semáforo para garantir acesso exclusivo
            if jogador_id not in respostas_jogadores[idx]:
                respostas_jogadores[idx].append(jogador_id)
        
        evento_respostas_completas.set()  # Sinaliza que o jogador respondeu
        evento_respostas_completas.clear()  # Limpa o evento para a próxima rodada

        evento_nova_pergunta.clear()  # Aguarda nova pergunta

#### Código do Servidor

def servidor(perguntas, pontuacao, respostas_jogadores, eventos_prontos, semaforos, evento_nova_pergunta, evento_respostas_completas, recompensas):
    print("Servidor está aguardando que todos os jogadores estejam prontos.")
    
    # Espera todos os jogadores sinalizarem que estão prontos
    for evento in eventos_prontos:
        evento.wait()
    
    print("Todos os jogadores estão prontos. Servidor começou a enviar perguntas.")
    
    num_perguntas = len(perguntas)
    num_jogadores = len(eventos_prontos)

    for idx in range(num_perguntas):
        time.sleep(2)  # Aguarda 2 segundos antes de enviar a pergunta

        # Exibe a pergunta no terminal assim que é enviada
        print(f"Enviando pergunta {idx + 1}: {perguntas[idx]['question']}")
        print("Opções:", perguntas[idx]['options'])

        # Notifica todos os jogadores que a pergunta foi enviada
        evento_nova_pergunta.set()

        # Aguarda todos os jogadores responderem
        respostas_recebidas = 0
        while respostas_recebidas < num_jogadores:
            if evento_respostas_completas.is_set():
                respostas_recebidas += 1
                evento_respostas_completas.clear()

        # Aguarda todos os jogadores processarem a pergunta antes de enviar a próxima
        for evento in eventos_prontos:
            evento.clear()
        
        # Notifica a todos os jogadores que a próxima pergunta está pronta
        evento_nova_pergunta.clear()

if __name__ == "__main__":
    with open('perguntas.json', 'r') as f:
        dados = json.load(f)
    
    perguntas = dados['questions']
    num_jogadores = 4

    pontuacao = multiprocessing.Manager().dict()  # Dicionário compartilhado de pontuação
    respostas_jogadores = multiprocessing.Manager().list([[] for _ in perguntas])  # Lista de respostas por pergunta
    eventos_prontos = [multiprocessing.Event() for _ in range(num_jogadores)]  # Eventos para cada jogador
    evento_nova_pergunta = multiprocessing.Event()  # Evento para sinalizar nova pergunta
    evento_respostas_completas = multiprocessing.Event()  # Evento para sinalizar quando todos responderam
    semaforos = [multiprocessing.Semaphore(1) for _ in perguntas]  # Um semáforo por pergunta
    recompensas = multiprocessing.Manager().list([40 for _ in perguntas])  # Lista de recompensas começando em 40 por pergunta

    # Criar e iniciar processos para os jogadores
    processos_jogadores = []
    for i in range(num_jogadores):
        p = multiprocessing.Process(target=jogar, args=(i, perguntas, semaforos, pontuacao, eventos_prontos[i], evento_nova_pergunta, evento_respostas_completas, respostas_jogadores, recompensas))
        processos_jogadores.append(p)
        p.start()

    # Inicia o servidor
    p_servidor = multiprocessing.Process(target=servidor, args=(perguntas, pontuacao, respostas_jogadores, eventos_prontos, semaforos, evento_nova_pergunta, evento_respostas_completas, recompensas))
    p_servidor.start()

    # Aguarda o término dos processos dos jogadores e do servidor
    for p in processos_jogadores:
        p.join()
    p_servidor.join()

    # Exibe a pontuação final após o término do jogo
    print("\nPontuação final:")
    for jogador_id, pontos in pontuacao.items():
        print(f"Jogador {jogador_id}: {pontos} pontos")
