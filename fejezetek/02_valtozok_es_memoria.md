# 2. Változók, elemi típusok és a Memóriamodell (Stack vs. Heap)

A számítógépes programozás legmélyebb lényege az adatok felvétele, memóriában való elhelyezése, logikai átalakítása és biztonságos kezelése. Míg a dinamikus nyelvekben (mint a Python vagy a JavaScript) a változók típusai futásidőben szabadon változhatnak, a modern C# egy **erősen típusos, statikusan ellenőrzött nyelv**.

Ez azt jelenti, hogy a C# fordítóprogramja (Roslyn) még azelőtt ellenőrzi a típusok összeférhetőségét, hogy a program egyetlen sora is lefutna a számítógépen. Ha egy szöveghez számot akarsz hozzáadni, a C# azonnal hibát jelez a szerkesztődben, megelőzve az éles szervereken felbukkanó váratlan leállásokat.

Ebben a fejezetben megértjük a változók logikáját, leleplezzük a számítógép memóriájának két nagy birodalmát: a **Stack (Verem)** és a **Heap (Kupac)** működését, megismerjük az értéktípusok és referenciatípusok közötti döntő különbséget, elsajátítjuk a `var` kulcsszó intelligens típusinferenciáját, a pénzügyi számításokhoz kötelező `decimal` típust, valamint a modern C# egyik legnagyobb innovációját: a **Nullable Reference Types** rendszert, amellyel végleg száműzhetjük a szoftverfejlesztés rettegett „milliárd dolláros hibáját”, a `NullReferenceException`-t.

A fejezet végén egy komplett, éles **Webáruház Pénzügyi Számlázó és Valutakonverziós Esettanulmányt** valósítunk meg!

---

## 2.1 Mi az a változó, és hogyan deklaráljuk a C#-ban?

A változó egy elnevezett rekesz a számítógép munkamemóriájában (RAM), amelyben meghatározott típusú adatot tárolunk.

A klasszikus C# szintaxisban a változó deklarálásakor először megadjuk a **típust**, utána a változó **nevét**, majd az értékadó operátorral (`=`) hozzárendeljük a kezdőértéket:

```csharp
int eletkor = 34;
string felhasznaloNev = "kovacs_bela";
double egyenleg = 15420.50;
bool aktivTagsag = true;
```

### Az intelligens típusinferencia: a `var` kulcsszó
A C# 3.0 óta nem szükséges kézzel kiírnod a típus nevét, ha a jobb oldalon álló értékből a fordító számára 100%-ban egyértelmű, hogy milyen típusról van szó. Erre szolgál a **`var`** kulcsszó:

```csharp
var pontszam = 100;                 // A fordító automatikusan 'int' típusként kezeli!
var arfolyam = 398.50;              // A fordító automatikusan 'double' típusként kezeli!
var uzenet = "Rendszer elindult";   // A fordító automatikusan 'string' típusként kezeli!
```

> [!IMPORTANT] A `var` nem jelent dinamikus típust!
> Nagyon sok, Pythonból vagy JavaScriptből érkező tanuló tévesen azt hiszi, hogy a `var` a C#-ban olyan, mint a Python dinamikus változói vagy a JavaScript `let/var` kulcsszava.
> **Ez óriási tévedés!** A C#-ban a `var` **statikus típusosságot jelent**:
> ```csharp
> var szam = 42;  // A 'szam' változó típusa végérvényesen 'int' lett a fordítás pillanatában!
> // szam = "negyvenketto";  <-- FORDÍTÁSI HIBA! CS0029: Cannot implicitly convert type 'string' to 'int'
> ```
> A `var` csupán gépelést takarít meg a programozónak (Syntax Sugar), a kód futási sebessége és típusbiztonsága pontosan ugyanaz, mintha kiírtad volna, hogy `int`.

