
# Markdown syntax (Cheat Sheet)

This chapter lists the examples of the supported MarkDown language commands and gives a brief overview of the supported syntax.

## Chapter / headings / titles

Headings are supported up to the 5th order and prefixed with `#`.  
The first three headings are numbered. The fourth and fifth order headings correspond to the block title in Word, whereby the fifth order heading is included in the table of contents.

```plaintext
# First order heading
## Second order heading
### Third-order heading
#### Fourth-order heading ( Block Title)
##### Fifth-order heading ( Block Title incl. table of contents)
```

## Paragraphs / Line Breaks

To create a paragraph with Markdown, simply write text of any length. The line before and the line after must be empty.

Simple line breaks are created at the end of the line with two spaces before the line break itself, or with a hard line break at the end of the line `\`.  
Without these spaces, the line break is not recognized as such, so it can be used in the MarkDown source for simple structuring.

## Horizontal line and Page break

Horizontal lines are created with three hyphens `---`.

**Appearance**

---

Page breaks are created with six hyphens `------`.  

---

NOTE
:    Before or after figures, lists, tables, note boxes, math blocks or code blocks, three hyphens `---` create a blank line.

#### Example:

```plaintext
Text before

---

Figure, List, Table, Note box, Math block or Code block

---

Text afterwards
```

------

## Text formatting

With Markdown you can use the following text formatting:

| Formatting                                     | Appearance                                     |
| ---------------------------------------------- | ---------------------------------------------- |
| This text is \*italic\*                        | "This text is *italic*"                        |
| This text is \_italic\_                        | "This text is _italic_"                        |
| This text is \*\*BOLD \*\*                     | "This text is **BOLD**"                        |
| This text is \_\_BOLD \_\_                     | "This text is __BOLD__"                        |
| This text is \*\*\*BOLD and Italic\*\*\*       | "This text is ***BOLD and Italic***"           |
| This text is \_\*\*BOLD and Italic\*\*\_       | "This text is _**BOLD and Italic**_"           |
| This test is \~\~strikethrough\~\~             | "This text is ~~strikethrough~~"               |
| This text is \~subscript\~                     | "This text is ~subscript~"                     |
| This text is \^superscript\^                   | "This text is ^superscript^"                   |
| This text is \=\=yellow highlighted/marked\=\= | "This text is ==yellow highlighted/marked=="   |

## Lists / Enumerations

Markdown supports sorted and unsorted lists (enumerations).

#### Unsorted lists

You create unsorted lists with an asterisk followed by a space. You can indent a subordinate list with three spaces.

```plaintext
* Unsorted list with nesting
   1. simple subordinated sorted list
   2. further list entry
* second unsorted list entry
```

---

**Appearance**

* Unsorted list with nesting
   1. simple subordinated sorted list
   2. further list entry
* second unsorted list entry

#### Sorted lists

You create sorted lists with a number followed by a dot and a space.

```plaintext
1. Simple sorted list with nesting
   * unsorted child list
   * second list entry
2. further list entry
```

---

**Appearance**

1. Simple sorted list with nesting
   * unsorted child list
   * second list entry
2. further list entry

------

## Indented text / Block Quote / Quotations

You can get an indented text for e.g. quotes with `>` followed by a space.

```plaintext
> Block Quote  
second line in quote
```

---

**Appearance**

> block quote  
second line in quote

## Inline code

Create `inline-code` with surrounding back-ticks \`code\`.

## Code block

Insert a code block with three preceding and ending back-ticks or tildes, together with the abbreviation of the programming language, e.g. `SCL`:

~~~plaintext
```scl
stringVariable := 'code with syntax highlighting';
FunctionCall(stringVariable);
```
~~~

---

**Appearance**

```scl
stringVariable := 'code with syntax highlighting';
FunctionCall(stringVariable);
```

## Math formulas

Mathematical formulas can be generated with the notation from LaTeX / TexMath.

This is an inline $math block$ surrounded by `$` - `$math block$`.

`$\int_0^\infty \frac{x^3}{e^x-1}\,dx = \frac{\pi^4}{15}$`

**Appearance**

$\int_0^\infty \frac{x^3}{e^x-1}\,dx = \frac{\pi^4}{15}$

```plaintext
$$
  \int_0^\infty \frac{x^3}{e^x-1}\,dx = \frac{\pi^4}{15}
$$
```

---

**Appearance**
$$
  \int_0^\infty \frac{x^3}{e^x-1}\,dx = \frac{\pi^4}{15}
$$

---

NOTE
:    It is also possible to include mathematical formulas in the form of images instead of working with LaTeX scripts.

------

## Hyperlink

You can create hyperlinks without and with link text in square brackets.

Direct hyperlink:  
`https://support.industry.siemens.com`

