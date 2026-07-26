from board import Board
import board_util as bu
import network_client as net
import time
import sys

print(f"Iniciando voluntário. Conectando em: {net.TARGET_URL}")

puzzle = net.get_initial_board()

if not puzzle:
    print("Não foi possível carregar o tabuleiro. Encerrando.")
    sys.exit(1)

board = Board(puzzle)
print("Tabuleiro inicial recebido:")
print(board)
time.sleep(2)

solution_found = False
start_time = time.time()

print("Iniciando Simulated Annealing...")

while not solution_found:
    temp_decrease = 0.99 
    stuck_counter = 0 
    
    temp_board = bu.randomizeSudoku(board)
    temp = bu.initialTemp(board) 
    cost = bu.boardCost(temp_board) 
    iterations = bu.totalIterations(board)
    
    best_cost_so_far = cost
    
    if cost <= 0:
        solution_found = True

    while not solution_found:
        previous_cost = cost
        
        for i in range(iterations):
            temp_board, cost_diff = bu.chooseNewBoard(temp_board, board, cost, temp)
            cost += cost_diff

            #unrestricted shipping
            clean_matrix = bu.sanitize_board(temp_board)
            net.send_progress(clean_matrix)
            # Gatilho de Envio
            if cost < best_cost_so_far:
                best_cost_so_far = cost
                print(f"Novo progresso - Erros restantes: {cost}")
                

            if cost <= 0:
                solution_found = True
                break

        temp *= temp_decrease
        
        if cost <= 0:
            solution_found = True
        elif cost >= previous_cost:
            stuck_counter += 1
        else:
            stuck_counter = 0

        if stuck_counter >= 100:
            temp += 2
            
        if bu.boardCost(temp_board) == 0:
            print(f"Solução Encontrada - Tempo: {time.time() - start_time:.2f}s")
            print(temp_board)
            #final_matrix = bu.sanitize_board(temp_board)
            #net.send_progress(final_matrix)
            break

print("Execução finalizada com sucesso.")