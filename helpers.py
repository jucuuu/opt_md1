from timeslots_tabu import Kurss, Students, RegistracijasKursiem, TabuState, TabuKursi
from collections import defaultdict
from datetime import datetime
import random
import time
import json
import hashlib
import os

CACHE_FILE = "exact_cache.txt"
RESULTS_DIR = "results"

def graph_key(reg: RegistracijasKursiem):
    data = json.dumps([reg.get_vertices(), sorted(reg.get_edges())])
    return hashlib.sha1(data.encode()).hexdigest()

def load_cache():
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    cache[entry["key"]] = entry   # later lines override earlier ones
    return cache

def save_cache_entry(entry):
    with open(CACHE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def exact_measurements(reg, tabu_steps, max_iters, max_nodes):
    """ (lower, greedy_k, exact) from cache, or computed and cached. """
    key = graph_key(reg)
    cached = load_cache().get(key)
    if cached and (cached["exact"] is not None or (max_nodes or 0) <= cached["max_nodes"]):
        print("precīzās atbildes: no kešatmiņas")
        return cached["lower"], cached["greedy_k"], cached["exact"]

    checker = TabuKursi(tabu_steps, len(reg.get_vertices()), max_iters, reg)
    lower = len(checker.max_clique())
    greedy_k = max(checker.greedy_coloring().get_colors(), default=0)
    if lower == greedy_k:
        exact = lower
    elif max_nodes:
        exact = checker.exact_answer(lower, greedy_k, max_nodes)
    else:
        exact = None

    save_cache_entry({"key": key, "lower": lower, "greedy_k": greedy_k,
                      "exact": exact, "max_nodes": max_nodes or 0})
    return lower, greedy_k, exact

def schedule_by_slot(solution):
    """ { laiks: [kursu nosaukumi] } """
    by_slot = defaultdict(list)
    for kurss_id, slot in solution.state.items():
        by_slot[slot].append(Kurss.get_by_id(kurss_id).name)
    return {slot: by_slot[slot] for slot in sorted(by_slot)}

def print_schedule(name, best_k, solution):
    print(f"\nREZULTĀTS | {name}: {best_k} LAIKI")
    for slot, names in schedule_by_slot(solution).items():
        print(f"Eksāmeni {slot}. laikā: {', '.join(names)}")

def is_valid(solution: TabuState, reg: RegistracijasKursiem):
    return all(solution.get_vertex_color(u) != solution.get_vertex_color(v)
               for u, v in reg.get_edges())


def run_test(name, reg, max_iters, tabu_steps=10, verbose=False, max_nodes=2_000_000):
    print(f"\n========== {name} ==========")
    start_k = len(reg.get_vertices())

    # exact answers
    lower, greedy_k, exact = exact_measurements(reg, tabu_steps, max_iters, max_nodes)
    print(f"clique: {lower}, greedy: {greedy_k}, actual: {exact if exact is not None else 'nezināms'}")

    # tabu search (timed)
    solver = TabuKursi(tabu_steps, start_k, max_iters, reg)
    start = time.perf_counter()
    best_k, solution = solver.tabu(verbose)
    seconds = time.perf_counter() - start

    print_schedule(name, best_k, solution)
    valid = is_valid(solution, reg)
    print("derīgs risinājums:", valid)

    return {
        "name": name,
        "best_k": best_k,
        "greedy_k": greedy_k,
        "lower": lower,
        "exact": exact,
        "valid": valid,
        "failed": solver.failed,
        "seconds": seconds,
        "graph_key": graph_key(reg),
        "schedule": schedule_by_slot(solution),
    }

def save_run(started: datetime, args, results, summary_text):
    """
        Saglabā palaišanas rezultātus results/run_<laiks>.txt (lasāms)
        un results/run_<laiks>.json (pilni dati).
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    stamp = started.strftime("%Y-%m-%d_%H-%M-%S")
    base = os.path.join(RESULTS_DIR, f"run_{stamp}")
    settings = vars(args)

    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write(f"Palaists: {started:%Y-%m-%d %H:%M:%S}\n")
        f.write("Parametri: " + ", ".join(f"{k}={v}" for k, v in settings.items()) + "\n")
        f.write(summary_text + "\n")
        for r in results:
            f.write(f"\nREZULTĀTS | {r['name']}: {r['best_k']} LAIKI\n")
            for slot, names in r["schedule"].items():
                f.write(f"Eksāmeni {slot}. laikā: {', '.join(names)}\n")

    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump({"started": started.isoformat(timespec="seconds"),
                   "args": settings,
                   "results": results}, f, ensure_ascii=False, indent=2)

    print(f"\nRezultāti saglabāti: {base}.txt, {base}.json")

def random_registrations(students, course_ids, min_k, max_k):
    reg = RegistracijasKursiem()
    for s in students:
        reg.insert(s, random.sample(course_ids, random.randint(min_k, max_k)))
    return reg

def create_students(n):
    for i in range(n):
        Students(f"Vārds_{i}")