import multiprocessing
import json
import time
import random

def jogador(jogador_id, pontuacao, perguntas_respondidas_corretamente, evento_pronto, evento_nova_pergunta, semaforo_resposta, semaforo_exibir_resultado, lock_pontuacao, perguntas, respostas_certas, barreira_dormir, jogo_ativo):
    time.sleep(random.uniform(1, 3))  # Simula tempo aleatório para estar pronto
    print(f"Jogador {jogador_id} está pronto.")
    evento_pronto.set()  # Informa que está pronto

    while jogo_ativo.value:  # Verifica se o jogo ainda está ativo
        evento_nova_pergunta.wait()  # Espera pela nova pergunta
        evento_nova_pergunta.clear()  # Limpa o evento para esperar a próxima pergunta

        pergunta_atual = len([p for p in perguntas_respondidas_corretamente if p])  # Identifica qual pergunta está em jogo

        if pergunta_atual >= len(perguntas):
            break  # Todas as perguntas foram respondidas corretamente, termina o jogo

        while not perguntas_respondidas_corretamente[pergunta_atual]:  # Enquanto a pergunta não foi respondida corretamente
            time.sleep(random.uniform(1, 5))  # Simula tempo aleatório de resposta

            # Verifica se a pergunta ainda está em aberto
            if perguntas_respondidas_corretamente[pergunta_atual]:
                break  # Se a pergunta já foi respondida, sai do loop

            resposta = random.choice(perguntas[pergunta_atual]['options'])  # Escolhe uma resposta aleatória

            with semaforo_resposta:  # Controle para permitir apenas um jogador respondendo por vez
                print(f"Jogador {jogador_id} está respondendo a pergunta {pergunta_atual + 1}: {resposta}")

                # Verifica se a resposta está correta
                if resposta == respostas_certas[pergunta_atual]:
                    with lock_pontuacao:
                        pontuacao[jogador_id] += 1  # Atualiza a pontuação
                    perguntas_respondidas_corretamente[pergunta_atual] = True  # Marca a pergunta como respondida corretamente
                    print(f"Jogador {jogador_id} respondeu a pergunta {pergunta_atual + 1} corretamente e agora tem {pontuacao[jogador_id]} pontos.")
                else:
                    print(f"Jogador {jogador_id} respondeu a pergunta {pergunta_atual + 1} incorretamente.")
                    time.sleep(1)  # Atraso entre tentativas

                # Libera o semáforo para que o próximo jogador possa tentar
                semaforo_exibir_resultado.release()

        # Jogador dorme até a próxima pergunta
        print(f"Jogador {jogador_id} dormindo até a próxima pergunta.")
        time.sleep(2)  # Simula tempo de espera até a próxima pergunta

        # Aguarda na barreira até que todos os jogadores estejam dormindo
        barreira_dormir.wait()

    print(f"Jogador {jogador_id} encerrando o jogo.")


def servidor(perguntas, pontuacao, respostas_certas, eventos_prontos, evento_nova_pergunta, semaforo_resposta, semaforo_exibir_resultado, perguntas_respondidas_corretamente, barreira_dormir, jogo_ativo):
    print("Servidor está aguardando que todos os jogadores estejam prontos.")

    # Espera que todos os jogadores estejam prontos
    for evento in eventos_prontos:
        evento.wait()

    print("Todos os jogadores estão prontos. Preparando perguntas.")

    for idx, pergunta in enumerate(perguntas):
        time.sleep(2)  # Aguarda 2 segundos antes de enviar a pergunta

        print(f"Enviando pergunta {idx + 1}: {pergunta['question']}")
        print("Opções:", pergunta['options'])

        # Notifica os jogadores que uma nova pergunta está pronta
        evento_nova_pergunta.set()  # Acorda todos os jogadores para responder

        # Aguarda que a pergunta seja respondida corretamente
        while not perguntas_respondidas_corretamente[idx]:
            time.sleep(0.1)  # Verifica se a pergunta já foi respondida corretamente

        print(f"Pergunta {idx + 1} foi respondida corretamente. Preparando a próxima pergunta.")

        # Aguarda até que todos os jogadores estejam dormindo antes de passar para a próxima pergunta
        barreira_dormir.wait()

        # Atraso de 2 segundos antes de enviar a próxima pergunta
        time.sleep(2)

    print("Todas as perguntas foram respondidas. Encerrando o jogo.")
    
    # Marca que o jogo terminou
    jogo_ativo.value = False

    # Notifica os jogadores que o jogo acabou
    evento_nova_pergunta.set()  # Acorda os jogadores para verificar o término

    print("Pontuações finais:", dict(pontuacao))


if __name__ == "__main__":
    # Carregar as perguntas do arquivo JSON
    with open('perguntas.json', 'r') as f:
        dados = json.load(f)

    perguntas = dados['questions']
    num_jogadores = 4  # Número de jogadores

    manager = multiprocessing.Manager()
    pontuacao = manager.dict({i: 0 for i in range(num_jogadores)})  # Inicializa a pontuação para cada jogador
    perguntas_respondidas_corretamente = manager.list([False] * len(perguntas))  # Controla se uma pergunta já foi respondida corretamente
    respostas_certas = [pergunta['answer'] for pergunta in perguntas]  # Extrai as respostas corretas (usando "answer" agora)

    # Variável compartilhada para indicar se o jogo está ativo
    jogo_ativo = manager.Value('b', True)  # Usando 'b' para um valor booleano

    # Eventos e semáforos para sincronização
    eventos_prontos = [multiprocessing.Event() for _ in range(num_jogadores)]  # Cada jogador terá um evento
    evento_nova_pergunta = multiprocessing.Event()  # Evento para sinalizar que uma nova pergunta foi enviada
    semaforo_resposta = multiprocessing.Lock()  # Controle para permitir apenas um jogador respondendo por vez
    semaforo_exibir_resultado = multiprocessing.Semaphore(0)  # Semáforo para controlar a exibição dos resultados
    lock_pontuacao = multiprocessing.Lock()  # Lock para controlar a atualização da pontuação

    # Barreira para sincronizar o momento em que todos os jogadores entram no estado de "dormir"
    barreira_dormir = multiprocessing.Barrier(num_jogadores + 1)  # +1 para incluir o servidor na barreira

    # Criar e iniciar processos para os jogadores
    processos_jogadores = []
    for i in range(num_jogadores):
        p = multiprocessing.Process(target=jogador, args=(i, pontuacao, perguntas_respondidas_corretamente, eventos_prontos[i], evento_nova_pergunta, semaforo_resposta, semaforo_exibir_resultado, lock_pontuacao, perguntas, respostas_certas, barreira_dormir, jogo_ativo))
        processos_jogadores.append(p)
        p.start()

    # Inicia o servidor
    p_servidor = multiprocessing.Process(target=servidor, args=(perguntas, pontuacao, respostas_certas, eventos_prontos, evento_nova_pergunta, semaforo_resposta, semaforo_exibir_resultado, perguntas_respondidas_corretamente, barreira_dormir, jogo_ativo))
    p_servidor.start()

    # Aguarda o término dos processos dos jogadores e do servidor
    for p in processos_jogadores:
        p.join()
    p_servidor.join()