### Névadási konvenciók (C# Ipari Szabvány):
* **`camelCase`:** Kis kezdőbetű, minden további szó nagybetűvel indul. Helyi változókhoz és metódusparaméterekhez kötelező: `felhasznaloNev`, `aktualisEgyenleg`, `maxProbalkozas`.
* **`PascalCase`:** Nagy kezdőbetű minden szónál. Osztályokhoz, metódusokhoz, tulajdonságokhoz (Properties) és konstansokhoz kötelező: `CalculateInvoice()`, `CustomerName`.

---

## 2.2 A C# Memóriamodellje: Stack (Verem) vs. Heap (Kupac)

A mély és magabiztos C# tudás legfontosabb sarokköve annak megértése, hogy hogyan gazdálkodik a program a memóriával. A .NET futtatókörnyezetben (CLR) a memória két nagy területre oszlik:

```text
       STACK (Verem)                                HEAP (Kupac)
  ┌───────────────────────┐                  ┌───────────────────────────────┐
  │ • Villámgyors LIFO    │                  │ • Dinamikus, óriási terület   │
  │ • CPU hardveres szint │                  │ • Itt élnek az összetett      │
  │ • Értéktípusok (int)  │                  │   objektumok és stringek      │
  │ • Referenciák mutatói │ ───────────────► │ • A Garbage Collector (GC)   │
  │ • Automatikus törlés  │                  │   takarítja el automatikusan  │
  └───────────────────────┘                  └───────────────────────────────┘
```

1. **Stack (Verem):**  
   * Kisméretű, de elképesztően gyors memóriaterület.
   * LIFO (Last In, First Out) elven működik: amikor belépsz egy metódusba, a helyi változók felkerülnek a verem tetejére; amikor a metódus véget ér, a verem azonnal és automatikusan leugrik róluk. Nincs szükség takarítóra, a felszabadítás azonnali.
2. **Heap (Kupac):**  
   * Óriási, dinamikusan növekvő memóriaterület.
   * Ide kerülnek a komplex, hosszabb életű objektumok, tömbök és szövegek.
   * A Heap takarítását a háttérben futó **Szemétgyűjtő (Garbage Collector - GC)** végzi periodikusan, felkutatva a gazdátlanná vált objektumokat.

---

## 2.3 Értéktípusok (Value Types) vs. Referenciatípusok (Reference Types)

Ez a kettősség a C# architektúrájának legfontosabb fundamentuma:

### 1. Értéktípusok (Value Types - `struct`)
* **Ide tartoznak:** `int`, `long`, `short`, `byte`, `float`, `double`, `decimal`, `bool`, `char`, `enum`, és a saját `struct`-ok.
* **Hogyan tárolódnak?** Közvetlenül magát a **nyers bináris értéket hordozzák** a Stack memóriában.
* **Másoláskor:** Érték szerinti másolás (Copy by Value) történik. Ha átadod egy másik változónak, egy teljesen független fizikai másolat jön létre!

```csharp
int a = 10;
int b = a;  // A 10-es szám LEMÁSOLÓDIK egy új memóriarekeszbe!
b = 20;

Console.WriteLine(a); // 10 (Az eredeti 'a' teljesen sértetlen maradt!)
Console.WriteLine(b); // 20
```

### 2. Referenciatípusok (Reference Types - `class`)
* **Ide tartoznak:** `string`, tömbök (`int[]`), listák (`List<T>`), osztályok (`class`), interfészek, `object`.
* **Hogyan tárolódnak?** Két részből állnak:
  1. Maga a tényleges adat a **Heap (Kupac)** memóriában jön létre.
  2. A Stacken csupán egy apró **memóriacímke (mutató / referencia)** él, amely a Heap-re mutat!
* **Másoláskor:** Referencia szerinti másolás (Copy by Reference) történik. Csak a mutató másolódik le, az adat közös marad!

```csharp
int[] szamokA = new int[] { 1, 2, 3 };
int[] szamokB = szamokA; // Csak a mutató másolódik! Mindkettő ugyanarra a tömbre néz a Heap-en!

szamokB[0] = 99;

Console.WriteLine(szamokA[0]); // 99 -> Az eredeti 'szamokA' is megváltozott!
```

