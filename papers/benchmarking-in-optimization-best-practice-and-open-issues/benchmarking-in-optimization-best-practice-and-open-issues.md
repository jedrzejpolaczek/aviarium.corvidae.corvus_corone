---
title: "Benchmarking w optymalizacji: dobre praktyki i otwarte problemy"
author: "Tłumaczenie automatyczne z języka angielskiego"
date: "2020-12-18 (oryginał), tłumaczenie: [uzupełnij]"
---

# Benchmarking w optymalizacji: dobre praktyki i otwarte problemy

Thomas Bartz-Beielstein¹, Carola Doerr², Daan van den Berg³, Jakob Bossek⁶,  
Sowmya Chandrasekaran¹, Tome Eftimov⁵, Andreas Fischbach¹, Pascal Kerschke⁶,  
William La Cava⁹, Manuel López-Ibáñez⁷, Katherine M. Malan⁸, Jason H. Moore⁹,  

Boris Naujoks¹, Patryk Orzechowski⁹˒¹⁰, Vanessa Volz¹¹, Markus Wagner⁴  
i Thomas Weise¹²  

¹ Institute for Data Science, Engineering, and Analytics, TH Köln, Niemcy  
² Sorbonne Université, CNRS, LIP6, Paryż, Francja  
³ Yamasan Science & Education  
⁴ Optimisation and Logistics, School of Computer Science, The University of Adelaide, Adelaide, Australia  
⁵ Computer Systems Department, Jožef Stefan Institute, Lublana, Słowenia  
⁶ Statistics and Optimization Group, University of Münster, Münster, Niemcy  
⁷ School of Computer Science and Engineering, University of Málaga, Málaga, Hiszpania  
⁸ Department of Decision Sciences, University of South Africa, Pretoria, RPA  
⁹ Institute for Biomedical Informatics, University of Pennsylvania, Philadelphia, PA, USA  
¹⁰ Department of Automatics, AGH University of Science and Technology, Kraków, Polska  
¹¹ modl.ai, Kopenhaga, Dania  
¹² Institute of Applied Optimization, School of Artificial Intelligence and Big Data, Hefei University, Hefei, Chiny  

benchmarkingbestpractice@gmail.com  

**18 grudnia 2020**  
Wersja 2  

---

## Abstrakt

Niniejsze opracowanie zbiera idee i rekomendacje od ponad tuzina badaczy o różnych profilach i z różnych instytucji na całym świecie. Promowanie najlepszych praktyk w benchmarkingu jest jego głównym celem. Artykuł omawia osiem kluczowych zagadnień związanych z benchmarkingiem: jasno określone cele, dobrze zdefiniowane problemy, odpowiednie algorytmy, adekwatne miary wydajności, przemyślaną analizę, skuteczne i efektywne plany eksperymentalne, zrozumiałą prezentację wyników oraz zagwarantowaną odtwarzalność. Ostatecznym celem jest dostarczenie dobrze akceptowanych wytycznych (reguł), które mogą być użyteczne dla autorów i recenzentów. Ponieważ benchmarking w optymalizacji jest aktywną i rozwijającą się dziedziną badań, niniejszy rękopis ma współewoluować w czasie poprzez okresowe aktualizacje.

---

## 1 Wprowadzenie

Wprowadzenie nowego algorytmu bez przetestowania go na zestawie funkcji benchmarkowych wydaje się bardzo dziwne dla każdego praktyka optymalizacji – chyba że istnieje silna motywacja teoretyczna, uzasadniająca zainteresowanie tym algorytmem. Poza pracami skoncentrowanymi na teorii, od samego początku – już w latach 60. – niemal każdej publikacji z zakresu obliczeń ewolucyjnych (Evolutionary Computation, EC) towarzyszyły badania benchmarkowe. Jeden z głównych promotorów EC, Hans-Paul Schwefel [1975], napisał w swojej rozprawie doktorskiej:

> Ogromna i stale rosnąca liczba metod optymalizacji nieuchronnie prowadzi do pytania o najlepszą strategię. Nie wydaje się, aby istniała jednoznaczna odpowiedź. Bo gdyby istniał optymalny proces optymalizacji, wszystkie inne metody byłyby zbędne...

Słynne badania, takie jak prace Moré i in. [1981], były prowadzone w tym okresie i ustanowiły funkcje testowe, które do dziś są dobrze znane twórcom algorytmów. Niektóre z nich nadal pojawiają się w zestawach benchmarkowych, np. funkcja Rosenbrocka [Rosenbrock, 1960]. W latach 60. eksperymenty można było wielokrotnie powtórzyć tylko w bardzo ograniczonym stopniu – z użyciem różnych punktów startowych lub ziaren losowości. Ta sytuacja uległa jednak drastycznej zmianie: obecnie nowe algorytmy mogą być uruchamiane setki, a nawet tysiące razy. Umożliwia to tworzenie bardzo złożonych i zaawansowanych zestawów benchmarkowych, takich jak te dostępne na platformie COCO (Comparing Continuous Optimizers) [Hansen et al., 2016b] lub w bibliotece Nevergrad [Rapin and Teytaud, 2018].  

Niemniej jednak pytania, na które ma odpowiadać benchmarking, pozostają zasadniczo takie same, np.:

- jak dobrze dany algorytm radzi sobie z danym problemem?
- dlaczego algorytm odnosi sukces / ponosi porażkę na konkretnym problemie testowym?

Określenie celu badania benchmarkowego jest równie ważne jak samo badanie, ponieważ kształtuje ono konfigurację eksperymentu – tzn. wybór instancji problemu, instancji algorytmu, kryteriów wydajności oraz narzędzi statystycznych. Typowe cele, na które użytkownik lub badacz chce odpowiedzieć poprzez badanie benchmarkowe, omawiamy w sekcji 2.

Nie tylko moc obliczeniowa wzrosła znacząco w ostatnich dekadach. Teoria również poczyniła ważne postępy. W latach 80. niektórzy badacze twierdzili, że istnieje algorytm, który jest w stanie przeciętnie przewyższać wszystkie inne algorytmy [Goldberg, 1989]. Zestaw twierdzeń typu „no free lunch” (NFL, „brak darmowego obiadu”), przedstawiony przez Wolperta i Macready’ego [1997], zmienił tę sytuację [Adam et al., 2019]. Stwierdzenia dotyczące wydajności algorytmów powinny być powiązane z klasą problemów, a nawet z konkretnymi instancjami problemu. Brownlee [2007] podsumowuje konsekwencje NFL i formułuje następujące zalecenia:

1. ograniczaj twierdzenia o przydatności algorytmu lub parametrów do instancji problemu, które faktycznie zostały przetestowane,
2. badania nad tworzeniem klas problemów i dopasowywaniem odpowiednich algorytmów do klas są pożądane,
3. zachowaj ostrożność przy uogólnianiu wyników wydajności na inne instancje problemu,
4. bądź bardzo ostrożny przy uogólnianiu wydajności na inne klasy problemów lub dziedziny.

Haftka [2016] opisuje konsekwencje NFL następująco:

> Ulepszenie algorytmu dla jednej klasy problemów prawdopodobnie sprawi, że będzie on gorzej działał dla innych problemów.

Niektórzy autorzy twierdzą, że to sformułowanie jest zbyt ogólne i należy je doprecyzować: poprawa wydajności algorytmu (np. poprzez strojenie parametrów) dla pewnego podzbioru problemów może pogorszyć jego działanie dla innego podzbioru. Nie działa to jednak tak dobrze dla całych klas problemów, chyba że zbiory te są skończone i małe. Nie działa też dla dowolnych dwóch podzbiorów, ponieważ mogą być one skorelowane w taki sposób, że prowadzą do lepszej wydajności algorytmu. Wiele prac dyskutuje ograniczenia i wpływ NFL, m.in. García-Martínez et al. [2012] i McDermott [2020]. Przykładowo, Culberson [1998] stwierdził:  

> W kontekście problemów przeszukiwania, twierdzenie NFL w ścisłym sensie ma zastosowanie tylko wtedy, gdy rozważa się zupełnie dowolne „krajobrazy” funkcji celu, podczas gdy instancje praktycznie każdego interesującego problemu przeszukiwania mają zwarte opisy i dlatego nie mogą generować całkowicie dowolnych krajobrazów.

Nie ulega wątpliwości, że NFL zmieniło sposób postrzegania benchmarkingu w EC. Problemy wynikające z NFL są nadal przedmiotem aktualnych badań – np. Liu et al. [2019] omawiają paradoksy związane z numerycznym porównywaniem algorytmów optymalizacji na podstawie NFL. Whitley et al. [2002] analizują sens i znaczenie benchmarków w świetle wyników teoretycznych takich jak NFL.

Niezależnie od trwającej dyskusji wokół NFL, benchmarking odgrywa centralną rolę we współczesnych badaniach, zarówno od strony teorii, jak i praktyki. Trzy główne aspekty, które trzeba uwzględnić w każdym badaniu benchmarkowym, to wybór:

1. miar wydajności,
2. problemów (instancji),
3. algorytmów (instancji).

Od wielu lat istnieją znakomite prace o tym, jak przygotować dobre testy benchmarkowe. Hooker i Johnson to tylko dwaj autorzy, którzy opublikowali artykuły nadal warte lektury [Hooker, 1994, 1996, Johnson et al., 1989, 1991, Johnson, 2002b]. McGeoch [1986] może być uważany za kamień milowy w dziedzinie „algorithmics eksperymentalnych”, która stanowi fundament badań benchmarkowych. Gent i Walsh [1994] stwierdzili, że empiryczne badanie algorytmów jest stosunkowo niedojrzałym polem badań – i uważamy, że niestety sytuacja ta w ostatnich 25 latach nie uległa znaczącej zmianie. Przyczyny tego niezadowalającego stanu rzeczy w EC są liczne. Między innymi społeczność EC nie uzgodniła ogólnej metodologii prowadzenia badań benchmarkowych – takiej, jaka istnieje np. w statystycznym Planowaniu Doświadczeń (Design of Experiments, DoE) czy data miningu [Chapman et al., 2000, Montgomery, 2017]. Dziedziny te oferują ustrukturyzowane metody, które zachęcają praktyków do uwzględniania ważnych kwestii przed rozpoczęciem badań. Niektóre czasopisma wprowadzają wręcz minimalne standardy wymagań².

Pozostaje pytanie: dlaczego minimalne standardy nie są brane pod uwagę w każdej pracy zgłaszanej na konferencje i do czasopism EC? Albo, inaczej: dlaczego najlepsze praktyki nie stały się minimalnymi wymaganymi standardami? Jedną z odpowiedzi może być: przygotowanie solidnego badania benchmarkowego jest bardzo skomplikowane. Istnieje wiele pułapek, szczególnie wynikających ze złożonych zagadnień statystycznych [Črepinšek et al., 2014]. Aby „niczego nie zepsuć”, praktycy często raportują jedynie wartości średnie udekorowane odpowiednimi odchyleniami standardowymi, wartościami p lub wykresami pudełkowymi. Inną odpowiedzią może być: brakuje praktycznych wytycznych. Gdyby istniały dobre przykłady, badacze z informatyki chętniej stosowaliby te rekomendacje. Niniejsza praca jest wspólną inicjatywą kilku badaczy EC. Przedstawia przykłady najlepszych praktyk z odniesieniami do odpowiedniej literatury i dyskutuje otwarte problemy. Inicjatywa została zainicjowana podczas seminarium Dagstuhl 19431 „Theory of Randomized Optimization Heuristics”, które odbyło się w październiku 2019 r. Od tego czasu zbieramy pomysły obejmujące szerokie spektrum dyscyplin powiązanych z EC.

Mamy świadomość, że każda wersja tej pracy stanowi jedynie „migawkę”, ponieważ dziedzina ta ciągle się rozwija. Mogą pojawiać się nowe wyniki teoretyczne, np. nowe twierdzenia typu „no free lunch”, nowe algorytmy (obliczenia kwantowe, heurystyki wspomagane głębokim uczeniem itp.) oraz nowe miary oparte np. na intensywnym próbkowaniu (Monte Carlo) wywodzące się z metod statystycznych.

Traktujemy tę pracę jako punkt wyjścia – pierwszą próbę wsparcia społeczności EC w podnoszeniu jakości badań benchmarkowych. Z pewnością nie obejmuje ona każdego pojedynczego aspektu związanego z benchmarkingiem. Choć skupiamy się głównie na problemach optymalizacji jednokryterialnej, bez ograniczeń, wyniki można stosunkowo łatwo przenieść do innych domen, np. optymalizacji wielokryterialnej lub z ograniczeniami. Cele w innych domenach mogą się nieco różnić i wymagać innych miar wydajności, ale treść większości sekcji pozostaje aktualna.  

Każda z kolejnych sekcji prezentuje przykłady dobrych praktyk, odsyła do literatury i omawia otwarte kwestie. Następujące aspekty, istotne dla każdego badania benchmarkowego, omawiamy w dalszych częściach:

1. **Cele**: dlaczego wykonujemy badania benchmarkowe (sekcja 2)?  
2. **Problemy**: jak wybierać odpowiednie problemy (sekcja 3)?  
3. **Algorytmy**: jak dobrać portfolio algorytmów do badania benchmarkowego (sekcja 4)?  
4. **Wydajność**: jak mierzyć wydajność (sekcja 5)?  
5. **Analiza**: jak oceniać wyniki (sekcja 6)?  
6. **Plan eksperymentu**: jak zaprojektować badanie, np. ile wykonać uruchomień (sekcja 7)?  
7. **Prezentacja**: jak przedstawiać wyniki (sekcja 8)?  
8. **Reprodukowalność**: jak zagwarantować naukowo rzetelne wyniki i długotrwały wpływ, np. w sensie porównywalności (sekcja 9)?

Artykuł kończy się podsumowaniem i spojrzeniem w przyszłość w sekcji 10.

### Uogólnianie wyników benchmarkingu

Jak wspomniano powyżej w kontekście NFL, zalecamy bardzo precyzyjny opis algorytmów i instancji problemu wykorzystanych w badaniu benchmarkowym. Ekstrapolacja wydajności lub uogólnienia muszą zawsze być wyraźnie oznaczone jako takie, a tam, gdzie algorytmy są ze sobą porównywane, należy jasno wskazać podstawę porównania. Sugerujemy bardzo ostrożne rozróżnianie między **algorytmami** (np. „CMA-ES” – Covariance Matrix Adaptation Evolution Strategy [Hansen, 2000]) a **instancjami algorytmów** (np. konkretna implementacja pycma-es [Hansen et al., 2020] z rozmiarem populacji 8, budżetem 100, strategią restartu X itd.).³  

Podobna zasada odnosi się do problemów (np. „funkcja sferyczna”) w porównaniu z **konkretną instancją problemu** (np. pięciowymiarowa funkcja sferyczna  
\( f : \mathbb{R}^5 \to \mathbb{R}, x \mapsto \alpha \sum_{i=1}^d x_i^2 + \beta \)  
z centrum w początku układu współrzędnych, skalowaniem multiplikatywnym \(\alpha\) oraz dodatnim przesunięciem \(\beta\)).  

Idąc o krok dalej, można nawet argumentować, że tak naprawdę benchmarkujemy jedynie **konkretną implementację** danej instancji algorytmu, która zależy od wyboru języka programowania, kompilatora, optymalizacji systemu operacyjnego oraz konkretnych wersji bibliotek programistycznych.

Instancje algorytmów i problemów mogą być (i często są) zrandomizowane, więc wydajność instancji algorytmu na danej instancji problemu jest **ciągiem (z reguły silnie skorelowanych) zmiennych losowych**, po jednej dla każdego kroku algorytmu. W praktyce, replikowalność często osiąga się poprzez ustalenie generatora liczb losowych i zapamiętanie ziarna losowości, co odgrywa ważną rolę w zapewnieniu reprodukowalności, jak omówiono w sekcji 9.

---

## 2 Cele działań benchmarkowych

Motywacje stojące za wykonywaniem badań benchmarkowych nad algorytmami optymalizacji są tak zróżnicowane, jak same algorytmy i problemy. Oprócz celów naukowych, benchmarking może służyć także popularyzacji podejść algorytmicznych lub konkretnych problemów. W tej sekcji koncentrujemy się na podsumowaniu najczęściej spotykanych **celów naukowych** badań benchmarkowych. Rysunek 1 podsumowuje te cele. Znaczenie poszczególnych celów może się różnić w zależności od badania, a proponowana kategoryzacja nie jest jedyną możliwą. Należy ją traktować jako próbę zaproponowania struktury, która dobrze reprezentuje cele benchmarkingu w szeroko rozumianej społeczności naukowej.

Większość wymienionych poniżej celów ma ostatecznie przyczynić się do **lepszego wykorzystania algorytmów w praktyce**, zazwyczaj poprzez lepsze zrozumienie współzależności między wyborami konstrukcyjnymi algorytmu a cechami instancji problemu. Benchmarking odgrywa jednak również ważną rolę jako **pośrednik** między społecznością naukową a użytkownikami heurystyk optymalizacyjnych, a także jako pośrednik między nurtem silniej zorientowanym teoretycznie i nurtem nastawionym na badania empiryczne.

### Rysunek 1. Podsumowanie typowych celów badań benchmarkowych

---

#### G1: Wizualizacja i podstawowa ocena algorytmów oraz problemów

- **G1.1** Podstawowa ocena wydajności i zachowania procesu poszukiwania  
- **G1.2** Porównanie algorytmów  
- **G1.3** Rywalizacja / konkurs (wyłonienie zwycięzcy)  
- **G1.4** Ocena problemu optymalizacyjnego  
- **G1.5** Ilustrowanie zachowania procesu poszukiwania  

---

#### G2: Wrażliwość wydajności na projekt algorytmu i cechy problemu

- **G2.1** Testowanie niezmienniczości (invariances)  
- **G2.2** Strojenie (tuning) parametrów algorytmu  
- **G2.3** Zrozumienie wpływu parametrów i komponentów algorytmicznych  
- **G2.4** Charakteryzowanie wydajności algorytmów poprzez cechy problemu (instancji) i odwrotnie  

---

#### G3: Benchmarking jako trening – ekstrapolacja wydajności

- **G3.1** Regresja wydajności (modelowanie zależności wydajności od cech problemu)  
- **G3.2** Automatyczny dobór, projektowanie i konfiguracja algorytmów (np. AutoML, wybór algorytmu na podstawie danych z benchmarków)  

---

#### G4: Cele zorientowane na teorię

- **G4.1** Walidacja krzyżowa i uzupełnienie wyników teoretycznych  
- **G4.2** Źródło inspiracji dla badań teoretycznych  
- **G4.3** Benchmarking jako pomost między teorią a praktyką  

---

#### G5: Benchmarking w rozwoju algorytmów

- **G5.1** Walidacja kodu źródłowego (sprawdzanie poprawności implementacji)  
- **G5.2** Rozwój algorytmów (identyfikacja słabych stron i ulepszanie metod)  

---

### 2.1 Wizualizacja i podstawowa ocena algorytmów oraz problemów

**(G1.1) Podstawowa ocena wydajności i zachowania procesu poszukiwania.**  
Prawdopodobnie najprostszym pytaniem badawczym, na które można chcieć odpowiedzieć za pomocą badania benchmarkowego, jest: **jak dobrze dany algorytm radzi sobie z danym problemem**. W sytuacji braku analiz matematycznych i wcześniejszych danych, najprostszym podejściem jest uruchomienie jednej lub kilku instancji algorytmu (idealnie: wielokrotnie, jeśli algorytm lub problem są stochastyczne) na jednej lub kilku instancjach problemu i obserwowanie zachowania algorytmu. Na podstawie tych danych można przeanalizować typowy profil wydajności na danej instancji problemu, sposób, w jaki jakość rozwiązań ewoluuje w czasie, poziom stabilności wyników itd. Kryteria oceny mogą być bardzo różne, co omawiamy w sekcji 5.  

Wszystkie badania realizujące cel G1.1 mają jednak wspólną cechę: dążą do odpowiedzi na podstawowe pytania typu „Jak dobrze **ten konkretny algorytm** radzi sobie z **tą konkretną instancją problemu**?” lub „Jak wygląda **konkretny przebieg** działania algorytmu na danym problemie?”.

**(G1.2) Porównanie algorytmów.**  
Zdecydowana większość badań benchmarkowych nie skupia się na pojedynczym algorytmie, lecz porównuje wydajność i/lub zachowanie procesu przeszukiwania **dwóch lub więcej algorytmów**. Porównywanie algorytmów służy przede wszystkim zrozumieniu mocnych i słabych stron różnych podejść algorytmicznych dla różnych typów problemów lub instancji problemu, a także dla różnych etapów procesu optymalizacji. Te spostrzeżenia można wykorzystać do zaprojektowania lub wyboru – dla danej klasy problemów lub konkretnej instancji – najbardziej odpowiedniej instancji algorytmu.