**Appearance**

https://support.industry.siemens.com

Hyperlink with link text:  
`[go to SIEMENS Industry Support](https://support.industry.siemens.com)`

**Appearance**

[go to SIEMENS Industry Support](https://support.industry.siemens.com)

**Spaces in filename or path**

Relative Hyperlinks including spaces can be created by enclosing them between the `<` and `>` characters :

`[LCode2Docu_DemoType_FC.htm](<../../../../../code2doc_demo/UserFiles/UserDocumentation/en-US/Library Types/LCode2Docu_DemoType_FC.htm>)`

--- 

NOTE
:    Relative paths can only be displayed as Hyperlinks in HTML but not in Word or PDF documents.

------

## Graphics / Images ( Figures )

Graphics and images to be used in the documentation are stored within the TIA Portal project structure in the folder `\UserFiles\Code2Docu\images\`.

Images can also be stored outside of the project folder structure and will be copied automatically into the `images` folder. You can configure such an external image path in the `Settings`. For further information please see chapter `Dialog box Settings / Code2Docu options`.

You can also store PowerPoint presentations in the `images` folder directly as well as in the configured external image folder. The slides of each presentation are exported as `png` image files and saved in the same folder as their corresponding presentation. The names of the exported image files follow the pattern `PresentationName_SlideNumber.png`. If a presentation contains only a single slide, then the underscore and slide number are omitted from the resulting image file name.

To include images in the documentation, use the following syntax:

`![ALT text] (path/image.PNG "optional title")`.

In the square brackets, specify the alt attribute. In the round brackets, specify the relative path using the slash `/` to the image. This way it is also possible to group images in subdirectories. Optionally you can specify a title in quotes.

---

NOTE
:    The following file formats for graphics and images are supported:  
`png`, `jpg`, `bmp`, `svg`.
:    Space in Name or Path of Image file should be avoided. 

#### Examples

Image indented with text (text width):

`![Code2Docu Graphic](subFolder/Code2Docu_ProcessFlow.PNG "Code2Docu - Process Flow")`

**Appearance**

![Code2Docu - Process Flow](subFolder/Code2Docu_ProcessFlow.PNG "Code2Docu - Process Flow")

------

Image over full page width with attribute `{.pageWidth}` in the line before the image:

```plaintext
{.pageWidth}
![Code2Docu Graphic](subFolder/Code2Docu_ProcessFlow.PNG "Code2Docu - Process Flow")
```

---

**Appearance**

{.pageWidth}
![Code2Docu - Process Flow](subFolder/Code2Docu_ProcessFlow.PNG "Code2Docu - Process Flow")

------

## Tables

You can use tables for a clear arrangement of data and texts.

### Simple table (Pipe Table)

Pipe tables are created from vertical bars `|` and hyphens `-` as well as the texts. You can use colons `:` in the separator between the header and the rest of the lines to specify the alignment of the text.

Table indented with the text:  

```plaintext
| tables      | are           | great |
| ----------- |:-------------:| -----:|
| column 1 is | left aligned  |   456 |
| column 2 is | centered      |   123 |
| column 3 is | right aligned | 0815  |
```

---

**Appearance**

| tables      | are           | great |
| ----------- |:-------------:| -----:|
| column 1 is | left aligned  |   456 |
| column 2 is | centered      |   123 |
| column 3 is | right aligned | 0815  |

---

Table over full-page width without indentation with prefixed attribute [pageWidth]:

```plaintext
{.pageWidth}
| tables      | are           | great |
| ----------- |:-------------:| -----:|
| column 1 is | left aligned  |   456 |
| column 2 is | centered      |   123 |
| column 3 is | right aligned | 0815  |
```

---

**Appearance**

{.pageWidth}
| tables      | are           | great |
| ----------- |:-------------:| -----:|
| column 1 is | left aligned  |   456 |
| column 2 is | centered      |   123 |
| column 3 is | right aligned | 0815  |

---

NOTE
:    Tables are always to be considered as independent paragraphs, i.e. there must always be a blank line before and after a table.

------

### Complex table (Grid Table)

Grid tables additionally use the plus sign `+` and equal sign `=`. The plus sign defines the nodes of the grid lines, and the equal sign defines the separation between the header row and the rest of the rows. Grid tables allow multiple rows per cell as well as connecting a cell across multiple columns. 
 
 The following figure shows you a simple grid table:

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

**Appearance**

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

#### Rules

* A table must be preceded by a blank line, and the table must then start with the column separator `+`.
* Each column separator starts with an optional space...
  * followed by an optional `:` to specify left alignment, followed by optional spaces (alignment can be specified on the first line) 
  * followed by a sequence of at least one `-` character, followed by optional spaces
  * followed by an optional `:` to specify the right alignment (or the middle alignment if the left alignment is also defined)
  * followed by optional spaces

* A table header is separated with `+========+` instead of `+---------+`.
* The first line separator must be followed by a *regular line*. 
* A regular line must start with the `|` character, which starts at the same position as the `+` column separator of the first line separator.
* A regular line can continue a previous regular line if the column separators `|` are in the same position as the previous line. If they are in the same position, the column can span several columns.
* The last column separator `|` can be omitted.
* A table must not have irregularly shaped cells.
* The respective width of the columns is calculated from the ratio of the total size of the first table row without considering the `+`:  
`+----+--------+----+` would be divided into `4/16 = 25%, 8/16 = 50%, 4/16 = 25%`.

---

A grid table can have cells that span columns as well as rows.

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

**Appearance**

+---+---+---+
| AAAAA | B |
+---+---+ B +
| D | E | B |
+ D +---+---+
| D | CCCCC |
+---+---+---+

A cell can be connected by columns as well as by rows.

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

**Appearance**

+---+---+---+
| AAAAA | B |
+ AAAAA +---+
| AAAAA | C |
+---+---+---+
| D | E | F |
+---+---+---+  

------

## Note boxes

You create note boxes as follows:  
The first line is set in a new paragraph and contains the keyword. The second line starts with a colon `:` and FOUR spaces. This is followed by the text over several lines. The final line is an empty line followed by a horizontal line `---` which is not visible in the document.

A blank line before the hint box can also be generated with `---` and a blank line in front of the note box.

The keywords are (English / German):

* NOTE / Hinweis
* NOTICE / Achtung
* CAUTION / Vorsicht
* WARNING / Warnung
* DANGER / Gefahr
* ReadMe / LiesMich

---

```plaintext

---

NOTE
:    indicates an advantage. Has tip character.
:    New line in the box.

---

```

---

**Appearance**

NOTE
:    Indicates an advantage, has the character of a Tipp.
  
---
  
NOTICE
:    **What is the danger?**
:    What threatens if the danger is disregarded?
:    How can the danger be avoided?

---
  
CAUTION
:    **What is the danger?**
:    What threatens if the danger is disregarded?
:    How can the danger be avoided?

---
  
WARNING
:    **What is the danger?**
:    What threatens if the danger is disregarded?
:    How can the danger be avoided?
  
---
  
DANGER
:    **What is the danger?**
:    What threatens if the danger is disregarded?
:    How can the danger be avoided?
  
---
  
ReadMe
:    **Reference to literature**
:    What to read?
:    Why?

------

## Special characters with Unicode

Unicode formatting can be used to insert special characters into the documentation.

Examples:

| Character  | Unicode    | Character  | Unicode     |
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

Decimal / Hexadecimal notation

| Character  | Decimal    | Character  | Hexadecimal |
| ---------- | ---------- | ---------- | ----------- |
| &#10004;   | `&#10004;` | &#x2714;   | `&#x2714;`  |

---

NOTE
:    The list shown here is only an selection of possible Unicode characters. Other Unicode characters are possible, the display depends on the system and must therefore be tested.

------

## Include external Markdown files

External Markdown files to be included in the documentation are stored within the TIA Portal project structure in the folder `\UserFiles\Code2Docu\files\`.

Markdown files can also be stored outside of the project folder structure (e.g. on a network drive). They will be read and their contents will be included at the marked positions when generating the documentation.

To include external Markdown files in the documentation, use the following syntax:

```plaintext
{!filename.md!}
```

---

Specify the path to the Markdown file between the exclamation marks.

---

NOTE
:    Only the file format Markdown with the file name extension `md` is supported.

---

You can also specify a relative path (relative to the folder `\UserFiles\Code2Docu\files\`), an absolute path or a network path.

Included Markdown files do not need to be delivered together with the documentation as their contents have already been included when the documentation has been generated.

#### Examples

**Relative path:**

```plaintext
{!sub-directory\filename.md!}
```

---

**Absolute path:**

```plaintext
{!C:\directory\filename.md!}
```

---

**UNC network path ("shared folder"):**

```plaintext
{!\\server\shared-folder\filename.md!}

or as a URI:

{!file://server/shared-folder/filename.md!}
```

---

NOTICE
:    The external Markdown files have to be accessible and readable when the documentation is generated. You might have to check the file permissions, especially if the files are stored on a network drive.

---

NOTE
:    Including files over the internet (using [URI schemes](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier#Syntax) like `http`, `ftp`, etc.) is not supported.

---
