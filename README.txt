Patryk Ożóg 184601

QGraphicsScene (1 pkt) - Zrobione
Dziedziczenie po QGraphicsItem (1 pkt) - Zrobione
Każda bierka musi być kilkalna i przeciągalna, menue na rpm zmieniające grafikę (3 pkt)  Zrobione, ale zmiana grafiki odbywa się poprzez double click
Sterowanie z klawiatury za pomocą notacji szachowej w polu tekstowym (2 pkt) - Działa dla ruchu, jednakże z notacji nie można bić
Grafiki zewnętrzne zaciągane z pliku .rc (1 pkt) - Grafiki zewnętrze są, ale nie z pliku .rc
Zaznaczanie możliwych ruchów (2 pkt) - Zrobione
Reguły gry wliczając roszady, bicie w przelocie, promocję piona, sprawdzanie szacha i mata (3 pkt) - Jest sprawdzanie szacha oraz ograniczenie ruchu na szachu, promocja
Analogowy, klikalny zegar szachowy ze wskazówką milisekundnika (2 pkt) - Zrobione ale nie dla analogowego

Osobista suma punktów 11-12

Program jest podzielony na 3 klasy:
- QGraphicsScene - tutaj inicjowane ogólne zmiany na scenie
- QGraphicsPixmapItem - Odpowiada za generowanie pionków oraz sterowanie
- QGraphicsView - Inicjuje scene

Zaimplementowane został poprawny ruch wszystkich pionków, dodatkowo jest promocja oraz szach. Niestety jeszcze nie zaimplementowałem szach-mat
Podwójny click powoduje zmiane grafiki
Notacja szachowa obsługuje tylko zapisy z "-" np: Qa5-a4 (Królowa z a5 na a4). Niestety nie udało mi się jeszcze zaimplementować bicia używając notacji,
niestety nie mam pojęcia, czemu jedna funkcja do usuwania pionków działa poprawnie a druga nie (były identyczne).
Zaimplementowany został zwykły zegar cyfrowy odmierzający minisekundy. Aby gracz mógł skończyć swoją turę, musi wykonać ruch oraz kliknąć guzik skończenia tury.