**(G1.3) Rywalizacja / konkurs.**  
Jedną z motywacji porównywania algorytmów jest chęć określenia „zwycięzcy”, tzn. algorytmu, który **przewyższa wszystkich konkurentów** dla danej miary wydajności i zadanego zbioru instancji problemu. Benchmarking jest bardzo cenny w wyborze najbardziej odpowiedniego algorytmu, zwłaszcza w zastosowaniach rzeczywistych [Beiranvand et al., 2017]. Rola badań o charakterze „konkursowym” w benchmarkingu bywa przedmiotem kontrowersji [Hooker, 1996], ponieważ mogą one promować algorytmy nadmiernie dopasowane do problemów, na których zostały przetestowane, prowadząc do przeuczenia (overfittingu). Z drugiej strony nie można ignorować faktu, że konkursy mogą stanowić **silny bodziec** do tworzenia nowych idei algorytmicznych i poprawy strategii wyboru algorytmów.

**(G1.4) Ocena problemu optymalizacyjnego.**  
W wielu rzeczywistych problemach – takich jak szeregowanie zadań, pakowanie kontenerów, sterowanie pracą zakładu chemicznego czy zwijanie białek – globalne optimum jest nieznane, a w innych przypadkach trzeba radzić sobie z ograniczoną wiedzą lub brakiem jawnego wzoru matematycznego. W takich sytuacjach do oceny jakości kandydującego rozwiązania potrzebne są symulacje komputerowe, a nawet rzeczywiste eksperymenty fizyczne. Ponadto, nawet jeśli problem jest jawnie opisany formułą matematyczną, nadal może być trudno zrozumieć jego strukturę lub uzyskać intuicję co do kształtu „krajobrazu” funkcji celu. Podobnie, gdy problem składa się z wielu instancji, może być trudno zrozumieć, pod jakim względem instancje są podobne, a w jakich aspektach się różnią.  

Benchmarking prostych heurystyk optymalizacyjnych może pomóc **analizować i wizualizować** problem optymalizacyjny, a także zdobyć wiedzę o jego charakterystyce.

**(G1.5) Ilustrowanie zachowania procesu poszukiwania.**  
Zrozumienie, w jaki sposób heurystyka optymalizacyjna działa na danym problemie, może być trudne na podstawie samego opisu algorytmu i problemu. Jednym z najbardziej podstawowych celów benchmarkingu jest dostarczenie **ilustracji liczbowych i graficznych** procesu optymalizacji. Dzięki tym liczbom i wizualizacjom można uzyskać pierwsze wyobrażenie o przebiegu optymalizacji. Obejmuje to również ocenę stochastyczności – jeśli rozważamy kilka uruchomień algorytmu losowego lub algorytm działający na stochastycznym problemie. W podobnym duchu benchmarking oferuje praktyczny sposób ilustrowania efektów, które trudno uchwycić wyłącznie z poziomu opisów matematycznych. Tam, gdzie wyrażenia matematyczne nie są dla wszystkich łatwo przyswajalne, benchmarking może posłużyć do zobrazowania opisywanych zjawisk.

### 2.2 Wrażliwość wydajności na projekt algorytmu i cechy problemu

**(G2.1) Testowanie niezmienniczości (invariances).**  
Wielu badaczy argumentuje, że idealnie wydajność algorytmu optymalizacyjnego powinna być **niezmiennicza** względem pewnych aspektów osadzenia problemu, takich jak skalowanie i przesunięcie wartości funkcji celu [Vrielink and van den Berg, 2019], wzrost wymiarowości [De Jonge and van den Berg, 2020] czy rotacja przestrzeni poszukiwań (zob. Hansen [2000] i cytowane tam prace oraz Lehre and Witt [2012], Rowe and Vose [2011] dla przykładów formalizujących pojęcie algorytmów „nieuprzedzonych”, unbiased).

Niektóre niezmienniczości, takie jak „porównaniowość” (comparison-baseness), można zazwyczaj łatwo wywnioskować z pseudokodu algorytmu. Inne (np. niezmienniczość względem translacji lub rotacji) mogą być trudniejsze do uchwycenia. W takich przypadkach benchmarking można wykorzystać do **empirycznego testowania**, czy algorytm faktycznie posiada pożądane własności niezmienniczości.

**(G2.2) Strojenie (tuning) algorytmu.**  
Większość heurystyk optymalizacyjnych jest **konfigurowalna**, czyli możemy zmieniać ich zachowanie (a przez to wydajność), modyfikując parametry. Typowe parametry algorytmów to m.in.:

- liczba osobników przetrzymywanych w pamięci (rozmiar populacji),  
- liczba osobników ocenianych w każdej iteracji,  
- parametry określające rozkład, z którego losowane są nowe próbki (np. średnia, wariancja, kierunek poszukiwań),  
- sposób wyboru osobników przeżywających do kolejnej populacji,  
- kryteria stopu.

Heurystyki stosowane w praktyce często mają **dziesiątki parametrów**, które wymagają dostrojenia.  

Znalezienie optymalnej konfiguracji algorytmu dla danej instancji problemu określa się mianem **offline parameter tuning** [Eiben and Jelasity, 2002, Eiben and Smith, 2015]. Strojenie można przeprowadzać ręcznie lub z pomocą narzędzi automatycznej konfiguracji [Akiba et al., 2019, Bergstra et al., 2013, Olson and Moore, 2016]. Benchmarking jest kluczowym elementem procesu strojenia parametrów. Wymaga on odpowiedniego **planu eksperymentu**, co jest warunkiem niezbędnym dla badań strojenia [Bartz-Beielstein, 2006, Orzechowski et al., 2018, 2020]. Strojenie parametrów jest koniecznym krokiem przed porównywaniem sensownie dostrojonej metody z innymi, ponieważ odrzucamy kombinacje parametrów, które nie dają obiecujących wyników.

Benchmarking pomaga również zrozumieć, jakie wybory parametrów i modułów algorytmu są korzystne. Wybór odpowiedniej parametryzacji dla danego problemu optymalizacyjnego jest żmudnym zadaniem [Fialho et al., 2010]. Oprócz wyboru algorytmu i instancji problemu, strojenie wymaga zdefiniowania miary wydajności, np. najlepszej znalezionej wartości funkcji celu po zadanej liczbie ocen (więcej w sekcji 5) oraz parametrów statystycznych (np. liczby powtórzeń), co omawiamy w sekcji 7.

Kolejną ważną kwestią dotyczącą strojenia jest **odporność wydajności na zmiany parametrów**, tzn. jak bardzo pogarsza się wydajność, gdy parametry zmienimy nieznacznie? Pod tym względem rekomendacje parametrowe o większej odporności mogą być preferowane względem mniej stabilnych, nawet kosztem nieco gorszej wydajności [Paenke et al., 2006].

**(G2.3) Zrozumienie wpływu parametrów i komponentów algorytmicznych.**  
Podczas gdy strojenie (G2.2) koncentruje się na znalezieniu najlepszej konfiguracji dla danego problemu, **zrozumienie** dotyczy pytania: **dlaczego** jeden algorytm działa lepiej niż drugi? Zrozumienie wymaga dodatkowych narzędzi statystycznych, np. analizy wariancji czy metod regresyjnych. Przykładowe pytanie brzmi: „Czy krzyżowanie ma istotny wpływ na wydajność?”.  

Kilka narzędzi łączących metody statystyczne i wizualizacyjne jest zintegrowanych w pakiecie **Sequential Parameter Optimization Toolbox (SPOT)**, zaprojektowanym właśnie do zrozumienia zachowania algorytmów optymalizacyjnych. SPOT dostarcza zestaw narzędzi do optymalizacji modelowej i strojenia algorytmów. Obejmuje modele zastępcze (surrogate), optymalizatory i podejścia DoE [Bartz-Beielstein et al., 2017].

**(G2.4) Charakteryzowanie wydajności algorytmów poprzez cechy problemu (instancji) i odwrotnie.**  
Podczas gdy zrozumienie (G2.3) skupia się na wglądzie w elementy i zasady działania algorytmów, **charakteryzowanie** dotyczy relacji między algorytmami a problemami. Celem jest powiązanie **cech problemu** z **wydajnością algorytmów**. Klasycznym przykładem pytania w tym podejściu jest: jak wydajność algorytmu skaluje się wraz ze wzrostem liczby zmiennych decyzyjnych?

Cechy instancji problemu mogą być cechami wysokiego poziomu, takimi jak wymiarowość, ograniczenia przestrzeni poszukiwań, struktura przestrzeni czy inne podstawowe właściwości problemu. Cechy niższego poziomu, takie jak wielomodalność, separowalność czy „chropowatość” krajobrazu, można wyprowadzić z formuły problemu lub uzyskać poprzez eksploracyjne próbkowanie [Kerschke and Trautmann, 2019a,b, Malan and Engelbrecht, 2013, Mersmann et al., 2010, 2011, Muñoz Acosta et al., 2015a,b].

### 2.3 Benchmarking jako trening: ekstrapolacja wydajności

**(G3.1) Regresja wydajności.**  
Być może najklasyczniejszą nadzieją związaną z benchmarkingiem jest możliwość wykorzystania wygenerowanych danych do **ekstrapolacji wydajności algorytmu na inne, dotąd niebadane instancje problemu**. Taka ekstrapolacja jest bardzo istotna przy wyborze algorytmu i jego konfiguracji, co omawiamy w kolejnej sekcji. Ekstrapolacja wydajności wymaga dobrego zrozumienia, jak wydajność zależy od cech problemu – co było celem G2.4.

W kontekście uczenia maszynowego ekstrapolację wydajności określa się także mianem **transfer learning** [Pan and Yang, 2010]. Można ją realizować ręcznie lub za pomocą zaawansowanych metod regresyjnych. Niezależnie od podejścia, kluczowym aspektem w tym zadaniu jest odpowiedni **dobór instancji problemu**, na których testowane są algorytmy / konfiguracje. W przypadku ekstrapolacji opartej na uczeniu nadzorowanym równie istotny jest odpowiedni wybór metod ekstrakcji cech problemu, co wpływa na dopasowanie pomiędzy ekstrapolowaną a rzeczywistą wydajnością.

**(G3.2) Automatyczny dobór, projektowanie i konfiguracja algorytmów.**  
Gdy zależność wydajności algorytmów od istotnych cech problemu jest znana i można w rozsądny sposób ekstrapolować wyniki na nowe instancje, dane z benchmarkingu można wykorzystać do **projektowania, wyboru lub konfigurowania algorytmu dla rozważanego zadania optymalizacyjnego**. Celem badania benchmarkowego jest wtedy dostarczenie **danych treningowych**, na podstawie których można wyprowadzić reguły pomagające użytkownikowi w wyborze najlepszego algorytmu dla konkretnego zadania.  

Wytyczne te mogą mieć postać **reguł zrozumiałych dla człowieka**, jak np. w [Bartz-Beielstein, 2006; Liu et al., 2020], lub mogą być wyznaczane implicite przez metody **AutoML** [Hutter et al., 2019, Kerschke and Trautmann, 2019a, Kerschke et al., 2019, Olson and Moore, 2016].

### 2.4 Cele zorientowane na teorię

**(G4.1) Walidacja krzyżowa i uzupełnienie wyników teoretycznych.**  
Wyniki teoretyczne w kontekście optymalizacji są często wyrażane w postaci **asymptotycznych oszacowań czasu działania** [Auger and Doerr, 2011, Doerr and Neumann, 2020, Neumann and Witt, 2010], przez co zazwyczaj trudno jest z nich wywnioskować konkretne wartości wydajności, np. dla określonego wymiaru, określonych wartości celu itd. Aby przeanalizować zachowanie algorytmu w małych wymiarach i/lub rozszerzyć zakres, w którym oszacowania teoretyczne są wiarygodne, badanie benchmarkowe może posłużyć jako **uzupełnienie istniejących wyników teoretycznych**.

**(G4.2) Źródło inspiracji dla badań teoretycznych.**  
Co istotne, wyniki empiryczne uzyskane z badań benchmarkowych stanowią **ważne źródło inspiracji** dla prac teoretycznych. W szczególności, gdy wydajność empiryczna nie odpowiada intuicji lub gdy obserwujemy efekty, które nie są dobrze rozumiane od strony matematycznej, badania benchmarkowe mogą pomóc te efekty wskazać i uczynić je dostępnymi dla analiz teoretycznych (por. [Doerr et al., 2019]).

**(G4.3) Benchmarking jako pomost między teorią a praktyką.**  
Dwa poprzednie cele (G4.1 i G4.2), wraz z G1.1 i G1.2, podkreślają rolę benchmarkingu jako **ważnego pośrednika** między nurtem empirycznym a nurtem matematycznie zorientowanym w dziedzinie heurystyk optymalizacyjnych [Müller-Hannemann and Schirra, 2010]. W tym sensie benchmarking odgrywa podobną rolę dla heurystyk optymalizacyjnych, jak **Algorithm Engineering** [Kliemann and Sanders, 2016] dla klasycznych algorytmów.

### 2.5 Benchmarking w rozwoju algorytmów

**(G5.1) Walidacja kodu źródłowego.**  
Kolejnym ważnym aspektem benchmarkingu jest to, że może on służyć do **weryfikacji poprawności implementacji**. W tym celu algorytmy mogą być oceniane na instancjach problemów o znanych własnościach. Jeśli algorytm konsekwentnie nie zachowuje się zgodnie z oczekiwaniami, może to być sygnał potrzeby przeglądu kodu źródłowego.

**(G5.2) Rozwój algorytmów.**  
Oprócz zrozumienia wydajności, benchmarking służy również **identyfikacji słabych punktów** z myślą o opracowywaniu lepiej działających algorytmów. Obejmuje to m.in. pierwsze empiryczne porównania nowych pomysłów, by ocenić, czy warto je dalej badać. Może to prowadzić do swoistej „pętli” analiz empiryczno-teoretycznych. Dobrym przykładem jest **kontrola parametrów w czasie działania** (parameter control): zaobserwowano stosunkowo wcześnie, że dynamiczny dobór parametrów może być korzystniejszy niż ich stałe wartości [Karafotias et al., 2015]. To z kolei pobudziło dalsze badania zarówno empiryczne, jak i teoretyczne.

### 2.6 Otwarte kwestie i wyzwania

Wiele z wymienionych celów wymaga **szczegółowych zapisów „śladów” działania algorytmów**, co rodzi problem przechowywania, udostępniania i ponownego wykorzystywania danych z badań benchmarkowych. Kilka środowisk benchmarkowych oferuje repozytoria danych, pozwalające użytkownikom na ponowne wykorzystanie wyników wcześniejszych eksperymentów. Jednak **kompatybilność formatów danych** pomiędzy różnymi platformami jest dość słaba, a wspólnie uzgodniony standard byłby bardzo pożądany – zarówno dla lepszej porównywalności, jak i dla bardziej „ekologicznej” (oszczędzającej zasoby) kultury benchmarkingu. Dopóki takie standardy nie istnieją, można korzystać z narzędzi, które elastycznie interpretują różne formaty danych. Przykładowo, moduł oceny wydajności **IOHanalyzer** w środowisku benchmarkowym IOHprofiler [Doerr et al., 2018] potrafi obsługiwać różne formaty, w tym formaty dwóch najpowszechniej przyjętych środowisk benchmarkowych w EC – Nevergrad [Rapin and Teytaud, 2018] i COCO [Hansen et al., 2016b].

Wracając do „oszczędnej” kultury benchmarkingu, powtarzamy stwierdzenie z wprowadzenia: dwa najważniejsze kroki badania benchmarkowego to:

1. **sformułowanie jasnego pytania badawczego**, na które badanie ma odpowiedzieć,  
2. **zaprojektowanie planu eksperymentu**, który najlepiej odpowie na to pytanie poprzez odpowiednio zdefiniowany zestaw eksperymentów.

Zaskakuje, jak wiele artykułów naukowych nie wyjaśnia jasno, jakie jest główne pytanie badawcze i w jaki sposób przedstawione dane benchmarkowe podpierają główne tezy pracy.

Na koniec zauważmy, że same **cele** ulegają pewnym „trendom”, które nie muszą być stabilne w czasie. Powyższy zestaw celów należy zatem traktować jako „migawkę” tego, co obserwujemy obecnie – niektóre z nich mogą w przyszłości zyskać lub stracić na znaczeniu.

## 3. Instancje problemów

Krytycznym elementem benchmarkingu algorytmów jest wybór **instancji problemu**, ponieważ może on w dużym stopniu wpływać na wyniki badania. Zakładając, że (ostatecznie) zależy nam na rozwiązywaniu problemów rzeczywistych, idealnie zestaw problemów powinien być **reprezentatywny** dla analizowanego scenariusza rzeczywistego – w przeciwnym razie nie da się wyciągać ogólnych wniosków z wyników benchmarkingu. Dodatkowo ważne jest, aby zestawy problemów były **regularnie aktualizowane**, co ma zapobiec nadmiernemu dostrajaniu algorytmów do konkretnego, stałego zestawu testowego.

W tej sekcji omawiamy różne aspekty związane z zestawami problemów wykorzystywanymi w benchmarkingu. Zajmujemy się czterema pytaniami:

1. Jakie są pożądane właściwości dobrego zestawu problemów?  
2. Jak oceniać jakość zestawu problemów?  
3. Jakie zestawy benchmarkowe są publicznie dostępne?  
4. Jakie są otwarte problemy badawcze związane z zestawami problemów do benchmarkingu?

---

### 3.1. Pożądane cechy zestawu problemów

W tej części opisujemy ogólne właściwości, które wpływają na **użyteczność** zestawów problemów w benchmarkingu; stanowiska w tej sprawie można znaleźć m.in. w [Whitley i in., 1996] oraz [Shir i in., 2018].

**(B1.1) Zróżnicowanie.**  
Dobry zestaw benchmarkowy powinien zawierać problemy o **różnym stopniu trudności** [Olson i in., 2017]. To, co jest trudne dla jednego algorytmu, może być łatwe dla innego, dlatego pożądane jest, aby zestaw obejmował **szeroką gamę problemów o różnych charakterystykach**. Dzięki temu dobrze dobrany zestaw problemów może uwidaczniać **mocne i słabe strony** różnych algorytmów.

Problemy konkursowe są często rozróżniane na podstawie kilku prostych cech, takich jak **wielomodalność** (liczba lokalnych maksimów/minimów) czy **separowalność**, ale istnieje wiele innych właściwości, które mogą wpływać na trudność przeszukiwania przestrzeni rozwiązań [Kerschke i Trautmann, 2019b; Malan i Engelbrecht, 2013; Muñoz Acosta i in., 2015b]. Instancje w zestawie problemów powinny **łącznie** obejmować szeroki zakres takich charakterystyk.

**(B1.2) Reprezentatywność.**  
Po zakończeniu badania benchmarkowego zazwyczaj formułuje się **stwierdzenia o wydajności algorytmów**. Im bardziej zestaw benchmarkowy jest **reprezentatywny** dla klasy problemów, którą badamy, tym **silniejsze** są takie twierdzenia. Instancje wchodzące w skład zestawu powinny więc **zawierać trudności typowe dla rzeczywistych instancji** danej klasy problemów.

**(B1.3) Skalowalność i możliwość strojenia.**  
Idealnie zestaw/zestawy benchmarkowe lub całe „ramy” (framework) powinny umożliwiać **strojenie (konfigurowanie) charakterystyk problemów**. Przykładowo, dobrze jest móc ustawiać:

- wymiar problemu (liczbę zmiennych),  
- poziom zależności między zmiennymi,  
- liczbę celów (w problemach wielokryterialnych),  
- i inne cechy strukturalne.

**(B1.4) Znane rozwiązania / najlepsze wyniki.**  
Jeżeli dla danego problemu benchmarkowego znane są **optymalne rozwiązania**, znacznie ułatwia to **dokładne** mierzenie wydajności algorytmów – możemy wtedy porównać uzyskane wyniki z rzeczywistym optimum. Zdarza się jednak, że nawet dla stosunkowo prostych problemów optymalne rozwiązania nie są znane, nawet w niskich wymiarach (np. problem **Low Auto-correlation Binary Sequence (LABS)** [Packebusch i Mertens, 2016]). W takich przypadkach pożądane jest, aby dla konkretnych instancji była przynajmniej znana i opublikowana **najlepsza dotąd uzyskana wartość funkcji celu**.

---

### 3.2. Ocena jakości zestawu problemów

Łatwo jest stwierdzić, czy zestaw problemów zawiera informację o optymalnym rozwiązaniu lub czy da się go „stroić” (np. zmieniać wymiar). Nie jest natomiast wcale oczywiste, jak sprawdzić, czy zestaw problemów jest **wystarczająco zróżnicowany** oraz **reprezentatywny**. W tej części krótko omawiamy istniejące podejścia do oceny jakości zestawów problemów.

