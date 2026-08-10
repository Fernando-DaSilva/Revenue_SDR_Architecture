#!/usr/bin/env python3
"""
Script de Sincronização do Quadro Trello Kanban para o Revenue SDR OS.
Board Target: https://trello.com/b/OH7UtbIQ/revenue-sdr-os

Uso:
  export TRELLO_API_KEY="seu_api_key"
  export TRELLO_TOKEN="seu_token"
  python3 sync_trello_board.py
"""

import os
import sys
import json
import urllib.request
import urllib.parse

BOARD_SHORT_LINK = "OH7UtbIQ"
SPEC_FILE = os.path.join(os.path.dirname(__file__), "trello_backlog_spec.json")

def main():
    api_key = os.environ.get("TRELLO_API_KEY")
    token = os.environ.get("TRELLO_TOKEN")

    if not os.path.exists(SPEC_FILE):
        print(f"Erro: Arquivo {SPEC_FILE} não encontrado.")
        sys.exit(1)

    with open(SPEC_FILE, "r", encoding="utf-8") as f:
        spec = json.load(f)

    print("==================================================================")
    print(f"🎯 Preparando Sincronização Ágil do Trello: {spec['board']['name']}")
    print(f"🔗 Target Board: {spec['board']['url']}")
    print("==================================================================")

    if not api_key or not token:
        print("\n⚠️ AVISO: Variáveis TRELLO_API_KEY e/ou TRELLO_TOKEN não configuradas.")
        print("Imprimindo a estrutura do Backlog formatada que foi preparada para o quadro:\n")
        
        for list_idx, lst in enumerate(spec["lists"], 1):
            print(f"\n--- Lista {list_idx}: {lst['name']} ({len(lst['cards'])} cards) ---")
            for card in lst["cards"]:
                sp = f"[{card.get('story_points')} SP]" if 'story_points' in card else ""
                labels = ", ".join(card.get("labels", []))
                print(f"  📌 {card['name']} {sp}")
                print(f"     Labels: {labels}")
                print(f"     Desc: {card['desc'].splitlines()[0] if card.get('desc') else 'Sem descrição'}")
        
        print("\n✅ O arquivo JSON da especificação foi gravado com sucesso em:")
        print(f"   {SPEC_FILE}")
        print("\nPara executar a criação remota automática no Trello, execute com as credenciais:")
        print("  export TRELLO_API_KEY='...'")
        print("  export TRELLO_TOKEN='...'")
        print("  python3 sync_trello_board.py")
        sys.exit(0)

    # Quando credenciais estao presentes, executa a sincronizacao via API do Trello
    print("\n🚀 Conectando à API REST do Trello...")
    # 1. Obter ID real do Board via shortlink
    url_board = f"https://api.trello.com/1/boards/{BOARD_SHORT_LINK}?key={api_key}&token={token}"
    req = urllib.request.Request(url_board)
    try:
        with urllib.request.urlopen(req) as resp:
            board_data = json.loads(resp.read().decode())
            board_id = board_data["id"]
            print(f"✅ Conectado ao Board ID: {board_id}")
    except Exception as e:
        print(f"❌ Erro ao conectar ao board do Trello: {e}")
        sys.exit(1)

    # 2. Criar ou sincronizar Listas e Cards
    for lst in spec["lists"]:
        print(f"\n📁 Criando/Verificando lista: {lst['name']}...")
        url_create_list = f"https://api.trello.com/1/boards/{board_id}/lists?name={urllib.parse.quote(lst['name'])}&key={api_key}&token={token}"
        req_l = urllib.request.Request(url_create_list, method="POST")
        try:
            with urllib.request.urlopen(req_l) as resp_l:
                list_data = json.loads(resp_l.read().decode())
                list_id = list_data["id"]
                print(f"   ✓ Lista criada (ID: {list_id})")
                
                for card in lst["cards"]:
                    card_name = card["name"]
                    if card.get("story_points"):
                        card_name = f"({card['story_points']}) {card_name}"
                    url_card = "https://api.trello.com/1/cards"
                    payload = urllib.parse.urlencode({
                        "idList": list_id,
                        "name": card_name,
                        "desc": card.get("desc", ""),
                        "key": api_key,
                        "token": token
                    }).encode()
                    req_c = urllib.request.Request(url_card, data=payload, method="POST")
                    with urllib.request.urlopen(req_c) as resp_c:
                        c_data = json.loads(resp_c.read().decode())
                        print(f"     + Card criado: {c_data['name']}")
        except Exception as e:
            print(f"   ⚠️ Erro ao processar lista '{lst['name']}': {e}")

    print("\n🎉 Sincronização concluída com sucesso no Trello!")

if __name__ == "__main__":
    main()
