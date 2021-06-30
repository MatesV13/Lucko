# Lucko
Discord bot Lucko koji podupire dohvaćanje zadataka s codeforcesa i praćenje vježbanja članova servera


Setup:

Najprije file secret.bot napunite s potrebnim podacima (uredite ga kao text file)

Stvorite discord server i dodajte bota na njega - jedino nužno ograničenje o izgledu servera je da kako bi koristili GLVforces cog, morate imati kategoriju Prijedlozi s text kanalom main - u njega idu svi ;propose, i u kategoriji se stvaraju prijedlozi.



Što se tiče naredba unutar discord servera:

Koristi ;help <ime naredbe> za više informacija o pojedinoj naredbi

Codeforces
- Naredbe nad javnim codeforces zadatcima

;gimmeCF - Daje nasumičan zadatak s codeforcesa
;findCF - Pronalazi zadatak s javno dostupnih codeforces zadatka
;stalkCF - Provjerava nedavnu aktivnost korisnika


Custom
- Dodaje jednostavne text to text naredbe, prefix je $

;add_cc - Dodaje custom naredbu
;del_cc - Miče custom naredbu
;help_cc - Vraća popis dostupnih naredbi


GLVoni
- Sve naredbe koje podržavaju rad s grupom na codeforcesu i zadatcima u njoj!

;link - Povezuje discord s drugim platformama
;gimmeGLV - Zadaje nasumičan zadatak s GLVforces natjecanja
;findGLV - Pomaže u pronalaženju zadatka s GLVforces natjecanja
;solveGLV - U DM šalje editorial za neko natjecanje.


Speedforces
- Naredbe vezane za korištenje funkcija Speedforcesa

;allSF - Vraća sve dostupne Speedforcese!
;delSF - Briše speedforces po njegovom kodu
;addSF - Stvara novi Speedforces
;startSF - Započinje Speedforces po njegovom kodu
;statusSF - Pokazuje standings za specifičan Speedforces


Lockout
- Naredbe koje podupiru stvaranje Lockout duela!

;del_duel - Briše aktivni duel u kojem si član.
;all_duels - Ispisuje listu aktivnih duela!
;lets_duel - Prihvaća duel protiv drugog korisnika!
;lockout - Stvara duel protiv drugog korisnika


Admin
- Služi uglavnom za administriranje bazama podataka

;problem_info - Vraća sve informacije o zadatku po njegovom izvoru!
;problem_edit - Mjenja podatke zadatka u bazi
;problem_add - Dodaje zadatak u bazu
;problem_del - Briše zadatak iz baze
;add_contest - Povlači zadatke s codeforces natjecanja
;add_editorial - Dodaje editorijal svim zadatcima s istog natjecanje


Debug
- Samo za Admine bota, uglavnom služi za rad s bazama podataka

;debug - Vraća zapisnike sustava
;update_user - Provjerava što su korisnici riješili
;update_data - Gura lokalnu verziju u bazu podataka
;reload - Briše radnu verziju podataka i učitava one iz baze podataka
;update_bot - Aktivira promjene u cogovima
;kill - Gasi bota


GLVforces
- Podrška za Autore natjecanja i predlaganje problema

;propose - Predloži zadatak
;ime - Mijenja ime zadatka
;problem - Mijenja uži tekst zadatka
;tekst - Mijenja tekst zadatka
;ogranicenja - Mijenja ogranicenja zadatka
;rjesenje - Mijenja rješenje zadatka
;zadatak - Vraća izgled zadatka
;end_propose - Kraj predlaganja zadatka
