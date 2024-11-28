# German Website Crawler

## Reference

- [Wortschatz Goethe-Zertifikate | DWDS](https://www.dwds.de/lemma/wortschatz-goethe-zertifikat)
- [API (Schnittstellen zum DWDS) | DWDS](https://www.dwds.de/d/api#wb-list-goethe)

## Listen Wortschatz Goethe-Zertifikat

Das DWDS bietet 3 Listen an, die Struktur der JSON-Daten finden Sie in der nachfolgenden Tabelle dokumentiert:

- [Wortschatz für das Goethe-Zertifikat A1 als CSV](https://www.dwds.de/api/lemma/goethe/A1.csv)
- [Wortschatz für das Goethe-Zertifikat A1 als JSON](https://www.dwds.de/api/lemma/goethe/A1.json)
- [Wortschatz für das Goethe-Zertifikat A2 als CSV](https://www.dwds.de/api/lemma/goethe/A2.csv)
- [Wortschatz für das Goethe-Zertifikat A2 als JSON](https://www.dwds.de/api/lemma/goethe/A2.json)
- [Wortschatz für das Goethe-Zertifikat B1 als CSV](https://www.dwds.de/api/lemma/goethe/B1.csv)
- [Wortschatz für das Goethe-Zertifikat B1 als JSON](https://www.dwds.de/api/lemma/goethe/B1.json)

Die CSV-Dateien sind derart gegliedert, dass es für jede gültige Schreibung eines Wortes bzw. Ausdrucks eine separate Zeile mit allen im DWDS-Wörterbuch dazu vorhandenen Angaben gibt. Sind bei einem Eintrag mehrere Genera bzw. bestimmte Artikel möglich, werden diese durch Komma getrennt. Beispielauszug:

```csv
"Lemma","URL","Wortart","Genus","Artikel","nur_im_Plural"
"abschließen","https://www.dwds.de/wb/abschlie%C3%9Fen","Verb","","","0"
"Ahnung","https://www.dwds.de/wb/Ahnung","Substantiv","fem.","die","0"
"Leute","https://www.dwds.de/wb/Leute","Substantiv","","","1"
"Teil","https://www.dwds.de/wb/Teil","Substantiv","mask., neutr.","der, das","0"
```

Die Struktur der JSON-Daten finden Sie in der nachfolgenden Tabelle dokumentiert:

| Feldname    | Beschreibung                                                                            |
| ----------- | --------------------------------------------------------------------------------------- |
| articles    | optional, bei Nomen: Liste mit entsprechenden bestimmten Artikeln (der, die, das)       |
| genera      | optional: Liste der zum Lemma gehörigen Genera (mask., fem., neutr.)                    |
| onlypl      | optional: fester Wert nur im Plural, falls ein Wort nur im Plural verwendet werden kann |
| pos         | Wortart, siehe Wortarten im DWDS                                                        |
| sch         | Liste mit Schreibungen bzw. Formen im Wörterbuchartikel                                 |
| sch / lemma | Schreibung des Lemmas                                                                   |
| sch / hidx  | optional: Homographenindex (bei mehreren Wörterbucheinträgen wie ¹Bank und ²Bank)       |
| url         | kanonische URL zum zugehörigen Wörterbuchartikel                                        |

### Wortarten im DWDS

| Feldname               | Chinese Translation | Description                                                                                                                                        | example                     |
| ---------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| Substantiv             | 名词                | a word used as the name of a person, animal, place, state, or thing.                                                                               | `Haus`, `Hund`              |
| Eigenname              | 专有名词            | a name that is used to refer to a particular person, place, or thing.                                                                              | `Berlin`, `Peter`           |
| Kardinalzahl           | 基数词              | a number used to count things.                                                                                                                     | `eins`, `zwei`              |
| Ordinalzahl            | 序数词              | a number that shows the position of something in a list.                                                                                           | `erste`, `zweite`           |
| Pronomen               | 代词                | a word that is used instead of a noun or a noun phrase.                                                                                            | `ich`, `du`                 |
| Personalpronomen       | 人称代词            | a pronoun that is used to show who is affected by an action.                                                                                       | `ich`, `du`                 |
| Possessivpronomen      | 物主代词            | a pronoun that shows who something belongs to.                                                                                                     | `mein`, `dein`              |
| Reflexivpronomen       | 反身代词            | a pronoun that refers to the subject of a sentence.                                                                                                | `mich`, `dich`              |
| Indefinitpronomen      | 不定代词            | a pronoun that does not refer to any specific person or thing.                                                                                     | `man`, `jemand`             |
| Demonstrativpronomen   | 指示代词            | a pronoun that points to a particular thing or person.                                                                                             | `dieser`, `jener`           |
| Interrogativpronomen   | 疑问代词            | a pronoun that is used to ask questions.                                                                                                           | `wer`, `was`                |
| Adjektiv               | 形容词              | a word that describes a noun or pronoun.                                                                                                           | `gut`, `schön`              |
| Komparativ             | 比较级              | the form of an adjective or adverb that is used to compare two things.                                                                             | `besser`, `schöner`         |
| Superlativ             | 最高级              | the form of an adjective or adverb that is used to say that one thing is better, worse, etc., than all others.                                     | `am besten`, `am schönsten` |
| partizipiales Adjektiv | 分词形容词          | a word that is formed from a verb and used like an adjective.                                                                                      | `gelesen`, `gekocht`        |
| Verb                   | 动词                | a word that is used to describe an action, state, or occurrence.                                                                                   | `gehen`, `essen`            |
| Adverb                 | 副词                | a word that is used to describe a verb, an adjective, another adverb, or a sentence and that is often used to show time, manner, place, or degree. | `schnell`, `gut`            |
| Pronominaladverb       | 代词副词            | a word that is used as an adverb but that is formed from a pronoun.                                                                                | `dort`, `deshalb`           |
| Präposition            | 介词                | a word or group of words that is used with a noun, pronoun, or noun phrase to show direction, location, or time, or to introduce an object.        | `in`, `auf`                 |
| Präposition + Artikel  | 介词 + 冠词         | a word or group of words that is used with a noun, pronoun, or noun phrase to show direction, location, or time, or to introduce an object.        | `im`, `aufs`                |
| Konjunktion            | 连词                | a word that joins together sentences, clauses, phrases, or words.                                                                                  | `und`, `oder`               |
| bestimmer Artikel      | 定冠词              | a word that is used with a noun to show that the noun is known to the reader or listener.                                                          | `der`, `die`, `das`         |
| Interjektion           | 感叹词              | a word or phrase that is used to express a strong feeling of surprise, pleasure, or anger.                                                         | `Ach!`, `Oh!`               |
| Partikel               | 助词                | a word that is used with a verb to express a particular grammatical meaning.                                                                       | `nicht`, `ja`               |
| Affix                  | 词缀                | a letter or group of letters that is added to the beginning or end of a word to change its meaning.                                                | `un-`, `-los`               |
| Mehrwortausdruck       | 复合词              | a group of words that functions as a single unit and that has a meaning of its own.                                                                | `Fußball`, `Hochzeit`       |
| Symbol                 | 符号                | a letter, group of letters, character, or picture that is used instead of a word or group of words.                                                | `+`, `=`, `&`               |