**(B2.1) Przestrzeń cech (feature space).**  
Jednym ze sposobów oceny zróżnicowania zestawu instancji jest analiza tego, **jak dobrze instancje pokrywają zakres różnych cech problemu**. Jeżeli cechy te da się w jakiś sposób **zmierzyć**, możemy mówić o tym, że instancje zajmują szeroki zakres wartości cech (ang. feature values).

Garden i Engelbrecht [2014] wykorzystują **samoorganizującą się mapę cech (self-organizing feature map)** do klasteryzacji i analizy zestawów problemów BBOB (Black-Box Optimization Benchmarking) oraz CEC, bazując na cechach krajobrazu funkcji celu, takich jak:

- „chropowatość” (ruggedness),  
- obecność wielu lejków (funnels) itd.

Podobnie Škvorc i in. [2020] używają cech z **Exploratory Landscape Analysis (ELA)** [Mersmann i in., 2011] w połączeniu z klasteryzacją oraz wizualizacją typu **t-SNE (t-distributed stochastic neighbor embedding)** do analizy rozkładu instancji problemu w przestrzeni cech.

**(B2.2) Przestrzeń wydajności (performance space).**  
Proste statystyki, takie jak średnia czy najlepszy wynik z wielu uruchomień, silnie **agregują informację** i nie zawsze pozwalają dobrze odróżnić dwa (lub więcej) algorytmy. Dwa algorytmy mogą być bardzo podobne (i z tego powodu mieć zbliżone wyniki), ale mogą też być **strukturalnie zupełnie różne**, a mimo to – po agregacji – otrzymujemy bardzo podobne statystyki.

Z obszaru **portfolio algorytmów** można zapożyczyć koncepcje oparte na rankingach, takie jak:

- **marginalny wkład** pojedynczego algorytmu do całego portfolio,  
- **wartości Shapleya**, które uwzględniają wszystkie możliwe konfiguracje portfolio [Fréchette i in., 2016].

Do celów benchmarkingu – i lepszego zrozumienia wpływu decyzji projektowych na wydajność – może być jednak pożądane **skupienie się na takich instancjach**, które **dobrze rozróżniają algorytmy w przestrzeni wydajności** (czyli nie „zaciemniają” różnic).

W tym miejscu pojawia się pojęcie **celowego konstruowania instancji**. Jedną z pierwszych prac, w której „ewoluowano” małe instancje problemu komiwojażera (TSP), które są trudne lub łatwe dla konkretnego algorytmu, jest praca Mersmanna i in. [2013]. Później podejście to rozszerzono na problemy **ciągłe** oraz problemy z **ograniczeniami**. Niedawno uogólniono je do **jawnego rozróżniania par algorytmów** na większych instancjach TSP [Bossek i in., 2019], co wymagało bardziej „agresywnych” operatorów mutacji.

**(B2.3) Przestrzeń instancji (instance space).**  
Smith-Miles i współautorzy [Smith-Miles i Tan, 2012] wprowadzili metodologię zwaną **analizą przestrzeni instancji (instance space analysis)**, która służy do wizualizacji instancji problemu na podstawie cech skorelowanych z trudnością problemu dla konkretnych algorytmów. To podejście można traktować jako **połączenie cech problemu i wydajności algorytmów w jednej przestrzeni**.

W tej przestrzeni:

- regiony dobrej wydajności (tzw. „odciski stóp” – footprints) wskazują, jakie typy problemów dany algorytm jest w stanie **stosunkowo łatwo** rozwiązać,  
- wizualizacja przestrzeni instancji może pokazywać **rozrzut** instancji danego zestawu w przestrzeni cech, a co za tym idzie – pozwala ocenić, czy zestaw benchmarkowy rzeczywiście obejmuje **zróżnicowany wachlarz instancji** dla analizowanych algorytmów.

Przykłady zastosowania tej metodologii obejmują analizę TSP [Smith-Miles i Tan, 2012] oraz ciągłych problemów optymalizacji typu „czarna skrzynka” [Muñoz i Smith-Miles, 2017]. Ciekawym rozszerzeniem jest **ewoluowanie instancji**, które wypełniają „luki” w przestrzeni instancji pozostawione przez dotychczasowe problemy [Smith-Miles i Bowly, 2015], albo bezpośrednie ewoluowanie **zestawów zróżnicowanych instancji** [Neumann i in., 2019].

---

### 3.3. Dostępne zestawy benchmarkowe

Na przestrzeni lat konkursy i specjalne sesje na międzynarodowych konferencjach dostarczyły ogromnej ilości **zasobów do benchmarkingu algorytmów optymalizacyjnych**. Część badań nad metaheurystykami również udostępniła kod i instancje. W tej sekcji w skrócie opisujemy niektóre z tych zasobów, głównie:

- w **porządku alfabetycznym** według ich kluczowych cech,  
- koncentrując się na zestawach, które są **fundamentalnie różne** od siebie oraz mają **dostępną dokumentację i kod** online.

Ze względu na ten nacisk na różnice fundamentalne zazwyczaj **nie wchodzimy** w szczegóły dotyczące **konfigurowalnych instancji** i **parametryzowanych generatorów instancji**.

Warto od razu zaznaczyć, że wiele z wymienionych poniżej problemów benchmarkowych jest dostępnych w platformie **Nevergrad** [Rapin i Teytaud, 2018].

---

**(B3.1) Sztuczne problemy dyskretnej optymalizacji.**  
Subiektywnie rzecz biorąc, jest to obszar z jednymi z **najbogatszych** zestawów benchmarkowych. Wiele z nich jest inspirowanych problemami występującymi w rzeczywistości, ale z czasem stały się **fundamentalnymi problemami informatyki**. Do ważniejszych podobszarów optymalizacji dyskretnej należą:

- optymalizacja kombinatoryczna,  
- programowanie całkowitoliczbowe,  
- programowanie z ograniczeniami (constraint programming).

Dla wielu z nich istnieją duże, historycznie rozwijane zestawy benchmarków. Przykłady:

- konkursy z zakresu **spełnialności formuł Boole’a (SAT)** i **max-SAT** (maksymalnej spełnialności)⁵,  
- biblioteka problemów komiwojażera **TSPLIB**⁶,  
- biblioteka problemów **mixed integer programming (MIPLIB)**⁷.

W przeciwieństwie do tych zestawów opartych bezpośrednio na instancjach rzeczywistych, istnieją też bardziej **abstrakcyjne modele**, które definiują **interakcje między zmiennymi** na najniższym poziomie (tj. niezależnie od konkretnego problemu), a następnie konstruują instancje na bazie pewnych fundamentalnych charakterystyk. W przypadku binarnej reprezentacji przykłady obejmują:

- **krajobrazy NK** [Kauffman, 1993] – z konfigurowalną „chropowatością” (ruggedness),  
- **W-Model** [Weise i Wu, 2018] – z konfigurowalnymi cechami takimi jak długość, neutralność, epistaza, wielokryterialność, wartości funkcji celu, chropowatość,  
- zestaw Pseudo-Boolean Optimization (PBO) – 23 binarne funkcje benchmarkowe Doerra i in. [2020], które obejmują szerokie spektrum cech krajobrazu i rozszerzają W-model na różne sposoby (m.in. poprzez nakładanie transformacji na inne problemy bazowe).

**(B3.2) Sztuczne problemy z parametrami rzeczywistymi (real-parameter).**  
Zestawy benchmarkowe tego typu były definiowane na potrzeby specjalnych sesji, warsztatów i konkursów zarówno na konferencji **GECCO (ACM Genetic and Evolutionary Computation Conference)**, jak i **IEEE CEC**. Dokumentacja i kod są publicznie dostępne – m.in.:

- dla GECCO: **BBOB**⁸,  
- dla CEC: odpowiednie zestawy funkcji⁹.

**(B3.3) Sztuczne problemy z mieszaną reprezentacją.**  
Zestawy benchmarkowe łączące zmienne **dyskretne i ciągłe** obejmują m.in.:

- mieszane (mixed-integer) krajobrazy NK [Li i in., 2006],  
- problemy wielokryterialne z kodowaniem binarnym i rzeczywistym [McClymont i Keedwell, 2011],  
- problemy mieszane oparte na funkcjach CEC [Liao i in., 2014],  
- zestaw problemów mieszanych oparty na funkcjach BBOB (bbob-mixint) z bi-kryterialną wersją (bbob-biobj-mixint) [Tušar i in., 2019].

**(B3.4) Problemy optymalizacji czarnej skrzynki (black-box).**  
We wszystkich wymienionych dotąd benchmarkach formuła problemu i instancje są zazwyczaj **jawnie dostępne**, co nieuchronnie prowadzi do **specjalizacji algorytmów** na te właśnie problemy. Konkurs **Black-Box Optimization Competition**¹⁰ próbował obejść ten problem, proponując **jedno- i wielokryterialne problemy ciągłej optymalizacji typu „czarna skrzynka”**, w których dokładna postać funkcji nie jest znana uczestnikom. W 2019 roku udostępniono jednak kod oceniający te instancje.

**(B3.5) Problemy z ograniczeniami (constrained) z parametrami rzeczywistymi.**  
Większość benchmarków z parametrami rzeczywistymi jest **nieograniczona** (poza prostymi ograniczeniami na zakres zmiennych). W społeczności EC odczuwalny jest więc **niedobór zestawów z ograniczeniami**. Do wyjątków należą:

- zestaw 18 sztucznych, skalowalnych problemów na potrzeby **CEC 2010 Competition on Constrained Real-Parameter Optimization**¹¹,  
- sześć wielokryterialnych, rzeczywistych problemów z ograniczeniami zaproponowanych przez Tanabe i Ishibuchi [2020],  
- zestaw 57 rzeczywistych problemów z ograniczeniami¹², przygotowany na konkursy GECCO i CEC 2020.

**(B3.6) Dynamiczne problemy jednokryterialne.**  
Benchmarki do analizy algorytmów ewolucyjnych w **dynamicznych środowiskach** powinny idealnie umożliwiać **konfigurowanie charakteru zmian** – np. ich **częstotliwości** i **intensywności**. Przydatnym źródłem na temat benchmarków do środowisk dynamicznych jest obszerna praca przeglądowa Nguyen i in. [2012].

**(B3.7) Problemy drogie obliczeniowo (expensive optimization).**  
W **GECCO 2020 Industrial Challenge** zaproponowano zestaw dyskretnych problemów projektowania elektrycznego odpylacza elektrostatycznego, w których ocena rozwiązania wymaga **kosztownych symulacji**¹³. Alternatywnym podejściem do benchmarkingu optymalizacji drogich funkcji (wykorzystywanym m.in. w konkursach CEC) jest **ograniczenie liczby dopuszczalnych wywołań funkcji celu** dla istniejących już zestawów problemów.

**(B3.8) Optymalizacja wielomodalna (niching).**  
Zestawy benchmarkowe dla metod niszowania (niching) obejmują:

- konkursy GECCO i CEC dotyczące metod niszowania dla **wielomodalnych problemów optymalizacji**¹⁴,  
- problemy z konkursu **single-objective multi-niche**¹⁵.

**(B3.9) Problemy z szumem (noisy).**  
Pierwotna wersja platformy **Nevergrad** [Rapin i Teytaud, 2018]¹⁶ była silnie nastawiona na problemy z **szumem**. Obecnie platforma obejmuje jednak także problemy:

- dyskretne, ciągłe i mieszane,  
- z ograniczeniami i bez,  
- z szumem i bez szumu,  
- jawnie modelowane i w pełni typu „czarna skrzynka”.

Zestawy problemów optymalizacji danych EEG w ramach **CEC Optimization of Big Data 2015**¹⁷ zawierają również wersje z szumem.

**(B3.10) Problemy z współzależnymi komponentami.**  
Wiele badań zajmuje się **pojedynczymi** problemami kombinatorycznymi, rozpatrywanymi w oderwaniu od reszty systemu. W rzeczywistości wiele problemów ma jednak strukturę **wieloskładnikową**, gdzie kilka podproblemów jest ze sobą powiązanych [Bonyadi i in., 2019].

Problem **Travelling Thief Problem (TTP)** [Bonyadi i in., 2013] został opracowany jako akademicka platforma do systematycznego badania efektów takich współzależności. Zawiera on **9720 instancji** [Polyakovskiy i in., 2014]¹⁸, zróżnicowanych w czterech wymiarach. Od czasu jego wprowadzenia zaproponowano wiele rozszerzeń – jedno- i wielokryterialnych, statycznych i dynamicznych [Sachdeva i in., 2020].

**(B3.11) Rzeczywiste problemy dyskretne.**  
Konkurs GECCO dotyczący **optymalnego rozmieszczenia kamer (Optimal Camera Placement, OCP)** oraz **problemu pokrycia zbioru unicost (USCP)** obejmuje zestaw rzeczywistych instancji dyskretnych¹⁹. Inne przykłady rzeczywistych problemów to:

- **problem Mazdy**²⁰ – skalowalny, wielokryterialny, dyskretny problem z ograniczeniami, oparty na rzeczywistym zadaniu projektowania struktury samochodu,  
- zestaw problemów projektowania kombinatorycznych układów logicznych [de Souza i in., 2020], obejmujący różne charakterystyki wpływające na trudność zadania.

**(B3.12) Rzeczywiste problemy numeryczne (real-world numerical optimization).**  
Zdefiniowano zestaw **57 jednokryterialnych, rzeczywistych problemów z ograniczeniami** na potrzeby konkursów na kilku konferencjach²¹. Inne benchmarki obejmują m.in.:

- problemy optymalizacji danych EEG [Goh i in., 2015],  
- zestaw benchmarków dla algorytmów grupowania typu „sum-of-squares clustering” [Gallagher, 2016],  
- konkursy **Smart Grid Problems** dla rzeczywistych problemów z obszaru energetyki²²,  
- **Game Benchmark for EAs** [Volz i in., 2019] – zestaw funkcji testowych inspirowanych problemami związanymi z grami²³.

---

### 3.4. Otwarte problemy

Widzimy szereg **możliwości badawczych** związanych z zestawami problemów do benchmarkingu.

Po pierwsze, liczba dostępnych benchmarków rzeczywistych wydaje się **o rzędy wielkości mniejsza** niż rzeczywista liczba problemów optymalizacyjnych, które są rozwiązywane na co dzień – szczególnie w optymalizacji ciągłej. Tam, gdzie istnieją „porządne” rzeczywiste problemy (np. zbiory danych w problemach kombinatorycznych lub konkursowe problemy CEC), często są to sytuacje **„jednorazowej optymalizacji”** (single-shot), w których można wykonać tylko jedno uruchomienie algorytmu. Utrudnia to uzyskanie wyników **uogólnialnych**. Mimo to niedawno podjęto próbę zebrania i scharakteryzowania takich problemów w postaci ankiety²⁴ przygotowanej przez grupę roboczą **MACODA (Many Criteria Optimization and Decision Analysis)**.

Po drugie, **dostępność zróżnicowanych instancji oraz kodu źródłowego** (funkcji celu, generatorów problemów, ale też samych algorytmów) nadal pozostawia wiele do życzenia. Idealne byłyby duże kolekcje instancji wraz z ich cechami, algorytmami i wynikami – biblioteka **ASlib** (Algorithm Selection Library)²⁵ [Bischl i in., 2016] zawiera takie dane, choć w innym celu. Jako efekt uboczny takie (najlepiej rosnące) repozytoria mogą:

- przeciwdziałać „wynajdywaniu koła na nowo”,  
- zapobiegać sytuacji, w której porównujemy się do rzekomo „dobrze ugruntowanych” algorytmów tylko dlatego, że są często cytowane – choć może są często cytowane właśnie dlatego, że **łatwo je pokonać**.

Po trzecie – to bardziej **szansa edukacyjna** – jako społeczność powinniśmy uważniej formułować nasze **twierdzenia wynikające z benchmarkingu**. Nie wystarczy mówić: „mój algorytm jest lepszy od twojego”; warto również badać:

- czego nowego dowiadujemy się o **samych problemach**,  
- czego dowiadujemy się o **algorytmach** (por. dyskusja w [Agrawal i in., 2020] w kontekście data miningu),

tak aby wnioski mogły **informować tworzenie nowych instancji**. Innymi słowy, należy jasno określić, **jakie wnioski wolno nam próbować wyciągać**, skoro porównanie wydajności zawsze dotyczy **konkretnego zestawu benchmarkowego**, a nie całej, abstrakcyjnej klasy problemów.

Po czwarte, zaletą zestawów testowych jest to, że zapewniają one **obiektywną** podstawę do porównywania systemów. Mają jednak także swoje wady. Whitley i in. [2002] zauważają, że systemy mogą zostać **przeuczone (overfitted)** do dobrze wypadających wyników na konkretnych benchmarkach, a dobra wydajność na benchmarkach nie musi przekładać się na **dobre wyniki w zadaniach rzeczywistych**. Fischbach i Bartz-Beielstein [2020] wymieniają i omawiają kilka wad takich zestawów testowych, m.in.:

1. instancje problemów są **sztuczne** i nie zawsze mają bezpośredni związek z rzeczywistymi scenariuszami,  
2. ponieważ liczba testowych instancji jest **ograniczona**, algorytmy mogą być silnie dostrojone do tego konkretnego, wąskiego zestawu funkcji,  
3. narzędzia statystyczne do porównywania wielu algorytmów na wielu instancjach są **złożone** i trudne w interpretacji.

Na koniec zauważmy, że dla większości benchmarków (i wielu problemów rzeczywistych) wartość funkcji celu jest **deterministyczna**, ale istnieje też wiele problemów, w których ocena dopasowania odbywa się **w warunkach szumu**. Odpowiednie obchodzenie się z szumem ma kluczowe znaczenie, aby algorytmy mogły **stabilnie eksplorować i eksploatować przestrzeń rozwiązań**. Branke i in. [2001] omawiają strategie radzenia sobie z szumem, a Jin i Branke [2005] przedstawiają dobry przegląd. W praktyce, w eksperymentach komputerowych szum często jest generowany z **prostych rozkładów**, podczas gdy w rzeczywistych zastosowaniach szum może być **nienormalny, zmienny w czasie**, a nawet **zależny od stanu systemu**.

Aby rzetelnie weryfikować wyniki eksperymentów w tak szumnych środowiskach, potrzebne są mechanizmy **wykraczające daleko poza proste podejście „zrób n powtórzeń”**; Bokhari i in. [2020] porównują pięć takich podejść.

> **Linki z oryginału (do ewentualnego użycia jako przypisy):**  
> ⁴ https://matilda.unimelb.edu.au/matilda/  
> ⁵ http://www.satcompetition.org/ , https://maxsat-evaluations.github.io/  
> ⁶ http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/ , http://www.math.uwaterloo.ca/tsp/index.html  
> ⁷ https://miplib.zib.de/  
> ⁸ https://coco.gforge.inria.fr  
> ⁹ https://github.com/P-N-Suganthan/2020-Bound-Constrained-Opt-Benchmark  
> ¹⁰ https://www.ini.rub.de/PEOPLE/glasmtbl/projects/bbcomp/  
> ¹¹ https://github.com/P-N-Suganthan/CEC2010-Constrained  
> ¹² https://github.com/P-N-Suganthan/2020-RW-Constrained-Optimisation  
> ¹³ https://www.th-koeln.de/informatik-und-ingenieurwissenschaften/gecco-challenge-2020_72989.php  
> ¹⁴ http://epitropakis.co.uk/gecco2020/  
> ¹⁵ https://github.com/P-N-Suganthan/CEC2015-Niching  
> ¹⁶ https://github.com/facebookresearch/nevergrad  
> ¹⁷ http://www.husseinabbass.net/BigOpt.html  
> ¹⁸ https://cs.adelaide.edu.au/~optlog/research/combinatorial.php  
> ¹⁹ http://www.mage.fst.uha.fr/brevilliers/gecco-2020-ocp-uscp-competition/  
> ²⁰ http://ladse.eng.isas.jaxa.jp/benchmark/  
> ²¹ https://github.com/P-N-Suganthan/2020-RW-Constrained-Optimisation  
> ²² http://www.gecad.isep.ipp.pt/ERM-competitions/home/  
> ²³ http://www.gm.fh-koeln.de/~naujoks/gbea/gamesbench.html

## 4. Algorytmy

Aby zrozumieć mocne i słabe strony różnych idei algorytmicznych, ważny jest wybór **odpowiedniego zestawu algorytmów**, które będą testowane w badaniu benchmarkowym. Choć portfolio algorytmów jest z pewnością jednym z najbardziej subiektywnych wyborów w takim badaniu, istnieje jednak kilka zasad projektowych, których warto się trzymać. W tej sekcji podsumowujemy najistotniejsze z tych wytycznych.

### 4.1 Rodziny algorytmów

Aby ocenić jakość różnych pomysłów algorytmicznych, użyteczne jest porównywanie **instancji algorytmów z różnych rodzin**. Na przykład można włączyć do badania solvery z następujących grup:

- **algorytmy „jednostrzałowe” (one-shot)** optymalizacji,  
  np. czysto losowe przeszukiwanie, projektowanie typu *Latin Hypercube Design (LHD)* [McKay et al., 2000] czy konstrukcje punktów quasi-losowych,

- **zachłanne algorytmy lokalnego przeszukiwania**,  
  np. zrandomizowane lokalne przeszukiwanie (*Randomized Local Search*), algorytm Broydena–Fletchera–Goldfarba–Shanno (*BFGS*) [Shanno, 1970], metody sprzężonych gradientów [Fletcher, 1976] czy metoda Neldera–Meada [Nelder i Mead, 1965],

- **niezachłanne algorytmy lokalnego przeszukiwania**,  
  np. *Simulated Annealing (SANN)* [Kirkpatrick et al., 1983], *Threshold Accepting* [Dueck i Scheuer, 1990] czy *Tabu Search* [Glover, 1989],

- **algorytmy globalnego przeszukiwania z pojedynczym punktem**  
  (single-point global search),  
  np. strategie ewolucyjne typu (1+λ) [Eiben i Smith, 2015] czy *Variable Neighborhood Search* [Mladenović i Hansen, 1997],

- **algorytmy populacyjne**,  
  np. *Particle Swarm Optimization (PSO)* [Kennedy i Eberhart, 1995; Shi i Eberhart, 1998], algorytmy mrówkowe [Dorigo et al., 2006; Socha i Dorigo, 2008], większość algorytmów ewolucyjnych [Bäck et al., 1997; Eiben i Smith, 2015] oraz algorytmy estymacji rozkładu (*Estimation of Distribution Algorithms, EDA*) [Larrañaga i Lozano, 2002; Mühlenbein i Paaß, 1996], takie jak CMA-ES [Hansen et al., 2003],

- **algorytmy z modelami zastępczymi (surrogate-based)**,  
  np. *Efficient Global Optimization (EGO)* [Jones et al., 1998] oraz inne algorytmy optymalizacji bayesowskiej.

Należy zauważyć, że powyższa „klasyfikacja” w żadnym razie nie jest ani wyczerpująca, ani ściśle rozłączna. Schematy klasyfikacji heurystyk optymalizacyjnych mają zwykle charakter **nieostry**, ponieważ hybrydyzacja pomiędzy różnymi ideami czy komponentami algorytmicznymi jest czymś powszechnym. Przypisanie algorytmu do konkretnej kategorii jest więc często subiektywne; przykłady dyskusji na ten temat można znaleźć m.in. w [Birattari et al., 2003; Boussaïd et al., 2013; Stork et al., 2020].

### 4.2 Wyzwania i wskazówki dla praktyka

Poniższa lista podsumowuje kwestie, które powinny kierować wyborem portfolio algorytmów. Lista ta **nie ma** na celu rekomendowania konkretnych algorytmów do rozwiązywania danej klasy problemów, lecz raczej **pokazanie, jakie aspekty warto rozważyć** przed rozpoczęciem badania benchmarkowego.

#### (C4.1) Cechy problemu

Prawdopodobnie najbardziej decydującym kryterium wyboru portfolio algorytmów jest **typ problemów**, które mają być benchmarkowane. Tam, gdzie dostępne są informacje takie jak **gradienty**, do badania należy włączyć metody bazujące na gradientach. Gdy przestrzeń decyzyjna ma charakter **mieszany całkowitoliczbowo–ciągły**, potrzebne są inne algorytmy niż w przypadku problemów czysto numerycznych czy czysto kombinatorycznych. Inne cechy, takie jak stopień interakcji między zmiennymi, (domniemany) kształt krajobrazu wartości funkcji celu itp., również powinny wpływać na dobór algorytmów.

Zalecamy wykorzystanie **wszystkich dostępnych informacji** o problemie, np. cech krajobrazu [Kerschke et al., 2019] oraz wcześniejszych wyników wydajności algorytmów dla danej klasy problemów [Kerschke et al., 2019]. Nawet jeśli celem badania benchmarkowego **nie jest** wyłonienie zwycięzcy, to wgląd w wyniki wcześniejszych konkursów czy warsztatów może dostarczyć cennych wskazówek, które algorytmy warto włączyć do porównania. Repozytoria danych z benchmarków, takie jak te zebrane w [Wang et al., 2020], zostały stworzone właśnie po to, by wspierać użytkowników w takich zadaniach.

#### (C4.2) Budżet i zbieżność

Moc obliczeniowa oraz dostępność zasobów na analizę wyników benchmarku mają silny wpływ na **liczbę algorytmów**, które da się porównać, podczas gdy **budżet obliczeniowy przypadający na każdy algorytm** jest zwykle określany przez pytanie badawcze lub rozważaną aplikację. Budżet ten może wpływać na dobór algorytmów.  

Przykładowo:

- algorytmy wspomagane modelami zastępczymi (surrogate-assisted) często są naturalnym wyborem przy **małych budżetach**,  
- strategie ewolucyjne okazują się konkurencyjne przy **średnich i dużych budżetach**.

#### (C4.3) Stan wiedzy (state of the art)

Wyniki badania benchmarkowego mogą być łatwo **zaburzone**, jeżeli uwzględnimy w nim wyłącznie **przestarzałe algorytmy**. Zdecydowanie zalecamy zapoznanie się ze **stanem wiedzy (state of the art)** w zakresie algorytmów dla rozważanego typu problemu, gdzie „state of the art” może odnosić się zarówno do wydajności na danej klasie problemów, jak i do danej rodziny algorytmów.

Wstępne eksperymenty mogą posłużyć do odpowiedniej preselekcji (tj. wykluczenia) algorytmów. Praktyk powinien mieć pewność, że porównuje swój algorytm z **najlepszymi dostępnymi podejściami**. W konsekwencji należy zawsze porównywać się z **najświeższymi wersjami i implementacjami** algorytmów. Dotyczy to również używanej **platformy programistycznej** i jej wersji.

Jeśli implementacje algorytmów dostępne są na platformach programistycznych czy systemach operacyjnych, z którymi praktyk nie jest zaznajomiony, warto skorzystać z dostępnych współcześnie **technologii ułatwiających przenoszenie środowisk**, np. konteneryzacji (Docker itp.) lub wirtualizacji.  

Szczegółowe kwestie związane z **projektem eksperymentu** – takie jak liczba porównywanych algorytmów, liczba powtórzeń, liczba instancji problemu, liczba rozważanych ustawień parametrów czy zastosowanie projektów sekwencyjnych w sytuacji, gdy stan wiedzy nie jest jasny – omawiamy w sekcji 7.

#### (C4.4) Obsługa hiperparametrów

Wszystkie opisane rodziny algorytmów wymagają ustawienia **jeden lub kilku parametrów sterujących**. Aby umożliwić **uczciwe porównanie** ich wydajności i ocenić efektywność, kluczowe jest unikanie **słabych konfiguracji parametrów** i właściwe dostrojenie algorytmów rozważanych w badaniu [Beiranvand et al., 2017; Eiben i Smit, 2011].

Nawet dobrze działająca konfiguracja parametrów dla danego scenariusza (np. przy ustalonym budżecie) może sprawdzać się **znacznie gorzej** przy istotnie innym budżecie. Jak wspomniano w sekcji 2 przy celu (G2.2), **odporność algorytmu na zmiany hiperparametrów** może być ważną własnością z punktu widzenia użytkownika; w takim przypadku zagadnienie to powinno być włączone do badania benchmarkowego (a nawet może stanowić jego główny cel).

Ponadto praktyk powinien upewnić się, że implementacja algorytmu **poprawnie korzysta z podanych ustawień parametrów**. Zdarza się, że niektóre implementacje **nie ostrzegają**, gdy ustawienia parametrów wychodzą poza dopuszczalne zakresy.

Dostępnych jest kilka narzędzi do **automatycznej konfiguracji parametrów**, m.in.:

- *iterated racing (irace)* [López-Ibáñez et al., 2016],  
- *Iterated Local Search in Parameter Configuration Space (ParamILS)* [Hutter et al., 2009],  
- *SPOT* [Bartz-Beielstein et al., 2005],  
- *Sequential Model-based Algorithm Configuration (SMAC)* [Hutter et al., 2011],  
- *GGA* [Ansótegui et al., 2015],  
- *hyperband* [Li et al., 2017],

by wymienić tylko kilka.

Ponieważ ręczne strojenie może być **stronnicze**, zwłaszcza dla algorytmów słabo znanych eksperymentatorowi, **automatyczna konfiguracja** jest obecnie **standardem** i jest wysoce zalecana. Wraz z rozwojem badań nad automatyczną konfiguracją algorytmów i optymalizacją hiperparametrów powstało kilka powiązanych **platform benchmarkowych**, takich jak:

- biblioteka konfiguracji algorytmów *Algorithm Configuration Library (ACLib)* [Hutter et al., 2014],  
- biblioteka optymalizacji hiperparametrów *HPOlib* [Eggensperger et al., 2013],

które koncentrują się bezpośrednio na tych zagadnieniach.

#### (C4.5) Inicjalizacja

Dobre badanie benchmarkowe powinno zapewniać, że uzyskane wyniki **nie są dziełem przypadku**. Ważne jest więc, aby uwzględnić możliwość, że wydajność algorytmów jest **błędnie oceniana z powodu (np. losowej) inicjalizacji**. W zależności od instancji problemu, punkt startowy wyznaczony na podstawie ziarna losowości może być dla algorytmu korzystny, jeśli znajduje się w pobliżu (lub dokładnie w miejscu) jednego bądź kilku lokalnych optimum.

W konsekwencji praktyk powinien mieć świadomość, że wydajność algorytmów może być **zabiasowana** przez sposób inicjalizacji, np. przez:

- dobór ziarna losowości,  
- wybór punktów startowych,  
- zastosowaną strategię próbkowania,

w powiązaniu z trudnością wybranej instancji problemu.

Zalecamy, aby **wszystkie porównywane algorytmy korzystały z tych samych punktów startowych**, zwłaszcza gdy celem benchmarku jest:

- bezpośrednie porównanie algorytmów (cele G1.2 i G1.3),  
- analiza zachowania procesu przeszukiwania (cel G1.1).

Rekomendacja ta rozciąga się również na **porównania z danymi historycznymi**.

Przemyślany **plan eksperymentu** (zob. sekcja 7) może odzwierciedlać powyższe rozważania poprzez odpowiedni dobór:

- liczby instancji problemu,  
- liczby powtórzeń,  
- strategii próbkowania (w kontekście parametryzacji algorytmu),  
- oraz ziaren losowych.

W kwestii wyboru i obsługi ziaren losowości oraz innych aspektów reprodukowalności odsyłamy do sekcji 9.

#### (C4.6) Ocena wydajności

Różne algorytmy umożliwiają konfigurację **różnych kryteriów stopu** lub robią to w odmienny sposób. Może to **wpływać na przebieg przeszukiwania** [Beiranvand et al., 2017] i musi być uwzględnione przy interpretacji wyników.  

Przykładowo, implementacja algorytmu może **nie przestrzegać** zadanego limitu liczby wywołań funkcji celu. Jeśli nie zostanie to wykryte przez eksperymentatora, ocena wyników benchmarku może zostać w istotny sposób **zaburzona**.

### 4.3 Wyzwania i otwarte kwestie

Dobór algorytmów do uwzględnienia w badaniu benchmarkowym zależy w dużej mierze od:

- doświadczenia użytkownika,  
- dostępności gotowych lub łatwych do dostosowania implementacji,  
- dostępności danych o problemach i/lub algorytmach itd.

Zidentyfikowanie odpowiednich algorytmów, zbiorów danych, publikacji naukowych często wymaga **znacznego nakładu pracy**. Nawet gdy dane i implementacje są łatwo dostępne, **formaty plików i interfejsy** mogą się znacząco różnić między badaniami, co utrudnia ich efektywne wykorzystanie. Wierzymy zatem, że **wspólne formaty danych**, **wspólne interfejsy benchmarkowe** oraz lepsza **kompatybilność istniejącego oprogramowania** wspierającego benchmarking heurystyk optymalizacyjnych byłyby ogromnie pomocne.

Kolejnym istotnym problemem w obecnym krajobrazie benchmarkowania jest **brak szczegółowości w opisie algorytmów**. W szczególności w przypadku złożonych, np. wspomaganych modelami zastępczymi heurystyk optymalizacyjnych, nie wszystkie parametry i komponenty są explicite opisane w artykule. Gdy kod jest dostępny w trybie otwartego dostępu, użytkownik może odnaleźć te szczegóły w implementacji. Niemniej jednak **dostępność implementacji algorytmów** wciąż stanowi poważne wąskie gardło w naszej społeczności.

## 5. Jak mierzyć wydajność?

Wydajność algorytmów można mierzyć względem kilku różnych celów, z których dwa najbardziej oczywiste to:

- **jakość rozwiązania**,  
- **zużyty budżet** (np. liczba wywołań funkcji celu lub czas obliczeń) – por. Rys. 2.

Przy benchmarkowaniu algorytmów zazwyczaj patrzymy na jedno z dwóch pytań:

- **„Jak szybko algorytmy osiągają zadaną jakość rozwiązania?”** (sekcja 5.1), albo  
- **„Jaką jakość rozwiązania algorytmy osiągają przy danym budżecie?”** (sekcja 5.2).

Te dwa scenariusze odpowiadają odpowiednio **pionowym i poziomym przekrojom** wykresu wydajności, jak omówiono w [Hansen i in., 2012] oraz [Finck i in., 2015] (zob. Rys. 2):

- **Scenariusz stałego budżetu (fixed-budget, przekrój pionowy)**  
  – jego zaletą jest to, że wyniki są dobrze zdefiniowane: każda realna procedura obliczeniowa ma ograniczony budżet.  

- **Scenariusz stałego celu (fixed-target, przekrój poziomy)**  
  – ułatwia formułowanie intuicyjnych wniosków, typu:  
  *„instancja algorytmu **b** jest dziesięć razy szybsza niż instancja **a** w rozwiązaniu tego problemu”*  
  jest zwykle bardziej zrozumiałe niż:  
  *„wartość funkcji celu uzyskana przez algorytm **b** jest o 0,2% lepsza niż dla algorytmu **a**”*.  

Problemem scenariusza stałego celu jest to, że **nie wszystkie uruchomienia** muszą osiągnąć wymagany poziom jakości, więc trzeba z góry określić, **jak traktujemy nieudane przebiegi**.

W zależności od przyjętego budżetu czasowego lub docelowej jakości rozwiązania, **różne algorytmy mogą wypadać lepiej** – albo pod względem jakości, albo czasu działania. Zamiast więc patrzeć tylko na pojedynczy punkt (stały budżet lub stały cel), można analizować **pełne krzywe „anytime”** [Bossek i in., 2020b; Jesus i in., 2020], opisujące zachowanie algorytmu w czasie. W takim ujęciu wydajność to już nie jedna liczba, lecz **cały przebieg** na wykresie jakość–czas.  

Każde z tych trzech podejść (stały budżet, stały cel, krzywe anytime) ma swoje uzasadnienie i inne zastosowania. **To od konkretnej aplikacji zależy, który punkt widzenia jest najwłaściwszy.**

Dodatkowo, w centrum zainteresowania może znaleźć się **odporność (robustness) otrzymanego rozwiązania**, na którą wpływają m.in.:

- stochastyczność algorytmu,  
- szum w problemie optymalizacyjnym,  
- „gładkość” krajobrazu w otoczeniu rozwiązania.  

Jak jednak pokazujemy w sekcji 5.3, **mierzenie odporności jest trudnym zagadnieniem**.

---

### 5.1 Pomiar czasu  

### Rysunek 2. Perspektywy stałego budżetu i stałego celu

Układ odniesienia:

- Oś **pozioma (x): Budżet**  
  (np. liczba wywołań funkcji celu, czas obliczeń)

- Oś **pionowa (y): Wydajność**  
  (np. najlepsza dotąd wartość funkcji celu – im niżej, tym lepiej, jeśli minimalizujemy)

Na wykresie rozważamy dwie podstawowe perspektywy oceny algorytmu:

---

#### 1. Perspektywa stałego budżetu (fixed budget)

- Na wykresie odpowiada jej **pionowa linia** (w oryginale zielona).  
- Wybieramy **konkretny budżet** – np. 10 000 ewaluacji funkcji celu.  
- Dla każdego algorytmu patrzymy, **jaka jakość rozwiązania** została osiągnięta, gdy wykorzystano dokładnie ten budżet.  
- Innymi słowy:  
  > „Przy danym budżecie: który algorytm daje lepszy wynik jakościowy?”

---

#### 2. Perspektywa stałego celu (fixed target)

- Na wykresie odpowiada jej **pozioma linia** (w oryginale pomarańczowa).  
- Wybieramy **konkretny poziom jakości** – np. wartość funkcji celu równą 1e-3 powyżej optimum.  
- Dla każdego algorytmu patrzymy, **jak duży budżet** (ile ewaluacji / czasu) jest potrzebny, by osiągnąć ten poziom.  
- Innymi słowy:  
  > „Dla zadanego celu jakościowego: który algorytm osiąga go szybciej / taniej?”

---

#### 3. Trajektorie wydajności (krzywe anytime)

- Na wykresie narysowane są **trzy przerywane krzywe**, odpowiadające **przykładowym przebiegom wydajności** trzech różnych algorytmów.  
- Każda krzywa opisuje, jak **poprawia się wynik w czasie**:  
  - na początku jakość jest słaba,  
  - w miarę upływu budżetu (wzdłuż osi x) wynik staje się coraz lepszy (spadek wartości na osi y).  

Przecięcia tych krzywych z:

- **pionową linią (stały budżet)** pokazują,  
  jaką jakość ma każdy algorytm przy tym samym budżecie;

- **poziomą linią (stały cel)** pokazują,  
  ile budżetu potrzebuje każdy algorytm, aby osiągnąć tę samą jakość.

---

Ten rysunek ilustruje, że:

- **perspektywa stałego budżetu** odpowiada „przekrojowi pionowemu” krzywych wydajności,  
- **perspektywa stałego celu** odpowiada „przekrojowi poziomemu” tych krzywych,

a pełne krzywe (trajektorie) opisują **zachowanie anytime** algorytmów w czasie.

Czas można mierzyć na różne sposoby – najbardziej intuicyjne są:

- **czas zegarowy (wall-clock time)**,  
- **czas CPU**.

W wielu problemach kombinatorycznych (np. TSP [Kerschke i in., 2018b] czy SAT [Xu i in., 2008]) standardem jest **czas CPU**. Jest on jednak bardzo wrażliwy na czynniki zewnętrzne, takie jak:

- użyty sprzęt,  
- język programowania,  
- aktualne obciążenie procesorów itd.

Przez to wyniki oparte wyłącznie na czasie CPU są **trudniej replikowalne** i **mniej porównywalne**.

Aby złagodzić ten problem, Johnson i McGeoch [2002] zaproponowali **znormalizowany czas**, liczony jako:

> czas naszego algorytmu  
> ÷  
> czas standardowej implementacji standardowego algorytmu  
> (uruchomionej na tej samej lub porównywalnej instancji problemu).

Alternatywną miarą czasu są **wywołania funkcji celu (Function Evaluations, FEs)** – tzn. liczba w pełni ocenionych kandydatów. W optymalizacji próbkowanej, np. klasycznej optymalizacji ciągłej, jest to **najczęściej stosowana, niezależna od maszyny miara wysiłku obliczeniowego** [Hansen i in., 2016a].  

Trzeba jednak pamiętać, że z perspektywy czasu rzeczywistego **jedno wywołanie funkcji celu może mieć różny koszt** dla różnych algorytmów [Weise i in., 2014]. W takich przypadkach pomocne bywa zliczanie **kroków specyficznych dla danej dziedziny**, np.:

- liczby obliczeń odległości w TSP [Weise],  
- liczby flipów bitów w problemie MAX-SAT [Hains i in., 2013].

W społeczności EC **liczba FEs pozostaje jednak główną i najpowszechniej akceptowaną miarą „wysiłku” algorytmu**.

Z praktycznego punktu widzenia, obie miary mają swoje zalety:

- jeśli budżet z góry określamy w **czasie zegarowym**  
  (np. modele mają być wytrenowane „do rana”, albo decyzje giełdowe muszą być podjęte w ciągu sekund),  
  to **czas CPU** jest bardziej adekwatny,

- jeśli natomiast pojedyncze wywołanie funkcji celu jest **drogie**  
  (np. eksperyment fizyczny, kosztowna symulacja numeryczna),  
  to **liczba FEs** jest dobrą aproksymacją czasu rzeczywistego i bardziej **uniwersalną miarą**.

**Najlepszą praktyką** jest raportowanie **obu miar**:  
zarówno liczby FEs, jak i czasu CPU.

W sytuacjach, w których pojedyncze wywołanie funkcji celu jest kosztowne, warto dodatkowo **rozbić czas CPU** na:

