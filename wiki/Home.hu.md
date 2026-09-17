# Wiki — Agents SDK (providerfüggetlen fork)

[🇬🇧 English](Home.md) · 🇭🇺 Magyar

Üdv. Ez a wiki a fork saját kiegészítéseit írja le, és azt, hogyan tartsd függetlenül az
upstreamtől. Az alap-SDK részletes API-leírásához a `docs/` oldalt használd (MkDocs-szal építve).

## Oldalak

- **[Telepítés](../INSTALL.hu.md)** — a fork és eszközeinek beállítása.
- **[Providerek](Providers.hu.md)** — futtatás bármelyik nyelvi modellen, OpenAI-kulcs nélkül.
- **[Funkciók](Features.hu.md)** — a vezénylő, a rendszergyár és a vizuális tervező.
- **[Fork karbantartása](Maintaining-the-Fork.hu.md)** — maradj leválasztva az upstreamről, hogy egy
  szinkron sose írja felül a munkádat.

## Mi ez a fork

A [openai/openai-agents-python](https://github.com/openai/openai-agents-python) önálló forkja (MIT,
© 2025 OpenAI), amelyben a „bármelyik provider" lett az alapérték, és amely kiegészült
munkafolyamat-vezényléssel, rendszergenerálással és vizuális tervezővel — miközben az eredeti
`agents` API érintetlen marad.

## A wiki közzététele GitHubon

Ezek az oldalak a repóban, a `wiki/` mappában élnek, így a kóddal együtt verziózódnak. Ha
GitHub-wikiként is ki szeretnéd szolgálni: kapcsold be a **Settings → Features → Wikis** opciót, majd
másold be ezeket a fájlokat a wikibe (a wiki külön git-repó a
`github.com/Pocomotoxx/agents-python.wiki.git` címen), vagy nézegesd őket itt, a `wiki/` mappában.
