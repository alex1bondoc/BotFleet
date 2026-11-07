Open CourseWare
Recent changesLogin
Proiect: Joc 2D - Armada
Pentru partea practică, vă propunem următorul joc în care jucătorul nu apasă nicio tastă în timpul partidei, căci agentul autonom conduce flota, iar un motor de simulare nevăzut și un vizualizator grafic, dezvoltate în paralel, transformă codul lui într-un spectacol.


Proiectul la MPS pe direcția 1 va fi dezvoltat în echipe de 7-8 persoane, valorând un total de 3 puncte, evaluate pe parcursul semestrului, în cadrul laboratorului. Evaluarea se face pe baza livrabilelor prezentate la Milestone-uri.
Idee de bază
Tema propune dezvoltarea unui joc de strategie și optimizare, de tip Halite, distribuit ca aplicație de sine stătătoare cu arhitectură client-server. Jocurile în care participanții nu joacă ei înșiși, ci programează un agent care joacă în locul lor, au o tradiție consolidată. Competiția Halite, organizată de Two Sigma, a cerut participanților să scrie programe care conduc unități pe o hartă, într-o partidă rulată de un motor comun și revăzută apoi într-un vizualizator. Ideea aduce împreună două lumi: pe de o parte, noțiunea clasică de agent, un program care percepe mediul și acționează asupra lui în mod autonom, iar pe de altă parte plăcerea concretă a unui joc de strategie, în care rezultatul poate fi urmărit pe ecran.

Jucătorul nu controlează navele prin acțiuni directe, cu mouse-ul sau cu tastatura. Jocul folosește agenți autonomi, care primesc în fiecare pas starea lumii și răspund cu comenzi pentru fiecare navă a flotei sale. Doi agenți se înfruntă pe o hartă generată procedural cu ajutorul unui seed, strângând resurse, ferindu-se de coliziuni și încercând să ajungă la finalul partidei cu mai multă energie decât adversarul.

Produsul este format din două componente majore:

un motor de simulare (Backend);
un vizualizator grafic interactiv (Frontend).

Rolul de server îl are motorul de simulare, iar rolul de client îl are aplicația grafică; cele două comunică prin fișier și linie de comandă, pe aceeași mașină.


Motorul rulează partida și scrie într-un fișier istoricul ei complet. Vizualizatorul citește acest fișier și îl redă grafic. Singurele lucruri pe care cele două componente le au în comun sunt contractele (căile și modul, regulile) de comunicare, adică protocolul dintre motor și agenți, formatul fișierului de istoric și interfața în linia de comandă a motorului.

Obiective
Proiectul are în vedere cinci mari obiective:

Implementarea unui motor de simulare determinist, care aplică regulile jocului pe pași discreți și rezistă la agenți defectuoși
Implementarea unui client grafic pentru vizualizarea și revederea partidelor, cu controale de redare
Definirea și respectarea unor contracte versionate între componente (protocol, format de istoric, linie de comandă)
Implementarea unor agenți care joacă efectiv, atât de referință, cât și proprii
Organizarea echipei

Accentul proiectului cade pe ciclul de viață al dezvoltării software: livrarea unui produs complet, măsurabil și scalabil, obținută prin definirea clară a interfețelor dintre componente, prin lucrul în sprinturi și prin conducerea unor echipe tehnice de către un manager de proiect care răspunde de arhitectura de nivel înalt, nu de implementarea low-level.


