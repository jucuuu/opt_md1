# opt_md1

Izmantotas tikai native Python bibliotēkas.

Palaiž visus testus:

```
python main.py
```

Visi argumenti:

--test: testu nr. (var norādīt vienu, var vairākus)

--maxi-iters: maksimālais iterāciju skaits tabu algoritmā

--tabu-steps: tabu rindas lielums

--seed: random() inicializācijas vērtība

--exact-limit: maksimālais iterāciju skaits palīgf-jām, kas aprēķina faktisko mazāko laiku skaitu

```
python main.py --test 1 2 3 4 5 --max-iters 100000 --tabu-steps 10 --seed 14 --exact-limit 2000000
```

Kur 1 - primitīvs tests (3 kursi, 3 minimālās krāsas);

2 - mazs tests (6 kursi, 5 studenti; cikli 1-2-3 + cikls 3-4-5-6-1 -> minimālais skaits: 3 laiki);

3 - vidējie piemēri ar 40 studentiem un 12 kursiem un 2-4 un 4-6 izvēlētām reģistrācijām;

4 - lielie piemēri ar 200 studentiem un 33 kursiem un 4-6 un 5-8 izvēlētām reģistrācijām;

5 - lielie piemēri ar 200 studentiem un 33 kursiem, kas veido 32/33 virsotņu ciklus vai div-/trīs-/četrdaļīgus grafus.
