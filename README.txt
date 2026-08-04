Alle .py bestanden in deze repo werken door de directory te verplaatsen naar de desbetrevende (test)vaart (bijvoorbeeld cd 'C:\Users\NAAM\OneDrive - HvA\CleanMobility - Vaartochten gebruikt voor data analyse\0088 - 20260615T090441 5h0m30s 24.360km Dapperbuurt - Ouderkerk aan de Amstel - Dapperbuurt).
In dit bestand moeten de .csv betanden zitten die je wilt uitlezen (bijvoorbeeld 1_Master_08_05.csv, 5_LoadCell_21_03.csv). 
Wanneer je een error krijgt dat hij het bestand niet kan vinden dubbel check de namen in de map, over de jaren willen de namen
van .csv betanden nog wel eens veranderen. 

Sommige scripts werken niet wanneer alle benodigde bestanden aanwezig zijn, sommige wel. 

Data plot boot.py

CHANGELOG 

V1.1

- Toevoegen van factor= , dit maakt simpele berekeningen mogelijk zoals delen door 5 of maal 100, handig voor reductiekast of duty-cycle factor 
- Toevoegen van label_suffix=, wanneer er een factor= is toegepast en deze lijn er ook in staat laat hij alleen de suffix zien. Zie dit als een naamgeving voor de factor.  
- Wanneer een bepaalde kolom meerdere keren word geplot op dezelfde als dan zal deze maar 1 x worden weergegeven.

V1.2

- Toevoegen van de Accu als .csv bestand, Alleen de accu percentage is nu toegevoegd. 


Limitaties:
- Kan niet verschillende testvaarten vergelijken 
- Kan nog niet loadcell data inladen (WIP)
- Kan alleen tijd op de x-as (Technisch gezien kan je ook andere data op de x-as maar alleen uit de master)
- Factor lijkt niet helemaal te werken 
- De legenda overlapt soms met de data-lijnen
- Met sommige matplotlib versies staat alleen de y2 waarde rechtsonder

Uitleg:
Veel staat in het bestand zelf. Niet alle datalines van datalogformat zitten erin, deze kunnen toegevoegd worden onder kopje veldnamen. 
Zorg wel dat je ditg onder de desbetrevende csv bestand naam doet. (kijk boven bijn CSV_BESTANDEN =)

loadcell uitlezen.py

CHANGELOG

V1
- Je kan de loadcell waarde uitlezen over de tijd 
- Loadcell Newton waarde is zo geplot dat het de stuwkracht typeert. 


Limitaties:
- Kan alleen ten opzichte van de tijd 
- In deze versie is de hefboom in excel verwerkt, er is dus alleen een lineare formule. 

P-v diagram.py 

CHANGELOG

V1
- Mechanisch en elektrisch vermogen wordt over de snelheid geplot
- Elekrisch vermogen trendlijn toegevoegd
- Trendlijn sleeptest verslag TN Quincy en Bono toegevoegd 
- Je kan kiezen tussen snelheid t.o.v. het water en de grond (veld 11 vs 18)

V1.1
- Datapunten hebben nu een kleur op basis van tijd in de datalogger (master). Dit kan uit en aan gezet worden. 

Limitaties:
- Nog geen trendline voor mechanisch vermogen (niet verwarren met de trendlijn van de sleeptest)
- Nog geen filter die uitschieters eruit haalt, hierdoor kan de trendlijn van het elektrisch vermogen soms raar zijn (WIP)