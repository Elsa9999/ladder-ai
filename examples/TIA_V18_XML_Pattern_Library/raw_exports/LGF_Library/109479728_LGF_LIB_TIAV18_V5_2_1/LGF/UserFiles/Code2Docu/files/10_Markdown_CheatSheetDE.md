
# MarkDown Syntax (Cheat Sheet)

In diesem Kapitel sind die Beispiele für die unterstützen MarkDown-Sprachbefehle aufgeführt und es gibt einen kurzen Überblick der unterstützten Syntax.

## Kapitel / Überschriften / Titel

Überschriften werden bis zur 5. Ordnung unterstützt und mit vorangestellten `#` eingeleitet.  
Die ersten drei Überschriften sind nummeriert. Die Überschriften vierter und fünfter Ordnung entsprechen in Word dem Blocktitel, wobei die Überschrift fünfter Ordnung mit ins Inhaltsverzeichnis übernommen wird.

```plaintext
# Überschrift erster Ordnung
## Überschrift zweiter Ordnung
### Überschrift dritter Ordnung
#### Überschrift vierter Ordnung (Block Titel)
##### Überschrift fünfter Ordnung (Block Title inkl. Inhaltsverzeichnis)
```

## Absätze / Zeilenumbrüche

Um mit Markdown einen Absatz zu erzeugen, schreiben Sie einfach einen beliebig langen Text. Die Zeile davor und die Zeile danach müssen leer sein.

Einfache Zeilenumbrüche werden am Zeilenende mit zwei Leerzeichen vor dem Zeilenumbruch selbst erzeugt, oder mit einem hartem Zeilenumbruch am Zeilenende `\`.  
Ohne diese Leerzeichen wird der Zeilenumbruch nicht als solcher erkannt, er kann daher in der MarkDown Quelle zur einfachen Strukturierung genutzt werden.

## Horizontale Linie und Seitenumbruch

Horizontale Linien werden mit drei Bindestrichen `---` erstellt.

**Darstellung**

---

Seitenumbrüche werden mit sechs Bindestrichen `------` erstellt.

---

Hinweis
:    Vor oder nach Abbildungen, Listen, Tabellen, Hinweisboxen, Mathematischen Blöcken oder Code Blöcken erzeugen drei Bindestriche `---` eine Leerzeile.

#### Beispiel

```plaintext
Text vorher

---

Bild, Liste, Tabelle, Hinweisbox, Formel Block oder Code Block

---

Text danach
```

------

## Textformatierungen

Mit Markdown können Sie folgende Textformatierungen verwenden:

| Formatierung                                       | Darstellung                                        |
| -------------------------------------------------- | -------------------------------------------------- |
| Dieser Text ist \*Kursiv\*                         | "Dieser Text ist *Kursiv*"                         |
| Dieser Text ist \_Kursiv\_                         | "Dieser Text ist _Kursiv_"                         |
| Dieser Text ist \*\*ist FETT \*\*                  | "Dieser Text ist **FETT**"                         |
| Dieser Text ist \_\_ist FETT\_\_                   | "Dieser Text ist __FETT__"                         |
| Dieser Text ist \*\*\*FETT und Kursiv\*\*\*        | "Dieser Text ist ***FETT und Kursiv***"            |
| Dieser Text ist \_\*\*FETT und Kursiv\*\*\_        | "Dieser Text ist _**FETT und Kursiv**_"            |
| Dieser Text ist \~\~durchgestrichen\~\~            | "Dieser Text ist ~~durchgestrichen~~"              |
| Dieser Text ist \~tiefgestellt\~                   | "Dieser Text ist ~tiefgestellt~"                   |
| Dieser Text ist \^hochgestellt\^                   | "Dieser Text ist ^hochgestellt^"                   |
| Dieser Text ist \=\=gelb hinterlegt / markiert\=\= | "Dieser Text ist ==gelb hinterlegt / markiert=="   |

## Listen / Aufzählungen

Markdown unterstützt sortierte und unsortierte Listen (Aufzählungen).  

#### Unsortierte Listen

Unsortierte Listen erstellen Sie mit einem Sternchen gefolgt von einem Leerzeichen. Die Einrückung einer untergeordneten Liste erreichen Sie mit drei Leerzeichen. 

```plaintext
* Unsortierte Liste mit Verschachtelung
   1. Einfache untergeordnete sortierte Liste
   2. weiterer Listeneintrag
