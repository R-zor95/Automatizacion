# Importación de bibliotecas
import numpy as np
import matplotlib.pyplot as plt

# Intento de importación del módulo 'algen' para la lógica de algoritmos genéticos.
try:
    import laberinto.algen as ag
except:
    try:
        import Ejercicios.Laberinto.laberinto.algen as ag
    except:
        print('Problema al cargar el módulo')

# Clase 'Map' para definir las características del mapa y sus operaciones.
class Map():
    def __init__(self, max_steps=50, veneno=0):
        # Definición de los atributos del mapa.
        self.max_steps = max_steps
        self.veneno = veneno
        self.list_caminos = []
        self.history = []
        self.bestpath = None
        self.bestscore = -10E8
        self.dict_genes = {}
        
        # Inicialización del diccionario de genes.
        for i in range(10):
            for j in range(10):
                self.dict_genes[i, j] = 2

        # Matriz que describe las fronteras de cada celda en binario.
        
        self.grid = np.array([
            [9,  5, 3, 9, 5, 3, 9, 3, 9, 3],
            [10, 0, 12, 2, 0, 8, 0, 2, 8, 6],
            [10, 0, 0, 10, 0, 10, 11, 14, 10, 11],
            [8,  3, 0, 10, 0, 10, 0, 0, 10, 10],
            [8,  0, 1, 0, 5, 0, 3, 0, 12, 2],
            [10, 10, 8, 2, 0, 8, 0, 3, 11, 10],
            [12, 0, 2, 10, 0, 10, 11, 12, 2, 10],
            [9, 4, 2, 8, 5, 2, 0, 0, 8, 2],
            [10, 0, 8, 2, 0, 8, 3, 0, 8, 2],
            [12, 5, 6, 12, 5, 6, 12, 5, 6, 12]
        ])
        '''
        self.grid = np.array([
                [9,  3,  9,  5,  5,  5,  5,  5,  5,  3 ],
                [10, 12, 6,  9,  1,  5,  5,  3,  9,  6 ],
                [10, 9,  3,  10, 10, 9,  3,  10, 10, 11],
                [10, 10, 10, 10, 10, 12, 6,  10, 8,  2 ],
                [8,  2,  8,  6,  12, 5,  5,  6,  10, 12],
                [10, 10, 12, 1,  5,  5,  1,  3,  12, 3 ],
                [10, 12, 3,  10, 9,  5,  6,  12, 3,  10],
                [8,  5,  6,  10, 10, 9,  3,  11, 10, 10],
                [10, 9,  3,  10, 12, 6,  12, 2,  10, 10],
                [12, 6,  12, 4,  5,  5,  5,  6,  12, 6 ]
            ])'''
        # Matriz de fondo para estética del tablero.
        self.back = np.zeros([10, 10])
        self.back[::2, ::2] = 1
        self.back[1::2, 1::2] = 1

        # Matriz de feromonas para marcar lugares visitados.
        self.feromap = np.zeros((10, 10))

    # Método para dibujar el tablero.
    def draw_tablero(self):
        '''Dibuja el laberinto'''
        plt.figure(1, figsize=(10, 10))
        plt.matshow(self.back, fignum=1, cmap=plt.cm.Oranges, alpha=0.4)
        plt.xlim(-1, 10)
        plt.ylim(-1, 10)
        
        # Dibuja las fronteras basadas en la matriz 'grid'.
        for i in range(10):
            for j in range(10):
                if self.grid[j, i] & 1:
                    plt.plot([i - 0.5, i + 0.5], [j - 0.5, j - 0.5], 'k', linewidth=3)
                if self.grid[j, i] & 2:
                    plt.plot([i + 0.5, i + 0.5], [j - 0.5, j + 0.5], 'k', linewidth=3)
                if self.grid[j, i] & 4:
                    plt.plot([i - 0.5, i + 0.5], [j + 0.5, j + 0.5], 'k', linewidth=3)
                if self.grid[j, i] & 8:
                    plt.plot([i - 0.5, i - 0.5], [j - 0.5, j + 0.5], 'k', linewidth=3)
        plt.gca().invert_yaxis()

    # Método para generar caminos aleatorios.
    def create_camino(self):
        '''Crea un nuevo camino aleatorio'''
        self.list_caminos.append(Camino(False, [self]))

    # Analiza las puntuaciones de los caminos actuales.
    def statistics(self):
        '''Analiza los valores de la puntuación de la población'''
        scores = [camino.fitness for camino in self.list_caminos]
        if max(scores) > self.bestscore:
            self.bestscore = max(scores)
            self.bestpath = self.list_caminos[scores.index(self.bestscore)]
        self.history.append([min(scores), sum(scores) / len(scores), max(scores)])

    # Método para graficar la evolución de puntuaciones.
    def draw_history(self):
        '''Dibuja las gráficas de evolución de la puntuación'''
        plt.figure(None, figsize=(10, 8))
        history = np.array(self.history)
        for i in range(3):
            plt.plot(history[:, i])
        plt.title('Puntuación máxima, media y mínima para cada generación')

            
    def draw_best(self):
        '''Dibuja el mejor camino encontrado.
        Es necesario pintar el tablero por separado'''
        self.bestpath.draw_path(alpha = 0.5, c = 'b', w = 4)
        
    def draw_poison(self):
        '''Dibuja las toxinas o feromonas del mapa.
        Es necesario pintar el tablero por separado'''
        if self.veneno != 0:
            maxpoison = np.max(self.feromap)
            for i in range(10):
                for j in range(10):
                    poison = 0.8 * self.feromap[j,i] / maxpoison
                    plt.plot(i , j, 'o', color = 'g', alpha = poison, markersize=40)
    
    def reload_poison(self):
        '''Actualiza las feromonas y el valor de la aptitud de las soluciones'''
        self.bestpath = None
        self.bestscore = -10E8
        self.feromap /=2
        for i in self.list_caminos:
            i.deploy_poison()
        for i in self.list_caminos:
            calculate_fitness(i)

        