---

## 2.4 Elemi adattípusok összefoglaló táblázata

| Típus kulcsszó | .NET típus | Méret | Értéktartomány / Jellemző | Példa literál |
|---|---|---|---|---|
| **`int`** | `System.Int32` | 4 bájt | -2.14 milliárd és +2.14 milliárd között | `42`, `-105` |
| **`long`** | `System.Int64` | 8 bájt | -9 trillió és +9 trillió között (64 bit) | `9_000_000_000L` |
| **`double`** | `System.Double` | 8 bájt | ~15-17 tizedesjegy pontosság (IEEE 754) | `3.14159` |
| **`decimal`** | `System.Decimal` | 16 bájt | 28-29 tizedesjegy **100% pénzügyi pontosság** | `199.99M` (kötelező 'M' utótag!) |
| **`bool`** | `System.Boolean` | 1 bájt | `true` vagy `false` | `true`, `false` |
| **`char`** | `System.Char` | 2 bájt | Egyetlen Unicode karakter szimpla idézőjellel | `'A'`, `'€'`, `'\n'` |
| **`string`** | `System.String` | Változó | Karakterlánc a Heap-en, immutábilis | `"Helló C#!"` |

> [!WARNING] A lebegőpontos számok csapdája és a kötelező `decimal`
> Ahogyan azt már megtanultuk, a számítógépek a `float` és `double` típusokat kettes számrendszerben tárolják.
> Próbáld ki C#-ban:
> ```csharp
> double d1 = 0.1;
> double d2 = 0.2;
> Console.WriteLine(d1 + d2 == 0.3); // FALSE! (Mert az eredmény 0.30000000000000004)
> ```
> Ezért a C# világában létezik egy kőbe vésett törvény: **Pénzügyi számításokhoz, számlázáshoz, árfolyamokhoz és bankszámlákhoz KIZÁRÓLAG a `decimal` típust szabad használni!** A literál végére kötelező kitenni az `M` vagy `m` betűt:
> ```csharp
> decimal ar1 = 0.1m;
> decimal ar2 = 0.2m;
> Console.WriteLine(ar1 + ar2 == 0.3m); // TRUE! (Garantált 100%-os pontosság!)
> ```

---

## 2.5 Szövegek (`string`): Immutabilitás és String Interpoláció

A C#-ban a szövegek (`string`) referenciatípusok, de különleges tulajdonsággal bírnak: **megváltoztathatatlanok (Immutable)**. Ha egy stringen műveletet hajtasz végre (pl. hozzáfűzöl egy szót), a C# a háttérben **mindig egy vadonatúj string objektumot hoz létre a Heap-en**, a régit pedig otthagyja a szemétgyűjtőnek.

### Modern String Interpoláció (`$""`)
Felejtsd el a régi `String.Format()`-ot vagy a pluszjeles összefűzögetést! A modern C# a dollárjeles interpolációt (`$""`) használja, amelyben kapcsos zárójelekbe (`{}`) közvetlenül beágyazhatunk változókat és formázási specifikációkat:

```csharp
string termek = "Gamer Egér";
decimal ar = 14990.50m;
int darab = 3;

// Beágyazás és formázás:
// :C -> Valuta formátum helyi pénznemben
// :N2 -> Ezres tagolás 2 tizedesjeggyel
Console.WriteLine($"Termék: {termek} | Mennyiség: {darab} db");
Console.WriteLine($"Egységár: {ar:N2} Ft | Végösszeg: {ar * darab:N2} Ft");
```

### Többsoros és Nyers Szövegek (C# 11 Raw String Literals)
Ha JSON-t, SQL parancsot vagy HTML-t kell a C# kódba ágyaznod, a C# 11 bevezette a három idézőjeles nyers szövegeket (`"""..."""`), amelyekben nincs szükség felesleges visszaperjeles escape-elésre (`\"`):