* zweiter unsortierter Listeneintrag
```

---

**Darstellung**

* Unsortierte Liste mit Verschachtelung
   1. Einfache untergeordnete sortierte Liste
   2. weiterer Listeneintrag
* zweiter unsortierter Listeneintrag

#### Sortierte Listen

Sortierte Listen erstellen Sie mit einer Nummer gefolgt von einem Punkt und einem Leerzeichen.

```plaintext
1. Einfache sortierte Liste mit Verschachtelung
   * unsortierte untergeordnete Liste
   * zweiter Listeneintrag
2. weiterer Listeneintrag
```

---

**Darstellung**

1. Einfache sortierte Liste mit Verschachtelung
   * unsortierte untergeordnete Liste
   * zweiter Listeneintrag
2. weiterer Listeneintrag

------

## Eingerückter Text / Block Quote / Zitate

Einen eingerückten Text für z.B. Zitate erhalten Sie mit `>` gefolgt von einem Leerzeichen.

```plaintext
> Block Quote  
zweite Zeile im Zitat
```

---

**Darstellung**

> Block Quote  
zweite Zeile im Zitat

## Inline-Code

`Inline-code` erzeugen Sie mit umgebenden Back-ticks \`code\`.

## Code Block

Einen Code Block fügen Sie mit drei vorangestellten und abschließenden Back-ticks oder Tilden, zusammen mit dem Kürzel der Programmiersprache ein, z.B. `SCL`:

~~~plaintext
```scl
stringVariable := 'code with syntax highlighting';
FunctionCall(stringVariable);
```
~~~

---

**Darstellung**

```scl
stringVariable := 'code with syntax highlighting';
FunctionCall(stringVariable);
```

## Mathematische Formeln

Mathematische Formeln können mit der Schreibweise aus LaTeX / TexMath generiert werden.

Das ist ein Inline $math block$, umgeben von `$` - `$math block$`.

`$\int_0^\infty \frac{x^3}{e^x-1}\,dx = \frac{\pi^4}{15}$`

**Darstellung**

$\int_0^\infty \frac{x^3}{e^x-1}\,dx = \frac{\pi^4}{15}$

```plaintext
$$
  \int_0^\infty \frac{x^3}{e^x-1}\,dx = \frac{\pi^4}{15}
$$
```

---

**Darstellung**
$$
  \int_0^\infty \frac{x^3}{e^x-1}\,dx = \frac{\pi^4}{15}
$$

---

Hinweis
:    Es ist ebenso möglich, Mathematische Formeln in Form von Bildern einzubinden, anstatt mit LaTeX Skripten zu arbeiten.

------

## Hyperlink

Hyperlinks können Sie ohne und mit Linktext in eckigen Klammern erstellen.

Direkter Hyperlink:  
`https://support.industry.siemens.com`

**Darstellung**

https://support.industry.siemens.com

Hyperlink mit Linktext:  
`[gehe zu SIEMENS Industry Support](https://support.industry.siemens.com)`

**Darstellung**

