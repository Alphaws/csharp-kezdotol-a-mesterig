# 1. Bevezetés, .NET SDK és a modern C# környezet

Üdvözöllek a modern C# és a .NET izgalmas világában! Ha korábban hallottál már a C#-ról, felejtsd el az elavult sztereotípiákat: a C# ma már nem egy Windows-hoz láncolt, nehézkes technológia, hanem az iparág egyik leggyorsabb, legelegánsabb, teljesen nyílt forráskódú és platformfüggetlen fejlesztői környezete.

Ebben a fejezetben megértjük a .NET platform működését, beállítjuk a fejlesztői környezetet Linuxon, macOS-en és Windowson, és megírjuk életünk első modern C# programját.

---

## 1.1 Mi a .NET és hogyan működik a C# a háttérben?

Amikor C# kódot írsz, az nem közvetlenül gépi kóddá alakul, mint a C vagy C++ esetében, de nem is futásidőben sorról sorra értelmeződik, mint a tiszta Python szkriptek. A .NET egy intelligens, kétlépcsős fordítási modellt alkalmaz:

```text
  [ C# Forráskód (.cs) ]
            │
            ▼  (Roslyn fordító / dotnet build)
  [ Köztes Nyelv / Bytecode (IL - Intermediate Language) (.dll) ]
            │
            ▼  (Common Language Runtime - CLR)
  [ JIT Fordító (Just-In-Time Compiler) a futtatáskor ]
            │
            ▼
  [ Natív Gépi Kód (CPU utasítások: x64, ARM64) ]
```

### A .NET verziók és a kiadási ciklus (LTS vs. STS)

A modern szoftverfejlesztésben elengedhetetlen ismerni a technológia életciklusát. A Microsoft kiszámítható, éves ritmusban adja ki az új .NET verziókat (minden év novemberében):

| Verzió | Típus | C# nyelvverzió | Szerepe a fejlesztésben | Támogatási időtartam |
|---|---|---|---|---|
| **.NET 8** | **LTS** | C# 12 | A jelenlegi globális nagyvállalati alappillér. Stabil, kiforrott, a legtöbb éles rendszer ezen fut. | 3 év (hosszú távú) |
| **.NET 9** | STS | C# 13 | Gyorsabb kiadás felhő- és AI-optimalizációkkal, hibrid gyorsítótárazással (`HybridCache`). | 2 év (szabványos távú) |
| **.NET 10** | **LTS** | C# 14 | A legfrissebb hosszú távú vállalati szabvány: új LINQ motor, zéró allokációs optimalizációk. | 3 év (hosszú távú) |
| **.NET 11** | STS / Preview | C# 15 | A legújabb kísérleti és fejlesztői funkciók (Extension Properties, NPU integráció). | 2 év (szabványos távú) |

*Tipp:* Ha a gépeden régebbi .NET 8, vagy a legfrissebb .NET 10 / .NET 11 fut (például a `11.1.100` SDK), a könyv összes alapvető kódja hibátlanul és garantáltan működni fog, hiszen a C# szigorúan ügyel a visszafelé kompatibilitásra!

### A rendszer kulcselemei:
1. **Roslyn fordító:** Amikor kiadod a `dotnet build` parancsot, a C# kódot egy platformfüggetlen köztes nyelvre (**IL – Intermediate Language**) fordítja.
2. **CLR (Common Language Runtime):** A .NET virtuális gépe (futtatókörnyezete). Ez felel a memóriakezelésért, a szemétgyűjtésért (Garbage Collection), a típusbiztonság ellenőrzéséért és a szálkezelésért.
3. **JIT (Just-In-Time) fordító:** Amikor elindítod a programot, a JIT fordító az IL kódot villámgyorsan átalakítja a számítógéped processzora által közvetlenül értelmezhető natív gépi kódra. Sőt, a legújabb .NET verziók képesek **Native AOT** (Ahead-Of-Time) fordításra is, amellyel közvetlenül, futtatókörnyezet nélkül induló natív bináris fájlt kapunk!

---

## 1.2 Fejlesztői környezet kialakítása

> [!TIP]
> ### 💡 Nulladik lépés teljesen kezdőknek: Mi az a terminál és a parancssor?
> Ha még soha nem programoztál: a terminál (Windowson a PowerShell vagy CMD, Linuxon/macOS-en a Bash/Zsh) nem más, mint egy közvetlen szöveges vezérlőablak a gépedhez. Nem egérrel kattintasz, hanem begépeled a parancsot (pl. `dotnet --version`), és a gép azonnal válaszol. Minden parancs, amit itt látsz, a terminálba gépelendő be.

### 1. A .NET SDK telepítése
A kódoláshoz a **.NET SDK**-ra (Software Development Kit) van szükségünk, amely tartalmazza a fordítót, a futtatókörnyezetet és a `dotnet` parancssori eszközt.

* **Linux (Ubuntu / Debian):**
  ```bash
  sudo apt-get update && sudo apt-get install -y dotnet-sdk-8.0
  ```
* **macOS (Homebrew-val):**
  ```bash
  brew install dotnet-sdk
  ```
* **Windows:**
  Töltsd le az ingyenes telepítőt a hivatalos oldalról: `https://dotnet.microsoft.com/download`

A telepítés ellenőrzése a terminálban:
```bash
dotnet --version
```
Ha megjelenik a verziószám (pl. `8.0.xxx`, `9.0.xxx` vagy `10.0.xxx`), a géped készen áll a munkára!

