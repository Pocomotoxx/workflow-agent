# Fork karbantartása

[🇬🇧 English](Maintaining-the-Fork.md) · 🇭🇺 Magyar

Cél: a saját fejlesztésed úgy legyen biztonságban, hogy egy upstream-frissítés vagy szinkron sose
írhassa felül.

## Kezdjük a jó hírrel

- Ebben a repóban **nincs automatikus upstream-szinkron**. Semmilyen workflow, action vagy
  Dependabot-beállítás nem húz be a `openai/openai-agents-python`-ból. Magától semmi nem szinkronizál.
- Upstream-kód csak **kézzel** kerülhet ide: a GitHub **„Sync fork"** gombjával, vagy ha a gépeden
  `git pull`/`git merge`/`git reset` parancsot futtatsz egy upstream remote ellen.

A „biztonságban maradás" tehát főként arról szól, hogy ezt a két dolgot *nem* teszed meg — és ha
akarod, teljesen le is választod.

## 1. szint — lokális védelem (ezt most csináld meg)

Minden klónban, amiben dolgozol, távolítsd el az upstream remote-ot, hogy egy véletlen pull ne érje
el:

```bash
git remote remove upstream        # ha létezik
git remote -v                     # csak az 'origin' látszódjon -> a te forkod
```

Ha alkalmi cherry-pickeléshez meg akarod tartani az upstreamet, tartsd **csak-fetch** módban, és
sose fésüld a saját ágadba:

```bash
git remote set-url --push upstream DISABLED
```

## 2. szint — sose kattints a „Sync fork" gombra

GitHubon a repódon lévő **„Sync fork"** gomb az upstream alapértelmezett ágát fésüli a tiédbe. Nem
törli némán a commitjaidat, viszont konfliktusokat vagy nem kívánt merge-commitokat okozhat. Hagyd
békén. Védd is a `main`-t: **Settings → Branches → Add rule** a `main`-re (PR-t kérj, a force-push
legyen tiltva), így semmi nem írja át az előzményedet.

## 3. szint — teljes leválasztás a fork-hálózatról (választható, végleges)

A GitHub még mindig *forknak* jelöli ezt a repót, ezért mennek az új PR-ek alapból az upstreamre, és
ezért jelenik meg a „Sync fork" gomb. Hogy önálló repó legyen belőle:

**A lehetőség — kérd a GitHub Supportot.** A GitHub le tudja választani a forkot a szülő-hálózatról.
Nyiss kérést a <https://support.github.com/> oldalon („detach my fork into a standalone repository").
Az URL, a csillagok és az előzmény megmarad.

**B lehetőség — újra létrehozás friss repóként (teljes kontroll, új URL).**

```bash
# 1. Hozz létre egy ÜRES új repót GitHubon (ne forkot), pl. Pocomotoxx/agents-platform
# 2. Tükrözd bele az előzményedet:
git clone --bare https://github.com/Pocomotoxx/workflow-agent.git tmp-mirror
cd tmp-mirror
git push --mirror https://github.com/Pocomotoxx/agents-platform.git
cd .. && rm -rf tmp-mirror
# 3. Állítsd a munkaklónodat az új originre:
git remote set-url origin https://github.com/Pocomotoxx/agents-platform.git
```

Az új repó nem tagja semmilyen fork-hálózatnak, így a `gh pr create` alapból rá irányul, és nincs
„Sync fork" gomb. Utána archiváld vagy töröld a régi forkot.

## Konkrét upstream-javítások átvétele később (szándékosan)

A leválasztás nem jelenti, hogy sose vehetsz át egy upstream-javítást — csak azt, hogy semmi nem
történik magától. Amikor *akarsz* egy konkrét upstream-változást, szándékosan cherry-pickeld:

```bash
git remote add upstream https://github.com/openai/openai-agents-python.git   # ideiglenesen
git fetch upstream
git log --oneline upstream/main -20            # keresd meg a kívánt commitot
git cherry-pick <sha>                          # csak azt az egyet alkalmazd
git remote remove upstream                     # válaszd le újra
```

## Licenc-megjegyzés

A fork MIT-licencű. Az upstream szerzői jogi megjelölést (© 2025 OpenAI) meg kell tartani a
`LICENSE`-ben. A saját hozzájárulásaidhoz hozzáadhatsz egy saját copyright-sort, például:

```
Copyright (c) 2025 OpenAI
Copyright (c) 2026 Pocomotoxx (fork modifications)
```

Az eredeti megjelölést ne töröld — ezt az egyet követeli meg az MIT-licenc egy forktól.