```csharp
string sqlParancs = """
    SELECT id, felhasznalonev, egyenleg
    FROM ugyfelek
    WHERE aktiv = 1 AND egyenleg > 50000
    ORDER BY egyenleg DESC;
    """;
```

---

## 2.6 A „Milliárd Dolláros Hiba” kivédése: Nullable Reference Types (`T?`)

Sir Tony Hoare, a `null` referencia megalkotója 2009-ben nyilvánosan bocsánatot kért a világ programozóitól, „milliárd dolláros hibának” nevezve a null pointer kitalálását. A szoftverfejlesztés történetének legtöbb váratlan szerverleállását és kék halálát az okozta, hogy a kód megpróbált hozzáférni egy olyan objektumhoz, ami valójában nem létezett (`NullReferenceException`).

A C# 8.0 egy forradalmi védelmi vonalat vezetett be: a **Nullable Reference Types (NRT)** rendszert, amely a .NET 8 / 10 / 11 alapértelmezett szabványa!

### Hogyan működik a Null-biztonság?
A C#-ban egy típus alapértelmezésben **NEM LEHET NULL**!
Ha egy változó megengedheti a hiányzó értéket (`null`), ezt kérdőjellel (`?`) kifejezetten jeleznünk kell a fordítónak:

```csharp
string biztosNev = "Kovács Béla"; // Ez a változó SOSEM lehet null!
// biztosNev = null;  <-- A fordító azonnal sárga figyelmeztetést dob!

string? opcionálisCím = null;     // A '?' jelzi: ez az érték HIÁNYOZHAT is!
```

### Biztonságos hozzáférés operátorok:
1. **Null-Conditional Operátor (`?.`):** Csak akkor hívja meg a metódust, ha az objektum nem null:
   ```csharp
   int? hossz = opcionálisCím?.Length; // Ha opcionálisCím null, a hossz is null lesz hiba nélkül!
   ```
2. **Null-Coalescing Operátor (`??`):** Tartalék alapértelmezett értéket ad, ha a bal oldal null:
   ```csharp
   string megjelenítendőCím = opcionálisCím ?? "Nincs lakcím megadva";
   ```
3. **Null-Coalescing Értékadás (`??=`):** Csak akkor ad értéket a változónak, ha az jelenleg null:
   ```csharp
   opcionálisCím ??= "Budapest, Alapértelmezett utca 1.";
   ```

---

## 2.7 Részletes Gyakorlati Esettanulmány: Valutakonverziós és Számlázó Pénzügyi Motor

Építsünk fel egy professzionális, ipari szintű számlázó modult, amely bemutatja:
1. A `decimal` típus 100%-os pénzügyi pontosságát;
2. A Nullable Reference Types (`string?`) és null-biztonsági operátorok (`??`) használatát;
3. A Stack és Heap memóriamegosztás tudatos alkalmazását;
4. A precíz formázást és kerekítést.

### A számlázó motor C# forráskódja

