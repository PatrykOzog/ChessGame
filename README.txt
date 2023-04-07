Patryk Ożóg 184601

QGraphicsScene (1 pkt) - Zrobione
Dziedziczenie po QGraphicsItem (1 pkt) - Zrobione
Każda bierka musi być kilkalna i przeciągalna, menue na rpm zmieniające grafikę (3 pkt)  Zrobione, ale zmiana grafiki odbywa się poprzez double click
Sterowanie z klawiatury za pomocą notacji szachowej w polu tekstowym (2 pkt) - Zrobione
Grafiki zewnętrzne zaciągane z pliku .rc (1 pkt) - Zrobione
Zaznaczanie możliwych ruchów (2 pkt) - Zrobione
Reguły gry wliczając roszady, bicie w przelocie, promocję piona, sprawdzanie szacha i mata (3 pkt) - Wszystko oprócz mata i bicia w przelocie
Analogowy, klikalny zegar szachowy ze wskazówką milisekundnika (2 pkt) - Zrobione

Osobista suma punktów = 14

Program jest podzielony na 3 klasy:
- AnalogClock(QWidget) - klasa inicjująca zegar analogowy oraz odliczanie czasu
- ChessScene(QGraphicsScene) - tutaj inicjowane ogólne zmiany na scenie
- ChessPiece(QGraphicsPixmapItem) - Odpowiada za generowanie pionków oraz sterowanie
- ChessView(QGraphicsView) - Inicjuje scene

Figurami można dowolnie sterować za pomocą notacji szachowej oraz myszki.
Tura rozpoczyna się od białych, następnie po wykonaniu ruchu użytkownik musi kliknąc przycisk nad swoim zegarem aby zakończyć turę.
Następnie drugi gracz robi dokładnie to samo. W momencie gdy czas na zegarze sie skończy. Program wyświetla zwycięzce i automatycznie zamyka grę.
Każda figura jest tworzona jako osobny item klasy ChessPiece, czyli ma swoją właśną pozycję, kolor i rodzaj co jest bardzo wygodne w klikaniu na poszczególną figurę,
gdyż nie trzeba przeszukiwać całej tablicy w celu znaleziena tej konkretnej na którą klikamy.
Oczywiście jest też pełna tablica wszystkich figur (all_pieces) i ich pozycji, koloru, rodzaju, a także tablica ich "id" (pieces_id). Czyli tablica wywołania klas.
Przy kliknięciu na figurę, generowane są wszystkie możliwe ruchy (possible_moves) dla danego rodzaju a dopiero później te ruchy są uszczuplane i dostosywane do aktualnej sytuacji na planszy.
Niektóre figury mają specjalne zasady takie jak promocja, roszada, pierwszy podwójny ruch piona.
Następnie po puszczeniu figury program sprawdza, czy taki ruch jest możliwy, czy nie zbija, czy nie wykonuje specjalnej zasady i jeżeli nie, to figura przemieszcza się na wkazane miejsce.
Zbite figury trafiają na prawy skraj ekranu, bardzo spodobała mi się taka koncepcja, gdyż gracze będą wiedzieć ile mniej więcej figur zostało już usuniętych z gry.
Zaimplementowana została także zasada szachu, czyli król nie może dowolnie się poruszać, gdy jest szach, trzeba króla zasłonić itp. Na ten moment nie ma mata, ale ogólnie,
gra się skończy gdyż wtedy drugi gracz nie będzie mógł wykonać ruchu i czas mu się skończy.
Zegar ma 3 wskazówki - minut, sekund i milisekund - Ustawiony jest na ten moment na 5 minut i odświerza się co jedną milisekundę.
Kod został także poprawiony trochę sylistyczne od ostatniego razu więc mam nadzieję, że wygląda lepiej.