class Camino():
    '''Este objeto contiene una disposición dada de direcciones sobre el mapa, 
    con la que se puede construir un camino'''
    def __init__(self, genome = False, opciones = False):
        self.poison = 0
        if not opciones:
            self.mapa = None
        else:
            self.mapa = opciones[0]
        self.dict_genes = {}
        for i in range (10):
            for j in range (10):
                self.dict_genes[i,j] = 2
                
        if not genome:
            self.genome = np.random.randint(0,2,200)
        else:
            self.genome = genome
        
                
    def draw_directions(self):
        '''Dibuja el tablero y a continuación, dibuja sobre él
        el mapa de direcciones'''
        self.mapa.draw_tablero()
        x = list(range(10))
        y = x
        for i in x:
            for j in y:

                if self.directions[j ,i] == 0:
                    plt.arrow(i, j + 0.4, 0, -0.6, head_width=0.1, head_length=0.2, fc='b', ec='b')
                if self.directions[j ,i] == 1:
                    plt.arrow(i - 0.4, j,  0.6, 0, head_width=0.1, head_length=0.2, fc='b', ec='b')
                if self.directions[j ,i] == 2:
                    plt.arrow(i, j - 0.4, 0,  0.6, head_width=0.1, head_length=0.2, fc='b', ec='b')
                if self.directions[j ,i] == 3:
                    plt.arrow(i + 0.4, j, -0.6, 0, head_width=0.1, head_length=0.2, fc='b', ec='b')
                    
    #-- Funciones para calcular el camino
                    
    def move(self, row, col, direction):
        '''Intenta moverse a la siguiente casilla'''
        grid = self.mapa.grid
        d = 2 ** direction
        
        if not grid[row, col] & d:

            if direction == 0:
                return row -1, col
            elif direction == 1:
                return row , col+1
            elif direction == 2:
                return row +1, col
            elif direction == 3:
                return row , col-1
        else:
            return None

    def step(self, row, col, direction, path):
        '''Intenta moverse a la siguiente casilla, si no lo consigue
        (porque choca con una pared), intenta moverse en otras direcciones.
        Si después de varios intentos sigue sin conseguir moverse, se queda quieto.

        Devuelve información sobre si ha chocado o si ha vuelto a la casilla en la que estaba
        en el paso anterior'''
        wall = False
        u_turn = False
        attempts = 0  # contador de intentos

        while attempts < 4:  # permite hasta 4 intentos antes de quedarse quieto
            newpos = self.move(row, col, direction)
            if newpos is not None:
                row, col = newpos
                if len(path) >= 2 and [row, col] == path[-2]:  # si regresa a la posición anterior
                    u_turn = True
                return row, col, wall, u_turn
            else:
                wall = True
                direction = (direction + 1) % 4  # prueba con la siguiente dirección (0, 1, 2, 3 en secuencia)
                attempts += 1

        # Si después de 4 intentos no encuentra un camino, regresa los valores originales (quieto)
        return row, col, wall, u_turn

    def get_path(self):
        '''Calcula el camino a partir del mapa de direcciones'''
        max_steps = self.mapa.max_steps        
        path = [[4,0]]
        wall_count = 0
        u_turn_count = 0

        for nstep in range(max_steps):
            row, col = path[nstep]
            direction = self.directions[row, col]

            # Modificación: se intenta avanzar varias veces si la primera dirección falla
            for _ in range(4):  
                row, col, wall, u_turn = self.step(row, col, direction, path)
                wall_count += wall
                u_turn_count += u_turn
                if not wall:  # Si logra moverse, se rompe el ciclo
                    break
                direction = (direction + 1) % 4  # Prueba otra dirección

            path.append([row, col])
            if [row, col] == [9, 10]:  # fin del laberinto
                break

        self.path, self.wall_count, self.u_turn_count = np.array(path), wall_count, u_turn_count


    def deploy_poison(self):
        '''Deposita feromonas negativas en las casillas que ha visitado'''
        if self.mapa.veneno != 0 :
            for i in range(self.path.shape[0]):
                row = self.path[i, 0]
                col = self.path[i, 1]
                if col < 10:
                    self.poison += self.mapa.feromap[row,col]
                    self.mapa.feromap[row,col] += 0.1 * self.mapa.veneno
                    
    def draw_path(self, alpha = 0.5, c = 'r', w = 8):
        '''Dibuja su camino sobre el mapa.
        Es necesario pintar el tablero por separado'''
        plt.plot(self.path[:,1], self.path[:,0], c, linewidth = w, alpha = alpha)

    