```csharp
// Top-Level Statements és tiszta típusbiztonság a modern .NET-ben
using System;

Console.WriteLine("=====================================================");
Console.WriteLine("    PRSTART PÉNZÜGYI SZÁMLÁZÓ ÉS VALUTAMOTOR (C#)");
Console.WriteLine("=====================================================\n");

// 1. Állandó üzleti konstansok (PascalCase)
const decimal AfaKulcs = 0.27m;                   // 27% magyar ÁFA
const decimal EurHufArfolyam = 398.75m;           // 1 EUR = 398.75 HUF
const decimal IngyenesSzallitasHatar = 25000.00m; // 25 000 Ft felett nincs szállítás
const decimal AlapertelmezettSzallitas = 1990.00m;

// 2. Számlázási folyamat végrehajtása metódussal
void KiallitSzamlat(
    string ugyfelNev,
    string? kuponKod,
    decimal nettoEgysegar,
    int darabszam,
    string penznem = "HUF"
)
{
    Console.WriteLine($"Vevő neve: {ugyfelNev}");
    
    // Null-coalescing operátor a kupon kezelésére:
    string kuponInfo = kuponKod ?? "[Nincs kupon érvényesítve]";
    Console.WriteLine($"Alkalmazott kupon: {kuponInfo}");

    // Részösszeg számítása precíz decimal aritmetikával (Stacken fut!):
    decimal alapar = nettoEgysegar * darabszam;
    decimal kedvezmenySzazalek = 0.0m;

    if (kuponKod == "SPRING20")
    {
        kedvezmenySzazalek = 0.20m; // 20% kedvezmény
    }
    else if (kuponKod == "VIP10")
    {
        kedvezmenySzazalek = 0.10m; // 10% kedvezmény
    }

    decimal kedvezmenyOsszeg = alapar * kedvezmenySzazalek;
    decimal kedvezmenyesNetto = alapar - kedvezmenyOsszeg;

    // Szállítási költség logikája
    decimal szallitasiDij = (kedvezmenyesNetto >= IngyenesSzallitasHatar || kedvezmenyesNetto == 0)
        ? 0.0m
        : AlapertelmezettSzallitas;

    // ÁFA és Bruttó végösszeg kalkulációja
    decimal afaOsszeg = kedvezmenyesNetto * AfaKulcs;
    decimal bruttoVegosszeg = kedvezmenyesNetto + afaOsszeg + szallitasiDij;

    // Pénznem átszámítás, ha EUR-t kértek
    decimal vegsoFizetendo = bruttoVegosszeg;
    string kiirtPenznem = penznem.ToUpper();

    if (kiirtPenznem == "EUR")
    {
        vegsoFizetendo = Math.Round(bruttoVegosszeg / EurHufArfolyam, 2);
    }

    // Professzionális bizonylat kiírása String Interpolációval:
    Console.WriteLine("-----------------------------------------------------");
    Console.WriteLine($"Termék nettó egységár:   {nettoEgysegar,15:N2} Ft");
    Console.WriteLine($"Rendelt darabszám:        {darabszam,15} db");
    Console.WriteLine($"Eredeti részösszeg:       {alapar,15:N2} Ft");

    if (kedvezmenySzazalek > 0)
    {
        Console.WriteLine($"Kupon kedvezmény:        -{kedvezmenyOsszeg,15:N2} Ft ({kedvezmenySzazalek * 100:N0}%)");
        Console.WriteLine($"Kedvezményes nettó:      {kedvezmenyesNetto,15:N2} Ft");
    }

    Console.WriteLine($"27% ÁFA tartalom:         {afaOsszeg,15:N2} Ft");
    Console.WriteLine($"Szállítási díj:           {(szallitasiDij == 0 ? "INGYENES" : $"{szallitasiDij:N2} Ft"),15}");
    Console.WriteLine("=====================================================");
    
    if (kiirtPenznem == "EUR")
    {
        Console.WriteLine($"FIZETENDŐ EURÓBAN:        {vegsoFizetendo,15:N2} EUR");
        Console.WriteLine($"  (HUF egyenérték:        {bruttoVegosszeg,15:N2} Ft)");
    }
    else
    {
        Console.WriteLine($"FIZETENDŐ BRUTTÓ:         {bruttoVegosszeg,15:N2} Ft");
    }
    Console.WriteLine("=====================================================\n");
}

// 3. Rendszertesztek futtatása
KiallitSzamlat(
    ugyfelNev: "Kovács Béla",
    kuponKod: "SPRING20",
    nettoEgysegar: 12500.00m,
    darabszam: 2,
    penznem: "HUF"
);

KiallitSzamlat(
    ugyfelNev: "International Partner Ltd.",
    kuponKod: null, // Szándékosan hiányzó érték (NRT tesztelése!)
    nettoEgysegar: 8500.00m,
    darabszam: 4,
    penznem: "EUR"
);
```

---

## 2.8 Fejezetzáró összefoglaló és gyakorlatok

