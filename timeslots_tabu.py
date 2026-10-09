from itertools import combinations
from collections import deque, defaultdict
import random


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

    @staticmethod
    def get_by_id(id):
        return Kurss.all_kursi[id - 1]           # id starts w 1

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

    @staticmethod
    def get_by_id(id):
        return Students.all_studenti[id - 1]    # id starts w 1


class RegistracijasKursiem:
    """
        {
            "studenta_id": ["1kursa_id","2kursa_id",...],
            "1": [1,2,3],
            "2": [2,4],
            ...
        }
    """
    def __init__(self, registracijas_kursiem=None):
        self.dict = dict(registracijas_kursiem) if registracijas_kursiem else {}
    
    def insert(self, students, kursi):
        if isinstance(kursi, list):
            self.dict[students.id] = kursi
        else:
            self.dict[students.id] = [kursi]
    
    def get(self):
        return self.dict
    
    def get_vertices(self):
        # flat map of dict values
        return sorted({ x for v in self.dict.values() for x in v })
    
    def get_edges(self) -> set[tuple]:
        # returns list of tuples [(course1,course2), (...), ...]
        edges = set()
        for course_list in self.dict.values():
            for pair in combinations(sorted(set(course_list)), 2):
                edges.add(pair)
        return edges
    
class TabuState:
    """
        { class_id: timeslot_id }[]
    """
    def __init__(self, courses=None, state=None):
        if state is not None:
            self.state = dict(state)            # copy...
        else:
            self.state = {c: 1 for c in (courses or [])}

    def set_vertex_color(self, course, color):
        self.state[course] = color
    
    def get_vertex_color(self, course):
        return self.state[course]
    
    def get_colors(self):
        return self.state.values()
    
    def copy(self):
        return TabuState(state=self.state)

    def __repr__(self):
        return f"{self.state}"


class _NodeLimit(Exception):
    """ Precīzā pārlase pārsniedza atļauto virsotņu skaitu. """

