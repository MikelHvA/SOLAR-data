Deze branch word gebruikt voor een merge met of main of boat-route-map, zie het als WIP of open Beta. 

Voor stabiliteit gebruik dus niet deze branch. 

KNOW ISSUES: 
- Je kan nog niet meerdere testvaarten met elkaar vergelijken
- De legenda overlapt soms met de data-lijnen. 
- Met sommige matplotlib versies staat alleen de y2 waarde rechtsonder


CHANGELOG 

V1.1

- Toevoegen van factor= , dit maakt simpele berekeningen mogelijk zoals delen door 5 of maal 100, handig voor reductiekast of duty-cycle factor 
- Toevoegen van label_suffix=, wanneer er een factor= is toegepast en deze lijn er ook in staat laat hij alleen de suffix zien. Zie dit als een naamgeving voor de factor.  
- Wanneer een bepaalde kolom meerdere keren word geplot op dezelfde als dan zal deze maar 1 x worden weergegeven.

V1.2

- Toevoegen van de Accu als .csv bestand, Alleen de accu percentage is nu toegevoegd. 
- 