def calculate_performances(individual):
    '''Calcula las performances de un individuo:
    En este caso, el camino a partir del mapa de direcciones.
    En este paso también se depositan las feromonas'''
    
    individual.directions = np.zeros([10,10], dtype=np.int)
    for i in range (10):
        for j in range (10):
            individual.directions[i,j] = individual.traits[(i,j)]
    individual.get_path()
    individual.deploy_poison()
    
def calculate_fitness(individual):
    '''Calcula la aptitud de un individuo'''
    path, wall_count, u_turn_count = individual.path, individual.wall_count, individual.u_turn_count
    poison = individual.poison
    max_steps = individual.mapa.max_steps
    endx = path[-1,1]
    victory = max_steps + 1 - len(path) # >0 si ha llegado al final, mayor cuanto más corto sea el camino
    individual.fitness = endx * 4 -  2 * wall_count - 3 * u_turn_count - 0.03 * poison + victory * 5

def avanzar(mapa, n = 100, 
           max_pop = 100, min_pop = 10,
           reproduction_rate = 8, mutation_rate = 0.05):
    '''Efectua una cantidad n de generaciones '''
    for i in range(n):
        print(i+1, end='·')
        ag.immigration(mapa.list_caminos, max_pop, 
                   calculate_performances, calculate_fitness,
                   mapa.dict_genes, Camino, mapa)
        ag.tournament(mapa.list_caminos, min_pop)
        mapa.reload_poison()
        ag.crossover(mapa.list_caminos, reproduction_rate, mutation_rate, 
                   calculate_performances, calculate_fitness,
                   mapa.dict_genes, Camino, mapa)
        mapa.statistics()

def draw_all(mapa):
    '''Dibuja el mapa con todas las soluciones de la generación actual,
    las feromonas del mapa, y gráficas de evolución.'''
    mapa.bestpath.draw_directions()
    mapa.draw_poison()
    for x in mapa.list_caminos:
        x.draw_path(0.1)

    mapa.draw_best()
    mapa.draw_history()



   

    
    