class TabuKursi:
    def __init__(self, tabu_queue_steps, timeslots, max_iters, registracijas_kursiem: RegistracijasKursiem):
        super().__init__()
        self.tabu_queue = deque(maxlen=tabu_queue_steps)  # not allowed!
        self.best_graph = {}                              # best state
        self.timeslots = timeslots                        # timeslots (gradually lowered to check if it's still doable)
        
        # graph stuff
        self.vertices = registracijas_kursiem.get_vertices()   # vertex - a course
        self.edges = registracijas_kursiem.get_edges()         # edge - between all courses that a student takes at once
        
        self.neighbor_vertices = defaultdict(set)
        for u,v in self.edges:
            self.neighbor_vertices[u].add(v)
            self.neighbor_vertices[v].add(u)
        
        # starting state: all vertices are the same color
        # because we start by coloring all vertices the same color, all edges create "conflicts" between vertices
        self.state = TabuState(self.vertices)
        self.starting_state = TabuState(self.vertices)
        self.conflicts = set(self.edges)
        self.cost_value = len(self.conflicts)
        
        self.best_state = self.state.copy()
        self.best_cost = self.cost_value
        
        self.max_iters = max_iters
        self.stop_reason = None
        self.failed = None

    def cost(self):
        """
            Šķautņu skaits, kam abos galos ir vienas krāsas virsotnes.
        """
        return sum(1 for u,v in self.edges if self.state.get_vertex_color(u) == self.state.get_vertex_color(v))

    def conflicts_if_step(self, kurss, color):
        """Prognosis for conflict count if step is made..."""
        previous_color = self.state.get_vertex_color(kurss)
        delta = 0
        for v in self.neighbor_vertices[kurss]:
            v_color = self.state.get_vertex_color(v)
            if v_color == color: delta += 1
            elif v_color == previous_color: delta -= 1
        return delta
    
    def neighbourhood(self):
        """
            Gājieni, ko var veikt (bez tabu...).
        """
        conflicting = {v for edge in self.conflicts for v in edge}
        neighbours = []
        
        for kurss in conflicting:
            current_color = self.state.get_vertex_color(kurss)
            for color in range(1, self.timeslots + 1):
                if color == current_color: continue
                new_cost = self.cost_value + self.conflicts_if_step(kurss, color)
                if (((kurss, color) in self.tabu_queue) and new_cost >= self.best_cost): continue
                neighbours.append((kurss, color, new_cost))
        
        return neighbours
    
    def _edge(self, u, v):
        return (u,v) if u < v else (v,u)
    
    def step(self, kurss, color):
        """
            Gājiens: 1 pārkrāsota virsotne.
        """
        previous_col = self.state.get_vertex_color(kurss)
        self.state.set_vertex_color(kurss, color)
        
        for v in self.neighbor_vertices[kurss]:
            v_color = self.state.get_vertex_color(v)
            e = self._edge(kurss, v)
            if v_color == previous_col: self.conflicts.discard(e) # resolved conflict!
            elif v_color == color: self.conflicts.add(e)
        
        self.cost_value = len(self.conflicts)
        
        self.tabu_queue.append((kurss, previous_col))
        
        if self.cost_value < self.best_cost:
            self.best_cost = self.cost_value
            self.best_state = self.state.copy()
    
    def tabu_loop(self, verbose=True):
        def log(*args):
            if verbose: print(*args)
        
        log(f"Beginning tabu... checking if max_timeslots={self.timeslots} is enough, curr cost={self.cost_value}")
        log("state:", self.state)
        
        for it in range(self.max_iters):
            if self.cost_value == 0:
                self.stop_reason = "Atrisināts"
                log(f"DONE at iteration {it}/{self.max_iters} with max_timeslots={self.timeslots}")
                return True
            
            log(f"ITERATION {it}")
            log("state before:",self.state)
            log("tabu before:",self.tabu_queue)
            log(f"cost before: {self.cost_value}")
            log(f"conflicts before: {sorted(self.conflicts)}")
            
            neighbourhood = self.neighbourhood()
            log(f"neighbourhood move cnt: {len(neighbourhood)}")
            for kurss, color, cost in sorted(neighbourhood, key=lambda n: n[2]):
                log(f"course {kurss} / color {color} / cost {cost}")
            
            if not neighbourhood:
                log("no allowed moves.")
                self.stop_reason = "Nav atļautu gājienu"
                return False

            best_n_cost = min(n[2] for n in neighbourhood) # [2] -> cost
            kurss, color, _ = random.choice([n for n in neighbourhood if n[2] == best_n_cost])
            
            self.step(kurss, color)
            
            log("tabu after:", list(self.tabu_queue))
            log("state after:", self.state)
            log("cost after:",self.cost_value)
            log("current best:",self.best_cost)

        if self.best_cost == 0:     # solved on the very last iteration
            self.stop_reason = "Atrisināts"
            return True

        self.stop_reason = "Max iterācijas"
        log("FINISHED, best cost:",self.best_cost)
        return False

    def reset(self):
        """
            Sākuma stāvoklis.
        """
        self.state = self.starting_state.copy()
        self.conflicts = {e for e in self.edges
                        if self.state.get_vertex_color(e[0]) == self.state.get_vertex_color(e[1])}
        self.cost_value = len(self.conflicts)

        self.tabu_queue.clear()

        self.best_state = self.state.copy()
        self.best_cost = self.cost_value
    
    def tabu(self, verbose=True):
        best_k = len(self.vertices)
        best_solution = TabuState(state={v: i + 1 for i, v in enumerate(self.vertices)})
        self.failed = None
        print(f"RUNNING WITH MAX_TIMESLOTS={self.timeslots}")
        while self.timeslots >= 1:
            self.reset()
            if not self.tabu_loop(verbose):
                self.failed = (self.timeslots, self.stop_reason, self.best_cost)
                print(f"max {self.timeslots} timeslots failed (best cost reached: {self.best_cost})")
                break
            best_k, best_solution = self.timeslots, self.best_state.copy()
            self.timeslots -= 1

        print(f"FINAL BEST: {best_k} timeslots, cost 0")
        return best_k, best_solution

    # ------------------------------------------- precīzā pārbaude (Claude)

    def greedy_coloring(self):
        """ Derīgs sadalījums ar greedy; tikai augšējā robeža precīzajai pārbaudei. """
        colors = {}
        for v in sorted(self.vertices, key=lambda v: -len(self.neighbor_vertices[v])):
            used = {colors[u] for u in self.neighbor_vertices[v] if u in colors}
            c = 1
            while c in used:
                c += 1
            colors[v] = c
        return TabuState(state=colors)

    def max_clique(self):
        """ Max clique (Brona–Kerboša algoritms ar pivotu) = apakšējā robeža. """
        best = []

        def expand(R, P, X):
            nonlocal best
            if not P and not X:
                if len(R) > len(best):
                    best = R
                return
            if len(R) + len(P) <= len(best):    # nevar pārspēt esošo
                return
            pivot = max(P | X, key=lambda u: len(self.neighbor_vertices[u] & P))
            for v in list(P - self.neighbor_vertices[pivot]):
                expand(R + [v], P & self.neighbor_vertices[v], X & self.neighbor_vertices[v])
                P = P - {v}
                X = X | {v}

        expand([], set(self.vertices), set())
        return best

    def is_k_colorable(self, k, max_nodes=None):
        """
            Precīza pārbaude (pilnā pārlase): vai var sadalīt k laikos?
            returns True / False, vai None, ja pārsniegts max_nodes.
        """
        order = sorted(self.vertices, key=lambda v: -len(self.neighbor_vertices[v]))
        colors = {}
        nodes = 0

        def bt(i, highest):
            nonlocal nodes
            nodes += 1
            if max_nodes is not None and nodes > max_nodes:
                raise _NodeLimit
            if i == len(order):
                return True
            v = order[i]
            used = {colors[u] for u in self.neighbor_vertices[v] if u in colors}
            # laiki ir savstarpēji aizvietojami: jaunu laiku atver tikai pa vienam
            for c in range(1, min(k, highest + 1) + 1):
                if c not in used:
                    colors[v] = c
                    if bt(i + 1, max(highest, c)):
                        return True
                    del colors[v]
            return False

        try:
            return bt(0, 0)
        except _NodeLimit:
            return None

    def exact_answer(self, lower, upper, max_nodes=None):
        """
            Mazākais derīgais k intervālā [lower, upper]; upper zināms kā derīgs.
            returns k, vai None, ja pārlase bija par lielu.
        """
        for k in range(lower, upper):
            result = self.is_k_colorable(k, max_nodes)
            if result is None:
                return None
            if result:
                return k
        return upper