### 2. A kódszerkesztő (IDE)
Bármilyen szövegszerkesztő megfelel, de a két legnépszerűbb és leghatékonyabb eszköz:
- **Visual Studio Code (Ingyenes, könnyű, cross-platform):** Telepítsd hozzá a hivatalos **C# Dev Kit** kiegészítőt.
- **Visual Studio Community (Windowsra):** Nagyvállalati szintű, mindent magában foglaló ingyenes környezet.

---

## 1.3 Az első C# projektünk a `dotnet` CLI-vel

Felejtsük el az egérrel való kattintgatást: a modern fejlesztők a `dotnet` parancssori eszközt használják. Hozzunk létre egy új konzolos alkalmazást!

Nyiss meg egy terminált, és add ki a következő parancsokat:

```bash
# 1. Hozzunk létre egy új projektmappát:
mkdir ElsoCSharpProjektem
cd ElsoCSharpProjektem

# 2. Hozzunk létre egy új konzolos C# sablont:
dotnet new console

# 3. Futtassuk a projektet:
dotnet run
```

A képernyőn azonnal megjelenik:
```text
Hello, World!
```

Nézzük meg, mi jött létre a mappánkban:
* **`ElsoCSharpProjektem.csproj`:** A projekt konfigurációs fájlja XML formátumban (itt szerepel a célverzió, pl. `<TargetFramework>net8.0</TargetFramework>`).
* **`Program.cs`:** A tényleges C# forráskódunk!

---

## 1.4 A modern C# forradalma: Top-Level Statements

Nyisd meg a generált `Program.cs` fájlt egy szerkesztőben! Korábban a C# hírhedt volt arról, hogy egy egyszerű szöveg kiírásához is rengeteg bonyolult formai sallang kellett:

```csharp
// RÉGI, NEHÉZKES C# (Így nézett ki régen):
using System;

namespace ElsoProjektem
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello, World!");
        }
    }
}
```

A modern C#-ban (C# 9 és afelett) mindezt elfelejthetjük! A fenti felesleges sallang helyett a `Program.cs` ma már mindössze ennyi:

```csharp
// MODERN C# (Top-Level Statements):
Console.WriteLine("Helló, modern C# világ!");
```

A háttérben a fordítóprogram láthatatlanul legenerálja a `Program` osztályt és a `Main` belépési pontot, így nekünk csak arra kell figyelnünk, ami valóban számít: a tiszta logikára!

---

## 1.5 Interaktív bemenet és string interpoláció

Írjunk egy barátságos, interaktív programot, amely bekéri a felhasználó nevét és születési évét, majd üdvözli őt!

Módosítsd a `Program.cs` fájl tartalmát az alábbira:

```csharp
// Interaktív üdvözlő program C# nyelven
Console.Write("Kérlek, add meg a neved: ");
string nev = Console.ReadLine() ?? "Ismeretlen";

Console.Write("Hány éves vagy? ");
string eletkorSzoveg = Console.ReadLine() ?? "0";

// Típusátalakítás: szövegből egész szám
int eletkor = int.Parse(eletkorSzoveg);
int szuletesiEv = DateTime.Now.Year - eletkor;

// String interpoláció a $ jellel (hasonló a Python f-stringhez):
Console.WriteLine($"\nÜdvözöllek, {nev}!");
Console.WriteLine($"Körülbelül {szuletesiEv}-ben születtél.");
```

Futtasd a terminálból a `dotnet run` paranccsal!

---

## 1.6 Git gyorstalpaló C# projektekhez

Minden professzionális projekt alapja a verziókövetés. A C# projekteknél különösen fontos a `.gitignore` fájl, mert a fordítás során ideiglenes bináris fájlok (`bin/`, `obj/`) jönnek létre, amelyeket szigorúan tilos gitbe menteni!

A .NET CLI automatikusan tud generálni tökéletes C# `.gitignore` fájlt:

```bash
# 1. Hozzunk létre egy hivatalos .NET gitignore fájlt:
dotnet new gitignore

# 2. Inicializáljuk a Git-et:
git init

# 3. Készítsük el az első commitunkat:
git add .
git commit -m "init: elso C# projektem letrehozasa"
```

---

## 1.7 Fejezetzáró gyakorlatok és feladatok

1. **Környezetellenőrzés:** Nyisd meg a terminált, és hívd meg a `dotnet --info` parancsot! Nézd meg, milyen SDK-k és futtatókörnyezetek találhatók a gépeden.
2. **Karakter-banner készítő:** Készíts egy konzolos C# programot, amely bekéri a felhasználó nevét a `Console.ReadLine()`-nal, majd kiírja azt egy csillagokból (`*`) álló díszkeretben!
3. **Napi bölcsesség kalkulátor:** Kérd be a felhasználó születési évét, és számold ki, hogy hány napot élt eddig körülbelül (`eletkor * 365.25`), majd írd ki szépen formázott f-string/interpolált formában!

---

### 📖 Útravaló kis szójegyzék a fejezethez

* **.NET SDK:** Fejlesztői csomag, amely a fordítót (`csc`), a futtatót és a parancssori eszközöket tartalmazza.
* **CLR (Common Language Runtime):** A .NET virtuális gépe, amely gondoskodik a program futtatásáról, memóriájáról és biztonságáról.
* **Top-Level Statements:** Modern C# nyelvi funkció, amellyel a felesleges `class Program` és `static void Main` burkoló kód elhagyható.
* **String Interpoláció (`$""`):** Szövegformázási technika, amellyel változókat közvetlenül a szövegbe ágyazhatunk: `$"Helló {nev}!"`.