- część zużytą przez samą funkcję celu,  
- część zużytą przez „logikę” algorytmu (aktualizacje, selekcja, modele itd.).

W optymalizacji z modelami zastępczymi algorytmy często **zwalniają w czasie**, ponieważ złożoność modelu rośnie wraz z liczbą zgromadzonych próbek [Bliek i in., 2020; Ueno i in., 2016]. W skrajnym przypadku **sam algorytm może stać się droższy niż pojedyncza, oryginalnie droga ocena funkcji celu**. Mierząc oddzielnie:

- czas CPU zużywany przez algorytm,  
- czas CPU zużywany przez funkcje celu,

możemy sprawdzić, czy **liczba FEs rzeczywiście jest czynnikiem ograniczającym**, a ponadto lepiej zrozumieć:

- jak kosztowny jest cały benchmark,  
- czy wszystkie wywołania funkcji celu są **jednakowo kosztowne**.

Jeśli jednak funkcje celu są drogie nie ze względu na czas obliczeń, lecz z innych powodów (np. zużycie drogich próbek biologicznych, użycie kosztownego sprzętu, udział człowieka), samo liczenie **FEs może być wystarczające**.

Warto zauważyć, że w społeczności EC często używa się także **liczby generacji** jako czasopodobnej, niezależnej od maszyny miary. Jednak raportowanie **tylko generacji** jest niebezpieczne: relacja między **FEs a generacjami** nie zawsze jest jasna (różne algorytmy mogą wywoływać funkcję celu w różny sposób), co utrudnia porównania np. z algorytmami lokalnego przeszukiwania.  

Dlatego, jeżeli podajemy liczbę generacji, **powinniśmy zawsze podawać również liczbę FEs**.

---

### 5.2 Pomiar jakości rozwiązania

Istnieje wiele „naturalnych” miar jakości, zależnych od konkretnego problemu, np.:

- wartość funkcji dopasowania (fitness) w optymalizacji ciągłej,  
- długość trasy w TSP,  
- dokładność klasyfikatora w zadaniu uczenia maszynowego,  
- liczba jedynek w ciągu binarnym w problemie OneMax.

Interpretowanie **samych surowych wartości** funkcji celu jest jednak zwykle:

- trudne,  
- silnie zależne od konkretnej instancji (skala, przesunięcia itd.).

Dlatego warto rozważyć **bardziej intuicyjne i mniej zależne od problemu** miary [Johnson, 2002a; Talbi, 2009].

Jeśli dla danej instancji znamy **optymalne rozwiązanie**, można użyć:

- **bezwzględnej** lub  
- **względnej różnicy** względem optymalnej wartości celu.

Alternatywnie, jeśli optimum nie jest znane, można korzystać z **najlepszego znanego dolnego ograniczenia**. Przykładowo, w TSP często porównuje się wyniki do **dolnego ograniczenia Held-Karpa** [Johnson, 2002a].

Ponieważ różnice **bezwzględne** silnie zależą od skali wartości funkcji celu, **zdecydowanie zaleca się używanie różnic względnych**, np.:

> procentowy nadmiar (excess) względem optymalnego rozwiązania,

co jest od dawna standardem w literaturze TSP [Christofides, 1976]. Co ciekawe, w continuous BBOB [Hansen i in., 2016b] wciąż często korzysta się z różnic **absolutnych**.

Inną możliwością jest normalizacja względem **określonej, prostej heurystyki** [Johnson, 2002a], np.:

- porównanie do rozwiązania znalezionego przez prostą, standardową metodę,  
- raportowanie „nadmiaru względem najlepszego znanego rozwiązania”.

Takie podejście jest częste np. w **szeregowaniu zadań (Job Shop Scheduling)** [Weise, 2019], ale wymaga:

- dobrej znajomości literatury,  
- i może być trudniejsze do interpretacji w dalszej przyszłości.

W niektórych domenach dostępne są **rozwiązania referencyjne** – wtedy można raportować **nadmiar względem ich jakości**.

**Optymalizacja z ograniczeniami.**  
W problemach z ograniczeniami rozwiązanie jest **dopuszczalne** (feasible) lub nie, zgodnie z zestawem ograniczeń. Wtedy jako miary jakości można stosować np.:

- **sumę bezwzględnych naruszeń** wszystkich ograniczeń [Hellwig i Beyer, 2019; Kumar i in., 2020].

---

### 5.3 Pomiar odporności (robustness)

Jeśli chodzi o analizę odporności, można wyróżnić **trzy główne źródła zmienności wyników**:

1. **stochastyczne zachowanie algorytmu** (np. losowe heurystyki wyszukiwania),  
2. **szum w problemie** (np. losowe pomiary, losowe symulacje),  
3. **chropowatość (ruggedness) lub gładkość krajobrazu** funkcji celu.

W praktyce **chropowate krajobrazy** mogą być bardzo problematyczne. Przykłady:

- sterowanie parametrami samolotu,  
- planowanie operacji medycznych.

W takich zastosowaniach **globalne optimum** często **nie** jest celem samym w sobie, jeśli minimalne zmiany w przestrzeni rozwiązań mogą powodować **niebezpieczne skutki** w przestrzeni wyników (np. bezpieczeństwo lotu, zdrowie pacjenta) [Branke, 1998; Tsutsui i in., 1996]. Zamiast tego:

> bardziej interesuje nas znalezienie **lokalnych optymów**,  
> których wartości są:
> - bardzo zbliżone do globalnego optimum,  
> - ale **mało wrażliwe** na niewielkie zaburzenia rozwiązania.

Drugim częstym problemem w praktyce jest **szum**. W eksperymentach fizycznych i symulacjach stochastycznych wynik oceny **może się różnić mimo identycznego rozwiązania** [Arnold, 2012; Cauwet i Teytaud, 2016].

Trzecim źródłem zmienności jest **stochastyczność samych algorytmów**. Wiele współczesnych metod optymalizacji próbkowanej to **losowe heurystyki**, przez co wyniki będą się różnić przy powtórzeniu doświadczenia (kolejne uruchomienie z tymi samymi danymi).

Dlatego standardowo używa się **metryk agregujących wyniki wielu (idealnie niezależnych) uruchomień**, aby otrzymać wiarygodne oszacowania wydajności algorytmu.

#### Położenie: miary zachowania „centralnego”

W podejściu **stałego budżetu** (przekrój pionowy) jakość rozwiązania zazwyczaj agreguje się za pomocą **średniej arytmetycznej**. Można jednak stosować też inne miary:

- **medianę**,  
- **średnią geometryczną** [Fleming i Wallace, 1986] – szczególnie przy agregacji wyników znormalizowanych.

W scenariuszach, gdzie głównym celem jest osiągnięcie **zadanego poziomu jakości** (przekrój poziomy), trzeba często agregować **zarówno udane, jak i nieudane uruchomienia**. Najczęściej stosuje się wtedy 2–3 metryki, m.in.:

- **Expected Running Time (ERT)** – „oczekiwany czas działania” [Auger i Hansen, 2005; Price, 1997]  
  Oblicza się go jako:

  > suma całkowitego zużytego budżetu we wszystkich uruchomieniach  
  > ÷  
  > liczba uruchomień zakończonych sukcesem [Hansen i in., 2012]

  W ten sposób otrzymujemy **średni czas potrzebny na osiągnięcie zadanej jakości**, przy założeniu, że w razie niepowodzenia algorytm jest restartowany po stałym czasie \(T\) aż do sukcesu.

- **Penalized Average Runtime (PAR)** – „kara za nieudane uruchomienia” [Bischl i in., 2016]  
  Częściej używana w domenach takich jak TSP, SAT itd.  
  Nieudane uruchomienia otrzymują **karę** równą np. 2× lub 10× maksymalnego budżetu:

  - **PAR2** – kara 2× budżet,  
  - **PAR10** – kara 10× budżet.  

  Po nałożeniu kar liczy się **średnią arytmetyczną** zużytego budżetu.

- **Penalized Quantile Runtime (PQR)** [Bossek i in., 2020a; Kerschke i in., 2018a]  
  Działa podobnie jak PAR, ale zamiast średniej używa **kwantyli** (zwykle **median**).  
  Dzięki temu PQR jest **bardziej odporne** na skrajne wartości niż PAR.

#### Rozrzut i niezawodność

Typową miarą **niezawodności** jest szacowane **prawdopodobieństwo sukcesu**, czyli:

> odsetek uruchomień, które osiągnęły zdefiniowany cel.

Bossek i in. [2020a] wykorzystują tę miarę, by spojrzeć na problem wielokryterialnie – łączą:

- prawdopodobieństwo sukcesu,  
- średni czas działania w uruchomieniach zakończonych sukcesem.

Podobnie Hellwig i Beyer [2019] agregują te dwie wielkości w pojedynczą miarę SP.

Jako miary **rozrzutu** dla danej metryki wydajności stosuje się:

- **odchylenie standardowe**,  
- **kwantyle** – zwykle preferowane, bo bardziej odporne na skrajne wartości.

W optymalizacji z ograniczeniami używa się m.in.:

- **współczynnika dopuszczalności (feasibility rate, FR)** [Kumar i in., 2020; Wu i in., 2017] – odsetek uruchomień, które znalazły przynajmniej jedno rozwiązanie dopuszczalne,  
- **liczby naruszonych ograniczeń** w rozwiązaniu medianowym [Kumar i in., 2020],  
- **średniej wielkości naruszeń ograniczeń** w najlepszych rozwiązaniach z każdego uruchomienia [Hellwig i Beyer, 2019].

---

### 5.4 Otwarte problemy

Choć w wielu dziedzinach optymalizacji ustaliły się już **standardowe metryki** (np. ERT, PAR, FR itd.), obszar pomiaru wydajności nadal ma wiele **otwartych pytań**. Przykładowo:

- Najczęściej wydajność mierzy się przy **stałej wartości** (budżet lub cel), ale w wielu zastosowaniach interesuje nas także **zachowanie anytime** – pełne krzywe jakości w czasie.
- Trzeba umieć **łączyć** w jednej analizie:
  - jakość i czas,  
  - koszty naruszeń ograniczeń (optymalizacja z ograniczeniami),  
  - wariancję/niepewność wyników (problemy szumne i odporne),  
  - rozrzut położenia lokalnych optymów (optymalizacja wielomodalna),  
  - „odległość” populacji od lokalnych i/lub globalnego optimum.

Innymi słowy, wciąż brakuje **uniwersalnych, dobrze ugruntowanych metryk**, które w spójny sposób uwzględniałyby wszystkie te aspekty.

## 6. Jak analizować wyniki?

### 6.1 Podejście trójpoziomowe

Gdy użytkownik wybierze miarę wydajności algorytmu i zbierze wszystkie dane z eksperymentów, kolejnym krokiem jest **analiza danych** i wyciągnięcie z nich wniosków. Spośród szczegółowo opisanych celów benchmarkingu w sekcji 2 skoncentrujemy się na celach (G1.2) i (G1.3), czyli:

- porównywaniu algorytmów,  
- „konkursach” pomiędzy wieloma algorytmami.

Będziemy zatem rozważać:

- **analizę pojedynczego problemu**,  
- **analizę wielu problemów**.

W obu scenariuszach zakładamy obecność **wielu algorytmów**, tzn. – zgodnie z notacją z sekcji 2 – mamy co najmniej dwie różne instancje algorytmu, powiedzmy \(a_j\) i \(a_k\) z algorytmu \(A\), lub przynajmniej dwie instancje \(a_j \in A\) i \(b_k \in B\), gdzie \(A\) i \(B\) oznaczają różne algorytmy.

**Analiza pojedynczego problemu** to sytuacja, w której dysponujemy wieloma uruchomieniami algorytmów na **jednej instancji problemu** \(\pi_i \in \Pi\). Jest to konieczne, ponieważ wiele algorytmów optymalizacyjnych ma charakter **stochastyczny**, więc nie ma gwarancji, że wynik będzie taki sam przy każdym uruchomieniu. Co więcej, często różni się również **ścieżka poszukiwania** prowadząca do rozwiązania. Z tego powodu **pojedyncze uruchomienie na problem** nie wystarczy – potrzeba wielu powtórzeń, aby móc coś sensownie stwierdzić. W tym scenariuszu wynik analizy mówi nam, **który algorytm jest najlepszy dla tej konkretnej instancji problemu**.

W **analizie wielu problemów**, przy nastawieniu na cel (G1.2), interesuje nas porównanie algorytmów na **zbiorze problemów benchmarkowych**. Dobre praktyki dotyczące wyboru reprezentatywnej wartości dla takich analiz (np. jaka statystyka ma reprezentować algorytm na danym problemie) omawiamy w sekcji 7.

Niezależnie od tego, czy analizujemy pojedynczy problem, czy wiele problemów, dobre praktyki sugerują, że analizę wyników warto prowadzić jako **podejście trójpoziomowe**, składające się z trzech kroków:

1. **Exploratory Data Analysis (EDA)** – eksploracyjna analiza danych,  
2. **Confirmatory Analysis** – analiza potwierdzająca (statystyczna),  
3. **Relevance Analysis** – analiza istotności praktycznej / relewancji.

W tej sekcji skupiamy się na analizie wyników empirycznych przy użyciu opisowych, graficznych i statystycznych narzędzi, które można wpasować w powyższe trzy poziomy. Więcej informacji o technikach i dobrych praktykach analizy wyników eksperymentalnych można znaleźć np. w: Crowder et al. (1979), Golden et al. (1986), Barr et al. (1995), Bartz-Beielstein et al. (2004, 2010), Chiarandini et al. (2007), García et al. (2009), Derrac et al. (2011), Eftimov et al. (2017), Beiranvand et al. (2017).

Mersmann et al. (2010) oraz nowsze prace Kerschke i Trautmann (2019a) przedstawiają metody oparte na **Exploratory Landscape Analysis (ELA)**, które pomagają odpowiedzieć na dwa podstawowe pytania pojawiające się przy benchmarkingu:

1. **Który algorytm jest „najlepszy”?**  
2. **Jakiego algorytmu powinienem użyć dla mojego rzeczywistego problemu?**

W dalszej części streszczamy najbardziej akceptowane i standardowe praktyki **rzetelnej oceny algorytmów**. Stosowanie tych metod może prowadzić do szerokiej akceptacji i stosowalności empirycznie testowanych algorytmów oraz stanowić przewodnik po „dżungli” narzędzi statystycznych.

---

### 6.2 Exploratory Data Analysis (EDA)

#### 6.2.1 Motywacja

**Exploratory Data Analysis (EDA)** to podstawowy zestaw narzędzi wykorzystujący techniki opisowe i graficzne do lepszego zrozumienia i eksploracji wyników empirycznych. EDA **powinna być wykonana jako pierwsza**, aby zweryfikować założenia dotyczące rozkładu wyników (np. normalność, niezależność), zanim zastosujemy bardziej zaawansowane techniki statystyczne omówione w sekcji 6.3.

Zalecamy rozpoczęcie od EDA, aby:

- uchwycić **podstawowe wzorce w danych**,  
- przygotować **(statystyczne) hipotezy**, które później będą testowane w analizie potwierdzającej.

W EDA preferowane są **narzędzia wizualne**, które:

- nie zakładają z góry konkretnego modelu probabilistycznego,  
- umożliwiają **elastyczną i indukcyjną** pracę z danymi – „pozwalają danym mówić”.

Częste motto EDA brzmi: **„let the data speak”** – dane podpowiadają ciekawe pytania; np. **niespodziewane obserwacje odstające** mogą wskazywać na poważny błąd w implementacji algorytmu.

EDA jest więc:

- sposobem **generowania hipotez**, które później analizujemy w drugim kroku (analiza potwierdzająca),  
- narzędziem do **pogłębionego zrozumienia** algorytmów,  
- ale **nie zawsze daje jednoznaczne odpowiedzi** – w takich przypadkach niezbędny jest kolejny krok.

Istnieje także ryzyko **przeuczenia**: jeśli zbyt mocno skupimy się na bardzo specyficznym projekcie eksperymentu i wynikach, możemy wyciągać nadmiernie pesymistyczne (lub zbyt optymistyczne) wnioski.

W praktyce EDA bazuje na **doświadczeniu, osądzie i pewnej „sztuce”**. Nie istnieje żaden sztywny „podręcznik kucharski”, ale raczej wiele „przepisów”.  

Poniżej przedstawiamy **kluczowe narzędzia EDA**, które:

- pozwalają formułować **ważne wnioski** w postaci graficznej,  
- często nie wymagają już dodatkowej, formalnej analizy statystycznej.

Klasycznym źródłem na temat EDA jest praca Tukeya (1977).

#### 6.2.2 „Wspaniała siódemka”

Statystyki opisowe, często nazywane tutaj **„wspaniałą siódemką”**, to:

- średnia,  
- mediana,  
- najlepsza i najgorsza wartość (minimum i maksimum),  
- pierwszy i trzeci kwartyl,  
- odchylenie standardowe.

Te siedem statystyk podsumowujących opisuje:

- **położenie centrum rozkładu** (tendencję centralną),  
- **rozproszenie wyników** (zmienność).

Trzeba jednak pamiętać, że:

- mogą być **wrażliwe na obserwacje odstające**,  
- mogą być zniekształcone przez **brakujące lub obciążone dane**,  
- **nie dają pełnego obrazu** wydajności, bo opierają się na konkretnej próbce danych.

Przykładowo:

- **średnia i odchylenie standardowe** są mocno podatne na wartości odstające – te mogą wynikać z pojedynczych „bardzo złych” przebiegów algorytmu albo z jego dużej zmienności (np. za mało powtórzeń, źle dobrane punkty startowe, zbyt mały budżet ewaluacji),  
- **mediana** jest statystyką bardziej odporną niż średnia – pod warunkiem, że dysponujemy **wystarczająco liczną próbą**,  
- **minimum i maksimum** dają inne spojrzenie na wydajność, ale opierają się tylko na jednym punkcie z \(n\), więc są **mało odporne**,  
- **kwantyle** (np. kwartyle) dzielą rozkład na części o równym prawdopodobieństwie – podobnie jak mediana wymagają jednak odpowiednio dużej liczby danych i **mają ograniczony sens dla bardzo małych prób**.

Szczegółową dyskusję tych podstawowych statystyk znaleźć można w Bartz-Beielstein (2006).

#### 6.2.3 Narzędzia graficzne

**Wizualizacja wyników końcowych.**  
Narzędzia graficzne dają wgląd w:

- rozkłady wyników,  
- obecność odstających wartości,  
- kształt rozkładu.

Do analizy **końcowych wyników** optymalizacji (np. najlepszych wartości funkcji celu na koniec każdego uruchomienia) przydatne są:

- **histogramy** – pokazują kształt rozkładu,  
- **wykresy pudełkowe (boxploty)** – w zwartej formie prezentują statystyki z sekcji 6.2.2 i ułatwiają wykrywanie odstających punktów.

Ponieważ on rozwój histogramu silnie zależy od szerokości „koszyków”, **zaleca się łączenie histogramów z wykresami gęstości** (density plots).

**Wizualizacja zachowania w czasie.**  
Druga grupa narzędzi służy do analizy **przebiegu algorytmu w czasie**, czyli:

- jak zmienia się miara wydajności wraz z kolejnymi ewaluacjami / iteracjami.

Przykładowo:

- **wykresy zbieżności (convergence plots)** – wartość funkcji celu (lub inna miara) w funkcji liczby ewaluacji; pozwalają w jednym wykresie porównać dynamikę kilku algorytmów,  
- „anytime plots” – podobna idea, ale nacisk na porównanie całego przebiegu zachowania algorytmu.

**Analiza wielu problemów.**  
Przy analizie wielu problemów również korzysta się z:

- histogramów,  
- boxplotów,

ale opracowano też **specjalne narzędzia**, np.:

- **profile wydajności (performance profiles)** Dolan i Moré (2002) – oparte na dystrybuancie (CDF) pewnej miary wydajności (np. czas CPU czy jakość rozwiązania). Dla każdego algorytmu rysujemy rozkład **ilorazu** jego wyniku do **najlepszego wyniku** wśród wszystkich algorytmów. Pozwala to graficznie przedstawić przewagi (lub słabości) algorytmów.

Profile wydajności **nie nadają się** do zastosowania, gdy **nie znamy prawdziwego optimum** (lub choćby dobrego przybliżenia). Można wtedy użyć:

- najlepszego dotąd znanego rozwiązania,  
- „domyślnie założonego optimum” na podstawie doświadczenia użytkownika – ale to jest podatne na błędy.

Ponieważ profile wydajności **nie są oparte na liczbie ewaluacji**, nie mówią nam:

> „jaki odsetek problemów można rozwiązać przy zadanym budżecie ewaluacji?”

Aby odpowiedzieć na takie pytanie, wykorzystuje się **profile danych (data profiles)**, zaproponowane dla optymalizacji bezgradientowej w scenariuszu **stałego budżetu** (Moré i Wild, 2009). Pozwalają one porównywać najlepsze rozwiązania osiągane przez różne algorytmy przy zachowaniu tego samego budżetu.

