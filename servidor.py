import multiprocessing
import json
import time

def servidor(perguntas, pontuacao, semaforos, eventos_prontos):
    print("Servidor está aguardando que todos os jogadores estejam prontos.")
    
    # Espera todos os 4 jogadores sinalizarem que estão prontos
    for evento in eventos_prontos:
        evento.wait()

    print("Todos os jogadores estão prontos. Servidor começou a enviar perguntas.")
    
    time.sleep(5)

    for idx, pergunta in enumerate(perguntas):
        print(f"Enviando pergunta {idx + 1}: {pergunta['question']}")
        print("Opções:", pergunta['options'])
  # Simula o tempo de resposta dos jogadores

        print(f"Resultados da pergunta {idx + 1}:")
        for jogador_id, pontos in pontuacao.items():
            print(f"Jogador {jogador_id} acumulou {pontos} pontos.")
        print("-" * 30)

if __name__ == "__main__":
    with open('perguntas.json', 'r') as f:
        dados = json.load(f)
    
    perguntas = dados['questions']
    num_jogadores = 4

    semaforos = [multiprocessing.Semaphore(1) for _ in perguntas]
    pontuacao = multiprocessing.Manager().dict()

    eventos_prontos = [multiprocessing.Event() for _ in range(num_jogadores)]  # Eventos para cada jogador

    p_servidor = multiprocessing.Process(target=servidor, args=(perguntas, pontuacao, semaforos, eventos_prontos))
    p_servidor.start()
    p_servidor.join()
