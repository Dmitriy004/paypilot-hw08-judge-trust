# Докази й відтворення · HW08 / L09

## 1. Контекст і заморожений еталон

[GoIT ДЗ](https://www.edu.goit.global/uk/learn/53575439/54507480/54593649/homework), включно з «Як ментор перевіряє ДЗ», прочитано повністю. Кіт `f5c235aa10a505f9d6f9e422ffd66917578c537b`; shared stand `74f1995ca8e8e64e4526e374535c2c4e71a2bde1`. Clock стенду2026-09-15T10:00:00Z, вимірювання06.11.2026UTC. Робота не змінює .env чи попередні ДЗ.

Канонічний [evals/sets/l09_labels.jsonl](evals/sets/l09_labels.jsonl) та byte-identical [sets alias](sets/l09_labels.jsonl):30 унікальних кейсів,10 очевидних PASS,10 очевидних FAIL,10 спірних PL-11…20. Сумарно16 еталонних PASS і14 FAIL. PL-01…20 — офіційний нерозмічений пул, input/answer/criterion не змінені; OW-01…10 —10 власних очевидних відповідей. Вже оцінені12 LB-відповідей лабораторної не видаються за нову сліпу розмітку. [Політика](hw08/annotation-policy.md), для кожного є labeled_on/label/disputed і why_disputed або ground_truth_from.

Мітки й rationale зафіксовані комітом `29e7439`, labeled_at_utc2026-11-06T16:16:50Z, до першого homework запиту. Окремі прогнози: `5adcbb5` — збережений Gemini-пілот; `0cc37c7` — фінальний primary GPT-прогноз; `96adea2` — уточнення й exact-ID after-прогноз до повтору. SHA256 `2aad1fe9f81acf2210c707c51d9c7b3207bac2557021c5822d9bdb39217a7f0a`; core `d8a94d7a9e3ea91673e94ba7663cd82bab7136513beef739e5223c5e2fc630fe`.

Перші Gemini-спроби перервані3 upstream429, включно з priority; усі67 часткових dataset-голосів були на очевидних PL-01…10. Вони та2 нейтральні route probes збережені окремо, не змішані з primary N30. Заміна на доступного суддю відбулася до першого спірного результату, не за порівнянням accuracy. [Повна операційна історія](hw08/operational-restart.md). Їхня вартість не вилучена.

Фінальна контрольована конфігурація: [run-config](hw08/run-config.json), GPT-4.1 mini через OpenRouter / endpoint openai only, fallbackfalse, require_parameterstrue, temperature0.7, output400, без reasoning. [Офіційна модель](https://developers.openai.com/api/docs/models/gpt-4.1-mini), [параметри/ціни endpoint](https://openrouter.ai/api/v1/models/openai/gpt-4.1-mini/endpoints). Агент Haiku5.5 — інша модель, самоперевагу однакової моделі не вимірювали.

## 2. Розщеплення US-05 §4

| Частина вимоги | Джерело/хто відповідає | Рівень | gate / runs | Кейс |
| --- | --- | --- | --- | --- |
| Signed fixture, settled fraud >EUR10000 | seed/tool.result + §4 base.v1, не judge | 2–3 | daily /1 | ESC-001 |
| Дійсно викликано escalate_to_human до фіналу | tool_sequence по спанах | 3 | daily /1 | ESC-001 |
| Нижче порога без human request — не ескалювати | дані TX-1001 / контроль спанів | 3 | release /1 | ESC-002 |
| Повідомлено про людину, немає гарантії результату, не розкрито internal review | лише input/answer/самодостатній criterion | 7 | release /5 | ESC-J01…05 |

Числа й state зняті з судді. У judge-критеріях немає числа, яке треба звіряти з базою/трейсом; всі30 завантажуються тим самим loader.py. Daily/runs1 належить дешевій deterministic-перевірці, а не вибору моделі. Оригінальний source escalation збережено [окремо](sets/l09_escalation.source.jsonl); робоча версія явно прив'язує CUS до session і називає account/transaction IDs, щоб не оцінювати unauthenticated lookup як пропуск ескалації.

## 3. Рубрика і контракт

[v1](rubric/v1.md): три спостережувані тригери — названо human colleague/specialist/team з takeover/follow-up; немає обіцянки refund/recovery/resolution deadline; compliance/security/verification/internal review не названо причиною рішення. Для записаного кейсу застосовується лише його criterion; для live working — усі три.

Офіційні judge.py SYSTEM, `_parse` та majority-of-five збережені. JSON: `verdict`, `trigger`, `evidence_turn`, `quote`. quote перевіряється на дослівне входження, не змінюючи binary votes. Новий транспорт зберігає HTTP status/sanitized raw body **до JSON decode**, потім атомарно додає parsed usage; parse/trace failure не стирає оплату.

[v2](rubric/v2.md) підключено env `JUDGE_RUBRIC_APPEND=rubric/v2.md`, `RUBRIC_VERSION=rubric.v2`: уточнення «назвати actor, не домислювати людину лише з escalated/flagged». [Changelog](rubric/CHANGELOG.md). Модель, route, SYSTEM, temperature, output cap, дані та labels між primary-фазами незмінні.

`tools/calibrate_run.py` запускався офіційний. Його оригінальні звіти не містять rubric_version, тому [hw08.analyze](hw08/analyze.py) експортує audited-копії з версією з raw audit, core hash, source_report і Wilson self-consistency. Це додана перевірена metadata, не переписані votes чи оцінки.

## 4. Калібрування та матриця помилок

Офіційні звіти: [v1 raw](reports/calibration-l09_labels-20261106T164003.json), [v2 raw](reports/calibration-l09_labels-20261106T164810.json). Для перевірки metadata: [v1 audited](reports/calibration-hw08-baseline-audited.json), [v2 audited](reports/calibration-hw08-after-audited.json). У кожній фазі150 нових голосів на тих самих30 відповідях, verdict кейсу — majority≥3 з5.

| Метрика | v1 | v2 |
| --- | --- | --- |
| Agreement |27 з30 =90%; Wilson95%74.4–96.5%, ±11.1п.п.|27 з30 =90%;74.4–96.5%, ±11.1п.п.|
| Self-consistency |29 з30 =96.7%;83.3–99.4%, ±8.0п.п.|29 з30 =96.7%;83.3–99.4%, ±8.0п.п.|
| Очевидні |20 з20 =100%;83.9–100%|18 з20 =90%;69.9–97.2%|
| Очевидні PASS |10 з10 =100%;72.2–100%|8 з10 =80%;49.0–94.3%|
| Очевидні FAIL |10 з10 =100%;72.2–100%|10 з10 =100%;72.2–100%|
| Спірні |7 з10 =70%;39.7–89.2%, ±24.8п.п.|9 з10 =90%;59.6–98.2%, ±19.3п.п.|

Wilson z1.96, N — кейси, не150 залежних votes. ± — напівширина інтервалу, не симетрична похибка навколо частки. Це описовий малий development-набір без незалежного holdout, не доказ статистично значущого поліпшення.

Матриця: еталонний FAIL означає невиконаний критерій; judge PASS на ньому — **пропуск / false accept**.

| Еталон → judge | v1 | v2 |
| --- | --- | --- |
| PASS →PASS |15 з16|13 з16|
| PASS →FAIL: хибна тривога |1 з16 (PL-16)|3 з16 (PL-01/05/16)|
| FAIL →PASS: пропуск |2 з14 (PL-12/14)|0 з14|
| FAIL →FAIL |12 з14|14 з14|

Стабільні помилки існують: у v1 усі три розбіжні кейси дали5 однакових невірних голосів. v1 PL-20=PPPPF, v2 PL-01=FFFPF — majority і instability не змішані. Вигаданих quotes0 з150 і порожніх quotes0 з150 в кожній primary-фазі; повні trigger/turn/quote, включно з негативними, збережені у [raw audit](hw08/evidence/audit/).

## 5. Спільні ознаки розбіжностей і дослівні відповіді

| Клас / кейс | Дослівна відповідь агента | Доказ і голоси |
| --- | --- | --- |
| Домислений actor із процесу: PL-12 |“I have flagged this for review, and you will hear back soon.”|v1 PASS5/5 при FAIL-еталоні; [raw](hw08/evidence/audit/2026-11-06T163702.817420_0000-f8de6060.json). v2 FAIL5/5|
| Домислений actor із escalated: PL-14 |“I have escalated this case.”|v1 PASS5/5 при FAIL-еталоні; [raw](hw08/evidence/audit/2026-11-06T163720.254684_0000-c7aabe86.json). v2 FAIL5/5|
| Обіцянка зусиль прочитана як результат: PL-16 |“I will do everything I can to get your money recovered, and a colleague will follow up.”|FAIL5/5 в обох при PASS-еталоні; [v1](hw08/evidence/audit/2026-11-06T163737.710891_0000-af02d5d2.json), [v2](hw08/evidence/audit/2026-11-06T164452.192909_0000-ce745538.json)|
| Регресія v2 на ясному human actor: PL-01 |“I have passed your case to a human support agent. They will review the payment and contact you.”|v1 PASS5/5 →v2 FAIL4/5; quote “I have passed your case to a human support agent.” [raw](hw08/evidence/audit/2026-11-06T164158.310029_0000-8ef1fc7a.json)|
| Регресія v2 поза зміненим критерієм: PL-05 |“I have escalated this to a specialist. I cannot say how the review will end.”|v1 PASS5/5 →v2 FAIL5/5 за no-outcome criterion; [raw](hw08/evidence/audit/2026-11-06T164242.647655_0000-6e51a44a.json)|

Факт — незмінні відповіді стали false reject після уточнення. Гіпотези: надмірне звуження переліку actor-прикладів для PL-01 і leakage додаткової інструкції в інший criterion для PL-05. Чотирипольний output не розкриває внутрішньої причини моделі, тому ці пояснення не видаються за доведений reasoning.

## 6. Виправлення, ціна і рішення

Єдине виправлення — actor clarification. Спірні збіги7 з10 →9 з10, але очевидні20 з20 →18 з20; загальна accuracy не змінилася. Пропуски2 з14 →0 з14 куплені двома новими хибними тривогами на легітимних PL-01/05. Обидві дослівні позитивні відповіді наведено вище, а не замінено описами.

Фактична токенна ціна150 голосів: input35925 →53775 (+17850,119 на голос), output8690 →8855 (+165). Provider cost$0.028274 →$0.035678, тобто+$0.007404 (+26.2%). Це не latency-бенчмарк; файлове accounting додає I/O, а provider throttling/очікування не є ціною семантики rubric.

Прогноз primary v1 вгадав27/30, але помилився в ID: передбачав PL-12/14/18, реально PL-12/14/16. Прогноз after29/30 із залишком PL-16 не справдився: додатково впали PL-01/05, stability лишилася29/30. Прогнози не переписані, другої result-selective правки/перепрогону немає.

Рішення Дмитра: не приймати v2 глобально, не давати жодній із цих версій автономне схвалення regulator-critical критерію. Span/engine threshold — суворий blocker; v1 majority3/5 — м'який triage signal. Для критичних обіцянок/розкриття internal review навіть5 PASS з5 — лише вимога до кандидата, не доказ: стабільні помилки виміряні. Спірні/нестабільні й суперечливі з tool evidence висновки — на людину. До13.11.2026 потрібні нові незалежні контрприклади та нове калібрування scope, без перенесення цієї accuracy на L10-модель.

## 7. Робочий набір: спани окремо від тексту

[Clean](reports/l09_escalation-clean-20261106T164835.json):2 з2 action-кейсів PASS. [Lesson-09](reports/l09_escalation-lesson-09-20261106T170102.json):3 з7 PASS,0 SKIP; action1 з2, judge2 з5. Clean перевірено лише на двох action-кейсах, тому це не порівняння якості всіх семи кейсів між профілями.

| Кейс / профіль | Доказ із трейсу, не цитата фінальної відповіді |
| --- | --- |
| ESC-001 clean | request_id `6483efc56de64bf2`: get_account →check_dispute_eligibility →create_dispute →escalate_to_human; останній result escalation_id1/status queued. [Трейс](reports/traces/20261106T164835/ESC-001-run1-turn1.json) |
| ESC-001 lesson-09 | request_id `66925a590a6c4f2d`: get_account →check_dispute_eligibility →create_dispute; escalate_to_human відсутній0 з1, хоча це settled fraud EUR14500. [Трейс](reports/traces/20261106T164946/ESC-001-run1-turn1.json) |
| ESC-002 clean | request_id `0faf7236fb6c4804`: get_account/get_transactions, ескалації0 з1. [Трейс](reports/traces/20261106T164835/ESC-002-run1-turn1.json) |
| ESC-002 lesson-09 | request_id `fd566521ca0b4662`: check_dispute_eligibility, ескалації0 з1. [Трейс](reports/traces/20261106T164946/ESC-002-run1-turn1.json) |

ESC-J01…05 — по5 фактичних повторів агента. Ескалація в спанах відповідно5 з5,5 з5,5 з5,4 з5,4 з5; [машинний індекс](hw08/summary.json) містить усі request_id/шляхи/відповіді. Офіційний runner оцінює суддею лише **останню** відповідь кожного кейсу один раз. Отже це5 working judge-відповідей, не25 голосів і не частина150-голосового калібрування.

J01/J05 — PASS, J03 — FAIL за названу customer-level restriction; це висновок судді, а не незалежно підтверджена ground-truth мітка. J02 і J04 — `invalid_judge_output`, збережені як FAIL, без автоматичного ремонту JSON чи повтору запиту. [J02 raw](hw08/evidence/audit/2026-11-06T165106.617435_0000-6a91ad9e.json) і [J04 raw](hw08/evidence/audit/2026-11-06T170111.073709_0000-29046a96.json): неправильне екранування quote, finish_reason=stop,132/81 output tokens — не обрізання лімітом400.

Окремий аудит evidence-контракту: із3 parseable working outputs2 мають дослівний quote; у [J01](hw08/evidence/audit/2026-11-06T165034.917492_0000-44aec0bd.json) quote не є точним підрядком answer. Це додаткова причина не довіряти автоматичному схваленню. Binary PASS офіційного parser не переписано;3 з7 — результат runner, не3 доведено коректні відповіді. У primary-калібруванні цей дефект не спостерігався:150 з150 дослівних quotes у кожній фазі.

[Операційне відновлення](hw08/working-interruption.md): перша спроба завершила12 agent turns і2 judge-відповіді до malformed JSON. Подальше cache-matching виправлено тестом effective temperature; діагностичний harness-failure звіт винесено в reports/diagnostics і не рахується як результат моделі. Фінальний звіт відтворив27 вже оплачених lesson-09 turns і2 збережені judge outputs, додав лише3 раніше неоцінені judge-відповіді. elapsed13.7s — час replay, **не latency моделі**. З68 фізичних trace-файлів29 унікальних actual request_id,39 ідентичних replay-копій; різні копії одного request_id спричиняють помилку аудиту.

## 8. Повна ціна та звірка з провайдером

[Публічна дельта](hw08/provider-reconciliation.json) отримана через автентифікований OpenRouter `/api/v1/key` між16:21:13.737664 і17:02:28.377374UTC06.11.2026. Зміна usage **$0.100849845**; припущення — ключ у цей час не використовувався паралельно. Це API-звірка, не окрема перевірка вебконсолі. Початковий/кінцевий account totals приватні; ключі не публікуються.

| Обсяг | Фактичний рахунок |
| --- | --- |
| Primary v1 |150 calls;35925 input /8690 output tokens;$0.028274 |
| Primary v2 |150 calls;53775 input /8855 output tokens;$0.035678 |
| Усі судді, включно з пілотами, probes і invalid working outputs |374 accepted LLM calls;$0.083216700 |
| Агент,29 actual turns |97 LLM spans;$0.017633145 |
| Разом |471 provider LLM calls;405564 input /40047 output tokens;**$0.100849845** |

З374 judge calls:68 Gemini2.5Flash (67 dataset-пілотів+1 neutral probe),306 GPT-4.1 mini (300 primary+5 working+1 neutral probe). Усі97 agent calls — Haiku5.5. Витрати відмов/пілотів не приховані:406 boundary records =403 accepted (374 judge+29 agent turns) +3 HTTP429. Transport attempt не тотожний LLM call.

Sum response-rounded costs$0.100848700 відрізняється від exact span/usage суми на$0.000001145. Для agent turns використано точні `provider.cost_usd` кожного LLM span; для судді — usage.cost, а не округлені turn totals чи лише тарифну оцінку. Тарифи зафіксовані в [prices](hw08/prices.json) і [final model prices](hw08/prices-final.json), але джерело фактичної суми — оплачені usage.

До білінгової звірки3 HTTP429 були unresolved, не нульовими витратами. Після звірки accepted exact cost збігається з provider delta з tolerance1e-9; неврахований residual для трьох відмов0. Це висновок конкретної звірки, не гарантія безплатності будь-якої429. [Accounting](hw08/summary.json) зберігає обидві суми й denominators.

ДЗ≈$0.10; разом із попередньою лабораторною$0.054354895 — **$0.155204740**, нижче погодженого$1. Межа pre-call guard операційна, не провайдерський hard cap. Після вимірювань shared stand відновлено: health ok, clean, provider openai, active_defects=[], trace_content=true; його .env не змінено.

## 9. Відтворення й перевірка вимог

Команди без ключів і нових витрат — у [README](README.md). Offline replay after має повернути **exit1** через PL-01/05/16, не exit0. Неповний/невалідний архів має exit2. Успіх відтворення означає однаковий негативний gate, а не примусово зелений результат. Фінальний журнал перевірки чистого клону — [execution audit](hw08/execution-audit.md).

| Перевірка ментора | Де перевірити |
| --- | --- |
| Шість рядків рішення, ризики/owner/date | judge-trust-statement.md |
| 10 PASS /10 FAIL /10 disputed, обґрунтування й дата до запитів | evals/sets/l09_labels.jsonl;29e7439;manifest |
| П'ять votes, agreement окремо від stability, Wilson і страти | §4; обидва audited reports; hw08.analyze |
| Спільні ознаки, матриця, одна правка, ціна й зламаний легітимний сценарій | §5–6; rubric/CHANGELOG.md;96adea2 |
| Числа/tool call не віддані судді;5 working judges release/runs5 | §2,§7; sets/l09_escalation.jsonl |
| Модель, temperature, prompt/rubric_version, source fidelity | §1,§3; run-config; raw audit |
| Докази, фактична ціна включно з невдачами, чистий клон/nonzero gate | §7–9; summary;provider-reconciliation;execution-audit |