---

### 6.3 Analiza potwierdzająca (Confirmatory Analysis)

#### 6.3.1 Motywacja

Drugim krokiem w podejściu trójpoziomowym jest **analiza potwierdzająca (confirmatory analysis)**, która należy do **statystyki wnioskowania (inferencyjnej)** i opiera się na podejściu dedukcyjnym:

> mamy **założenie / hipotezę statystyczną** i sprawdzamy je w świetle danych eksperymentalnych.

Celem jest udzielenie **jednoznacznych odpowiedzi** na **konkretnie postawione pytania**, powiązane z danym projektem eksperymentu. Ponieważ analiza potwierdzająca bazuje na **modelach probabilistycznych**, jej głównymi narzędziami są:

- **testy hipotez**,  
- **przedziały ufności**.

W idealnej sytuacji analiza potwierdzająca daje **bardziej precyzyjne odpowiedzi niż EDA**, ale tylko wtedy, gdy:

- **założenia modeli są spełnione**.  

W przeciwnym razie możemy otrzymać **fałszywe poczucie precyzji**.

W wielu przypadkach narzędzia EDA **nie wystarczają**, aby jasno wykazać różnice między algorytmami – szczególnie gdy:

- różnice są **niewielkie**,  
- dane są szumne,  
- wyniki mają dużą wariancję.

Wtedy potrzebna jest **statystyczna analiza porównawcza**. Szczegółowo dyskutowano to m.in. w: Amini i Barr (1993), Barr et al. (1995), Golden et al. (1986), McGeoch (1996), Chiarandini et al. (2007), Carrano et al. (2011), García et al. (2009), Eftimov et al. (2017).

Podstawą tej analizy jest **testowanie hipotez**. Przed analizą wydajności należy zdefiniować:

- **hipotezę zerową** \(H_0\),  
- **hipotezę alternatywną** \(H_1\).

Typowo:

- \(H_0\): „nie ma istotnej statystycznie różnicy między wydajnością algorytmów”,  
- \(H_1\): „istnieje istotna statystycznie różnica”.

Test może być:

- **dwustronny** (sprawdzamy, czy algorytmy różnią się ogólnie),  
- **jednostronny** (sprawdzamy, czy jeden z algorytmów jest lepszy od drugiego).

W benchmarkingu częściej interesuje nas przypadek **jednostronny**, bo chcemy spytać:

> „Czy instancja algorytmu **a** jest **lepsza** niż instancja **b**?”

Niech \(p(a)\) oznacza miarę wydajności algorytmu \(a\). W przypadku **minimalizacji** mniejsza wartość \(p(a)\) oznacza lepszy wynik (np. niższa wartość funkcji celu, krótszy czas działania). Stwierdzenie:

> „algorytm \(a\) jest lepszy niż \(b\)”

odpowiada:

> \(p(a) < p(b)\).

Możemy to sformułować jako hipotezę:

- \(H_1 : p(b) - p(a) > 0\).

Zgodnie ze standardową praktyką, testujemy tę hipotezę przeciw hipotezie zerowej:

- \(H_0 : p(b) - p(a) \le 0\),

która mówi, że **\(a\) nie jest lepszy niż \(b\)**.

Po zdefiniowaniu hipotez wybieramy **odpowiedni test statystyczny** \(T\). Test statystyczny to funkcja próbki losowej, która pozwala ocenić **jak bardzo** obserwowane dane są (lub nie są) zgodne z hipotezą zerową. Przykład:

- **średnia najlepszych znalezionych wartości** z \(n\) powtórzeń algorytmu.

Musimy też wybrać **poziom istotności** \(\alpha\) (np. 0,05, czyli 95% poziom ufności). Wybór \(\alpha\) zależy zarówno od:

- projektu eksperymentu,  
- charakteru pytania badawczego.

#### 6.3.2 Założenia bezpiecznego stosowania testów parametrycznych

Istnieją dwie główne klasy testów:

- **parametryczne**,  
- **nieparametryczne**.

Aby móc zastosować **test parametryczny**, muszą być spełnione pewne **standardowe założenia**, m.in.:

1. **Niezależność** obserwacji,  
2. **Normalność** rozkładu,  
3. **Jednorodność wariancji (homoscedastyczność)**.

W kontekście benchmarkingu:

- niezależność zazwyczaj jest spełniona, jeśli porównujemy wyniki z **niezależnych uruchomień algorytmu** z różnymi ziarnami losowymi,  
- normalność można sprawdzić za pomocą testów takich jak:
  - test Kołmogorowa–Smirnowa,  
  - test Shapiro–Wilka,  
  - test Andersona–Darlinga,  
  lub **wizualnie**:
  - histogramy,  
  - empiryczne dystrybuanty,  
  - wykresy kwantyl–kwantyl (Q–Q plots),  

- jednorodność wariancji można badać testami:
  - Levene’a,  
  - Bartletta.

Istnieją także **transformacje danych** (np. logarytmiczne, potęgowe), które mogą pomagać w osiągnięciu normalności – trzeba ich jednak używać **z dużą ostrożnością**, ponieważ zmieniają one skalę i interpretację wyników.

Jeśli założenia testów parametrycznych są spełnione, można je stosować – zwykle mają **większą moc** niż testy nieparametryczne. W przeciwnym razie należy wybrać **test nieparametryczny**.

Dodatkowo, przed wyborem testu powinniśmy ustalić, czy dane są:

- **sparowane (paired)** – naturalne pary obserwacji, np. ten sam problem, **to samo ziarno**, różne algorytmy,  
- **niesparowane (unpaired)** – brak takiej naturalnej pary.

To jest decyzja **na poziomie projektu eksperymentu**. Jedną z metod generowania danych sparowanych są:

- **Common Random Numbers (CRN)** – użycie tych samych sekwencji losowych (np. identycznych ziaren) w porównywanych algorytmach. CRN mogą **zmniejszyć wariancję** i prowadzić do bardziej stabilnych wniosków (Kleijnen, 1988; Nazzal et al., 2012).

### Rysunek 3. Schemat wyboru odpowiedniego testu statystycznego  
(na podstawie: Eftimov et al., 2020)

Poniżej przedstawiono **krok po kroku**, jak dobrać test statystyczny do porównania algorytmów optymalizacyjnych – w zależności od:

- liczby porównywanych algorytmów,
- liczby problemów (instancji),
- spełnienia / niespełnienia założeń testów parametrycznych,
- oraz tego, czy dane są sparowane, czy nie.

---

#### Krok 1. Co porównujesz?

1. **Scenariusz A: jeden problem (jedna instancja)**  
   Masz wiele uruchomień każdego algorytmu na **tej samej instancji problemu**.  
   Chcesz porównać wydajność **na tym konkretnym problemie**.

2. **Scenariusz B: wiele problemów / instancji**  
   Masz wyniki algorytmów na **wielu problemach** (benchmark).  
   Dla każdej pary (algorytm, problem) dysponujesz jedną wartością reprezentatywną (np. średnią lub medianą z wielu uruchomień).  
   Chcesz ocenić **ogólną przewagę / brak przewagi** w przekroju wielu problemów.

W obu scenariuszach musisz zdecydować, czy porównujesz:

- **tylko dwie metody** (porównanie parami), czy  
- **więcej niż dwie metody naraz** (porównanie wielokrotne).

---

#### Scenariusz A: jeden problem

##### A1. Porównanie dwóch algorytmów

1. Sprawdź, czy próbki można traktować jako:
   - **niesparowane** (najczęściej) – niezależne uruchomienia każdego algorytmu,  
   - **sparowane** – np. używasz tych samych ziaren losowych / punktów startowych dla obu algorytmów.

2. Sprawdź **założenia testu parametrycznego**:
   - czy rozkład wyników jest (w przybliżeniu) **normalny**?  
   - czy **wariancje są zbliżone** (homoscedastyczność)?

3. Wybierz test:

- Jeśli **założenia są spełnione**  
  - dane niesparowane → **test t-Studenta dla prób niezależnych**,  
  - dane sparowane → **test t-Studenta dla prób sparowanych**.

- Jeśli **założenia są naruszone**  
  - dane niesparowane → **test Manna–Whitneya U (Wilcoxon rank-sum)**,  
  - dane sparowane → **test Wilcoxona signed-rank**.

##### A2. Porównanie więcej niż dwóch algorytmów

1. Sprawdź założenia parametryczne (normalność, jednorodność wariancji).

2. Wybierz test globalny:

- Jeśli **założenia są spełnione** → **jednoczynnikowa ANOVA (one-way ANOVA)**.  
- Jeśli **założenia są naruszone** → **test Kruskala–Wallisa**.

3. Jeśli test globalny **odrzuci hipotezę zerową**  
   → wykonaj **testy post-hoc** (porównania par algorytmów) z odpowiednią **korektą wielokrotnych porównań** (Nemenyi, Holm, Shaffer, Bergmann itd.).

---

#### Scenariusz B: wiele problemów (benchmark wielu instancji)

Załóżmy, że:

- dla każdego algorytmu i problemu masz **jedną liczbę reprezentującą wydajność**, np.  
  - średnią z wielu uruchomień,  
  - medianę,  
  - lub ranking oparty na DSC / pDSC.

Dane traktujemy jako **sparowane** (każdy algorytm ma wynik na tym samym zbiorze problemów).

##### B1. Porównanie dwóch algorytmów

1. Sprawdź założenia parametryczne (normalność różnic itd.).

2. Wybierz test:

- **Założenia spełnione** → **test t-Studenta dla prób sparowanych**.  
- **Założenia naruszone** → **test Wilcoxona signed-rank**.

##### B2. Porównanie więcej niż dwóch algorytmów

1. Sprawdź założenia parametryczne.

2. Wybierz test globalny:

- **Założenia spełnione** → **ANOVA z powtarzanymi pomiarami (repeated-measures ANOVA)**.  
- **Założenia naruszone** →  
  - **test Friedmana**,  
  - lub jego warianty: **Friedman aligned ranks**, **test Imana–Davenporta**.

3. Jeśli test globalny **odrzuci hipotezę zerową**:

   - zastosuj **procedury post-hoc**:
     - **scenariusz „wszystkie pary”** → testować każdą parę algorytmów, z korektami typu Nemenyi, Holm, Shaffer, Bergmann itd.,  
     - **scenariusz „vs. kontrola”** → wybierasz algorytm referencyjny (np. Twój algorytm) i porównujesz go z każdym innym, używając korekt Bonferroni, Holm, Hochberg, Hommel, Holland, Rom, Finner, Li itd.

---

#### Uwagi końcowe

- Jeśli **założenia parametryczne są wątpliwe**, preferuj **testy nieparametryczne oparte na rangach**.  
- Przy **dużej liczbie porównań** zawsze stosuj **korekty dla wielokrotnych testów**, aby uniknąć inflacji błędu I rodzaju.  
- Schemat z Rysunku 3 nie narzuca jednego „jedynego słusznego” testu, ale **prowadzi użytkownika po drzewie decyzji**, pomagając dobrać test **adekwatny do danych i projektu eksperymentu**.

#### 6.3.3 Schemat wyboru odpowiedniego testu

Na rysunku 3 w oryginale przedstawiono **„pipeline” (schemat) wyboru testu statystycznego** dla benchmarkingu algorytmów optymalizacyjnych. Uwzględnia on:

- liczbę próbek (dwie czy więcej),  
- spełnienie lub niespełnienie założeń testów parametrycznych,  
- parowanie / brak parowania.

Poniżej streszczamy główne rekomendacje – osobno dla analizy pojedynczego problemu i wielu problemów.

##### Analiza pojedynczego problemu

W tym przypadku mamy:

- wiele uruchomień \(k\) instancji algorytmów \(a_1, \dots, a_k\)  
- na **jednej** instancji problemu \(\pi_j\).

Możemy wykonywać:

- **porównania parami (pairwise comparison)** – porównujemy dwa algorytmy na raz,  
- **porównania wielokrotne (multiple comparison)** – porównujemy naraz więcej niż dwa algorytmy.

Uwaga: „porównanie parami” **nie oznacza automatycznie, że próbki są sparowane** – większość porównań par algorytmów w praktyce używa próbek **niesparowanych**, bo rygorystyczne parowanie (CRN, kontrola strumieni RNG) bywa trudne wdrożeniowo.

Dla **porównań par algorytmów**:

- **test t-Studenta** – wersja parametryczna,  
- **test Manna–Whitneya U / Wilcoxona-rang sum** – odpowiednik nieparametryczny.

Dla **więcej niż dwóch algorytmów**:

- **jednoczynnikowa ANOVA (one-way ANOVA)** – wersja parametryczna,  
- **test Kruskala–Wallisa** – odpowiednik nieparametryczny.

Jeśli test wielokrotny (np. ANOVA lub Kruskal–Wallis) **odrzuci hipotezę zerową**, należy wykonać dodatkowo **procedurę post-hoc**, aby ustalić, **które konkretnie pary algorytmów** przyczyniają się do istotnej różnicy.

##### Analiza wielu problemów

Dla każdego algorytmu na każdej instancji problemu mamy wiele uruchomień; z tych danych musimy wybrać **wartość reprezentatywną**:

- najczęściej:
  - **średnią** miary wydajności, lub  
  - **medianę** (bardziej odporną na odstające przebiegi).

Obie wartości są jednak wrażliwe na **„błędy w epsilon-sąsiedztwie”** – bardzo małe różnice, których nie wychwytują rankingi testów nieparametrycznych, a które mogą **wpływać na wynik testu** przy dużej liczbie problemów.

Dlatego zaproponowano **Deep Statistical Comparison (DSC)** (Eftimov et al., 2017), który:

- opiera ranking nie na pojedynczej statystyce (średniej / medianie),  
- lecz na **całym rozkładzie** wyników dla danego algorytmu i problemu.

Wpływ wyboru:

1. średniej,  
2. mediany,  
3. klasycznego rankingu,

na wynik analizy wieloproblemowej omówiono w Eftimov i Korošec (2018).

**Testy statystyczne.**  
Po wybraniu transformacji (średnia, mediana, DSC) możemy dobrać test:

- dla **porównań par algorytmów**:
  - **test t-Studenta** – parametryczny,  
  - **test Wilcoxona signed-rank** – nieparametryczny odpowiednik (dla danych sparowanych – np. ten sam zestaw problemów),

- dla **więcej niż dwóch algorytmów**:
  - **ANOVA z powtarzanymi pomiarami (repeated measures ANOVA)** – parametryczna,  
  - **test Friedmana**, **Friedman aligned ranks**, **test Imana–Davenporta** – nieparametryczne odpowiedniki.

Jeśli test wielokrotny odrzuci \(H_0\), należy, podobnie jak wyżej, wykonać **procedury post-hoc**, aby zidentyfikować pary algorytmów odpowiedzialne za istotne różnice.

**Inne testy nieparametryczne.**  
Gdy założenia rozkładowe są wątpliwe, stosuje się **testy oparte na rangach**, w których:

- dane zastępuje się **rangami**,  
- p-wartości obliczane są dla rang, a nie dla surowych wartości,

co pomaga:

- zmniejszyć wpływ skośnych rozkładów,  
- lepiej radzić sobie z wartościami ekstremalnymi.

Przykłady:

- **test permutacyjny (permutation test)** – tworzy rozkład permutacyjny przez przetasowywanie danych (bez zwracania) i obliczanie wartości statystyki dla wielu permutacji (Pesarin, 2001),  
- **test trendu Page’a** – test nieparametryczny do analizy np. trendów zbieżności w czasie (Derrac et al., 2014).

**Procedury post-hoc.**  
Jeśli w porównaniu wielokrotnym (np. Friedman, Iman–Davenport) odrzucono \(H_0\), wiemy jedynie, że **„coś się różni”**, ale nie wiemy **co dokładnie**. Potrzebne są procedury post-hoc:

- **„wszystkie pary (all-pairwise)”** – porównujemy każdą parę algorytmów; przy \(k\) algorytmach mamy \(\frac{k(k-1)}{2}\) porównań,  
- **„porównania z kontrolą (vs. control)”** – wybieramy **algorytm referencyjny** (np. nową metodę) i porównujemy go z pozostałymi; mamy \(k-1\) porównań.

W obu przypadkach:

1. obliczamy statystykę post-hoc (zależną od testu głównego),  
2. korygujemy p-wartości, aby kontrolować **problem wielokrotnych porównań** (Family-Wise Error Rate, FWER).

Przykładowo, w przypadku testu Friedmana, Friedman aligned-ranks czy Imana–Davenporta można stosować korekty:

- **Nemenyi**,  
- **Holm**,  
- **Shaffer**,  
- **Bergmann** – w scenariuszu „wszystkie pary”.

W scenariuszu z **algorytmem kontrolnym** można użyć np.:

- **Bonferroni**,  
- **Holm**,  
- **Hochberg**,  
- **Hommel**,  
- **Holland**,  
- **Rom**,  
- **Finner**,  
- **Li**.

Alternatywnie można przeprowadzić serię **parowych testów** (np. Wilcoxon) między algorytmem kontrolnym a każdym innym algorytmem, ale wtedy:

- tracimy bezpośrednią kontrolę nad **FWER**,  
- interpretacja zbioru p-wartości staje się trudniejsza.

Sposoby obliczania „prawdziwej” istotności statystycznej w takim scenariuszu opisano m.in. w Eftimov et al. (2017) oraz García et al. (2009).

---

### 6.4 Analiza relewancji (Relevance Analysis)

#### 6.4.1 Motywacja

Trzeci krok w zalecanym podejściu dotyczy **praktycznej istotności** naszych wyników:

> Czy zaobserwowane różnice **naprawdę mają znaczenie w praktyce**, czy są jedynie **artefaktami statystycznymi**, np. spowodowanymi bardzo dużą liczebnością próby albo specyfiką projektu eksperymentu?

Typowy artefakt:

- różnica w wydajności \(\varepsilon\), która jest **statystycznie istotna**,  
- ale w praktyce **niewykrywalna / nieistotna**, bo \(\varepsilon\) jest znacznie mniejsza niż rzeczywista dokładność pomiaru lub sensowny próg błędu.

W takich przypadkach nadal istnieje **„przepaść” między teorią a praktyką**: wynik jest istotny statystycznie, ale **bez znaczenia naukowego / inżynierskiego**.

**Przykład 6.1 (linia montażowa).**  
Załóżmy, że porównujemy dwa algorytmy optymalizacyjne minimalizujące **średni czas procesu produkcyjnego** (np. na linii montażowej). Średnia różnica w wydajności wynosi \(\varepsilon = 10^{-14}\) i jest **statystycznie istotna**. W rzeczywistości ta różnica **nie ma żadnego znaczenia**, bo jest **o wiele rzędów wielkości mniejsza** niż dokładność pomiaru czasu na linii produkcyjnej.

Dlatego, oprócz „czy jest istotnie statystycznie?”, zawsze powinniśmy pytać:

- **„czy ta różnica ma sens praktyczny?”**,  
- „czy w mojej dziedzinie / aplikacji taka różnica w ogóle jest mierzalna lub użyteczna?”.

Trzeba pamiętać, że **praktyczna istotność** zależy:

- od konkretnego problemu,  
- od realnych ograniczeń pomiaru,  
- od szczegółów implementacyjnych (dokładność obliczeń zmiennoprzecinkowych, typy zmiennych, kryteria stopu itd.).

Na przykład:

- różne **typy liczb zmiennoprzecinkowych** (float 32-bit vs 64-bit),  
- różne **progi błędu** w kryterium stopu,

mogą generować drobne różnice w wyniku, które **formalne testy statystyczne wykryją**, ale które **nie reprezentują realnej różnicy w wydajności algorytmów**.

#### 6.4.2 „Severity” – relewancja wyników testów parametrycznych

Aby ocenić **sensowność** istotnego wyniku statystycznego, można zastosować **analizę post-hoc**. Jednym z podejść jest **miara „severity”** (Mayo i Spanos, 2006; Bartz-Beielstein et al., 2010) – meta-statystyczna zasada oceny:

- jak silnie dane **wspierają** decyzję podjętą w klasycznym teście hipotez.

W skrócie:

- „severity” to **rzeczywista moc testu uzyskana dla danych, które mamy**,  
- mierzy, jak **dobrze dane „pasują” do struktury testu**,  
- osobno rozważa się przypadek:
  - **odrzucenia \(H_0\)**,  
  - **nieodrzucenia \(H_0\)**.

Miara severity jest szczególnie przydatna, gdy:

- liczebność próby \(n\) jest bardzo duża (problem „large \(n\)”),  
- nawet minimalne różnice będą wtedy statystycznie istotne,  
- severity pomaga ocenić, czy **taka „mikro-różnica” naprawdę coś znaczy**.

#### 6.4.3 Analiza wielu problemów – CRS4EA i pDSC

