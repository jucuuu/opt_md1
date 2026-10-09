import argparse
import random
from timeslots_tabu import Students, Kurss, RegistracijasKursiem
from datetime import datetime
from helpers import create_students, run_test, random_registrations, save_run

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=int, nargs="+", choices=[1,2,3,4], default=[1,2,3,4],
                        help="1=primitīvs piemērs, 2=mazs piemērs, 3=vidējais piemērs, 4=lielais testa piemērs (pēc noklusējuma visi)")
    parser.add_argument("--max-iters", type=int, default=100_000, help="iterācijas vienam laikam")
    parser.add_argument("--tabu-steps", type=int, default=10, help="tabu rindas garums")
    parser.add_argument("--seed",type=int,default=14)
    parser.add_argument("--verbose", action="store_true", help="drukāt katru iterāciju")
    parser.add_argument("--exact-limit", type=int, default=2_000_000,
                        help="max pārlases soļi precīzajai atbildei (0 = nepārbaudīt)")
    return parser.parse_args()

def print_summary(results):
    lines = []
    lines.append("\n" + "=" * 110)
    lines.append("KOPSAVILKUMS")
    lines.append(f"{'tests':<34}{'tabu':>5}{'greedy':>8}{'clique':>7}{'exact':>9}  "
                 f"{'optimal':<10}{'valid':<8}{'tabu time':>11}  apstājās:")

    for r in results:
        if r["exact"] is not None:
            opt = "jā" if r["best_k"] == r["exact"] else "nē"
        elif r["best_k"] == r["lower"]:
            opt = "jā"
        else:
            opt = "?"

        exact = "?" if r["exact"] is None else r["exact"]

        if r["failed"] is None:
            stop = "-"
        else:
            fail_k, reason, cost = r["failed"]
            stop = f"mēģinot {fail_k}: {reason}, cost {cost}"

        lines.append(f"{r['name']:<34}{r['best_k']:>5}{r['greedy_k']:>8}{r['lower']:>7}{exact!s:>9}  "
                     f"{opt:<10}{r['valid']!s:<8}{r['seconds']:>9.3f} s  {stop}")

    lines.append(f"{'kopā (tabu)':<34}{'':>49}{sum(r['seconds'] for r in results):>9.3f} s")

    text = "\n".join(lines)
    print(text)
    return text


def main():
    args = parse_args()
    started = datetime.now()
    random.seed(args.seed)
    create_students(200)
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
    k = [kurss.id for kurss in kursi]

    tests = []   # (nosaukums, reģistrācijas)

    """
        Primitīvs testa piemērs - trijstūris -> 3 laiki.
    """
    if 1 in args.test:
        nano = RegistracijasKursiem()
        nano.insert(s[0], [k[0], k[1]])
        nano.insert(s[1], [k[1], k[2]])
        nano.insert(s[2], [k[0], k[2]])
        tests.append(("nano tests (trijstūris, 3 laiki)", nano))

    """
        Mazs testa piemērs: 6 kursi, 5 studenti.
        Cikls 1-2-3 + cikls 3-4-5-6-1 -> minimālais skaits: 3 laiki.
    """
    if 2 in args.test:
        mini = RegistracijasKursiem()
        mini.insert(s[0], [k[0], k[1], k[2]])
        mini.insert(s[1], [k[2], k[3]])
        mini.insert(s[2], [k[3], k[4]])
        mini.insert(s[3], [k[4], k[5]])
        mini.insert(s[4], [k[5], k[0]])
        tests.append(("mini tests (min=3)", mini))

    """
        Vidēji testa piemēri: 12 kursi, 40 studenti, katram 2-4 / 4-6 (nejauši) kursi.
    """
    if 3 in args.test:
        tests.append(("mid tests 1 (2-4 kursi)", random_registrations(s[:40], k[:12], 2, 4)))
        tests.append(("mid tests 2 (4-6 kursi)", random_registrations(s[:40], k[:12], 4, 6)))

    """
        Lielāki testa piemēri: 33 kursi, 200 studenti, katram 3-5 / 5-8 (nejauši) kursi.
    """
    if 4 in args.test:
        tests.append(("mega tests 1 (3-5 kursi)", random_registrations(s, k, 3, 5)))
        tests.append(("mega tests 2 (5-8 kursi)", random_registrations(s, k, 5, 8)))

    results = [run_test(name, reg, args.max_iters, args.tabu_steps, args.verbose, args.exact_limit)
               for name, reg in tests]
    summary_text = print_summary(results)
    save_run(started, args, results, summary_text)
if __name__ == "__main__":
    main()