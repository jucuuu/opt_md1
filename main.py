import argparse
import random
import time
from timeslots_tabu import Students, Kurss, RegistracijasKursiem
from helpers import create_students, run_test, random_registrations

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=int, nargs="+", choices=[1,2,3,4], default=[1,2,3,4],
                        help="1=primitīvs piemērs, 2=mazs piemērs, 3=vidējais piemērs, 4=lielais testa piemērs (pēc noklusējuma visi)")
    parser.add_argument("--seed",type=int,default=14)
    return parser.parse_args()

def main():
    args = parse_args()
    random.seed(14)
    create_students(200)
    results = []  # (test_name, best_k, valid, seconds)
    
    def timed(name, reg, max_iters, tabu_steps):
        start = time.perf_counter()
        best_k, valid, fail_info = run_test(name, reg, max_iters=max_iters, tabu_steps=tabu_steps)
        results.append((name, best_k, valid, fail_info, time.perf_counter() - start))
    
    s = Students.all_studenti
    kursi = [
        Kurss("Praktiskā kombinatoriālā optimizācija"),
        Kurss("Teorētiskā bastošana 3"),
        Kurss("Franču valoda 1"),
        Kurss("Matemātiskā analīze 1"),
        Kurss("Virtuālās vides"),
        Kurss("Praktiskā bastošana 1"),
        Kurss("Datortīkli 100"),
        *[Kurss(x) for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
    ]
    print(len(kursi))
    k = [kurss.id for kurss in kursi]
    
    """
        Primitīvs testa piemērs - trijstūris.
    """
    if (1 in args.test):
        nano_test = RegistracijasKursiem()
        nano_test.insert(s[0], [k[0], k[1]])
        nano_test.insert(s[1], [k[1], k[2]])
        nano_test.insert(s[2], [k[0], k[2]])
        timed("nano tests (trijstūris, 3 laiki)", nano_test, 100, 10)
    
    
    """
        Mazs testa piemērs: 6 kursi, 5 studenti.
        Cikls 1-2-3 + cikls 3-4-5-6-1 -> minimālais skaits: 3 laiki.
    """
    if (2 in args.test):
        mini_test = RegistracijasKursiem()
        mini_test.insert(s[0], [k[0], k[1], k[2]])
        mini_test.insert(s[1], [k[2], k[3]])
        mini_test.insert(s[2], [k[3], k[4]])
        mini_test.insert(s[3], [k[4], k[5]])
        mini_test.insert(s[4], [k[5], k[0]])
        timed("mini tests (min=3)", mini_test, 500, 10)

        
    """
        Vidējs testa piemērs: 12 kursi, 40 studenti, katram 2-4 (nejauši) kursi.
    """
    if (3 in args.test):
        mid = random_registrations(s[:40], k[:12], 2, 4)
        timed("mid tests 1", mid, 2000, 10)
        
    """
        Vidēja testa variācija: 12 kursi, 40 studenti, katram 4-6 (nejauši) kursi.
    """
    if (3 in args.test):
        mid = random_registrations(s[:40], k[:12], 4, 6)
        timed("mid tests 2", mid, 2000, 10)
    
    """
        Lielāks testa piemērs, reģistrēti 3-5 kursiem.
    """
    if (4 in args.test):
        mega = random_registrations(s, k, 3, 5)
        timed("mega tests 1", mega, 10000, 10)
    
    """
        Lielāks testa piemērs, reģistrēti 5-8 kursiem.
    """
    if (4 in args.test):
        mega = random_registrations(s, k, 5, 8)
        timed("mega tests 2", mega, 10000, 10)
    
    print("\nKOPSAVILKUMS")
    for name, best_k, valid, fail_info, seconds in results:
        if fail_info is None:
            stop = "-"
        else:
            fail_k, reason, cost = fail_info
            stop = f"mēģinot {fail_k}, stop_reason: {reason}, cost {cost}"
        print(f"{name:<35} laiki: {best_k!s:>4}; derīgs: {valid!s:<5} {seconds:8.3f} s | {stop}")
    print(f"{'kopā':<35} {sum(r[4] for r in results):8.3f} s")
    
if __name__ == "__main__":
    main()