W kontekście **wielu problemów** istnieją co najmniej dwa podejścia oceniające **praktyczną ważność** istotnych wyników:

1. **Chess Rating Systems for Evolutionary Algorithms (CRS4EA)** (Veček et al., 2014)  

   - traktuje algorytmy jako **zawodników w turnieju szachowym**,  
   - porównanie wyników dwóch algorytmów na danym problemie odpowiada **wynikowi pojedynczej partii**,  
   - użytkownik określa **próg „remisu”**, czyli jak duża (lub mała) różnica w wynikach jest uznawana za równoważną; próg jest **specyficzny dla problemu**,  
   - na końcu każdy algorytm ma **rating**, a analiza statystyczna opiera się na **przedziałach ufności dla ratingów**.

2. **practical Deep Statistical Comparison (pDSC)** – praktyczna modyfikacja DSC (Eftimov i Korošec, 2019)  

   - dane dla każdego problemu są najpierw **wstępnie przetwarzane** przy użyciu **poziomu praktycznej istotności**, zadanego przez użytkownika,  
   - następnie tak przetworzone dane są analizowane metodą DSC w celu wykrycia **różnic, które są zarówno statystycznie, jak i praktycznie istotne**,  
   - zaproponowano dwa sposoby wstępnego przetwarzania:
     1. **sekwencyjne** – przetwarza wyniki z kolejnych uruchomień w ustalonej kolejności,  
     2. **Monte Carlo** – losowo permutuje wyniki, aby uniknąć zależności od kolejności uruchomień.

Porównanie CRS4EA i pDSC przedstawiono w Eftimov i Korošec (2019). Oba podejścia służą do:

- analizy **scenariusza wielu problemów**,  
- wyciągania wniosków, które uwzględniają **praktyczną istotność** różnic.

Dodatkowo:

- rankingi pDSC wyliczone na poziomie pojedynczych problemów można również wykorzystać do **analizy pojedynczego problemu**.

---

### 6.5 Otwarte kwestie

Istotnym aspektem, który w tej wersji dokumentu **nie został jeszcze szczegółowo omówiony**, jest:

> **analiza samych problemów benchmarkowych**, a nie tylko wydajności algorytmów na tych problemach.

Innymi słowy:

- jakie istnieją metody badania **strukturalnych cech problemu benchmarkowego**?  
- w jaki sposób można **automatycznie wydobywać najistotniejsze informacje** o problemie?  
- jak te informacje **interpretować**?

Istnieje wiele podejść, które:

- poprawiają zrozumienie natury problemu (jego „krajobrazu”),  
- mogą wspomagać:
  - projektowanie algorytmów,  
  - wybór algorytmu,  
  - konfigurację parametrów.

Z powyższym wiąże się kwestia **wizualizacji krajobrazów problemów**. Na przykład:

- wizualizacja krajobrazu problemu ciągłego (np. w 2D lub 3D),  
- rysowanie przybliżonych tras dla konkretnych instancji TSP,

zwykle:

- poprawia zrozumienie **trudności i właściwości** problemu (np. wielomodalność, „lejki”),  
- ułatwia badanie **zachowania algorytmów** w czasie.

Niestety, w ogromnej większości prac kwestia **wizualizacji problemów** jest traktowana **bardzo pobieżnie**. Autorzy deklarują, że w kolejnych wersjach dokumentu temat ten zostanie omówiony dokładniej.

## 7. Projektowanie eksperymentów

### 7.1 Planowanie doświadczeń (Design of Experiments, DoE)

Niestety wiele empirycznych badań algorytmów optymalizacji jest wykonywanych i opisywanych **bez uwzględnienia podstawowych zasad projektowania eksperymentów** [Brownlee, 2007]. Aby porównania w benchmarkach były bardziej przejrzyste i obiektywne, warto korzystać z **metod DoE** i pokrewnych technik. Dają one **uporządkowaną procedurę** planowania porównań w taki sposób, by:

- świadomie dobrać, **które i ile uruchomień algorytmów** trzeba wykonać,  
- uzyskać **maksimum informacji przy minimalnej liczbie eksperymentów**.

W klasycznym ujęciu **projektowanie doświadczeń** to proces:

> planowania, przeprowadzania, analizowania i interpretowania kontrolowanych testów w taki sposób,  
> aby ocenić **wpływ zmieniających się czynników** na wynik eksperymentu.

Znaczenie i korzyści dobrze zaplanowanych eksperymentów podsumował m.in. Hooker [1996]. Johnson [2002b] zwraca uwagę, że w raportach należy podawać **nie tylko czas działania algorytmu**, ale też:

- opisać proces **przygotowania / strojenia** przed właściwym uruchomieniem,  
- oraz **wliczyć ten czas przygotowania** do raportowanego czasu działania,  
żeby nie zaniżać realnych kosztów obliczeń.

Kluczowe zagadnienia związane z DoE omawia Kleijnen [2001]. Obszerną listę nowszych publikacji o metodach projektowania podaje Kleijnen [2017]. Strategie projektowania i analizy **eksperymentów komputerowych (DACE – Design and Analysis of Computer Experiments)** opisują Santner i in. [2003].

---

### 7.2 Decyzje projektowe

Decyzje dotyczące projektu eksperymentu można podejmować, opierając się na:

- **kryteriach geometrycznych**, lub  
- **kryteriach statystycznych** [Pukelsheim, 1993; Santner i in., 2003].

W podejściu geometrycznym wyróżnia się dwa podstawowe typy projektów:

1. próbkowanie **na brzegach** przestrzeni (na granicach przedziałów),  
2. próbkowanie **wewnątrz** przestrzeni (w „wnętrzu” obszaru badania).

Klasyczne DoE zazwyczaj stosuje **projekty brzegowe**, natomiast w DACE częściej używa się projektów **wypełniających wnętrze** przestrzeni (space-filling).

Eksperyment nazywamy **sekwencyjnym**, jeśli sposób prowadzenia kolejnych kroków zależy od **aktualnie zebranych wyników**. Istnieją podejścia sekwencyjne zarówno dla projektów brzegowych, jak i space-filling.

Autorzy **zdecydowanie rekomendują** używanie:

- **projektów czynnikowych (factorial)** lub  
- **projektów wypełniających przestrzeń (space-filling)**

zamiast popularnych, ale bardzo ograniczonych projektów typu **„jeden czynnik naraz” (OFAT – One-Factor-At-a-Time)**.

Jeśli w eksperymencie występuje wiele czynników:

- strategia OFAT jest **nieefektywna** – wymaga bardzo wielu uruchomień,  
- **nie pozwala dobrze wykrywać interakcji** pomiędzy czynnikami.

Z tego powodu zaleca się stosowanie **projektów wieloczynnikowych** [Montgomery, 2017]. Projekty czynnikowe (pełne i ułamkowe) są:

- **bardziej odporne** na zakłócenia,  
- zwykle **szybsze** (bardziej informacyjne) w porównaniu z OFAT.

Więcej informacji o pełnych i ułamkowych projektach czynnikowych można znaleźć w [Montgomery, 2017]. Wariantem projektów ułamkowych jest **projekt Taguchiego** [Roy, 2001], który pozwala uzyskać **odporne projekty przy mniejszym koszcie**, z użyciem mniejszej liczby ewaluacji. Do wstępnego „przesiewu” czynników (screening) zaleca się m.in. projekt **Placketta–Burmana** [Plackett i Burman, 1946].

Współczesne projekty **space-filling** bywają jeszcze bardziej efektywne od projektów ułamkowych, zwłaszcza przy **układach silnie nieliniowych**, i często wymagają **mniejszej liczby punktów**. Przegląd takich projektów znajduje się m.in. w [Santner i in., 2003].

Jednocześnie pozostaje otwartym pytanie, **jakie cechy projektu są w praktyce najważniejsze**. Jak zauważają Santner i in. [2003, s. 161], potrzebne są szeroko zakrojone **badania empiryczne**, aby lepiej zrozumieć:

- które projekty sprawdzają się dobrze,  
- dla jakich modeli i w jakich warunkach.

---

### 7.3 Projekty dla badań benchmarkowych

W kontekście DoE i DACE **uruchomienia algorytmu optymalizacyjnego** traktujemy po prostu jako **eksperymenty**. Przy uruchamianiu instancji algorytmu mamy zwykle wiele **stopni swobody**:

- algorytmy wymagają ustawienia licznych **parametrów** (np. rozmiaru populacji w strategiach ewolucyjnych ES) **zanim** uruchomimy optymalizację.

Z punktu widzenia eksperymentatora **zmienne projektowe (czynniki)** to te parametry, które można **świadomie zmieniać** w trakcie eksperymentu.

Ogólnie można wyróżnić **dwie grupy czynników**, które wpływają na zachowanie algorytmu optymalizacyjnego:

1. **Czynniki związane z problemem** – np. konkretna funkcja celu, wymiar, dostępny budżet ewaluacji.  
2. **Czynniki związane z algorytmem** – np. rozmiar populacji ES, współczynniki mutacji/krzyżowania, parametry PSO itp.

W dalszej części rozważamy projekty eksperymentów, które zawierają **obie grupy** czynników.

Najpierw przyglądamy się **czynnikom algorytmicznym**. W literaturze [Beyer i Schwefel, 2002] rozróżnia się:

- **parametry jawne (explicit, exogenous)** – użytkownik widzi je w konfiguracji i może je zmieniać,  
- **parametry ukryte (implicit, endogenous)** – nie są wystawione na zewnątrz; mogą być:
  - niedostępne (np. gdy kod nie jest udostępniany),  
  - „ukryte” w implementacji i trudno je nawet zidentyfikować jako parametry, które można stroić.

**Projekt algorytmiczny** to:

- zestaw parametrów,  
- definiujący konkretne ustawienia dla zmiennych projektowych algorytmu,  
- a więc **konkretną instancję algorytmu**.

Projekt można opisać, podając **zakresy wartości** dla poszczególnych parametrów. Taki projekt:

- może nie zawierać **żadnego** punktu (gdy zakres jest pusty),  
- może zawierać jeden, kilka,  
- albo nawet **nieskończenie wiele punktów projektowych**,  
każdy punkt odpowiada **jednej instancji algorytmu**.

**Przykład – PSO.**  
Rozważmy algorytm PSO z następującymi ustawieniami:

- rozmiar roju: \(s = 10\),  
- parametr poznawczy: \(c_1 \in [1.5, 2]\),  
- parametr społeczny: \(c_2 = 2\),  
- początkowa waga inercji: \(w_{\max} = 0{,}9\),  
- końcowa waga inercji: \(w_{\text{scale}} = 0\),  
- część iteracji, w których zmniejszamy wagę inercji: \(w_{\text{iter\_scale}} = 1\),  
- maksymalny krok prędkości: \(v_{\max} = 100\).

Ponieważ \(c_1\) może przyjmować **dowolną wartość w przedziale** \([1{,}5, 2]\), ten projekt algorytmiczny zawiera **nieskończenie wiele punktów** (instancji algorytmu).

**Projekt problemowy** obejmuje informacje związane z samym zadaniem optymalizacyjnym, np.:

- dostępny budżet (liczbę ewaluacji funkcji celu),  
- wymiar problemu,  
- zakresy zmiennych, rodzaj ograniczeń itp.

**Eksperymentalny projekt benchmarku** to **połączenie**:

- projektu problemowego,  
- projektu algorytmicznego,  
- oraz **wybranych miar wydajności** (omówionych w sekcji 5).

Badania benchmarkowe zwykle mają **złożone projekty**, bo łączą **wiele projektów problemowych** (różne instancje, klasy problemów) i **wiele projektów algorytmicznych** (różne algorytmy/konfiguracje).

---

### 7.4 Jak wybrać projekt dla badania benchmarkowego? ⁽²⁶⁾

Przy projektowaniu badania benchmarkowego trzeba rozważyć co najmniej następujące kwestie:⁽²⁶⁾

- **Jakie są główne cele eksperymentu?**  
  (zob. sekcja 2)

- **Jaki(e) problem(y) testowy(e) bierzemy pod uwagę i jakie typy instancji wybieramy?**  
  (zob. sekcja 3)

- **Ile algorytmów chcemy przetestować?**  
  (zob. sekcja 4)

- **Ile problemów testowych / klas problemów jest istotnych dla badania?**  
  (zob. sekcja 3)

- **Jak będzie przeprowadzane strojenie (tuning) algorytmów?**  
  (zob. sekcja 4)

- **Jakie procedury walidacji wyników zastosujemy?**  
  (zob. sekcja 5)

- **W jaki sposób będziemy analizować wyniki?**  
  (zob. sekcja 6)

- **Jak przedstawimy wyniki (forma prezentacji)?**  
  (zob. sekcja 8)

- **Jak zapewnimy losowość i jednocześnie powtarzalność eksperymentu?**  
  (zob. sekcja 9)

> ⁽²⁶⁾ W momencie przygotowywania tej wersji pracy jest to **lista wstępna**, którą autorzy planują rozszerzyć w kolejnych wydaniach.

---

### 7.5 Strojenie przed benchmarkiem

Brownlee [2007] podkreśla znaczenie **strojenia parametrów algorytmu przed jego porównywaniem** na benchmarkach. Bartz-Beielstein i Preuss [2010] zwracają uwagę, że:

> porównywanie **algorytmu dostrojonego** z **algorytmem niedostrojonym** jest nieuczciwe  
> i należy takich porównań unikać.

W badaniach benchmarkowych **ustawienia parametrów** mają kluczowe znaczenie, ponieważ w dużym stopniu **determinują uzyskaną wydajność**.

W zależności od:

- dostępności kodu dla porównywanych algorytmów,  
- ilości czasu na poszukiwanie dobrych parametrów,

można zastosować różne strategie, by porównanie było **możliwie sprawiedliwe**:

1. **Najbardziej pożądany przypadek**  
   – dostępny jest **kod wszystkich metod**.  
   Wtedy można:
   - przeprowadzić **osobne strojenie** parametrów dla każdej kombinacji:
     - (algorytm, problem),  
   - użyć np. narzędzi do automatycznej konfiguracji.  
   Następnie w badaniu benchmarkowym porównujemy algorytmy, korzystając z **najlepszych znalezionych ustawień** dla każdego problemu.  
   Dzięki temu każdy algorytm jest testowany **na szczycie swoich możliwości**.

2. **Strojenie częściowe – gdy pełny tuning jest zbyt drogi**  
   Jeśli uruchomienia na danych problemach są **bardzo kosztowne** i pełny proces strojenia jest nierealny, można:

   - zbudować **prosty projekt wypełniający przestrzeń parametrów**, np.  
     - Latin Hypercube Design (LHD),  
     - zbiór punktów o niskiej dyspersji [Matoušek, 2009],  
   - użyć **niewielkiej liczby punktów projektowych i powtórzeń**.

   Taki zabieg:

   - **zmniejsza ryzyko fatalnych konfiguracji**,  
   - z dużym prawdopodobieństwem „wprowadza nas w okolice” (*„into the ball park”* [De Jong, 2007])  
     rozsądnych ustawień parametrów.

   Prawdopodobnie żaden z algorytmów **nie będzie w pełni zoptymalizowany**, ale:

   - porównanie pozostaje **względnie uczciwe**,  
   - żaden algorytm nie jest „przypadkiem ekstremalnie źle dobranym”.

3. **Brak kodu konkurencyjnych metod**  
   Jeżeli dostępny jest jedynie **własny kod** (a nie mamy implementacji konkurencyjnych algorytmów), pozostaje porównywanie z:

   - **parametrami domyślnymi** podawanymi w literaturze, dokumentacji itp.

   Dla nowego algorytmu parametry domyślne można ustalić np. poprzez **wspólne strojenie na całym zbiorze problemów**. Należy jednak wyraźnie zaznaczyć, że:

   - takie porównanie **świadomie rezygnuje** z dobierania parametrów **indywidualnie do poszczególnych problemów**,  
   - podczas gdy w rzeczywistych zastosowaniach często **dokładnie tak byśmy postąpili** (strojenie „pod problem”).

Dlatego autorzy podkreślają, że **uczciwe badanie benchmarkowe**:

- powinno jasno opisywać, **jak strojenie zostało przeprowadzone** (lub dlaczego go nie było),  
- a tam, gdzie to możliwe, **stosować przynajmniej podstawowe, systematyczne strojenie** zamiast przypadkowych wartości parametrów.

### 7.6 Otwarte kwestie

**(O7.1) Najlepsze projekty.**  
Ci sami autorzy (co wcześniej cytowani) traktują projekty typu **LHD (Latin Hypercube Design)** jako domyślny wybór, mimo że dla wielu zastosowań wykazano wyższość innych projektów wypełniających przestrzeń (space-filling) lub opartych na punktach o niskiej dyspersji (low-discrepancy) [Santner i in., 2003]. Pytanie **kiedy** preferować:

- niezależne i jednakowo rozłożone próbkowanie jednostajne (i.i.d. uniform),  
- LHD,  
- zbiory punktów o niskiej dyspersji,  
- inne projekty typu space-filling,  
- bądź zbiory minimalizujące jakieś inne kryterium różnorodności,

pozostaje w dużej mierze **otwarte**.

**(O7.2) Wiele celów.**  
Czasami do oceny jakości projektu (designu) wykorzystuje się **własności funkcji celu**. W związku z tym wciąż nie jest jasne, jak mierzyć jakość w sytuacjach, w których funkcja celu jest **nieznana**. Dodatkowo pojawiają się problemy, gdy przyjmie się **błędne założenia** na temat funkcji celu, np. liniowość. I wreszcie, w **optymalizacji wielokryterialnej (MOO)**, gdzie nie da się wskazać pojedynczej funkcji celu, znalezienie **optymalnego projektu** może być bardzo trudne [Santner i in., 2003].

## 8. Jak prezentować wyniki?

### 8.1 Ogólne zalecenia

W ostatnich latach opublikowano wiele prac zawierających **rekomendacje dotyczące raportowania wyników**. Jak już w 1994 r. zauważyli Gent i Walsh [1994], nawet jeśli uda się uzyskać dobre wyniki w badaniu benchmarkowym, wciąż można popełnić **wiele błędów na etapie ich prezentacji**. Autorzy ci formułują następujące zalecenia:

1. **Prezentuj statystyki.**  
   Stwierdzenia typu „algorytm *a* przewyższa *b*” powinny być **poparte odpowiednimi testami statystycznymi**, takimi jak te opisane w sekcji 6.

2. **Nie „przepychaj” deadlinów.**  
   Nie obniżaj jakości raportu tylko dlatego, że zbliża się termin nadsyłania prac. Warto zainwestować czas w **przemyślane zaplanowanie badań**:  
   - liczba eksperymentów,  
   - portfolio algorytmów,  
   - trudność instancji problemu – wszystko to, jak omawiano w sekcji 7.

3. **Raportuj wyniki negatywne.**  
   Należy **przedstawiać i omawiać instancje problemów, na których algorytmy zawodzą** – jest to kluczowy składnik dobrego raportu naukowego, o czym również mowa w tej sekcji.

Barr i in. [1995] w swojej klasycznej pracy o raportowaniu wyników empirycznych dotyczących heurystyk proponują **luźno zdefiniowaną metodologię** budowy eksperymentu, składającą się z następujących kroków:

1. zdefiniuj **cele eksperymentu**,  
2. wybierz **miary wydajności** i **czynniki**, które będą eksplorowane,  
3. **zaprojektuj i wykonaj** eksperyment,  
4. **przeanalizuj dane** i wyciągnij wnioski,  
5. **zraportuj wyniki eksperymentalne**.

Następnie formułują osiem szczegółowych zaleceń dotyczących raportowania wyników. W skrócie obejmują one:

- zapewnienie **reprodukowalności**,  
- wyspecyfikowanie wszystkich **wpływających czynników** (kod, środowisko obliczeniowe itd.),  
- precyzyjne określenie **mierzonych wielkości**,  
- dokładne wyspecyfikowanie **parametrów**,  
- użycie **statystycznego planowania eksperymentu**,  
- porównanie z **innymi metodami**,  
- redukcję **zmienności wyników**,  
- zapewnienie, że prezentowane wyniki są **wyczerpujące**.

Następnie autorzy ilustrują te zalecenia licznymi przykładami.

---

### 8.2 Metodologie raportowania

Poza ogólnymi rekomendacjami, które stanowią wartościowe wskazówki, **istnieją również kompletne metodologie raportowania wyników**, oparte na podejściu naukowym – np. na **testowaniu hipotez** [Popper, 1959, 1975].

Jedną z takich metodologii zaproponowali Bartz-Beielstein i Preuss [2010]. Proponują oni, aby **prezentację eksperymentów** organizować w siedmiu częściach:

**(R.1) Pytanie badawcze (Research question)**  
Nazwać możliwie krótko to, czym zajmuje się badanie – **(być może bardzo ogólny) cel**, najlepiej w jednym zdaniu. To zdanie służy jako swojego rodzaju **„nagłówek” raportu** i jest powiązane z głównym modelem.

