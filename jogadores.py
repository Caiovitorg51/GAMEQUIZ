import multiprocessing
import random
import time
import json

def jogar(jogador_id, perguntas, semaforos, pontuacao, evento_pronto):
    print(f"Jogador {jogador_id} está pronto.")
    evento_pronto.set()  # Sinaliza que este jogador está pronto

    total_pontos = 0
    for idx, pergunta in enumerate(perguntas):
        with semaforos[idx]:
            print(f"Jogador {jogador_id} está respondendo a pergunta {idx + 1}.")
            time.sleep(random.uniform(0.5, 2.0))  # Simula o tempo de resposta
            resposta = random.choice(pergunta['options'])
            if resposta == pergunta['answer']:
                pontos = (4 - jogador_id) * 10  # Pontuação baseada na rapidez
                print(f"Jogador {jogador_id} respondeu certo e ganhou {pontos} pontos!")
                total_pontos += pontos
            else:
                print(f"Jogador {jogador_id} errou.")
        pontuacao[jogador_id] = total_pontos
        print(f"Jogador {jogador_id} acumulou {total_pontos} pontos até agora.")

if __name__ == "__main__":
    with open('perguntas.json', 'r') as f:
        dados = json.load(f)
    
    perguntas = dados['questions']
    num_jogadores = 4

    semaforos = [multiprocessing.Semaphore(1) for _ in perguntas]
    pontuacao = multiprocessing.Manager().dict()

    eventos_prontos = [multiprocessing.Event() for _ in range(num_jogadores)]  # Eventos para cada jogador

    jogadores = []
    for jogador_id in range(num_jogadores):
        p = multiprocessing.Process(target=jogar, args=(jogador_id, perguntas, semaforos, pontuacao, eventos_prontos[jogador_id]))
        jogadores.append(p)
        p.start()

    for p in jogadores:
        p.join()

    print("\nPontuação final:")
    for jogador_id, pontos in pontuacao.items():
        print(f"Jogador {jogador_id}: {pontos} pontos")
