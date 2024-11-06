import random as random

# Función que selecciona un índice en base a probabilidades ponderadas
def weighted_choice_sub(weights):
    rnd = random.random() * sum(weights)  # Genera un número aleatorio entre 0 y la suma de los pesos
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:  # Si el valor alcanza cero, devuelve el índice
            return i

# Función lambda que genera una lista binaria aleatoria de tamaño `n`
generate_random_binary_list = lambda n: [random.randint(0,1) for b in range(1,n+1)]

# Clase que representa a un individuo con un genoma, rasgos y fitness
class Individual (object):
    
    def __init__(self, genome):
        self.genome = genome        
        self.traits = {}  # Diccionario de rasgos
        self.performances = {}  # Diccionario de rendimiento
        self.fitness = 0  # Valor de aptitud (fitness)

# Genera un genoma aleatorio según la cantidad de bits por cada rasgo en `dict_genes`
def generate_genome (dict_genes):
    number_of_bits = sum([dict_genes[trait] for trait in dict_genes])  # Suma de bits requeridos
    return generate_random_binary_list(number_of_bits)  # Genera un genoma aleatorio de esa longitud

# Calcula los rasgos de un individuo decodificando su genoma
def calculate_traits (individual, dict_genes):
    dict_traits = {}
    index = 0
    for trait in dict_genes:
        # Convierte la secuencia binaria en valor decimal para el rasgo correspondiente
        dict_traits[trait] = int(''.join(str(bit) for bit in individual.genome[index : index+dict_genes[trait]]), 2)
        index += dict_genes[trait]  # Mueve el índice según la longitud del rasgo en `dict_genes`
    individual.traits = dict_traits

# Agrega nuevos individuos a `society` hasta alcanzar `target_population`
def immigration (society, target_population, calculate_performances, calculate_fitness, dict_genes, Object = Individual, *args):
    while len(society) < target_population:
        new_individual = Object (generate_genome (dict_genes), args)
        calculate_traits (new_individual, dict_genes)  # Calcula sus rasgos
        calculate_performances (new_individual)  # Calcula su rendimiento
        calculate_fitness (new_individual)  # Calcula su fitness
        society.append (new_individual)  # Agrega el nuevo individuo a la sociedad

# Realiza el cruce (reproducción) de individuos en la sociedad y mutación de sus genomas
def crossover (society, reproduction_rate, mutation_rate, calculate_performances, calculate_fitness, dict_genes, Object = Individual, *args):
    fitness_list = [individual.fitness for individual in society]  # Lista de valores de fitness
    society_sorted = [x for (y, x) in sorted(zip(fitness_list, society), key=lambda x: x[0], reverse=True)]  # Ordena individuos por fitness
    probability = [i for i in reversed(range(1,len(society_sorted)+1))]  # Probabilidad descendente según el orden

    # Probabilidades de mutación
    mutation = [1 - mutation_rate, mutation_rate]    
    
    for i in range (int(len(society) * reproduction_rate)):
        # Selección de padres de forma aleatoria y ponderada
        father, mother = society_sorted[weighted_choice_sub(probability)], society_sorted[weighted_choice_sub(probability)]
        # Selección aleatoria de puntos de corte para el cruce
        a, b = random.randrange(0, len(father.genome)), random.randrange(0, len(father.genome))
        # Crea el genoma del hijo combinando los segmentos de genoma de los padres
        child_genome = father.genome[0:min(a,b)]+mother.genome[min(a,b):max(a,b)]+father.genome[max(a,b):]
        
        # Genera la mutación para los bits seleccionados
        n = [weighted_choice_sub(mutation) for ii in range(len(child_genome))]
        # Modifica los bits del genoma del hijo que deben mutar
        mutant_child_genome = [abs(n[i] -  child_genome[i]) for i in range(len(child_genome))]
        
        # Añade el nuevo individuo mutado a la sociedad
        newborn = Object(mutant_child_genome, args)
        calculate_traits (newborn, dict_genes)
        calculate_performances (newborn)
        calculate_fitness (newborn)
        society.append(newborn)

# Función de eliminación para reducir la sociedad al `target_population`
def tournament(society, target_population):
    while len(society) > target_population:
        # Elimina el individuo con el menor fitness de la sociedad
        fitness_list = [individual.fitness for individual in society]
        society.pop(fitness_list.index(min(fitness_list)))  