Concepte de bază
Partida. O rulare completă a jocului dintre doi agenți, definită de cele două scripturi, de seed și de parametrii de configurare.
Seed-ul. Un număr întreg din care se generează, cu un algoritm fixat în contract, harta și resursele. Aceelași seed produce întotdeauna aceeași hartă.
Harta. O grilă pătrată de celule, generată simetric pentru cei doi jucători. O celulă poate fi liberă, poate conține un zăcământ de energie (puncte bonus, booster), un obstacol sau o bază.
Baza. Celula de pornire a unui jucător, în care navele predau energia strânsă și în care se construiesc nave noi. Baza nu poate fi distrusă.
Zăcământul. O celulă cu o cantitate de energie care scade pe măsură ce este colectată.
Nava. O unitate mobilă a unui jucător, cu poziție, identificator și încărcătură de energie, limitată de o capacitate maximă.
Pasul de simulare (tick). Momentul discret în care motorul rezolvă comenzile tuturor agenților și actualizează starea jocului. Redarea grafică interpolează între pași.
Comanda. O instrucțiune pe care agentul o dă unei nave sau bazei într-un pas: mișcare într-o direcție, staționare sau construirea unei nave.
Bugetul de mutări. Numărul total de comenzi de mișcare pe care le poate emite un jucător în întreaga partidă. Când bugetul se epuizează, navele rămân pe loc.
Agentul. Un program independent, scris de jucător, care citește starea curentă a mediului și trimite comenzi. Rulează ca proces separat.
Motorul (Backend). Programul în linia de comandă care generează harta, rulează agenții, aplică regulile și scrie istoricul partidei.
Clientul (Frontend). Aplicația grafică care lansează motorul, citește fișierul de istoric și îl redă.
Istoricul partidei. Fișierul standardizat care conține tot ce este necesar pentru a reconstitui partida: antetul, starea inițială, evenimentele fiecărui pas și rezultatul final.
Amprenta de stare. O valoare calculată din starea jocului la fiecare pas și înscrisă în istoric. Servește la verificarea determinismului și la depistarea exactă a pasului în care două rulări încep să difere.
Contractul. Documentul versionat care definește protocolul dintre motor și agenți, formatul istoricului și interfața în linia de comandă a motorului.
Depășirea de timp (timeout). Situația în care un agent nu răspunde în limita alocată. Motorul îl întrerupe fără să își blocheze propria execuție.
Simularea folosește exclusiv numere întregi și este strict deterministă: același seed și aceleași scripturi produc aceeași partidă, pas cu pas, pe orice platformă. Orice situație neacoperită de reguli se rezolvă printr-o regulă adăugată în documentație, nu printr-un comportament implicit.

Mecanici Joc
Jocul se desfășoară pe o hartă reprezentată ca o grilă pătrată, cu latura între 32 și 64 de celule. Harta se generează dintr-o seed (un număr întreg): se produce o jumătate, care este apoi oglindită sau rotită pentru celălalt jucător, astfel încât ambii să aibă aceleași oportunități. O celulă poate fi liberă, poate conține un zăcământ de energie, un obstacol sau o bază. După generare, motorul verifică prin parcurgere că orice zăcământ poate fi atins din ambele baze; dacă nu, se generează determinist o hartă nouă dintr-un seed derivată.

Fiecare jucător pornește cu 1000 de unități de energie în bază și cu o navă. Regulile de bază sunt:

Colectarea: o navă poate transporta cel mult 100 de unități. Nava care rămâne pe loc într-o celulă cu zăcământ colectează, la fiecare pas, o zecime din cantitatea celulei (rotunjită în sus, limitată de spațiul liber din încărcătură). O navă care se mută nu colectează.
Predarea: când nava ajunge pe baza proprie, predă întreaga încărcătură, care se adaugă rezervei jucătorului.
Comenzile: într-un pas, o navă poate primi comandă de mișcare (nord, sud, est, vest) sau de staționare. Baza poate primi comandă de construire (500 de unități), care face să apară o navă nouă pe celula bazei în pasul următor, dacă aceasta este liberă.
Bugetul de mutări: fiecare comandă de mișcare consumă o unitate din bugetul jucătorului; staționarea nu consumă nimic. Când bugetul se epuizează, navele rămân pe loc.
Comenzi invalide: mișcarea într-un obstacol, în afara hărții sau spre baza adversarului este ignorată (nava rămâne pe loc) și este numărată în statistici.
Coliziunile: dacă după mișcare două sau mai multe nave se află în aceeași celulă, toate sunt distruse, indiferent de jucător, iar încărcătura lor se adaugă celulei. Excepție: baza proprie. Schimbul de celule între două nave nu este coliziune.
Sfârșitul partidei: după 500 de pași sau mai devreme, dacă ambii jucători și-au epuizat bugetul de mutări și nicio navă nu mai poate colecta. Scorul este rezerva de energie din bază la final. Departajarea se face, în ordine, după numărul de nave rămase, energia transportată și o regulă fixă documentată.
Ciclul unui pas
Motorul procesează fiecare pas în aceeași ordine, fără nicio excepție, pentru ca rezultatul să fie identic la fiecare rulare:

trimiterea către fiecare agent a stării vizibile a lumii;
citirea comenzilor, în limita de timp alocată;
validarea comenzilor și eliminarea celor invalide;
construirea navelor noi;
mișcarea simultană a tuturor navelor;
rezolvarea coliziunilor;
colectarea de către navele rămase pe loc;
predarea încărcăturilor în baze;
actualizarea bugetelor, calculul amprentei de stare și scrierea evenimentelor în istoric.
Agenți
Un agent este orice program care poate fi lansat din linia de comandă și care respectă protocolul: citește starea pe intrarea sa standard și scrie comenzile pe ieșirea sa standard. Motorul pornește fiecare agent ca proces separat. Se cere un set de pornire pentru agenți în cel puțin două limbaje de programare.

Protocolul se desfășoară astfel:

la început, agentul primește un mesaj de inițializare cu harta statică;
în fiecare pas primește doar starea dinamică (poziția navelor, energia din celule, rezerva bazei) și răspunde cu câte o comandă pentru fiecare navă;
există un semnal de sfârșit și un comportament definit în caz de eroare.
Pentru a proteja motorul, se impun limite de execuție:

fiecare agent are o limită de timp pe pas și o limită de memorie (prima inițializare primește un timp mai generos);
un pas în care agentul nu răspunde la timp este pierdut, iar navele lui rămân pe loc;
după trei depășiri consecutive, agentul este exclus din partidă, iar simularea continuă;
un răspuns malformat sau cu comenzi invalide nu oprește partida: comenzile invalide sunt ignorate și numărate;
un agent exclus rămâne în istoric, cu motivul și pasul excluderii.
Fiecare echipă trebuie să livreze cel puțin un agent de referință funcțional, folosit la demonstrații și la teste. Agenții se presupun de încredere (limitele apără motorul de erori, nu de cod ostil).

Arhitectura sistemului
Vedere de ansamblu
Pentru a simula un mediu de producție real, arhitectura este decuplată. Clientul lansează motorul ca proces separat și așteaptă terminarea lui. Motorul lansează la rândul lui cei doi agenți ca procese copil și comunică cu ei prin fluxurile standard. La sfârșit, motorul scrie fișierul de istoric, iar clientul îl încarcă și îl redă. Între client și motor nu există nicio legătură persistentă, nicio memorie comună și niciun apel direct de funcții: totul trece prin fișier și prin linia de comandă.

Motorul (Backend)
Motorul este nucleul jocului. Este un program în linia de comandă, care primește scripturile jucătorilor, seed-ul și parametrii, generează harta procedural și procesează logica fizică: mișcarea, coliziunile, colectarea și predarea resurselor. Se asigură că simularea este strict deterministă pe pași și că un agent defectuos nu îi poate bloca execuția. La final, exportă istoricul partidei într-un format standardizat.

Clientul (Frontend)
Clientul este interfața cu utilizatorul și modulul de randare. Conține un meniu principal, alegerea scripturilor și a seed-ului, lansarea motorului, vizualizatorul de partide și controalele media pentru reluare: Play, Pause, pasul următor, viteze multiple și derulare pe un timeline. Opțional, mai poate conține un editor de text integrat pentru scrierea agenților.

Contractele de comunicare
Protocolul motor-agent. Definește exact mesajele de inițializare, forma stării trimise în fiecare pas, forma comenzilor, semnalul de sfârșit și comportamentul în caz de eroare.
Formatul istoricului. Definește antetul cu versiunea formatului, seed-ul, parametrii și numele agenților, starea inițială, evenimentele fiecărui pas, amprentele de stare și rezultatul final.
Interfața motorului în linia de comandă. Definește argumentele acceptate, codurile de ieșire și locul în care se scrie fișierul rezultat.
Statistici Măsurabile
Pe lângă dezvoltarea jocului se are în vedere și măsurarea unor metrici, atât ale produsului, cât și ale echipei. Se propun următoarele.

