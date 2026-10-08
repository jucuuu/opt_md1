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

class TabuKursi:
    def __init__(self, steps, registracijas_kursiem: RegistracijasKursiem):
        super().__init__()
        self.tabu_list = []     # not allowed!
        self.best = {}          # best result
        self.steps = steps      # how many of the last moves to remember
        self.min_colors = 0
        
        # graph stuff
        self.vertices = registracijas_kursiem.get_vertices()   # vertex - a course
        self.edges = registracijas_kursiem.get_edges()         # edge - between all courses that a student takes at once
    
    def neighbourhood(self):
        pass
        
    def step(self):
        pass
    
    def tabu(self):
        # start with all cour
        pass

def create_students(n):
    for i in range(n):
        Students(f"Vārds_{i}")

def main():
    """
        stuff...
    """
    
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