esse programa é um teste como parte dos meus estudos de sistemas operacionais e a manipulação de processos concorrentes, como parte da minha nota da cadeira de SISTEMAS OPERACIONAIS.
ele consiste em um jogo de perguntas em que eu crio 4 processos para simularem jogadores que competem entre si, cada processo tentará acessar a memória compartilhada e um semáforo irá contolar o tráfego deles, quanto mais rapido um processo responder a pergunta de forma correta mais pontos ele receberá.

como executar:
- instale o python em seu dispositivo assim como todas as bibliotecas a seguir:
import multiprocessing
import random
import time
import json

- abra o diretório em que você fez o download do arquivo em seu dispositivo.
- execute o seguinte comando no terminal: python quiz.py

os dados do quiz serão mostrados no próprio terminal.