Metrici de joc (pe seturi de seed-uri):

scorul final și distribuția scorurilor
energia strânsă în timp, pentru fiecare jucător
numărul de nave rămase la final
numărul de coliziuni
numărul de comenzi invalide
numărul de depășiri de timp și de agenți excluși pe partidă
timpul de execuție al fiecărui agent
Metrici ale produsului:

timpul mediu de execuție al motorului pentru o partidă completă de 500 de pași (țintă: sub 2 secunde, fără a socoti timpul agenților)
numărul de cadre pe secundă ale clientului, mediu și minim, pe hărți de dimensiuni diferite (țintă: minim 30)
rata de succes a verificatorului de determinism (proporția seed-urilor pentru care două rulări produc aceleași amprente)
rata de succes a fișierelor de istoric acceptate de client și numărul de blocaje la integrare
Metrici ale echipei:

numărul de tichete (task-uri și defecte) rezolvate per sprint, pe Frontend și Backend
viteza echipei pe sprinturi și evoluția graficului burndown, comparate cu planul din diagrama Gantt
timpul scurs între raportarea și închiderea unui blocaj de comunicare între echipe
Livrabile
Pentru ca proiectul să fie considerat complet, fiecare echipă va trebui să prezinte următorul set de livrabile detaliat mai jos.

Se urmărește ca soluția software să fie dezvoltată în mod continuu în cadrul materiei, fiind țintit un progres constant, cu modificări majore o dată la cel mult două săptămâni. Soluțiile implementate pe ultima sută de metri vor fi depunctate în mod substanțial.

Funcționalități obligatorii (must-have)
Motor backend determinist, care primește două scripturi și un seed și simulează pașii de joc până la epuizarea bugetului de mutări sau până la limita de pași.
Generatorul procedural de hărți, simetric, verificat prin parcurgere și controlat exclusiv de seed.
Protocolul motor-agent prin fluxurile standard, împreună cu un set de pornire pentru agenți în cel puțin două limbaje.
Definirea și implementarea unui format de fișier standardizat, versionat, pentru istoricul complet al unei partide.
Client frontend cu interfață grafică, capabil să încarce fișierul de istoric și să redea grafic navele, harta și colectarea resurselor.
Controale de bază pentru redare: Pause, Pasul următor, Viteză x2 și x4 și derulare pe timeline.
Fluxul complet în client: alegerea a două scripturi locale, a unei semințe, lansarea motorului și deschiderea automată a rezultatului.
Întreruperea unui agent (timeout) care consumă prea multe resurse, fără blocarea motorului.
Amprentele de stare și un verificator de determinism care compară două rulări.
Suita de teste de integrare dintre client și server și tabloul de bord al proiectului, cu tichete, diagrama Gantt și graficul burndown.
Funcționalități opționale (nice-to-have)
Editorul de cod integrat. Direct în client, cu evidențierea sintaxei la nivel de bază.
Modul Campanie. Niveluri prestabilite, cu semințe fixe, în care adversarii AI au dificultate crescătoare.
Redare grafică avansată. Efecte de particule la coliziuni, urme ale navelor și animații ale colectării.
Grafice de analiză. Energia strânsă în timp, hărți de căldură ale ciocnirilor și ale zonelor vizitate.
Rularea în lot. Un modul în linia de comandă care joacă sute de partide pe seed-uri diferite și adună statistici.
Clasament. Un sistem de evaluare a agenților pe baza rezultatelor partidelor, de tip TrueSkill.
Agent controlat manual. Un mod în care jucătorul poate prelua temporar comenzile navelor, pentru încercări rapide.
Mai multe dimensiuni de hartă și variante de reguli, definite prin fișiere de configurare.

tl;dr;
Ce trebuie să poată arăta echipa la milestone-uri, în mare:

