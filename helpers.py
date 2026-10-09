from timeslots_tabu import Kurss, Students, RegistracijasKursiem, TabuState, TabuKursi
from collections import defaultdict
import random

def print_schedule(name, best_k, solution):
    print(f"\nREZULTĀTS | {name}: {best_k} LAIKI")
    if solution is None:
        print("no solution found")
        return
    by_slot = defaultdict(list)
    for kurss_id, slot in solution.state.items():
        by_slot[slot].append(Kurss.all_kursi[kurss_id - 1].name)   # ids start at 1
    for slot in sorted(by_slot):
        print(f"Eksāmeni {slot}. laikā: {', '.join(by_slot[slot])}")

def is_valid(solution: TabuState, reg: RegistracijasKursiem):
    return all(solution.get_vertex_color(u) != solution.get_vertex_color(v)
               for u, v in reg.get_edges())

def run_test(name, reg, max_iters, tabu_steps=7):
    start_k = len(reg.get_vertices())
    solver = TabuKursi(tabu_steps, start_k, max_iters, reg)
    best_k, solution = solver.tabu()
    print_schedule(name, best_k, solution)
    valid = solution is not None and is_valid(solution, reg)
    if solution is not None:
        print("derīgs risinājums:", valid)
    return best_k, valid, solver.failed

def random_registrations(students, course_ids, min_k, max_k):
    reg = RegistracijasKursiem()
    for s in students:
        reg.insert(s, random.sample(course_ids, random.randint(min_k, max_k)))
    return reg

def create_students(n):
    for i in range(n):
        Students(f"Vārds_{i}")