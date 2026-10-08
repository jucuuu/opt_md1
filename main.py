from itertools import combinations

class Kurss:
    total = 0
    all_kursi = []
    
    def __init__(self, name):
        Kurss.total += 1
        self.name = name
        self.id = Kurss.total
        Kurss.all_kursi.append(self)
    
    def get(self):
        return { "name": self.name, "id": self.id }
    
    def get_by_id(self, id):
        return Kurss.all_kursi[id]

class Students:
    total = 0
    all_studenti = []
    
    def __init__(self, name):
        Students.total += 1
        self.name = name
        self.id = Students.total
        Students.all_studenti.append(self)
    
    def get(self):
        return { "name": self.name, "id": self.id }
    
    def get_by_id(self, id):
        return Students.all_studenti[id]
    

class RegistracijasKursiem:
    """
        {
            "studenta_id": ["1kursa_id","2kursa_id",...],
            "1": [1,2,3],
            "2": [2,4],
            ...
        }
    """
    def __init__(self, registracijas_kursiem={}):
        super().__init__()
        self.dict = registracijas_kursiem
    
    def insert(self, students, kursi):
        if (isinstance(kursi), list):
            self.dict[students.id] = kursi
        else:
            self.dict[students.id] = [kursi]
    
    def get(self):
        return self.dict
    
    def get_vertices(self):
        # flat map of dict values
        return sorted({ x for v in self.dict.values() for x in v })
    
    def get_edges(self) -> list[tuple]:
        # returns list of tuples [(course1,course2), (...), ...]
        edges = []
        for course_list in self.dict.values():
            for pair in combinations(sorted(set(course_list)), 2):
                edges.add(pair)
        
        return list(set(edges))

class TabuState:
    """
        { class_id: color_id }[]
    """
    def __init__(self, courses=[], state={}):
        self.state = state if state else { c: 1 for c in courses }
    
    def set_vertex_color(self, course, color):
        self.state[course] = color
    
    def get_colors(self):
        return self.state.values()

class TabuKursi:
    def __init__(self, tabu_queue_steps, registracijas_kursiem: RegistracijasKursiem):
        super().__init__()
        self.tabu_queue = []                          # not allowed!
        self.tabu_queue_steps = tabu_queue_steps      # how many of the last moves to remember
        self.best_graph = {}                          # best state
        
        # cost function == current number of colors
        self.colors = 0
        
        # graph stuff
        self.vertices = registracijas_kursiem.get_vertices()   # vertex - a course
        self.edges = registracijas_kursiem.get_edges()         # edge - between all courses that a student takes at once
        
        # starting state: all vertices are the same color
        # because we start by coloring all vertices the same color, all edges create "conflicts" between vertices
        self.state = TabuState(self.vertices)
        self.cost_value = len(self.edges)                  
        self.conflicts = set(self.edges)
    
    def cost(self):
        """
            Šķautņu skaits, kam abos galos ir vienas krāsas virsotnes.
        """
        cost = 0
        for edge in self.edges:
            if self.state[edge[0]] == self.state[edge[1]]:
                cost += 1
        return cost
    
    def neighbourhood(self):
        """
            Risinājumi, ko var panākt ar vienu gājienu (izņemot tabu gājienus).
            
            returns { neighbour_count: int, neighbours: list[TabuState] }
        """
        pass
    
    def step(self, state, kurss, color):
        """
            Gājiens: 1 pārkrāsota virsotne.
        """
        new_state = TabuState(state=state)
        new_state.set_vertex_color(kurss, color)
        
        # process tabu queue
        if len(self.tabu_queue) == self.tabu_queue_steps:
            self.tabu_queue.pop(1)
        self.tabu_queue.append(( kurss, self.state[kurss] )) # don't recolor the vertex back for a while
        
        self.state = new_state
    
    def tabu(self):
        # start with the first class?
        pass

def create_students(n):
    for i in range(n):
        Students(f"Vārds_{i}")

def main():
    create_students(20)
    all_studenti = Students.all_studenti
    kursi = [
        Kurss("Praktiskā kombinatoriālā optimizācija"),
        Kurss("Teorētiskā bastošana 3"),
        Kurss("Franču valoda 1"),
        Kurss("Matemātiskā analīze 1"),
        Kurss("Virtuālās vides"),
        Kurss("Datortīkli 100"),
        *[Kurss(x) for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    ]
    
    """
        Primitīvs testa piemērs.
    """
    nano_registracijas_kursiem = []
    
    
    """
        Mazs testa piemērs: 6 kursi, 5 studenti.
    """
    mini_registracijas_kursiem = []
    
    """
        Vidējs testa piemērs.
    """
    mid_registracijas_kursiem = []
    
    """
        Lielāks testa piemērs.
    """
    mega_registracijas_kursiem = []