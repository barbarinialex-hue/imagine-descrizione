# Coerenza immagini IA

Programma Python ispirato all'esercizio `04_immagini.ipynb`: carichi una foto,
OpenRouter la analizza e il programma restituisce un JSON validato.
Interfaccia desktop e uso da terminale. Python 3.10 o successivo.

## Avvio rapido

1. Installa Python (su Windows seleziona **Add Python to PATH**).
2. Apri il terminale nella cartella del progetto.
3. Esegui:

```sh
python -m pip install -r requirements.txt
python app.py
```

Su Linux potrebbe servire il pacchetto `python3-tk` della distribuzione.
Su Windows Tkinter è incluso nell'installazione standard di Python.

Nella finestra inserisci la chiave ottenuta da https://openrouter.ai/settings/keys,
scegli la foto e premi **Analizza immagine**. La chiave resta in memoria.
Il campo descrizione è facoltativo, per esempio: “Una tazza di caffè su un tavolo”.
Il pulsante **Salva JSON** esporta solo un risultato validato.

## Significato del risultato

- `coerente: true`: nessuna incoerenza evidente e corrispondenza alla descrizione, se fornita.
- `coerente: false`: il modello identifica contraddizioni visibili o una mancata corrispondenza.
- `coerente: null`: non ci sono elementi sufficienti per decidere.
- `descrizione`, `motivazione`, `anomalie`, `limiti`: spiegazione in italiano.

Esempio illustrativo, non risultato di un'analisi reale:

```json
{
  "coerente": true,
  "descrizione": "Una tazza su un tavolo.",
  "motivazione": "Oggetti e prospettiva appaiono compatibili.",
  "anomalie": [],
  "limiti": ["La foto non permette di verificare la provenienza."]
}
```

La coerenza non prova che una foto sia autentica. Uno stile fantastico non è
automaticamente un errore. L'IA può sbagliare anche se il JSON è valido.

## Modelli e privacy

Con modello vuoto, il programma cerca nel catalogo un modello `:free` con input
immagine e `structured_outputs`. Se non c'è, si ferma: nessun passaggio automatico
a pagamento. Puoi indicare manualmente un ID compatibile dal catalogo
https://openrouter.ai/models; verifica costi e disponibilità.
Le quote dei modelli gratuiti possono esaurirsi.

La foto viene inviata a OpenRouter e al provider scelto. I file accettati sono
JPEG, PNG e WebP statici, massimo 10 MB e 20 megapixel. Prima dell'invio il
programma corregge l'orientamento, rimuove i metadati ricodificando e riduce
l'immagine a massimo 1024×1024: dettagli piccoli possono andare persi.
Non caricare immagini riservate. Non pubblicare chiavi API o foto nel repository.
Le immagini non sono salvate dal programma.

Lo schema JSON viene richiesto all'API e controllato anche localmente.
Risposte troncate, rifiuti, JSON malformato e campi errati vengono rifiutati.
Documentazione: https://openrouter.ai/docs/guides/features/structured-outputs

## Terminale

Imposta `OPENROUTER_API_KEY` nel tuo ambiente. Esempio PowerShell:

```powershell
$env:OPENROUTER_API_KEY="la-tua-chiave"
python analisi.py foto.jpg --descrizione "Una tazza sul tavolo"
```

Esempio Linux/macOS:

```sh
export OPENROUTER_API_KEY='la-tua-chiave'
python analisi.py foto.jpg --descrizione 'Una tazza sul tavolo' > analisi.json
```

`--modello ID` seleziona un modello; in alternativa usa `OPENROUTER_MODEL`.
Successo: JSON su stdout e codice uscita 0. Errore: JSON su stderr e codice 1.
Non caricare la chiave su GitHub né inserirla nei file del progetto.

## Test

```sh
python -m unittest discover -s tests -v
```

I test usano risposte simulate: non spendono credito. La verifica reale richiede
una chiave OpenRouter, un modello disponibile e una foto scelta dall'utente.

## Scaricare la repository

```sh
git clone https://github.com/barbarinialex-hue/imagine-descrizione.git
cd imagine-descrizione
python -m pip install -r requirements.txt
python app.py
```

In alternativa usa **Code → Download ZIP** su GitHub, estrai la cartella e
segui le istruzioni di avvio rapido.

## Verifiche eseguite

Cinque test automatici superati. Eseguita anche una chiamata reale a OpenRouter
su un'immagine sintetica con quadrato rosso e cerchio blu: risposta JSON valida.
Questo test verifica il collegamento e il formato, non l'accuratezza su ogni foto.
