# Aplicație de Chat UDP

O aplicație simplă de chat care utilizează protocolul UDP pentru comunicare între utilizatori pe rețeaua locală.

## Descriere

Această aplicație permite comunicarea între mai mulți utilizatori prin mesaje UDP direct, fără a utiliza un server central. Aplicația folosește porturile în intervalul 45000-45009, permițând până la 10 utilizatori simultani.

## Utilizare

Pentru a porni aplicația, rulați:

```
python udp_chat.py <numeutilizator>
```

Unde `<numeutilizator>` este numele cu care doriți să apăreți în chat.

## Comenzi disponibile

- **Mesaj normal**: Scrieți mesajul și apăsați Enter pentru a-l trimite tuturor
- **/p utilizator mesaj**: Trimite un mesaj privat utilizatorului specificat
- **/list**: Afișează lista utilizatorilor conectați
- **/refresh**: Actualizează lista de utilizatori
- **/quit**: Închide aplicația

## Funcționalități

- Descoperire automată a utilizatorilor
- Mesaje de grup (către toți utilizatorii)
- Mesaje private (către un utilizator specific)
- Detectarea utilizatorilor care se conectează sau se deconectează
- Eliminarea automată a utilizatorilor inactivi

## Exemplu de utilizare

1. Deschideți un terminal și rulați:
```
python udp_chat.py Ana
```

2. Deschideți un alt terminal și rulați:
```
python udp_chat.py Mihai
```

3. Acum utilizatorii pot comunica între ei:
   - Ana poate trimite un mesaj general tastând: `Salut tuturor!`
   - Mihai poate trimite un mesaj privat către Ana tastând: `/p Ana Salut, Ana!`
   - Oricare dintre utilizatori poate verifica cine este conectat tastând: `/list`

## Note

- Aplicația funcționează doar în rețeaua locală
- Nu există criptare pentru mesaje
- Fiecare utilizator trebuie să aibă un nume unic
- Aplicația folosește un sistem de heartbeat pentru a detecta utilizatorii activi
