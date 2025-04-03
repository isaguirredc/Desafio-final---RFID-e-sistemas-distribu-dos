import RPi.GPIO as GPIO

import requests

from mfrc522 import SimpleMFRC522

from time import sleep

leitorRfid = SimpleMFRC522()

# Função para enviar o POST request

def send_post_request(tag_id):

    data = {'data': f'Cartão RFID {tag_id} passado'}

    try:

        response = requests.post('http://localhost:5000', json=data)

        if response.status_code == 201:

            print("Mensagem enviada com sucesso!")

        else:

            print(f"Erro ao enviar mensagem: {response.status_code}")

    except Exception as e:

        print(f"Erro na conexão: {e}")



if __name__ == "__main__":

    result = int(input("1-Executar método\n2-Iniciar aplicação\nEscolha: "))



    if result == 1:

        tag_id, text = leitorRfid.read()

        send_post_request(tag_id)

    else:

        try:

            print("Aproxime a tag do leitor RFID...")

            while True:

                tag_id, text = leitorRfid.read()

                print(f"Cartão detectado! ID: {tag_id}")

                send_post_request(tag_id)

                sleep(1)  # Evita múltiplas leituras seguidas

        except KeyboardInterrupt:

            print("Programa interrompido")

        finally:

            GPIO.cleanup()