fluxul complet: deschiderea executabilului, selectarea a două scripturi locale și a unui seed ales și generarea meciului;
rularea în direct a vizualizatorului grafic, cu Play, Pause, pasul următor, viteze multiple și derulare pe timeline;
prezentarea arhitecturii de interfațare, adică modul în care Backend-ul independent comunică cu Frontend-ul grafic, prin protocol, prin fișier și prin linia de comandă, și dovada practică a decuplării, prin închiderea forțată a clientului în timpul unei rulări;
verificarea determinismului: același seed rulată de două ori, cu aceleași amprente;
o trecere în revistă a managementului de proiect: diagrama Gantt, provocările apărute pe parcurs și felul în care au fost rezolvate blocajele de comunicare dintre membrii echipei.

Documentație
Pe partea de documentație se doresc următoarele componente:

Repository pe Git cu README și/sau Wiki asociat care conține membrii echipei, rolurile lor, limbajele de programare utilizate, soluții externe, metodologia de dezvoltare aleasă și documentele menționate în continuare
Contractele versionate (protocol motor-agent, format de istoric, interfață linie de comandă) și regulile suplimentare adăugate pentru situațiile neacoperite
Document Design Software (SDD)
Planificare echipă/sarcini (ex: Diagramă Gantt, Kanban, Scrum Board, timeline, graficul burndown etc.)
Plan comunicare - minute întâlniri (decizii, acțiuni, responsabili, termene)
Rapoarte testare
Se punctează respectarea rolurilor în echipă, a sarcinilor planificate, și a timpilor estimați pentru fiecare sarcină.

Limitări
Produsul rulează local. Motorul și clientul rulează pe același calculator. Nu se cere un server public, conturi de utilizator, meciuri în rețea sau un sistem de găzduire a agenților trimiși de alte persoane.
Agenții se presupun de încredere. Limitele de timp și de memorie apără motorul de erori, nu de cod ostil, iar izolarea completă a codului nesigur nu face parte din temă.
Regulile, grafica și formatele sunt concepute original de echipă; nu se reproduc regulile, imaginile sau formatele de fișier ale altor competiții.
Grafica poate fi simplă, în două dimensiuni. Accentul cade pe corectitudine, pe contracte și pe integrare, nu pe realismul imaginii.
Editorul de cod integrat, modul Campanie și efectele grafice avansate sunt opționale și nu pot fi motiv de întârziere a produsului minim viabil.
Calendar
MPS Need to Know
Reguli generale și notare
Laboratoare
Laborator 1 - Introducere
Laborator 2 - Rolurile în echipă. Redactarea specificațiilor de proiect.
Laborator 3 - Mijloace de organizare a proiectului. Controlul versiunii
Laborator 4 - Utilitare pentru managementul și dezvoltarea proiectelor software
Laborator 5 - Comunicarea în cadrul proiectului
Laborator 6 - Monitorizarea, evaluarea și controlul evoluției proiectului
Laborator 7 - Documentație. Patterns. Modele de dezvoltare. Evaluarea rezultatelor proiectului.
Laborator 8 - Integrare
Laborator 9 - Testarea si asigurarea calitatii unui proiect
Laborator 10 - Conducere, motivare, inteligență emoțională
Laborator 11 - Tehnici de prezentare
Laborator 12 - Laborator final
Proiect
Proiect
Table of Contents
Proiect: Joc 2D - Armada
Idee de bază
Obiective
Concepte de bază
Mecanici Joc
Ciclul unui pas
Agenți
Arhitectura sistemului
Vedere de ansamblu
Motorul (Backend)
Clientul (Frontend)
Contractele de comunicare
Statistici Măsurabile
Livrabile
Funcționalități obligatorii (must-have)
Funcționalități opționale (nice-to-have)
Documentație
Limitări
mps/proiect.txt · Last modified: 2026/10/21 12:25 by giorgiana.vlasceanu
Old revisionsMedia ManagerBack to top
CC Attribution-Share Alike 3.0 Unported www.chimeric.de Valid CSS Driven by DokuWiki do yourself a favour and use a real browser - get firefox!! Recent changes RSS feed Valid XHTML 1.0