[gehe zu SIEMENS Industry Support](https://support.industry.siemens.com)

**Leerzeichen im Dateinamen oder Pfad**

Relative Hyperlinks, die Leerzeichen enthalten, können zwischen `<` und `>` Zeichen angegeben werden:

`[LCode2Docu_DemoType_FC.htm](<../../../../../code2doc_demo/UserFiles/UserDocumentation/en-US/Library Types/LCode2Docu_DemoType_FC.htm>)` 

--- 

Hinweis
:    Relative Pfade können nur in HTML aber nicht in Word- oder PDF-Dokumenten als Hyperlink dargestellt werden.  

------

## Grafiken / Bilder (Abbildungen)

Grafiken und Bilder, die in der Dokumentation verwendet werden sollen, speichern Sie innerhalb der TIA Portal-Projektstruktur im Ordner `\UserFiles\Code2Docu\images\`.

Bilder können auch komplett außerhalb des Projektordners abgelegt werden und werden dann in den Ordner `images` kopiert. Den externen Bildordner können Sie in den `Settings` konfigurieren. Weiterführende Informationen hierzu finden Sie im Kapitel `Dialogfenster Einstellungen / Code2Docu Optionen`.

Sie können sowohl im `images` Ordner als auch im konfigurierten externen Bildordner PowerPoint Präsentationen ablegen. Die Folien der Präsentationen werden als Bilddateien im `png`-Format exportiert und im Ordner neben der Präsentation abgelegt. Die Dateinamen der exportierten Bilder sind nach dem Schema `NameDerPräsentation_FolienNummer.png` aufgebaut. Besteht die Präsentation nur aus einer einzigen Folie, dann entfällt der Unterstrich und die Foliennummer.

Um Bilder in die Dokumentation einzubinden, verwenden Sie folgende Syntax:

`![ALT-Text] (Pfad/Bild.PNG "optionaler Titel")`

In den eckigen Klammern geben Sie das alt-Attribut an. In den runden Klammern geben Sie den relativen Pfad unter Verwendung des Schrägstrichs `/` zum Bild an. Dadurch ist es auch möglich Bilder in Unterverzeichnissen zu gruppieren. Optional können Sie noch einen Titel in Anführungszeichen angeben.

---

Hinweis
:    Es werden folgende Dateiformate für Grafiken und Bilder unterstützt:  
`png`, `jpg`, `bmp`, `svg`
:    Leerzeichen im Bildernamen oder Pfad sind zu vermeiden.

#### Beispiele

Bild mit Text eingerückt (Textbreite):

`![Code2Docu Grafik](subFolder/Code2Docu_ProcessFlow.PNG "Code2Docu - Prozessfluss")`

**Darstellung**

![Code2Docu - Prozessfluss](subFolder/Code2Docu_ProcessFlow.PNG "Code2Docu - Prozessfluss")

------

Bild über die volle Seitenbreite mit Attribut `{.pageWidth}` in der Zeile vor dem Bild:

```plaintext
{.pageWidth}
![Code2Docu Grafik](subFolder/Code2Docu_ProcessFlow.PNG "Code2Docu - Prozessfluss")
```

---

**Darstellung**

{.pageWidth}
![Code2Docu - Prozessfluss](subFolder/Code2Docu_ProcessFlow.PNG "Code2Docu - Prozessfluss")

------

## Tabellen

Für eine übersichtliche Anordnung von Daten und Texten können Sie Tabellen einsetzen.

### Einfache Tabelle (Pipe Table)

Pipe Tables erstellen Sie aus vertikalen Strichen `|` und Bindestrichen `-` sowie den Texten. Mit Doppelpunkten `:` im Trenner zwischen Kopfzeile und den restlichen Zeilen können Sie die Ausrichtung des Textes festlegen.

Tabelle eingerückt mit dem Text:  

```plaintext
| Tabellen      | sind          | toll  |
| ------------- |:-------------:| -----:|
| spalte 1 ist  | links bündig  |   456 |
| spalte 2 ist  | zentriert     |   123 |
| spalte 3 ist  | rechts bündig | 0815  |
```

---

**Darstellung**

| Tabellen      | sind          | toll  |
| ------------- |:-------------:| -----:|
| spalte 1 ist  | links bündig  |   456 |
| spalte 2 ist  | zentriert     |   123 |
| spalte 3 ist  | rechts bündig | 0815  |

---

Tabelle über die volle Seitenbreite ohne Einrückung mit vorangestelltem Attribut `{.pageWidth]`:

```plaintext
{.pageWidth}
| Tabellen      | sind          | toll  |
| ------------- |:-------------:| -----:|
| spalte 1 ist  | links bündig  |   456 |
| spalte 2 ist  | zentriert     |   123 |
| spalte 3 ist  | rechts bündig | 0815  |
```

---

**Darstellung**

{.pageWidth}
| Tabellen      | sind          | toll  |
| ------------- |:-------------:| -----:|
| spalte 1 ist  | links bündig  |   456 |
| spalte 2 ist  | zentriert     |   123 |
| spalte 3 ist  | rechts bündig | 0815  |

---

Hinweis
:    Tabellen sind immer als eigenständige Absätze zu betrachten, d.h. dass vor und nach einer Tabelle immer eine Leerzeile vorhanden sein muss.

------

### Komplexe Tabelle (Grid Table)

 Grid Tables (Gittertabellen) verwenden zusätzlich das Plus-Zeichen `+` und Gleichheitszeichen `=`. Mit dem Plus-Zeichen definieren Sie die Knotenpunkte der Gitterlinien und mit dem Gleichheitszeichen die Abtrennung zwischen Kopfzeile und den restlichen Zeilen. Gittertabellen erlauben mehrere Zeilen pro Zelle sowie eine Zelle über mehrere Spalten zu verbinden. 
 
 Die folgende Abbildung zeigt Ihnen eine einfache Rastertabelle:

```plaintext
+---------+---------+
| Header  | Header  |
| Column1 | Column2 |
+=========+=========+
| 1 ab    | the second column 
| 2 cde   | 
| 3 f     |
+---------+---------+
| Second row spanning
| on two columns
+---------+---------+
| Back    |         |
| to      |         |
| one     |         |
| column  |         | 
```

---

**Darstellung**

+---------+---------+
| Header  | Header  |
| Column1 | Column2 |
+=========+=========+
| 1 ab    | the second column 
| 2 cde   | 
| 3 f     |
+---------+---------+
| Second row spanning
| on two columns
+---------+---------+
| Back    |         |
| to      |         |
| one     |         |
| column  |         | 

---

#### Regeln

* Vor einer Tabelle muss eine Leerzeile stehen, und die Tabelle muss anschließend mit dem Spaltentrennzeichen `+` beginnen.
* Jeder Spaltentrenner beginnt mit einem optionalen Leerzeichen...
  * gefolgt von einem optionalen `:` zur Angabe der Linksausrichtung, gefolgt von optionalen Leerzeichen (die Ausrichtung kann in der ersten Zeile angegeben werden) 
  * gefolgt von einer Folge von mindestens einem `-` Zeichen, gefolgt von optionalen Leerzeichen
  * gefolgt von einem optionalen `:` zur Angabe der rechten Ausrichtung (oder der mittleren Ausrichtung, wenn auch die linke Ausrichtung definiert ist)
  * gefolgt von optionalen Leerzeichen

* Ein Tabellenkopf wird mit `+========+` statt mit `+---------+` getrennt.
* Auf das erste Zeilentrennzeichen muss eine *reguläre Zeile* folgen. 
* Eine reguläre Zeile muss mit dem Zeichen `|` beginnen, das an der gleichen Position wie der Spaltentrenner `+` des ersten Zeilentrenners beginnt.
* Eine reguläre Zeile kann eine vorhergehende reguläre Zeile fortsetzen, wenn die Spaltentrennzeichen `|` an der gleichen Position stehen, wie die vorherige Zeile. Wenn sie an der gleichen Stelle stehen, kann sich die Spalte über mehrere Spalten erstrecken.
* Das letzte Spaltentrennzeichen `|` kann weggelassen werden.
* Eine Tabelle darf keine unregelmäßig geformten Zellen haben.
* Die jeweilige Breite der Spalten errechnet sich aus dem Verhältnis der Gesamtgröße der ersten Tabellenzeile ohne Berücksichtigung des `+`:  
`+----+--------+----+` würde in `4/16 = 25%, 8/16 = 50%, 4/16 = 25%` aufgeteilt werden.

---

Eine Gitter-Tabelle kann Zellen besitzen, die sich über Spalten als auch über Zeilen erstrecken.

```plaintext
+---+---+---+
| AAAAA | B |
+---+---+ B +
| D | E | B |
+ D +---+---+
| D | CCCCC |
+---+---+---+
```  

---

**Darstellung**

+---+---+---+
| AAAAA | B |
+---+---+ B +
| D | E | B |
+ D +---+---+
| D | CCCCC |
+---+---+---+

---

Eine Zelle kann sowohl über Spalten als auch über Zeilen verbunden sein.

```plaintext
+---+---+---+
| AAAAA | B |
+ AAAAA +---+
| AAAAA | C |
+---+---+---+
| D | E | F |
+---+---+---+
```  

---

**Darstellung**

+---+---+---+
| AAAAA | B |
+ AAAAA +---+
| AAAAA | C |
+---+---+---+
| D | E | F |
+---+---+---+  

------

## Hinweis Boxen

Hinweisboxen erzeugen Sie folgendermaßen:  
Die erste Zeile beginnt in einem eigenen Absatz und enthält das Schlüsselwort. Die zweite Zeile beginnt mit einem Doppelpunkt `:` und VIER Leerzeichen. Danach folgt der Text über mehrere Zeilen. Den Abschluss bildet als Begrenzung eine Leerzeile gefolgt von einer horizontale Line `---` die im Dokument nicht sichtbar ist.

Eine Leerzeile vor der Hinweisbox kann ebenfalls mit `---` und einer Leerzeile vor der Box generiert werden.

Die Schlüsselwörter sind (Deutsch / Englisch):

* Hinweis / NOTE
* Achtung / NOTICE
* Vorsicht / CAUTION
* Warnung / WARNING
* Gefahr / DANGER
* ReadMe / LiesMich

---

```plaintext

---

Hinweis
:    zeigt auf einen möglichen Vorteil hin. Hat Tipp-Charakter.
:    Neue Zeile in der Box.

---
```

---

**Darstellung**

Hinweis
:    Hinweis zeigt auf einen möglichen Vorteil hin. Hat Tipp-Charakter
  
---
  
ACHTUNG
:    **Welche Gefahr besteht?**
:    Was droht bei Missachtung der Gefahr?
:    Wie kann die Gefahr vermieden werden?

---
  
VORSICHT
:    **Welche Gefahr besteht?**
:    Was droht bei Missachtung der Gefahr?
:    Wie kann die Gefahr vermieden werden?
  
---
  
WARNUNG
:    **Welche Gefahr besteht?**
:    Was droht bei Missachtung der Gefahr?
:    Wie kann die Gefahr vermieden werden?

---
  
GEFAHR
:    **Welche Gefahr besteht?**
:    Was droht bei Missachtung der Gefahr?
:    Wie kann die Gefahr vermieden werden?
  
---
  
LiesMich
:    **Literaturhinweis**
:    Was lesen?
:    Warum?

------

## Sonderzeichen Zeichen mit Unicode

mit Hilfe von Unicode Formatierungen können Sonderzeichen in die Dokumentation eingefügt werden.

Beispiele:

| Zeichen    | Unicode    | Zeichen    | Unicode    |
| ---------- | ---------- | ---------- | ----------- |
| &#9650;    | `&#9650;`  | &#9651;    | `&#9659;`   |
| &#9652;    | `&#9652;`  | &#9653;    | `&#9659;`   |
| &#9654;    | `&#9654;`  | &#9655;    | `&#9659;`   |
| &#9656;    | `&#9656;`  | &#9657;    | `&#9659;`   |
| &#9658;    | `&#9658;`  | &#9659;    | `&#9659;`   |
| &#9660;    | `&#9660;`  | &#9661;    | `&#9659;`   |
| &#9662;    | `&#9662;`  | &#9663;    | `&#9659;`   |
| &#9664;    | `&#9664;`  | &#9665;    | `&#9659;`   |
| &#9666;    | `&#9666;`  | &#9667;    | `&#9659;`   |
| &#9668;    | `&#9668;`  | &#9669;    | `&#9669;`   |
| &#751;     | `&#751;`   | &#752;     | `&#752;`    |
| &#753;     | `&#753;`   | &#754;     | `&#754;`    |
| &#9632;    | `&#9632;`  | &#9633;    | `&#9633;`   |
| &#9675;    | `&#9675;`  | &#9676;    | `&#9676;`   |
| &#9679;    | `&#9679;`  | &#9744;    | `&#9744;`   |
| &#9746;    | `&#9746;`  | &#10062;   | `&#10062;`  |
| &#9745;    | `&#9745;`  | &#9989;    | `&#9989;`   |
| &#10005;   | `&#10005;` | &#8730;    | `&#8730;`   |
| &#10003;   | `&#10003;` | &#10004;   | `&#10004;`  |
| &#10007;   | `&#10007;` | &#10008;   | `&#10008;`  |
| &#10060;   | `&#10060;` | &#10006;   | `&#10006;`  |
| &#10067;   | `&#10067;` | &#10068;   | `&#10068;`  |
| &#10071;   | `&#10071;` | &#10069;   | `&#10069;`  |

---

Schreibweise Dezimal / Hexadezimal

| Zeichen    | Dezimal    | Zeichen    | Hexadezimal |
| ---------- | ---------- | ---------- | ----------- |
| &#10004;   | `&#10004;` | &#x2714;   | `&#x2714;`  |

---

HINWEIS
:    Die hier gezeigte Liste ist nur ein Auszug aus möglichen Unicode Zeichen. Andere Unicode Zeichen sind möglich, die Darstellung ist abhängig vom System und ist daher zu testen.

------

## Externe Markdown-Dateien einbinden

Externe Markdown-Dateien speichern Sie innerhalb der TIA Portal-Projektstruktur im Ordner `\UserFiles\Code2Docu\files\`.

Markdown-Dateien können auch komplett außerhalb des Projektordners abgelegt werden (z.B. auf einem Netzlaufwerk) und werden bei der Generierung der Dokumentation eingelesen und ihr Inhalt an der markierten Stelle eingefügt.

Um externe Markdown-Dateien in die Dokumentation einzubinden, verwenden Sie folgende Syntax:

```plaintext
{!filename.md!}
```

---

Zwischen den Ausrufezeichen geben Sie den Pfad zur Markdown-Datei an.

---

Hinweis
:    Es wird nur das Dateiformat Markdown mit der Dateinamenserweiterung `md` unterstützt.

---

Sie können auch einen relativen Pfad (relativ zum Ordner `\UserFiles\Code2Docu\files\`) bzw. einen absoluten Pfad oder einen Netzwerkpfad verwenden.
  
Die eingebundenen Markdown-Dateien müssen nicht mit der Dokumentation ausgeliefert werden, da ihr Inhalt während der Generierung bereits in die Dokumentation übernommen wurde.

#### Beispiele

**Relativer Pfad:**

```plaintext
{!sub-directory\filename.md!}
```

---

**Absoluter Pfad:**

```plaintext
{!C:\directory\filename.md!}
```

---

**UNC Netzwerkpfad ("Shared Folder"):**

```plaintext
{!\\server\shared-folder\filename.md!}

oder als URI:

{!file://server/shared-folder/filename.md!}
```

---

Achtung
:    Die externen Markdown-Dateien müssen während der Generierung der Dokumentation erreichbar und lesbar sein, evtl. müssen Zugriffsrechte überprüft werden, gerade wenn die Dateien auf einem Netzlaufwerk gespeichert sind.

---

Hinweis
:    Das Einbinden über das Internet (mittels [URI Schemas](https://de.wikipedia.org/wiki/Uniform_Resource_Identifier#Schema_(Scheme)) wie `http`, `ftp`, etc.) wird nicht unterstützt.

---
