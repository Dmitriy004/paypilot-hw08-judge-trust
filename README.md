# ДЗ_8 — Judge Trust Statement, L09

[Рішення про довіру](judge-trust-statement.md) · [вимірювання й докази](calibration-appendix.md) · [машинний аудит](hw08/summary.json).

## Обов'язкові файли

- `evals/sets/l09_labels.jsonl` — канонічні30 кейсів:10 очевидних PASS,10 очевидних FAIL,10 спірних; мітки й обґрунтування зафіксовано до запитів.
- `sets/l09_labels.jsonl` — byte-identical alias для незміненого loader.py / tools/calibrate_run.py; source pool PL-01…20 збережено, додано OW-01…10.
- `sets/l09_escalation.jsonl` — working threshold daily/runs1, контроль і5 judge-кейсів release/runs5. Текст не доводить tool call.
- `rubric/v1.md`, `rubric/v2.md`, `rubric/CHANGELOG.md` — три спостережувані тригери та одне версійоване уточнення.
- `reports/calibration-hw08-baseline-audited.json`, `reports/calibration-hw08-after-audited.json` — офіційні голоси з перевіреною metadata версії; оригінальні звіти calibrate_run теж збережені.
- `hw08/evidence/`, `reports/traces/` — навмисно збережені вхідні дані для незалежного offline-аудиту. `hw08/private/`, .env, ключі, логи й IDE-файли не публікуються.

## Перевірка чистого клону — без ключа та нових витрат

```powershell
python -m unittest discover -v
python -m hw08.analyze
python -m hw08.replay reports/calibration-hw08-after-audited.json
```

`replay` обчислює majority з усіх5 votes, а не довіряє полю agree. Exit0 — усі збіглися з еталоном; exit1 — є розбіг; exit2 — неповні/невалідні дані. Негативний gate не слід «лагодити» зміною міток. Це offline replay фактичного досліду, не новий запит до моделі.

Docker-еквівалент (сусідній shared stand або явний STAND_DIR):

```powershell
$env:STAND_DIR='C:/Users/Admin/PycharmProjects/paypilot-stand-shared'
docker --context desktop-linux compose run --rm --entrypoint python eval -m unittest discover -v
docker --context desktop-linux compose run --rm --entrypoint python eval -m hw08.replay reports/calibration-hw08-after-audited.json
docker --context desktop-linux compose run --rm eval --set l09_labels --dry-run
docker --context desktop-linux compose run --rm eval --set l09_escalation --gate daily --dry-run
```

У Linux використайте власний STAND_DIR і звичайний `docker compose`, якщо немає контексту desktop-linux. Шлях вище — приклад цього Windows-середовища, не обов'язкова структура. Код stdlib; залежності не встановлюються. Runner повертає nonzero і за FAIL, і за SKIP; тест all-SKIP ловить початкову помилку офіційного кіту.

## Умови вимірювання

Фінальний суддя: **openrouter:openai/gpt-4.1-mini**, provider.only=openai, fallbacks=false, require_parameters=true, temperature0.7, max_tokens400. Неррассуждаюча модель: reasoning-параметр не надсилається. Модель агента окремо: anthropic/claude-haiku-5.5, reasoning off. [Конфігурація](hw08/run-config.json), [тарифи](hw08/prices-final.json).

Обидві повні фази на тих самих30 відповідях і тому самому маршруті; відрізняється лише додане уточнення рубрики/версія. Мітки, input, answer_under_test, criterion і set_hash незмінні. Прогноз перед after — окремий коміт. Невдалі прогнози не переписані.

Початкові Gemini-пілоти перервалися через upstream429: [операційна історія](hw08/operational-restart.md). Усі часткові результати/відмови/neutral probes збережені й входять у витрати, але не в primary N30. Модель вибрано через доступність, не за результатом спірної третини.

Фактичний calibrate_run.py запускався без зміни parser/majority. `hw08.calibrate` лише відновлює збережений успішний prefix після transport interruption, перевіряючи точний prompt/settings; не повторює його оплату й не робить прихованих retries. Для нового досліду потрібен новий LAB_AUDIT_DIR, він явно передається compose; не дописуйте нові голоси до завершеного архіву. Основні команди досліду:

```powershell
# OPENROUTER_API_KEY — лише process environment, значення ніде не виводити.
docker --context desktop-linux compose run --rm -e OPENROUTER_API_KEY -e LAB_PHASE=baseline -e LAB_PROVIDER_ROUTE=openai -e JUDGE_MODEL=openrouter:openai/gpt-4.1-mini -e TEMP=0.7 -e RUNS=5 --entrypoint python eval -m hw08.calibrate l09_labels
docker --context desktop-linux compose run --rm -e OPENROUTER_API_KEY -e LAB_PHASE=after -e LAB_PROVIDER_ROUTE=openai -e JUDGE_MODEL=openrouter:openai/gpt-4.1-mini -e RUBRIC_VERSION=rubric.v2 -e JUDGE_RUBRIC_APPEND=rubric/v2.md -e TEMP=0.7 -e RUNS=5 --entrypoint python eval -m hw08.calibrate l09_labels
```

Числа/поріг/виклик інструменту — рівні2–3, не judge. П'ять live working-кейсів запускаються офіційним runner по5 agent repeats; у цій версії він судить останній answer один раз. Це не150-vote recorded-answer calibration і не ще25 незалежних judge-голосів.

Межа витрат — операційний pre-call guard$0.85 для main, із запасом під попередню лабораторну й збережені пілоти в агрегатному$1. Це не гарантія білінг-ліміту для довільних великих запитів. Невідома вартість не дорівнює нулю;3 відмови залишаються unresolved до звірки з provider delta. Фінальний облік — за точними usage.cost / provider.cost_usd, не тільки тарифною оцінкою. Snapshot account totals приватний, публікується лише експериментальна дельта.

Офіційний [README джерельного кіту](docs/README.upstream.md) збережено окремо. Калібрувальні кейси не переносяться до golden без окремого рішення. Для L10 потрібно заново виміряти іншу модель, а не перенести число довіри цього судді.