| Téma | Szintaxis / Eszköz | Fő szabály |
|---|---|---|
| **Deklaráció** | `int x = 10;` | Statikus típusosság, fordítási idejű ellenőrzés. |
| **Típusinferencia** | `var szoveg = "Helló";` | Statikus típusmeghatározás a jobb oldal alapján. |
| **Stack vs. Heap** | Stack (nyers érték), Heap (objektum) | Értéktípusok másolódnak, referenciák mutatnak. |
| **Pénzügyi típus** | `decimal m = 19.99m;` | 100% pontosság, lebegőpontos kerekítési hibák nélkül. |
| **String Interpoláció** | `$"Összeg: {ar:N2} Ft"` | Kifejezések és formátumok beágyazása szövegbe. |
| **Null-biztonság** | `string? nev = null;` | Kérdőjellel engedélyezzük a null értéket. |
| **Null operátorok** | `x?.Length`, `x ?? "alapérték"` | Kivédik a `NullReferenceException` összeomlást. |

### Gyakorlati feladatok

1. **Stack vs. Heap memóriakísérlet konzolon:**  
   Hozz létre egy sima egész változót (`int a = 5; int b = a;`), majd változtasd meg `b`-t! Ezután hozz létre egy egészekből álló tömböt (`int[] t1 = {1, 2}; int[] t2 = t1;`), és változtasd meg a `t2[0]` elemet! Írasd ki a változók értékeit, és figyeld meg a másolás mechanizmusát!
2. **Kamatkalkulátor `decimal` típussal:**  
   Írj egy C# programot, amely bekéri a kezdőtőkét, az éves kamatlábat (pl. 8.5%) és az évek számát. Számítsd ki a kamatos kamattal növelt lejárati összeget a `decimal` modul precizitásával, és jelenítsd meg ezres tagolással!
3. **Null-biztos Felhasználói Profil Kezelő:**  
   Hozz létre egy konzolos alkalmazást, amely kezeli egy felhasználó kötelező nevét (`string`), opcionális becenevét (`string?`) és opcionális telefonszámát (`string?`). Használj null-coalescing (`??`) operátort a hiányzó adatok helyén a `"Nincs megadva"` szöveg elegáns megjelenítésére!

---

### 📖 Útravaló kis szójegyzék a fejezethez

* **Stack (Verem):** Kis méretű, villámgyors memóriaterület a közvetlen értéktípusok és hivatkozási mutatók tárolására.
* **Heap (Kupac):** Óriási, dinamikus memóriaterület az összetett objektumok és szövegek számára, amelyet a Garbage Collector takarít.
* **Értéktípus (Value Type):** Olyan típus, amely közvetlenül magát az értéket hordozza a Stacken (`int`, `double`, `decimal`, `struct`).
* **Referenciatípus (Reference Type):** Olyan típus, amelynek tényleges adatai a Heapen élnek, és csupán egy mutató hivatkozik rá (`string`, `class`, tömbök).
* **NRT (Nullable Reference Types):** A modern C# fordítóvédelme a váratlan `null` értékek és összeomlások ellen.

---

#### Mini Code Review Ellenőrzőlista

Mielőtt továbblépnél a 3. fejezetre, ellenőrizd le a kódodat:

| Szempont | Kérdés magadhoz | Ellenőrzés |
|---|---|---|
| **1. Típushelyesség** | Pénzügyi számításokhoz és árakhoz kizárólag a `decimal` (`m`) típust használtad? | [ ] |
| **2. Null-biztonság** | Ahol egy érték hiányozhat, kitetted a `?` jelet (`string?`), és kezeled a `??` operátorral? | [ ] |
| **3. Névkonvenciók** | Változóknál a `camelCase`, konstansoknál és metódusoknál a `PascalCase` formát követed? | [ ] |
| **4. String formázás** | Régi összefűzögetés helyett a modern `$""` interpolációt alkalmaztad? | [ ] |
| **5. Var tudatosság** | Tisztában vagy azzal, hogy a `var` statikus típust hoz létre a fordítás pillanatában? | [ ] |