**(R.2) Planowanie przedeksperymentalne (Pre-experimental planning)**  
Podsumowuje **pierwsze – często eksploracyjne – uruchomienia programu**, które prowadzą do sformułowania zadania (R.3) i ustawień (R.4).  
Decyzje dotyczące:

- użytych problemów benchmarkowych,  
- miar wydajności,

powinny być podejmowane w oparciu o dane zebrane w tych **wstępnych uruchomieniach**.  
Raport z planowania przedeksperymentalnego powinien uwzględniać **wyniki negatywne**, np.:

- modyfikacje algorytmu, które nie zadziałały,  
- problem testowy, który okazał się zbyt trudny,

jeśli dostarczają one nowych spostrzeżeń.

**(R.3) Zadanie (Task)**  
Doprecyzowuje **główne pytanie**, formułuje **twierdzenia naukowe** i wynikające z nich **hipotezy statystyczne** do przetestowania.

- Jedno twierdzenie naukowe może wymagać **kilku, a nawet setek hipotez statystycznych**.  
- W przypadku badań **czysto eksploracyjnych** (np. pierwsze testy nowego algorytmu) testy statystyczne mogą nie być stosowalne, ale **zadanie i tak powinno być sformułowane możliwie precyzyjnie**.  

Ten krok jest powiązany z **modelem eksperymentalnym**.

**(R.4) Ustawienia (Setup)**  
Określa:

- **projekt problemu** i **projekt algorytmu**,  
- badany algorytm,  
- parametry sterowalne i stałe,  
- wybraną **miarę wydajności**.

Obejmuje również informacje o **środowisku obliczeniowym** (sprzęt i oprogramowanie, użyte biblioteki i pakiety).  

Informacje w tej części powinny być **wystarczające, by ktoś inny mógł odtworzyć eksperyment**.

**(R.5) Wyniki / wizualizacja (Results/Visualization)**  
Prezentuje:

- **surowe albo przetworzone (filtrowane) dane** z eksperymentów,  
- podstawowe **wizualizacje**, jeśli są pomocne (wykresy, histogramy, wykresy zbieżności itd.).

Ta część jest powiązana z **modelem danych**.

**(R.6) Obserwacje (Observations)**  
Opisuje:

- **odchylenia od oczekiwanych rezultatów**,  
- **nietypowe wzorce** zauważone w danych,

bez subiektywnych ocen i interpretacji. Przykładowo, może mieć sens przyjrzenie się **interakcjom parametrów**. Dodatkowe wizualizacje mogą pomóc zrozumieć, co się dzieje.

**(R.7) Dyskusja (Discussion)**  
Na tym etapie:

- podejmuje się **decyzje dotyczące hipotez** sformułowanych w R.3,  
- formułuje się **koniecznie subiektywne interpretacje** zaobserwowanych zjawisk,  
- umieszcza się wyniki w **szerszym kontekście**.  

Przewodnie pytanie brzmi: **„Czego się nauczyliśmy?”**

Ta metodologia została rozwinięta i dopracowana w pracy Preuss [2015]. Szczególnie ważne jest **oddzielenie części R.6 i R.7**, żeby:

- umożliwić innym wyciąganie **innych wniosków** na podstawie tych samych wyników,  
- jasno rozróżnić to, **co zostało zaobserwowane**, od tego, **jak to interpretujemy**.

To rozróżnienie stopni **rosnącej subiektywności** przypomina propozycje Barra i in. [1995], którzy odróżniają:

- wyniki,  
- ich analizę,  
- oraz wnioski autora eksperymentu.

Warto zauważyć, że wszystkie powyższe elementy **już teraz pojawiają się w dobrych raportach eksperymentalnych**. Zwykle jednak nie są **wyraźnie rozdzielone**, lecz **mieszają się ze sobą**. Dlatego autorzy sugerują, aby **oznaczać te części w tekście etykietami**, co czyni jego strukturę bardziej przejrzystą.

Autorzy rekomendują również **prowadzenie „dziennika eksperymentów”**, zawierającego **pojedyncze raporty** zgodne z powyższym schematem. Umożliwia to:

- późniejsze odwoływanie się do wcześniejszych eksperymentów,  
- lepszy ogląd kolejnych badań,  
- unikanie **powtarzania tych samych testów**, które już kiedyś wykonano,

nawet jeśli pojedyncze eksperymenty **nigdy nie trafią do publikacji**.

---

### 8.3 Otwarte kwestie

**Raportowanie wyników negatywnych** ma wiele zalet, m.in.:

- pokazuje, **co już zostało zrobione i nie działa**, dzięki czemu inni badacze nie powtarzają tych samych błędów,  
- jest cennym narzędziem do **ilustrowania ograniczeń nowych podejść**.

Mimo to, jak dyskutowano także w sekcji 3, **prezentacja wyników negatywnych wciąż nie jest odpowiednio doceniana** w społeczności naukowej (por. Gent i Walsh [1994]).  

Podczas gdy artykuły:

- poprawiające dotychczasowe wyniki eksperymentalne,  
- albo **pokonujące** istniejący algorytm,

są **regularnie akceptowane do publikacji**, prace, które głównie prezentują **wyniki negatywne**, zazwyczaj:

- **nie są przyjmowane** do druku.

To z kolei zniekształca obraz publikowanych badań i utrudnia:

- realistyczną ocenę **ograniczeń metod**,  
- budowanie **kompletnego, niefiltrowanego** obrazu stanu wiedzy w benchmarkingu algorytmów.

## 9. Jak zagwarantować odtwarzalność?

Kwestia **odtwarzalności** (reproducibility) była przedmiotem zainteresowania w eksperymentalnej analizie algorytmów od wielu dekad. Klasyczne prace [Johnson, 2002a] zalecają zapewnianie odtwarzalności, ale jednocześnie ostrzegają, że klasyczne rozumienie odtwarzalności w informatyce (tj. uruchomienie *dokładnie tego samego kodu* na *tej samej maszynie* zwraca *dokładnie te same pomiary*) **znacząco różni się** od rozumienia odtwarzalności w innych naukach eksperymentalnych (tj. *inna implementacja* eksperymentu, przeprowadzona w *podobnych warunkach*, prowadzi do pomiarów, które pozwalają wyciągnąć *te same wnioski*).

Przykładowo, „**Reproducibility guidelines for AI research**”¹, które mają zostać zaadaptowane przez stowarzyszenie AAAI (Association for the Advancement of Artificial Intelligence), są wyraźnie skoncentrowane na **„informatycznym”** rozumieniu odtwarzalności.

Aby jasno zdefiniować różne pojęcia związane z odtwarzalnością, **ACM** rozróżnia następujące poziomy²:

- **Powtarzalność (Repeatability – ten sam zespół, to samo środowisko eksperymentalne)**  
  Pomiar może zostać uzyskany z zadaną precyzją przez **ten sam zespół**, stosujący **tę samą procedurę pomiarową**, **ten sam system pomiarowy**, w **tych samych warunkach pracy**, w **tym samym miejscu**, przy wielokrotnym powtarzaniu doświadczenia.  
  W przypadku eksperymentów obliczeniowych oznacza to, że badacz jest w stanie **wiarygodnie powtórzyć własne obliczenia**.

- **Odtwarzalność (Reproducibility – inny zespół, to samo środowisko eksperymentalne)**  
  Pomiar może zostać uzyskany z zadaną precyzją przez **inny zespół**, stosujący **tę samą procedurę pomiarową**, **ten sam system pomiarowy**, w tych samych warunkach pracy, w tym samym lub innym miejscu, przy wielokrotnym powtarzaniu.  
  Dla eksperymentów obliczeniowych oznacza to, że **niezależna grupa** może uzyskać **ten sam wynik**, korzystając z **artefaktów autora** (kod, dane, konfiguracje).

- **Replikowalność (Replicability – inny zespół, inne środowisko eksperymentalne)**  
  Pomiar może zostać uzyskany z zadaną precyzją przez **inny zespół**, z użyciem **innego systemu pomiarowego**, w **innym miejscu**, przy wielokrotnym powtarzaniu.  
  W eksperymentach obliczeniowych oznacza to, że niezależna grupa może uzyskać **ten sam wynik**, korzystając z artefaktów, które zostały **opracowane całkowicie niezależnie**.

Powyższa klasyfikacja pozwala zidentyfikować **różne poziomy odtwarzalności**, rezerwując termin **„replikowalność”** dla poziomu **najbardziej wartościowego naukowo**, ale też **najtrudniejszego do osiągnięcia**.

Istnieje wiele praktycznych wskazówek i systemów programistycznych, które pomagają zapewnić **powtarzalność** i **odtwarzalność** [Gent et al., 1997; Johnson, 2002a], w tym m.in.:

- systemy kontroli wersji kodu (Subversion, Git),  
- repozytoria danych (np. Zenodo),  
- narzędzia do tworzenia **reprodukowanych dokumentów** (Rmarkdown, Jupyter Notebooks),  
- narzędzia do odtwarzalnych środowisk programistycznych (np. OSF³, CodeOcean, Docker).

Znacznie mniej jasne jest jednak, **jak skutecznie osiągnąć replikowalność**. Aby uzyskać **replikowalne wyniki**, trzeba **zrezygnować z dążenia do dokładnego odtworzenia liczb** i zamiast tego:

- dostarczyć **statystycznych wytycznych**,  
- które są **powszechnie akceptowane w danej dziedzinie**,  
- i które zapewniają **wystarczające dowody** na rzecz danego wniosku,  
- nawet przy **innych, choć podobnych warunkach eksperymentalnych**.

To, co uznamy za „podobne warunki eksperymentalne”, **zależy od konkretnego eksperymentu** – i nie ma tu prostej odpowiedzi, zwłaszcza w kontekście **benchmarkingu algorytmów**.

Jednym z kroków w kierunku lepszej replikowalności jest **preregistracja (przedrejestracja) projektów eksperymentów** [Nosek et al., 2018], tzn.:

- z góry ustalamy **hipotezy** i **plan eksperymentu**,  
- a następnie **trzymamy się** tego planu.

Preregistracja:

- **zmniejsza ryzyko fałszywych rezultatów** wynikających z „dostosowywania analizy do danych”.

Jednak w przypadku **eksperymentów obliczeniowych** znacznie trudniej jest:

- **systematycznie kontrolować adaptacje** w przebiegu eksperymentu,  
- ponieważ – w odróżnieniu od randomizowanych badań klinicznych – takie eksperymenty **łatwo jest wielokrotnie uruchamiać i modyfikować** jeszcze **przed** formalną rejestracją.

> ¹ http://folk.idi.ntnu.no/odderik/reproducibility_guidelines.pdf  
> ² Cytat z: https://www.acm.org/publications/policies/artifact-review-and-badging-current  
> ³ https://osf.io/

---

## 10. Podsumowanie i perspektywy

Niniejsze opracowanie zbiera **idee i rekomendacje** od ponad **tuza badaczy** o różnych profilach i z różnych instytucji na całym świecie. Jego głównym celem jest **promowanie najlepszych praktyk w benchmarkingu**. Obecna wersja jest wynikiem **długich i owocnych dyskusji** w gronie autorów. Uzgodnili oni **osiem kluczowych zagadnień**, które powinny być brane pod uwagę w każdym badaniu benchmarkowym:

1. cele,  
2. problemy,  
3. algorytmy,  
4. miary wydajności,  
5. analiza wyników,  
6. projekt eksperymentu,  
7. prezentacja wyników,  
8. odtwarzalność.

Te tematy określiły **strukturę sekcji** niniejszego artykułu.

Choć tekst ten **nie jest podręcznikiem**, który szczegółowo omawia każde możliwe podejście, autorzy mają nadzieję, że stanowi on **dobry punkt wyjścia** do przygotowywania badań benchmarkowych. Można traktować go jako **przewodnik** (podobny w duchu do słynnego „hitch-hiker’s guide to EC” [Heitkötter i Beasley, 1994]) z **długą listą odsyłaczy**, obejmujących zarówno klasyczne publikacje, jak i najnowsze prace. Każda sekcja przedstawia:

- konkretne rekomendacje,  
- przykłady dobrych praktyk,  
- oraz otwarte problemy.

Jak już wspomniano, niniejsze opracowanie jest **dopiero początkiem pewnej drogi**. Może ono stanowić punkt wyjścia dla wielu działań, które:

- poprawią **jakość badań benchmarkowych**,  
- i w konsekwencji **podniosą poziom badań** w EC i dziedzinach pokrewnych.

Potencjalne **kolejne kroki** obejmują m.in.:

1. **organizowanie tutoriali i warsztatów**,  
2. przygotowanie **materiałów wideo**, które pokazują:
   - jak przygotować eksperymenty,  
   - jak analizować wyniki,  
   - jak raportować najważniejsze wnioski,  
3. udostępnianie **narzędzi programistycznych**,  
4. opracowanie **przejrzystej listy kontrolnej (checklisty)**, szczególnie z myślą o osobach dopiero zaczynających przygodę z benchmarkingiem,  
5. włączanie do każdej sekcji **części dyskusyjnej**, opisującej tematy i idee budzące kontrowersje.

Ostatecznym celem jest dostarczenie **dobrze akceptowanych wytycznych (reguł)**, które mogą być użyteczne dla autorów, recenzentów i innych osób. Przykładowo, rozważmy następującą – wciąż **bardzo wstępną i niepełną** – **listę kontrolną**, która może służyć jako przewodnik dla autorów i recenzentów:

1. **Cele**: czy autorzy jasno określili **powody** przeprowadzenia badania?  
2. **Problemy**: czy wybór instancji problemu jest **dobrze umotywowany i uzasadniony**?  
3. **Algorytmy**: czy porównania obejmują **istotnych konkurentów**?  
4. **Wydajność**: czy wybór miary wydajności jest **adekwatny**?  
5. **Analiza**: czy uwzględniono **standardy statystyczne**?  
6. **Projekt eksperymentu**: czy konfiguracja eksperymentu pozwala na **wydajne i uczciwe** porównania? Jakie kroki poczyniono, aby uniknąć **„wybierania wisienek” (cherry-picking)**?  
7. **Prezentacja**: czy wyniki są **dobrze uporządkowane i wyjaśnione**?  
8. **Odtwarzalność**: czy dane i kod są **dostępne**?

Przejrzyste, powszechnie akceptowane standardy **znacząco poprawią proces recenzji** w EC i dziedzinach pokrewnych. Wspólne standardy mogą również **przyspieszyć** proces recenzowania, ponieważ:

- podniosą **jakość zgłoszeń**,  
- pomogą recenzentom formułować **bardziej obiektywne oceny**.

Co równie ważne, **nie jest intencją autorów** narzucanie konkretnych:

- testów statystycznych,  
- projektów eksperymentów,  
- czy miar wydajności.

Zamiast tego twierdzą oni, że jakość publikacji w EC uległaby poprawie, gdyby autorzy **wyjaśniali**:

- **dlaczego** wybrali daną miarę,  
- **dlaczego** użyli konkretnego narzędzia,  
- **dlaczego** zdecydowali się na określony projekt eksperymentu,

oraz – co równie ważne – **jakie były cele ich badania**.

Choć autorzy starali się uwzględnić **najważniejsze prace**, są świadomi, że **pewne ważne wkłady mogły zostać pominięte**. Ponieważ akceptacja przedstawionych rekomendacji jest kluczowa, autorzy **zapraszają kolejnych badaczy** do dzielenia się wiedzą. Ze względu na to, że dziedzina benchmarkingu **ciągle się rozwija**, artykuł ten będzie **regularnie aktualizowany** i publikowany na arXiv [Bartz-Beielstein et al., 2020]. Zainteresowani czytelnicy mogą skontaktować się z autorami przez adres e-mail projektu:  
**benchmarkingbestpractice@gmail.com**.

Istnieje również szereg innych inicjatyw, których celem jest poprawa standardów benchmarkingu w dziedzinach optymalizacji opartych na zapytaniach (query-based optimization), np.:

- **Benchmarking Network**⁴ – inicjatywa powołana do konsolidacji i stymulowania działań na rzecz benchmarkingu iteracyjnych heurystyk optymalizacyjnych [Weinand et al., 2020].

Zdaniem autorów **rozpoczęcie i utrzymanie takiej publicznej dyskusji** jest bardzo ważne. Być może niniejszy przegląd stawia **więcej pytań niż daje odpowiedzi** – i to jest w porządku. Artykuł kończy się znanym powiedzeniem przypisywanym Richardowi Feynmanowi⁵:

> **„Wolę mieć pytania, na które nie ma odpowiedzi, niż odpowiedzi, których nie można kwestionować.”**

> ⁴ https://www.benchmarking-network.org/  
> ⁵ cytowane w różnych źródłach jako „I would rather have questions that can't be answered than answers that can't be questioned.”

## Podziękowania

Praca ta została zainicjowana podczas seminarium Dagstuhl 19431 *Theory of Randomized Optimization Heuristics*² oraz z wdzięcznością uznajemy wsparcie ośrodka seminariów Dagstuhl udzielone naszej społeczności.

Dziękujemy Carlosowi M. Fonsece za jego istotny wkład i owocne dyskusje, które pomogły nam ukształtować sekcję poświęconą miarom wydajności. Dziękujemy również uczestnikom warsztatów poświęconych benchmarkingowi na konferencjach GECCO 2020 i PPSN 2020 za liczne sugestie dotyczące ulepszenia niniejszej pracy. Dziękujemy także Nikolausowi Hansenowi za przekazanie uwag do wcześniejszej wersji tego przeglądu.

C. Doerr dziękuje za wsparcie regionowi Île-de-France oraz grantowi publicznemu w ramach projektu *Investissement d’avenir*, numer referencyjny ANR-11-LABX-0056-LMH, LabEx LMH.

J. Bossek dziękuje za wsparcie Australian Research Council (ARC), grant DP190103894.

J. Bossek i P. Kerschke dziękują za wsparcie European Research Center for Information Systems (ERCIS).

S. Chandrasekaran i T. Bartz-Beielstein dziękują za wsparcie Ministerstwu Kultury i Nauki Kraju Związkowego Nadrenia Północna-Westfalia (Ministerium für Kultur und Wissenschaft des Landes Nordrhein-Westfalen) w ramach programu finansowania **FH Zeit für Forschung**, grant nr 005-1703-0011 (OWOS).

T. Eftimov dziękuje za wsparcie Słoweńskiej Agencji Badawczej (Slovenian Research Agency) w ramach finansowania podstawowego nr P2-0098 oraz projektu nr Z2-1867.

A. Fischbach i T. Bartz-Beielstein dziękują za wsparcie Federalnemu Ministerstwu Edukacji i Badań Naukowych Niemiec (German Federal Ministry of Education and Research) w ramach programu **Forschung an Fachhochschulen**, grant nr 13FH007IB6 (KOARCH).

W. La Cava jest wspierany przez grant NIH K99-LM012926 przyznany przez National Library of Medicine.

M. López-Ibáñez jest „Beatriz Galindo” Senior Distinguished Researcher (BEAGAL 18/00053), finansowanym przez Ministerstwo Nauki i Innowacji Rządu Hiszpanii.

K. M. Malan dziękuje za wsparcie National Research Foundation of South Africa (grant nr 120837).

B. Naujoks i T. Bartz-Beielstein dziękują za wsparcie ze strony programu H2020 Komisji Europejskiej, H2020-MSCA-ITN-2016 UTOPIAE (umowa grantowa nr 722734), a także DAAD (Niemiecka Centrala Wymiany Akademickiej, German Academic Exchange Service), projekt-ID: 57515062 „Multi-objective Optimization for Artificial Intelligence Systems in Industry”.

M. Wagner dziękuje za wsparcie ze strony projektów ARC DE160100850, DP200102364 oraz DP210102670.

T. Weise dziękuje za wsparcie ze strony National Natural Science Foundation of China, grant 61673359, oraz programu Hefei Specially Recruited Foreign Expert.

Dziękujemy również za wsparcie akcji COST 15140 *Improving Applicability of Nature-Inspired Optimisation by Joining Theory and Practice* (ImAppNIO).

² https://www.dagstuhl.de/19431

---

## Literatura

Poniżej należy umieścić listę pozycji bibliograficznych z oryginalnego artykułu.  
Zazwyczaj **nie tłumaczy się formalnych opisów bibliograficznych** (nazwy czasopism, tytuły artykułów, nazwy konferencji itd.), dlatego najpraktyczniej jest:

- skopiować cały dział **References** z PDF,  
- wkleić go tutaj w niezmienionej formie (można jedynie zmienić nagłówek „References” na „Literatura” lub „Bibliografia”).

Przykładowo:

> **Literatura (References)**  
> Bartz-Beielstein, T. et al. *Benchmarking in Optimization: Best Practice and Open Issues*. arXiv preprint arXiv:2007.XXXX, 2020.  
> … (pozostałe pozycje z oryginalnego PDF)
